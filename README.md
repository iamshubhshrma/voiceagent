# 🎙️ Vani: Voice-Activated AI Agent With MCP and Custom Tools Integration

**Vani** is an intelligent, voice-interactive assistant built using **LangChain** and **LangGraph**. It leverages the **Model Context Protocol (MCP)** to bridge the gap between Large Language Models and local execution, providing a hands-free experience for managing files, browsing the web, and controlling Windows applications.



## ✨ Features

* **Voice-First Interface**: Native Speech-to-Text (STT) and Text-to-Speech (TTS) integration for a completely hands-free workflow.
* **MCP Integration**: Dynamic tool loading via Model Context Protocol, including local filesystem access and Tavily-powered web search.
* **Application Orchestration**: Ability to launch Windows applications like Chrome, Notepad, Excel, and Word through natural language.
* **Contextual Memory**: Powered by LangGraph's `MemorySaver`, allowing the agent to remember previous parts of the conversation within a session.
* **Speech Optimization**: Automatically cleans Markdown artifacts (like `**` or `#`) from LLM responses to ensure natural-sounding speech output.



## 🛠️ Prerequisites

* **Python**: 3.10 or higher (if running from source).
* **Node.js**: Required to execute MCP servers via `npx`.
* **Environment Variables**:
  * `GOOGLE_API_KEY`: Your Gemini API key.
  * `TAVILY_API_KEY`: (Optional) For web search capabilities.



## 🚀 Installation & Setup

1. **Clone the Repository**:
```bash
   git clone https://github.com/iamshubhshrma/voiceagent.git
   cd voiceagent
```

2. **Install Dependencies**:
```bash
   pip install requirements.txt
```
   *Note: If you encounter issues with PyAudio on Windows, use `pip install pipwin` followed by `pipwin install pyaudio`.*

3. **Configure Environment**:
```bash
   # Windows PowerShell
   $env:GOOGLE_API_KEY="your_key_here"
```


## 💻 Usage

Run the agent with the following command:
```bash
python agent.py
```

Once the agent says "Hi, I'm Vani," you can give commands such as:

* *"Create a python file named hello.py in this directory."*
* *"Open Chrome and search for the latest machine learning trends."*
* *"Launch Notepad and write a quick to-do list."*
* *Say "Exit" or "Goodbye" to terminate the session.*



## 📦 Windows Executable (.exe)

For a more convenient experience, you can use the standalone Windows executable. This version bundles the Python runtime and all necessary libraries into a single folder, so you don't need to manage a Python environment.

### **Download**

> 📥 [**VaniAssistant (.exe)**](https://drive.google.com/file/d/1F86oeBSBbDkegfCToqlfn9kangh3Deyt/view?usp=sharing)

### **Setup & Running the EXE**

1. **Extract**: Download the ZIP file and extract the contents to a folder on your PC.
2. **Node.js Dependency**: Since Vani uses MCP tools, you **must** have [Node.js](https://nodejs.org/) installed on your system for the filesystem and search tools to work.
3. **API Key**:
   * Open **Start**, search for "Environment Variables," and select "Edit the system environment variables."
   * Click **Environment Variables** and add a new User Variable named `GOOGLE_API_KEY` with your key as the value.
4. **Run**: Double-click `VaniAssistant.exe` to launch the assistant.



## 🔧 Technical Stack

| Component | Technology |
|:---|:---|
| **Orchestration** | LangGraph / LangChain |
| **Model** | Gemini 2.5 Flash |
| **Tool Protocol** | Model Context Protocol (MCP) |
| **Voice Processing** | SpeechRecognition & Pyttsx3 |
| **Storage** | LangGraph MemorySaver |
