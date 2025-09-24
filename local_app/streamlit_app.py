"""
Copilot Streamlit App - Lightweight frontend for the AI agent
"""
import streamlit as st
import uuid
from datetime import datetime
from agent import CopilotAgent
from utils import check_environment, get_previous_sessions, get_messages_for_session

# Page configuration
st.set_page_config(
    page_title="Copilot",
    page_icon="🤖",
    layout="wide"
)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'actor_id' not in st.session_state:
        st.session_state.actor_id = "default_user"
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'viewing_session' not in st.session_state:
        st.session_state.viewing_session = None

def display_environment_status():
    """Display environment configuration status"""
    with st.sidebar:
        env_status = check_environment()
        all_set = all(env_status.values())
        
        # Collapsible environment status
        with st.expander("🔧 Environment Status", expanded=not all_set):
            for var, is_set in env_status.items():
                status_icon = "✅" if is_set else "❌"
                st.text(f"{status_icon} {var}")
            
            if all_set:
                st.success("All configured!")
            else:
                st.error("Missing variables")
        
        return all_set

def display_session_management():
    """Display session management controls"""
    with st.sidebar:
        # Collapsible session management
        with st.expander("👤 Session Management", expanded=True):
            # Actor ID input
            new_actor_id = st.text_input(
                "Actor ID", 
                value=st.session_state.actor_id,
                help="Unique identifier for the user"
            )
            
            if new_actor_id != st.session_state.actor_id:
                st.session_state.actor_id = new_actor_id
                st.session_state.agent = None  # Reset agent
                st.rerun()
            
            # Session controls
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🆕 New Session"):
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.messages = []
                    st.session_state.agent = None
                    st.rerun()
            
            with col2:
                if st.button("📋 Show Previous Sessions"):
                    # Force refresh of previous sessions for current actor
                    st.rerun()
            
            # Display current session info
            st.text(f"Session: {st.session_state.session_id[:8]}...")
        
        # Previous sessions in separate collapsible section
        try:
            prev_sessions = get_previous_sessions(st.session_state.actor_id)
            if prev_sessions:
                with st.expander("📝 Previous Sessions", expanded=False):
                    for session in prev_sessions[:5]:  # Show last 5
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            if st.button(f"Load {session[:8]}...", key=f"load_{session}"):
                                st.session_state.session_id = session
                                st.session_state.messages = []
                                st.session_state.agent = None
                                st.rerun()
                        
                        with col2:
                            if st.button("👁️", key=f"view_{session}", help="View messages"):
                                # Set the session to view in main area
                                st.session_state.viewing_session = session
                                st.rerun()
        except Exception as e:
            st.error(f"Error loading sessions: {str(e)}")

def initialize_agent():
    """Initialize or get the agent instance"""
    if st.session_state.agent is None:
        try:
            with st.spinner("Initializing AI agent..."):
                st.session_state.agent = CopilotAgent(
                    actor_id=st.session_state.actor_id,
                    session_id=st.session_state.session_id
                )
            st.success("Agent initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            return False
    return True

def display_session_messages():
    """Display messages from a selected session"""
    if 'viewing_session' in st.session_state and st.session_state.viewing_session:
        session_id = st.session_state.viewing_session
        
        st.subheader(f"📝 Messages from Session: {session_id[:8]}...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("❌ Close View"):
                del st.session_state.viewing_session
                st.rerun()
        
        with col2:
            if st.button("📥 Load This Session"):
                st.session_state.session_id = session_id
                st.session_state.messages = []
                st.session_state.agent = None
                del st.session_state.viewing_session
                st.rerun()
        
        st.divider()
        
        # Get and display messages
        try:
            messages = get_messages_for_session(st.session_state.actor_id, session_id)
            if messages:
                st.success(f"Found {len(messages)} messages")
                for i, msg in enumerate(messages):
                    with st.expander(f"Message {i+1}", expanded=False):
                        st.json(msg)
            else:
                st.warning("No messages found for this session")
        except Exception as e:
            st.error(f"Error retrieving messages: {str(e)}")
        
        st.divider()
        return True
    return False

def display_chat_interface():
    """Display the main chat interface"""
    st.title("🤖 Copilot")
    st.markdown("AI Assistant with Memory and Knowledge Base Access")
    
    # Check if we're viewing a session's messages
    if display_session_messages():
        return  # Don't show chat interface when viewing session messages
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"*{message['timestamp']}*")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
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
                    response = st.session_state.agent.chat(prompt)
                    st.markdown(response)
                    
                    # Add assistant message
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
    """Main application function"""
    initialize_session_state()
    
    # Check environment and display status
    env_ready = display_environment_status()
    
    # Display session management
    display_session_management()
    
    if not env_ready:
        st.error("⚠️ Please configure all required environment variables before using the app.")
        st.info("Check the sidebar for missing configuration.")
        return
    
    # Initialize agent
    if not initialize_agent():
        return
    
    # Display chat interface
    display_chat_interface()
    
    # Footer - collapsible tools info
    with st.sidebar:
        with st.expander("🛠️ Available Tools", expanded=False):
            st.markdown("🔍 Knowledge Base Search")
            st.markdown("🌐 Web Search (Tavily)")
            st.markdown("🧠 Persistent Memory")

if __name__ == "__main__":
    main()