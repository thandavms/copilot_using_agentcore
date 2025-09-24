# AgentCore Deployment - Copilot Chat Application

A Streamlit-based chat application that integrates with AWS Bedrock AgentCore Runtime to provide AI-powered conversational capabilities with persistent memory, knowledge base search, and web search functionality.

## Features

- **Interactive Chat Interface**: Clean Streamlit web interface for conversations
- **Persistent Memory**: Session-based memory management using AgentCore
- **Knowledge Base Search**: Query integrated knowledge bases for specific information
- **Web Search**: Real-time web search capabilities via Tavily API
- **Session Management**: Multiple conversation sessions with unique identifiers
- **AWS Integration**: Deployed using AWS Bedrock AgentCore Runtime

## Architecture

- **streamlit_app.py**: Main chat interface and user interaction layer
- **agent.py**: Core agent logic with tools and memory management
- **agentcore_runtime.py**: AgentCore Runtime entrypoint for deployment
- **pages/**: Additional Streamlit pages for sessions and settings management

## Requirements

See `requirements.txt` for dependencies:
- strands-agents & strands-agents-tools
- bedrock-agentcore & bedrock-agentcore-starter-toolkit
- boto3 for AWS services
- tavily-python for web search
- python-dotenv for configuration

## Configuration

Configure the following variables in your environment or directly in the code:
- AWS region and credentials
- Bedrock model ID and guardrails
- Knowledge base ID
- Tavily API key for web search
- Memory configuration (Memory ID and ARN)

## Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Docker Deployment
```bash
docker build -t copilot-agent .
docker run -p 8080:8080 copilot-agent
```

### AgentCore Runtime
The application is designed to run as an AWS Bedrock AgentCore Runtime agent. Deploy using the provided `deploy_agentcore.ipynb` notebook.

## Usage

1. Access the web interface
2. Start a conversation in the main chat page
3. Use "New Chat" to start fresh sessions
4. Navigate to Sessions page to manage conversation history
5. Configure settings through the Settings page

The agent automatically determines when to use knowledge base search vs. web search based on the query context.