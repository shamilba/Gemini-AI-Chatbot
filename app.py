import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# -----------------------------
# Load API Key
# -----------------------------
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    api_key = st.secrets["GOOGLE_API_KEY"]

client = genai.Client(api_key=api_key)

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "New Chat 1": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat 1"

# Current Chat Messages
messages = st.session_state.all_chats[
    st.session_state.current_chat
]

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("🤖 Gemini AI")

    if st.button("➕ New Chat", use_container_width=True):

        chat_number = len(st.session_state.all_chats) + 1

        chat_name = f"New Chat {chat_number}"

        st.session_state.all_chats[chat_name] = []

        st.session_state.current_chat = chat_name

        st.rerun()

    st.markdown("---")

    # Show all chats
    for chat_name in st.session_state.all_chats.keys():

        if st.button(
            f"💬 {chat_name}",
            key=chat_name,
            use_container_width=True
        ):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.markdown("---")

    if st.button("🗑️ Clear Current Chat", use_container_width=True):

        st.session_state.all_chats[
            st.session_state.current_chat
        ] = []

        st.rerun()

    st.markdown("---")
    st.caption("Powered by Google Gemini")

    st.markdown("---")
    st.caption("Python • Streamlit • Gemini API")

# -----------------------------
# Main Page
# -----------------------------
st.title("🤖 Gemini AI Assistant")
st.caption(
    "Ask questions, generate ideas, and get AI-powered responses."
)

# Display Messages
for message in messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# -----------------------------
# Chat Input
# -----------------------------
prompt = st.chat_input("Ask anything...")

if prompt:

    # Save user message
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Rename chat using first message
    if (
        st.session_state.current_chat.startswith("New Chat")
        and len(messages) == 1
    ):

        new_title = prompt[:25].strip()

        if len(prompt) > 25:
            new_title += "..."

        # Avoid duplicate names
        original_title = new_title
        count = 2

        while new_title in st.session_state.all_chats:
            new_title = f"{original_title} ({count})"
            count += 1

        st.session_state.all_chats[new_title] = (
            st.session_state.all_chats.pop(
                st.session_state.current_chat
            )
        )

        st.session_state.current_chat = new_title
        messages = st.session_state.all_chats[
            st.session_state.current_chat
        ]

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build conversation
    conversation = ""

    for msg in messages:

        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"

        else:
            conversation += f"Assistant: {msg['content']}\n"

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Gemini is thinking..."):

            response = client.models.generate_content(
                model="models/gemini-3.7-flash",
                contents=conversation
            )

            reply = response.text

            st.markdown(reply)

    # Save AI response
    messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    st.rerun()