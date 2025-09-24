"""
Copilot - Settings & Configuration Page
"""
import streamlit as st
import boto3
import json

st.set_page_config(
    page_title="Settings - Copilot",
    page_icon="⚙️",
    layout="wide"
)

# Constants
AGENT_RUNTIME_ARN = 'arn:aws:bedrock-agentcore:us-east-1:924155096146:runtime/adp_copilot_agent-ey3rBD8Vnm'
REGION = 'us-east-1'
MEMORY_ID = ''

def test_agentcore_connection():
    """Test connection to AgentCore Runtime"""
    try:
        client = boto3.client('bedrock-agentcore', region_name=REGION)
        
        payload_dict = {
            "prompt": "Hello, this is a connection test.",
            "actor_id": "test_user",
            "session_id": "connection_test"
        }
        
        payload_bytes = json.dumps(payload_dict).encode('utf-8')
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=f"test_connection_{hash(str(payload_dict))}",
            payload=payload_bytes,
            qualifier="DEFAULT"
        )
        
        return response['statusCode'] == 200
        
    except Exception as e:
        st.error(f"Connection test failed: {str(e)}")
        return False

def test_memory_connection():
    """Test connection to AgentCore Memory"""
    try:
        client = boto3.client('bedrock-agentcore', region_name=REGION)
        
        # Try to list sessions to test memory access
        response = client.list_sessions(
            memoryId=MEMORY_ID,
            actorId="test_user"
        )
        
        return 'sessionSummaries' in response
        
    except Exception as e:
        st.error(f"Memory test failed: {str(e)}")
        return False

def display_runtime_config():
    """Display AgentCore Runtime configuration"""
    st.subheader("🚀 AgentCore Runtime Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Agent Runtime ARN:**")
        st.code(AGENT_RUNTIME_ARN, language=None)
        
        st.markdown("**Region:**")
        st.code(REGION, language=None)
    
    with col2:
        st.markdown("**Memory ID:**")
        st.code(MEMORY_ID, language=None)
        
        st.markdown("**Qualifier:**")
        st.code("DEFAULT", language=None)
    
    # Connection tests
    st.markdown("### 🔍 Connection Tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test AgentCore Runtime", use_container_width=True):
            with st.spinner("Testing runtime connection..."):
                success = test_agentcore_connection()
                if success:
                    st.success("✅ AgentCore Runtime connection successful!")
                else:
                    st.error("❌ AgentCore Runtime connection failed!")
    
    with col2:
        if st.button("Test Memory Access", use_container_width=True):
            with st.spinner("Testing memory access..."):
                success = test_memory_connection()
                if success:
                    st.success("✅ Memory access successful!")
                else:
                    st.error("❌ Memory access failed!")

def display_actor_settings():
    """Display actor/user settings"""
    st.subheader("👤 Actor Settings")
    
    # Initialize session state
    if 'actor_id' not in st.session_state:
        st.session_state.actor_id = "default_user"
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_actor_id = st.text_input(
            "Actor ID",
            value=st.session_state.actor_id,
            help="Unique identifier for the user. Changes will affect session history access."
        )
        
        if new_actor_id != st.session_state.actor_id:
            st.session_state.actor_id = new_actor_id
            st.success(f"Actor ID updated to: {new_actor_id}")
            st.info("Go to Sessions page to see history for this actor.")
    
    with col2:
        st.markdown("**Current Actor:**")
        st.code(st.session_state.actor_id, language=None)
        
        if st.button("Reset to Default"):
            st.session_state.actor_id = "default_user"
            st.rerun()

def display_session_info():
    """Display current session information"""
    st.subheader("📋 Current Session Info")
    
    if 'session_id' not in st.session_state:
        st.warning("No active session")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Session ID:**")
        st.code(st.session_state.session_id, language=None)
        
        st.markdown("**Runtime Session ID:**")
        if 'runtime_session_id' in st.session_state:
            st.code(st.session_state.runtime_session_id, language=None)
        else:
            st.code("Not initialized", language=None)
    
    with col2:
        st.markdown("**Messages in Session:**")
        if 'messages' in st.session_state:
            st.metric("Count", len(st.session_state.messages))
        else:
            st.metric("Count", 0)
        
        if st.button("Clear Current Session"):
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.runtime_session_id = f"streamlit_session_{uuid.uuid4().hex}"
            st.session_state.messages = []
            st.success("New session created!")

def display_tools_info():
    """Display information about available tools"""
    st.subheader("🛠️ Available Agent Tools")
    
    tools = [
        {
            "name": "Knowledge Base Search",
            "icon": "🔍",
            "description": "Search internal knowledge base for Agentic AI Memory information",
            "usage": "Automatically triggered for questions about AI Memory, agents, etc."
        },
        {
            "name": "Web Search (Tavily)",
            "icon": "🌐", 
            "description": "Search the web for current information and general questions",
            "usage": "Automatically triggered for general questions, current events, etc."
        },
        {
            "name": "Persistent Memory",
            "icon": "🧠",
            "description": "Remembers conversation history and user preferences across sessions",
            "usage": "Always active - agent remembers your previous conversations"
        }
    ]
    
    for tool in tools:
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 16px; 
                margin: 8px 0;
                background: #f9f9f9;
            ">
                <h4>{tool['icon']} {tool['name']}</h4>
                <p><strong>Description:</strong> {tool['description']}</p>
                <p><strong>Usage:</strong> {tool['usage']}</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Settings page"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Settings")
    
    with col2:
        menu = st.selectbox("", ["Settings", "Chat", "Sessions"], label_visibility="collapsed")
        if menu == "Chat":
            st.switch_page("streamlit_clean_app.py")
        elif menu == "Sessions":
            st.switch_page("pages/sessions.py")
    
    st.markdown("")
    
    # Simple settings
    if 'actor_id' not in st.session_state:
        st.session_state.actor_id = "default_user"
    
    new_actor_id = st.text_input("Your Name", value=st.session_state.actor_id)
    if new_actor_id != st.session_state.actor_id:
        st.session_state.actor_id = new_actor_id
        st.success("Name updated!")
    
    st.markdown("---")
    
    # Connection status
    st.markdown("**Connection Status**")
    if st.button("Test Connection"):
        with st.spinner("Testing..."):
            success = test_agentcore_connection()
            if success:
                st.success("✅ Connected")
            else:
                st.error("❌ Connection failed")
    
    # Advanced section (collapsed)
    with st.expander("Advanced", expanded=False):
        display_runtime_config()
        display_tools_info()

if __name__ == "__main__":
    main()