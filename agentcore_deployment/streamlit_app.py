"""
Copilot - Main Chat Page (Clean Multi-Page App)
"""
import streamlit as st
import uuid
import boto3
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Copilot Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# AgentCore Runtime configuration
AGENT_RUNTIME_ARN = 'arn:aws:bedrock-agentcore:us-east-1:924155096146:runtime/adp_copilot_agent-ey3rBD8Vnm'
REGION = 'us-east-1'

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'actor_id' not in st.session_state:
        st.session_state.actor_id = "default_user"
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'runtime_session_id' not in st.session_state:
        st.session_state.runtime_session_id = f"streamlit_session_{uuid.uuid4().hex}"

def invoke_agentcore_runtime(message: str) -> str:
    """Invoke the AgentCore Runtime agent"""
    try:
        client = boto3.client('bedrock-agentcore', region_name=REGION)
        
        payload_dict = {
            "prompt": message,
            "actor_id": st.session_state.actor_id,
            "session_id": st.session_state.session_id
        }
        
        payload_bytes = json.dumps(payload_dict).encode('utf-8')
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=st.session_state.runtime_session_id,
            payload=payload_bytes,
            qualifier="DEFAULT"
        )
        
        if response['statusCode'] == 200:
            response_body = response.get('response')
            if response_body:
                content = response_body.read().decode('utf-8')
                return content
            else:
                return "No response received from agent"
        else:
            return f"Error: Agent returned status code {response['statusCode']}"
            
    except Exception as e:
        return f"Error invoking AgentCore Runtime: {str(e)}"

def display_header():
    """Display clean header"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("💬 Copilot")
    
    with col2:
        if st.button("🆕 New Chat"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.runtime_session_id = f"streamlit_session_{uuid.uuid4().hex}"
            st.session_state.messages = []
            st.rerun()
    
    with col3:
        # Simple menu
        menu = st.selectbox("", ["Chat", "Sessions", "Settings"], label_visibility="collapsed")
        if menu == "Sessions":
            st.switch_page("pages/sessions.py")
        elif menu == "Settings":
            st.switch_page("pages/settings.py")

def display_chat_interface():
    """Display clean chat interface"""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"*{message['timestamp']}*")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about..."):
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"*{timestamp}*")
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = invoke_agentcore_runtime(prompt)
                    st.markdown(response)
                    
                    response_timestamp = datetime.now().strftime("%H:%M:%S")
                    st.caption(f"*{response_timestamp}*")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "timestamp": response_timestamp
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

def main():
    """Main chat page"""
    initialize_session_state()
    
    # Clean header
    display_header()
    
    # Chat interface
    display_chat_interface()

if __name__ == "__main__":
    main()