"""
Copilot - Sessions Management Page
"""
import streamlit as st
import uuid
import boto3
from datetime import datetime

st.set_page_config(
    page_title="Sessions - Copilot",
    page_icon="📝",
    layout="wide"
)

# Constants
MEMORY_ID = ''
REGION = 'us-east-1'

def get_previous_sessions(actor_id: str):
    """Get list of previous session IDs for an actor"""
    try:
        client = boto3.client('bedrock-agentcore', region_name=REGION)
        sessions = client.list_sessions(
            memoryId=MEMORY_ID,
            actorId=actor_id
        )
        
        session_data = []
        for session in sessions.get('sessionSummaries', []):
            session_data.append({
                'id': session.get('sessionId'),
                'created': session.get('createdTime', 'Unknown'),
                'updated': session.get('lastUpdatedTime', 'Unknown')
            })
        
        return session_data
        
    except Exception as e:
        st.error(f"Error getting sessions: {str(e)}")
        return []

def get_messages_for_session(actor_id: str, session_id: str):
    """Get messages for a specific session"""
    try:
        client = boto3.client('bedrock-agentcore', region_name=REGION)
        events = client.list_events(
            memoryId=MEMORY_ID,
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
        st.error(f"Error getting messages: {str(e)}")
        return []

def display_session_card(session_data, index):
    """Display a session in a single clean line"""
    session_id = session_data['id']
    short_id = session_id[:8]
    
    # Single line with all info
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        st.write(f"Session {index + 1}")
    
    with col2:
        st.write(f"`{short_id}...`")
    
    with col3:
        if st.button("📥", key=f"load_{index}", help="Continue conversation"):
            st.session_state.session_id = session_id
            st.session_state.runtime_session_id = f"streamlit_session_{uuid.uuid4().hex}"
            st.session_state.messages = []
            st.switch_page("streamlit_clean_app.py")
    
    with col4:
        if st.button("👁️", key=f"view_{index}", help="View messages"):
            # Toggle the viewing state
            if st.session_state.get('viewing_session') == session_id:
                st.session_state.viewing_session = None
            else:
                st.session_state.viewing_session = session_id
            st.rerun()
    
    # Expandable message view (only if this session is being viewed)
    if st.session_state.get('viewing_session') == session_id:
        with st.container():
            st.markdown("**Messages:**")
            messages = get_messages_for_session(st.session_state.actor_id, session_id)
            if messages:
                for i, msg in enumerate(messages[:10]):
                    try:
                        # msg is a list, get the first item
                        import json
                        msg_item = msg[0] if isinstance(msg, list) else msg
                        content = msg_item['conversational']['content']['text']
                        parsed = json.loads(content)
                        message_data = parsed['message']
                        role = message_data['role']
                        content_list = message_data['content']
                        
                        # Extract readable content based on type
                        display_text = ""
                        for content_item in content_list:
                            if 'text' in content_item:
                                display_text = content_item['text']
                                break
                            elif 'toolUse' in content_item:
                                tool_name = content_item['toolUse'].get('name', 'unknown_tool')
                                display_text = f"[Used tool: {tool_name}]"
                                break
                            elif 'toolResult' in content_item:
                                display_text = "[Tool result]"
                                break
                        
                        # Display with clean formatting
                        if role == 'user':
                            st.markdown(f"👤 **User:** {display_text[:200]}...")
                        elif role == 'assistant':
                            st.markdown(f"🤖 **Assistant:** {display_text[:200]}...")
                        
                    except Exception as e:
                        # If parsing fails, show raw but cleaner
                        st.text(f"{i+1}. [Parse error: {str(e)}]")
                        st.text(f"Raw: {str(msg)[:100]}...")
                
                if len(messages) > 10:
                    st.caption(f"... and {len(messages) - 10} more messages")
            else:
                st.caption("No messages found")
            st.markdown("---")

def display_session_messages(session_id):
    """Display messages for a specific session"""
    st.subheader(f"📝 Messages from Session: {session_id[:8]}...")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Back to Sessions"):
            if 'viewing_session' in st.session_state:
                del st.session_state.viewing_session
            st.rerun()
    
    with col2:
        if st.button("📥 Load This Session"):
            st.session_state.session_id = session_id
            st.session_state.runtime_session_id = f"streamlit_session_{uuid.uuid4().hex}"
            st.session_state.messages = []
            if 'viewing_session' in st.session_state:
                del st.session_state.viewing_session
            st.switch_page("streamlit_clean_app.py")
    
    st.divider()
    
    messages = get_messages_for_session(st.session_state.actor_id, session_id)
    if messages:
        st.success(f"Found {len(messages)} messages")
        
        for i, msg in enumerate(messages):
            with st.expander(f"Message {i+1}", expanded=False):
                st.json(msg)
    else:
        st.warning("No messages found for this session")

def main():
    """Sessions management page"""
    # Initialize session state
    if 'actor_id' not in st.session_state:
        st.session_state.actor_id = "default_user"
    if 'viewing_session' not in st.session_state:
        st.session_state.viewing_session = None
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📝 Conversations")
    
    with col2:
        menu = st.selectbox("", ["Sessions", "Chat", "Settings"], label_visibility="collapsed")
        if menu == "Chat":
            st.switch_page("streamlit_clean_app.py")
        elif menu == "Settings":
            st.switch_page("pages/settings.py")
    
    # Column headers
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        st.caption("**Session**")
    with col2:
        st.caption("**ID**")
    with col3:
        st.caption("**Continue**")
    with col4:
        st.caption("**View**")
    
    st.markdown("---")
    
    # Get and display sessions
    sessions = get_previous_sessions(st.session_state.actor_id)
    
    if sessions:
        for i, session in enumerate(sessions[:10]):
            display_session_card(session, i)
    else:
        st.markdown("No conversations yet")
        
        if st.button("🆕 Start Conversation", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.runtime_session_id = f"streamlit_session_{uuid.uuid4().hex}"
            st.session_state.messages = []
            st.switch_page("streamlit_clean_app.py")

if __name__ == "__main__":
    main()