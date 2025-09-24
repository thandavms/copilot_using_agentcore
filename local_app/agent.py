"""
ADP Copilot Backend - Core agent functionality extracted from notebook
"""
import os
import uuid
import boto3
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Load environment variables
load_dotenv()

@tool
def knowledge_base_search(query: str) -> str:
    """Search the knowledge base for relevant information."""
    try:
        print("Calling Knowledgebase to retrieve information")
        kb_id = os.getenv("KNOWLEDGE_BASE_ID")
        if not kb_id:
            return "Error: KNOWLEDGE_BASE_ID environment variable not set"
        
        region = os.getenv("AWS_REGION", "us-east-1")
        client = boto3.client('bedrock-agent-runtime', region_name=region)
        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': query},
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 3}}
        )
        
        results = []
        for result in response.get('retrievalResults', []):
            content = result.get('content', {}).get('text', '')
            results.append(content)
        
        return f"Knowledge Base Results: {' '.join(results)}" if results else "No results found"
    except Exception as e:
        return f"Knowledge base search error: {str(e)}"

@tool 
def web_search(query: str) -> str:
    """Search the web for current information using Tavily."""
    try:
        from tavily import TavilyClient
        print("Calling WEB SEARCH to retrieve information")

        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return "Error: TAVILY_API_KEY environment variable not set"
        
        client = TavilyClient(api_key=tavily_api_key)
        response = client.search(query=query, max_results=3)
        
        results = []
        for result in response.get('results', []):
            title = result.get('title', 'No title')
            content = result.get('content', 'No content')
            url = result.get('url', 'No URL')
            results.append(f"{title}: {content} ({url})")
        
        return f"Web search results: {' | '.join(results)}" if results else "No web results found"
    except Exception as e:
        return f"Web search error: {str(e)}"

class CopilotAgent:
    """Main agent class for Copilot functionality"""
    
    def __init__(self, actor_id: str = "default_user", session_id: Optional[str] = None):
        self.actor_id = actor_id
        self.session_id = session_id or str(uuid.uuid4())
        self.memory_id = os.getenv('MEMORY_ID')
        self.region = os.getenv('REGION', 'us-east-1')
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with memory and tools"""
        try:
            # Configure memory
            agentcore_memory_config = AgentCoreMemoryConfig(
                memory_id=self.memory_id,
                session_id=self.session_id,
                actor_id=self.actor_id
            )
            
            ac_session_manager = AgentCoreMemorySessionManager(
                agentcore_memory_config=agentcore_memory_config,
                region_name=self.region
            )
            
            # Configure Bedrock model
            bedrock_model = BedrockModel(
                model_id=os.getenv("BEDROCK_MODEL_ID"),
                guardrail_id=os.getenv("GUARDRAIL_ID"),
                guardrail_version=os.getenv("GUARDRAIL_VERSION", "1"),
                guardrail_trace=os.getenv("GUARDRAIL_TRACE", "enabled"),
                region_name=os.getenv("REGION")
            )
            
            # Create agent
            self.agent = Agent(
                system_prompt=f"""You are a helpful AI assistant with persistent memory capabilities for actor: {self.actor_id}.
                
                You have access to:
                - Knowledge base search: Use this for questions regarding Agentic AI Memory
                - Web search: Use this for general questions
                
                Use your memory to provide personalized, context-aware responses based on this user's history.""",
                model=bedrock_model,
                tools=[knowledge_base_search, web_search],
                session_manager=ac_session_manager
            )
            
        except Exception as e:
            raise Exception(f"Failed to initialize agent: {str(e)}")
    
    def chat(self, message: str) -> str:
        """Send a message to the agent and get response"""
        if not self.agent:
            return "Error: Agent not initialized"
        
        try:
            result = self.agent(message)
            
            # Extract response text
            response_text = ""
            if hasattr(result, 'message') and isinstance(result.message, dict):
                content = result.message.get('content', [])
                if content and isinstance(content, list) and len(content) > 0:
                    response_text = content[0].get('text', str(result))
            else:
                response_text = str(result)
            
            return response_text
            
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            'session_id': self.session_id,
            'actor_id': self.actor_id,
            'memory_id': self.memory_id
        }

