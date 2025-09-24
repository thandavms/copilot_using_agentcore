import os
import uuid
import boto3
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

def check_environment() -> Dict[str, bool]:
    """Check if all required environment variables are set"""
    required_vars = [
        'MEMORY_ID',
        'BEDROCK_MODEL_ID',
        'KNOWLEDGE_BASE_ID',
        'TAVILY_API_KEY',
        'REGION'
    ]
    
    status = {}
    for var in required_vars:
        status[var] = bool(os.getenv(var))
    
    return status

def get_previous_sessions(actor_id: str) -> List[str]:
    """Get list of previous session IDs for an actor"""
    try:
        memory_id = os.getenv('MEMORY_ID')
        region = os.getenv('REGION', 'us-east-1')
        
        client = boto3.client('bedrock-agentcore', region_name=region)

        sessions = client.list_sessions(
            memoryId=memory_id,
            actorId=actor_id
        )
        
        session_ids = []
        for session in sessions.get('sessionSummaries', []):
            session_id = session.get('sessionId')
            if session_id:
                session_ids.append(session_id)
        
        return session_ids
        
    except Exception as e:
        print(f"Error getting previous sessions: {str(e)}")
        return []

def get_messages_for_session(actor_id: str, session_id: str) -> List[Dict]:
    """Get messages for a specific session"""
    try:
        memory_id = os.getenv('MEMORY_ID')
        region = os.getenv('REGION', 'us-east-1')
        
        client = boto3.client('bedrock-agentcore', region_name=region)
        
        events = client.list_events(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id
        )
        
        messages = []
        for event in events.get('events', []):
            payload = event.get('payload', {})
            if payload:
                messages.append(payload)
        
        return messages
        
    except Exception as e:
        print(f"Error getting messages for session: {str(e)}")
        return []