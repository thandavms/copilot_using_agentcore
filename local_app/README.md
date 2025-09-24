# Copilot Streamlit App

A lightweight Streamlit frontend for the Copilot AI agent with persistent memory and knowledge base access.

## Features

- 🤖 AI Assistant with persistent memory
- 🔍 Knowledge base search capabilities  
- 🌐 Web search integration (Tavily)
- 💬 Interactive chat interface
- 📝 Session management and history
- 🔧 Environment status monitoring

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file with the following variables:
   ```
   MEMORY_ID=your_memory_id
   BEDROCK_MODEL_ID=your_model_id
   KNOWLEDGE_BASE_ID=your_kb_id
   TAVILY_API_KEY=your_tavily_key
   REGION=us-east-1
   GUARDRAIL_ID=your_guardrail_id
   GUARDRAIL_VERSION=1
   GUARDRAIL_TRACE=enabled
   AWS_REGION=us-east-1
   ```

3. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

1. **Environment Check:** The sidebar shows the status of all required environment variables
2. **Session Management:** Create new sessions or load previous ones
3. **Chat Interface:** Ask questions and get responses with persistent memory
4. **Tools:** The agent automatically uses knowledge base search or web search as needed

## Architecture

- `agent.py`: Core agent functionality and tools
- `streamlit_app.py`: Lightweight UI frontend
- Clean separation between backend logic and UI components

## Tools Available

- **Knowledge Base Search**: For questions about Agentic AI Memory
- **Web Search**: For general questions using Tavily API
- **Persistent Memory**: Maintains context across sessions per actor