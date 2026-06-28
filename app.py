import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# ── HISTORY FUNCTIONS ──────────────────────────────────────
HISTORY_FILE = "chat_history.json"

def load_all_chats():
    """Load all saved chat sessions"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            content = f.read()
            if content.strip() == "":
                return []
            return json.loads(content)
    return []

def save_all_chats(chats):
    """Save all chat sessions"""
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f, indent=4)

# ── 1. LOAD ENV ────────────────────────────────────────────
load_dotenv(dotenv_path="file.env")
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
client = Groq(api_key=api_key)
# ── 2. PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="CogniBuddy",
    page_icon="🤖",
    layout="wide"
)

# ── 3. CUSTOM CSS ──────────────────────────────────────────
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', sans-serif !important;
    }
    .stApp {
        background-color: #000000 !important;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* R Logo */
    .r-logo {
        width: 55px;
        height: 55px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        font-weight: bold;
        color: black !important;
        margin: 0 auto 10px auto;
    }
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        margin: 5px 0 !important;
    }
    [data-testid="stChatMessage"] *{
        color: white !important;
    }
    /* Code blocks */
    [data-testid="stChatMessage"] code {
        color: white !important;
        background-color: #222222 !important;
    }
    [data-testid="stChatMessage"] pre {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #888888 !important;
    }
    /* All text white */
    p, span, li, label, div {
        color: white !important;
    }
    h1, h2, h3 {
        color: white !important;
    }
    /* Buttons */
    .stButton button {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        width: 100% !important;
        text-align: left !important;
        padding: 8px 12px !important;
    }
    .stButton button:hover {
        background-color: #2a2a2a !important;
        border-color: #555555 !important;
    }
    /* New chat button */
    .new-chat-btn button {
        background-color: #222222 !important;
        text-align: center !important;
        font-weight: bold !important;
    }
    /* History item */
    .chat-session-title {
        font-size: 0.85rem;
        color: #cccccc !important;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    /* Divider */
    hr {
        border-color: #222222 !important;
    }
    /* Main area */
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white !important;
        padding: 10px 0;
    }
    .main-subtitle {
        text-align: center;
        color: #888888 !important;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ── 4. SESSION STATE INIT ──────────────────────────────────
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_all_chats()

if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = None

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

# ── 5. SYSTEM PROMPT ───────────────────────────────────────
SYSTEM_PROMPT = """
You are CogniBuddy, a warm, friendly and supportive AI companion.
Your role is to:
- Be a caring and supportive friend
- Help students study and understand concepts clearly
- Explain things simply using examples and analogies
- Motivate and encourage users when they feel stressed
- Make learning fun and engaging
Always be kind, patient, positive and enthusiastic!
If someone is stressed, first comfort them then help them.
Keep responses concise but helpful.
"""

# ── 6. HELPER FUNCTIONS ────────────────────────────────────
def get_chat_title(messages):
    """Get first user message as chat title"""
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"][:35]
            return title + "..." if len(msg["content"]) > 35 else title
    return "New Chat"

def start_new_chat():
    """Start a brand new chat session"""
    welcome = "Hey there! I'm **CogniBuddy**, your personal AI study companion! What's on your mind today?"
    new_chat = [{"role": "assistant", "content": welcome}]
    st.session_state.all_chats.insert(0, new_chat)
    st.session_state.current_chat_index = 0
    st.session_state.confirm_delete = None
    save_all_chats(st.session_state.all_chats)

# ── 7. SIDEBAR ─────────────────────────────────────────────
with st.sidebar:
    # R Logo
    st.markdown('<div class="r-logo">R</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; margin:0;'>CogniBuddy</h3>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888888; font-size:0.8rem;'>Your AI Study Companion</p>",
                unsafe_allow_html=True)
    st.markdown("---")

    # New Chat Button
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("+ New Chat"):
        start_new_chat()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#888888; font-size:0.8rem;'>CHAT HISTORY</p>",
                unsafe_allow_html=True)

    # Show all chat sessions
    if len(st.session_state.all_chats) == 0:
        st.markdown("<p style='color:#555555; font-size:0.85rem;'>No chats yet!</p>",
                    unsafe_allow_html=True)
    else:
        for i, chat in enumerate(st.session_state.all_chats):
            title = get_chat_title(chat)

            # Show delete confirmation if this chat selected for delete
            if st.session_state.confirm_delete == i:
                st.markdown(f"<p style='color:#ff4444; font-size:0.8rem;'>Delete this chat?</p>",
                            unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key=f"yes_{i}"):
                        st.session_state.all_chats.pop(i)
                        save_all_chats(st.session_state.all_chats)
                        if st.session_state.current_chat_index == i:
                            st.session_state.current_chat_index = None
                        elif st.session_state.current_chat_index and st.session_state.current_chat_index > i:
                            st.session_state.current_chat_index -= 1
                        st.session_state.confirm_delete = None
                        st.rerun()
                with col2:
                    if st.button("No", key=f"no_{i}"):
                        st.session_state.confirm_delete = None
                        st.rerun()
            else:
                # Highlight active chat
                is_active = st.session_state.current_chat_index == i
                prefix = "▶ " if is_active else "💬 "

                if st.button(f"{prefix}{title}", key=f"chat_{i}"):
                    if st.session_state.current_chat_index == i:
                        # Same chat clicked again = show delete confirm
                        st.session_state.confirm_delete = i
                    else:
                        # Different chat = switch to it
                        st.session_state.current_chat_index = i
                        st.session_state.confirm_delete = None
                    st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align:center; color:#555555; font-size:0.75rem;'>Built by Ragi</p>",
                unsafe_allow_html=True)

# ── 8. MAIN AREA ───────────────────────────────────────────
st.markdown("<p class='main-title'>CogniBuddy</p>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Your friendly AI Study Companion</p>",
            unsafe_allow_html=True)
st.markdown("---")

# If no chat selected, show welcome screen
if st.session_state.current_chat_index is None or \
   st.session_state.current_chat_index >= len(st.session_state.all_chats):

    st.markdown("""
        <div style='text-align:center; padding: 60px 20px;'>
            <h2 style='color:white;'>Welcome to CogniBuddy!</h2>
            <p style='color:#888888;'>Click "+ New Chat" in the sidebar to start a conversation</p>
            <p style='color:#888888;'>or select a previous chat from history</p>
        </div>
    """, unsafe_allow_html=True)

else:
    # Get current chat messages
    current_messages = st.session_state.all_chats[st.session_state.current_chat_index]

    # Display messages
    for message in current_messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
        else:
            with st.chat_message("user", avatar="🤓"):
                st.markdown(message["content"])

    # User input
    user_input = st.chat_input("Talk to CogniBuddy...")

    if user_input:
        with st.chat_message("user", avatar="🤓"):
            st.markdown(user_input)

        current_messages.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *current_messages
                ]
            )

        reply = response.choices[0].message.content

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply)

        current_messages.append({
            "role": "assistant",
            "content": reply
        })

        # Update and save
        st.session_state.all_chats[st.session_state.current_chat_index] = current_messages
        save_all_chats(st.session_state.all_chats)
        st.rerun()