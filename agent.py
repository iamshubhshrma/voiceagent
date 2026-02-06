import asyncio
import os
import sys
import webbrowser
import subprocess
import speech_recognition as sr
import pyttsx3
from datetime import datetime
from typing import Optional

# --- LOGGING FIX ---
# Suppress specific warnings from langchain_google_genai about unsupported schema keys
# This cleans up the console output while keeping the agent functional
import logging
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)

# --- Latest LangChain Agents Framework ---
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver

# # --- Hugging Face Imports (The Change) ---
# from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


# --- Configuration ---
ALLOWED_DIRECTORY = os.path.abspath(".")

# --- 1. Voice Input/Output Setup ---

def speak(text: str):
    """Converts text to speech using pyttsx3."""
    try:
        engine = pyttsx3.init()
        # Remove Markdown artifacts for smoother speech
        clean_text = text.replace("*", "").replace("#", "").replace("`", "")
        engine.say(clean_text)
        engine.runAndWait()
    except Exception as e:
        print(f"🔇 TTS Error: {e}")

def listen() -> Optional[str]:
    """Captures audio from the microphone and converts it to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening... (Speak now)")
        try:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("⏳ Recognizing...")
            text = r.recognize_google(audio)
            print(f"🗣️ You said: {text}")
            return text
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except Exception as e:
            print(f"Mic Error: {e}")
            return None

# --- 2. Custom Local Tools ---

@tool
def open_browser(url: str) -> str:
    """Opens a website in the default browser (ensure url has protocol)."""
    if not url.startswith('http'):
        url = 'https://' + url
    webbrowser.open(url)
    return f"Browser opened to {url}"

@tool
def open_app(app_name: str) -> str:
    """Opens a Windows application (notepad, calculator, chrome, edge, cmd, etc)."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "start chrome",
        "edge": "start msedge",
        "command prompt": "start cmd",
        "excel": "start excel",
        "word": "start winword"
    }
    cmd = apps.get(app_name.lower())
    try:
        if cmd:
            subprocess.Popen(cmd, shell=True)
            return f"Launched {app_name}"
        else:
            os.startfile(app_name)
            return f"Attempted to launch {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {e}"

# --- 3. Main Application Loop ---

async def run_voice_agent():
    # --- MCP Server Configuration ---
    mcp_servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", ALLOWED_DIRECTORY],
            "transport": "stdio"
        }
    }
    
    if os.environ.get("TAVILY_API_KEY"):
        mcp_servers["tavily"] = {
            "command": "npx",
            "args": ["-y", "@mcptools/mcp-tavily"],
            "transport": "stdio",
            "env": {"TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY")}
        }

    print("🔌 Connecting to Tools...")
    
    # A. Setup Tools - Use MultiServerMCPClient without context manager
    mcp_tools = []
    try:
        client = MultiServerMCPClient(mcp_servers)
        mcp_tools = await client.get_tools()
        print(f"✅ Loaded {len(mcp_tools)} MCP tools.")
    except Exception as e:
        print(f"⚠️ Warning: MCP tools failed to load ({e}). Using local tools only.")
        mcp_tools = []

    all_tools = mcp_tools + [open_browser, open_app]
    all_tools = mcp_tools + [open_browser, open_app]
    
    # B. Setup Model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        convert_system_message_to_human=True
    )

    # B. Setup Hugging Face Model
        # We use Llama-3-8B-Instruct for its excellent tool-following capabilities
    # print("🤗 Loading Llama-3.1-8B-Instruct from Hugging Face...")
        
    # llm = HuggingFaceEndpoint(
    #     repo_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
    #     task="text-generation",
    #     max_new_tokens=512,
    # )
    #     # ChatHuggingFace wraps the LLM to provide the Chat interface agents need
    # model = ChatHuggingFace(llm=llm)

    # C. Create Prompt Template for Agent
    prompt = """You are vani, an intelligent and helpful voice-activated assistant designed to assist users with various tasks through natural conversation.
**Your Capabilities:**
You have access to multiple tools that allow you to:
1. **File System Operations**: Read, write, search, and manage files and directories
2. **Web Browsing**: Open websites and URLs in the default browser
3. **Application Control**: Launch Windows applications (Notepad, Calculator, Chrome, Excel, Word, etc.)
4. **Web Search** (if available): Search the internet for current information using Tavily

**Tool Usage Guidelines:**
- ALWAYS use tools when the user's request requires external actions (opening apps, accessing files, browsing websites)
- Call tools proactively without asking for permission first - the user expects you to take action
- You can use multiple tools in sequence to accomplish complex tasks
- If a tool fails, try alternative approaches or inform the user clearly
- When using filesystem tools, work within the allowed directory: 

**Response Style:**
- Keep responses CONCISE and CONVERSATIONAL - this is voice output, not text
- Avoid long explanations unless specifically asked
- Speak naturally as if having a real conversation
- When performing actions, briefly confirm what you're doing (e.g., "Opening Chrome now" or "I found 3 files")
- Don't repeat the user's request back to them unnecessarily
- Use simple language and avoid technical jargon unless appropriate

**Behavior Standards:**
- Be proactive: If you can complete a task with available tools, do it immediately
- Be helpful: Offer suggestions or alternatives if the exact request isn't possible
- Be efficient: Complete tasks in the fewest steps necessary
- Be clear: If you need more information to proceed, ask specific questions
- Be honest: If you cannot do something, explain why clearly and suggest alternatives

**Examples of Good Responses:**
❌ BAD: "I understand you want me to open Notepad. Let me use the open_app tool to launch Notepad for you."
✅ GOOD: "Opening Notepad now."

❌ BAD: "I have successfully completed the task of creating a file named example.txt in your directory."
✅ GOOD: "Created example.txt."

❌ BAD: "Would you like me to search for information about Python programming?"
✅ GOOD: *Just searches and provides the information*

Remember: You're a voice assistant - be quick, natural, and action-oriented!"""
    

    # D. Create Agent with Checkpointer (Single Thread Memory)
    memory = MemorySaver()
    
    agent = create_agent(
        model=model,
        tools=all_tools,
        system_prompt=prompt,
        checkpointer=memory
    )

    speak("Hi, I'm vani. How can I help you today?")
    print("\n🤖 Agent Online. Waiting for voice commands...")
    print("💡 Tip: Say 'exit', 'stop', or 'quit' to end the session.\n")

    # E. Run Loop with Single Thread Configuration
    config = {"configurable": {"thread_id": "voice_session"}}
    
    while True:
        user_text = listen()
        if not user_text: 
            continue

        # Exit conditions
        if any(w in user_text.lower() for w in ["exit", "stop", "quit", "goodbye"]):
            speak("Goodbye. Have a great day!")
            break

        print("🤔 Processing...")
        
        try:
            # Invoke agent with checkpointer memory
            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_text)]},
                config=config
            )
            
            # Extract the last AI message
            if "messages" in response and len(response["messages"]) > 0:
                last_message = response["messages"][-1]
                output = last_message.content if hasattr(last_message, 'content') else str(last_message)
                
                if output:
                    print(f"💡 Response: {output}")
                    speak(output)
                else:
                    fallback = "I completed the task."
                    print(f"💡 {fallback}")
                    speak(fallback)
            else:
                fallback = "I completed the task."
                print(f"💡 {fallback}")
                speak(fallback)
                    
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            print(f"❌ Error: {e}")
            speak(error_msg)

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable not set.")
        print("   Set it using: export GOOGLE_API_KEY='your-api-key'")
        sys.exit(1)
    else:
        try:
            asyncio.run(run_voice_agent())
        except KeyboardInterrupt:
            print("\n👋 Exiting gracefully...")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            sys.exit(1)