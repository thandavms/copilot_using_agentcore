"""
Copilot Agent for AgentCore Runtime
Following the official Strands + Bedrock model pattern from AWS samples
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from agent import CopilotAgent

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# Global agent cache for session management
agent_cache = {}

@app.entrypoint
def copilot_agent(payload):
    """
    Main entrypoint for AgentCore Runtime
    Receives payload and returns agent response
    """
    try:
        # Extract parameters from payload
        user_input = payload.get("prompt", payload.get("message", ""))
        actor_id = payload.get("actor_id", "default_user")
        session_id = payload.get("session_id")
        
        if not user_input:
            return "Error: No input message provided"
        
        if not session_id:
            return "Error: session_id is required"
        
        # Create cache key for this session
        cache_key = f"{actor_id}:{session_id}"
        
        # Get or create agent for this session
        if cache_key not in agent_cache:
            agent_cache[cache_key] = CopilotAgent(
                actor_id=actor_id,
                session_id=session_id
            )
        
        agent = agent_cache[cache_key]
        
        # Process the message using existing agent logic
        response = agent.chat(user_input)
        
        return response
        
    except Exception as e:
        return f"Error processing request: {str(e)}"

if __name__ == "__main__":
    app.run()