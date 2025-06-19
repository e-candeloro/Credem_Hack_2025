import os
from datetime import datetime
from typing import Any, Dict, List

import httpx
import streamlit as st

# Environment variables for configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="AI Chat - AI HR System",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for chat interface with dark theme support
st.markdown(
    """
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: rgba(33, 150, 243, 0.1);
        border-left-color: #2196f3;
        color: inherit;
    }
    .assistant-message {
        background-color: rgba(156, 39, 176, 0.1);
        border-left-color: #9c27b0;
        color: inherit;
    }
    .system-message {
        background-color: rgba(255, 152, 0, 0.1);
        border-left-color: #ff9800;
        color: inherit;
    }
    .error-message {
        background-color: rgba(244, 67, 54, 0.1);
        border-left-color: #f44336;
        color: inherit;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: rgba(128, 128, 128, 0.05);
    }
    .stTextInput > div > div > input {
        border-radius: 25px;
    }
    .stButton > button {
        border-radius: 25px;
        background-color: #1f77b4;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "llm"
if "message_sent" not in st.session_state:
    st.session_state.message_sent = False


def send_message_to_api(
    message: str, mode: str, system_prompt: str = "You are a helpful AI assistant."
) -> dict[str, Any]:
    """Send message to the appropriate API endpoint."""
    try:
        if mode == "llm":
            # Direct LLM test
            payload = {
                "message": message,
                "system_prompt": system_prompt or "You are a helpful AI assistant.",
            }
            response = httpx.post(
                f"{API_BASE_URL}/api/v1/test-llm", json=payload, timeout=30.0
            )
            if response.status_code == 200:
                return {"success": True, "response": response.json()["response"]}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}

        elif mode == "agent":
            # Agent chat with tools
            payload = {"messages": [{"role": "user", "content": message}]}
            response = httpx.post(
                f"{API_BASE_URL}/api/v1/chat", json=payload, timeout=60.0
            )
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "response": result["output"]}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}
        # Always return a value
        return {"success": False, "error": "Unknown mode."}
    except httpx.TimeoutException:
        return {"success": False, "error": "Request timed out. Please try again."}
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}


def display_chat_message(role: str, content: str, timestamp: str = None):
    """Display a chat message with appropriate styling."""
    if role == "user":
        st.markdown(
            f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong><br>
                {content}
                {f'<br><small><em>{timestamp}</em></small>' if timestamp else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif role == "assistant":
        st.markdown(
            f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>
                {content}
                {f'<br><small><em>{timestamp}</em></small>' if timestamp else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif role == "system":
        st.markdown(
            f"""
            <div class="chat-message system-message">
                <strong>⚙️ System:</strong><br>
                {content}
                {f'<br><small><em>{timestamp}</em></small>' if timestamp else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif role == "error":
        st.markdown(
            f"""
            <div class="chat-message error-message">
                <strong>❌ Error:</strong><br>
                {content}
                {f'<br><small><em>{timestamp}</em></small>' if timestamp else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )


# Main chat interface
st.title("💬 AI Chat Interface")

# Sidebar configuration
with st.sidebar:
    st.header("🔧 Chat Configuration")

    # Mode selection
    mode = st.selectbox(
        "Select Chat Mode",
        ["llm", "agent"],
        format_func=lambda x: "Direct LLM" if x == "llm" else "Agent with Tools",
        index=0 if st.session_state.current_mode == "llm" else 1,
    )
    st.session_state.current_mode = mode

    st.markdown("---")

    # System prompt for LLM mode
    if mode == "llm":
        st.subheader("🤖 LLM Settings")
        default_prompt = "You are a helpful AI assistant."
        current_prompt = str(st.session_state.get("system_prompt") or default_prompt)
        system_prompt = (
            st.text_area(
                "System Prompt",
                value=current_prompt,
                height=100,
                help="Customize the system prompt for the LLM",
            )
            or default_prompt
        )
        st.session_state["system_prompt"] = system_prompt
    else:
        system_prompt = "You are a helpful AI assistant."
        st.subheader("🛠️ Agent Settings")
        st.info(
            "Agent mode includes access to tools like calculator, search, and database queries."
        )

    st.markdown("---")

    # Chat controls
    st.subheader("💬 Chat Controls")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.message_sent = False
            st.rerun()

    with col2:
        if st.button("📥 Export Chat", use_container_width=True):
            if st.session_state.chat_history:
                chat_text = "\n\n".join(
                    [
                        f"{msg['role'].upper()}: {msg['content']}"
                        for msg in st.session_state.chat_history
                    ]
                )
                st.download_button(
                    label="Download Chat",
                    data=chat_text,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

    st.markdown("---")

    # API Status
    st.subheader("🔍 API Status")
    try:
        response = httpx.get(f"{API_BASE_URL}/api/v1/health", timeout=5.0)
        if response.status_code == 200:
            st.success("✅ Backend API Online")
        else:
            st.error("❌ Backend API Error")
    except:
        st.error("❌ Backend API Offline")

# Main chat area
st.subheader(f"Chat Mode: {'Direct LLM' if mode == 'llm' else 'Agent with Tools'}")

# Display chat history
if st.session_state.chat_history:
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            display_chat_message(
                message["role"], message["content"], message.get("timestamp")
            )
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("💡 Start a conversation by typing a message below!")

# Input area using form to prevent infinite loops
st.markdown("---")
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_input(
            "Type your message here...",
            placeholder="Ask me anything!",
            label_visibility="collapsed",
        )

    with col2:
        send_button = st.form_submit_button("Send", use_container_width=True)

# Handle message sending
if send_button and user_input.strip():
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input.strip(), "timestamp": timestamp}
    )

    # Send to API - ensure system_prompt is always a string
    current_system_prompt = (
        str(system_prompt) if system_prompt else "You are a helpful AI assistant."
    )
    with st.spinner("🤖 Thinking..."):
        result = send_message_to_api(user_input.strip(), mode, current_system_prompt)

    if result["success"]:
        # Add assistant response to history
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
    else:
        # Add error message to history
        st.session_state.chat_history.append(
            {
                "role": "error",
                "content": result["error"],
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )

    # Mark message as sent to prevent reprocessing
    st.session_state.message_sent = True
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        💡 <strong>Tips:</strong><br>
        • Use <strong>Direct LLM</strong> for simple conversations<br>
        • Use <strong>Agent with Tools</strong> for tasks requiring calculations, searches, or data queries<br>
        • The agent can access tools like calculator, web search, and database queries
    </div>
    """,
    unsafe_allow_html=True,
)
