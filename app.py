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
    api_key = st.secrets.get("GOOGLE_API_KEY")

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

# Current chat messages
messages = st.session_state.all_chats[
    st.session_state.current_chat
]

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("🤖 Gemini AI")

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):

        chat_number = len(st.session_state.all_chats) + 1

        chat_name = f"New Chat {chat_number}"

        st.session_state.all_chats[chat_name] = []

        st.session_state.current_chat = chat_name

        st.rerun()

    st.markdown("---")

    # Rename Current Chat
    new_name = st.text_input(
        "✏️ Rename Current Chat",
        value=st.session_state.current_chat,
        key="rename_chat"
    )

    if st.button(
        "Rename Chat",
        use_container_width=True
    ):

        old_name = st.session_state.current_chat

        if (
            new_name.strip()
            and new_name != old_name
            and new_name not in st.session_state.all_chats
        ):

            st.session_state.all_chats[new_name] = (
                st.session_state.all_chats.pop(old_name)
            )

            st.session_state.current_chat = new_name

            st.rerun()

    st.markdown("---")

    st.subheader("💬 Chats")

    # Display Chat List
    for chat_name in list(st.session_state.all_chats.keys()):

        col1, col2 = st.columns([5,1])

        with col1:

            if st.button(
                chat_name,
                key=f"open_{chat_name}",
                use_container_width=True
            ):

                st.session_state.current_chat = chat_name

                st.rerun()

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_{chat_name}"
            ):

                del st.session_state.all_chats[chat_name]

                if len(st.session_state.all_chats) == 0:

                    st.session_state.all_chats["New Chat 1"] = []

                    st.session_state.current_chat = "New Chat 1"

                elif st.session_state.current_chat == chat_name:

                    st.session_state.current_chat = list(
                        st.session_state.all_chats.keys()
                    )[0]

                st.rerun()

    st.markdown("---")

    if st.button(
        "🗑️ Clear Current Chat",
        use_container_width=True
    ):

        st.session_state.all_chats[
            st.session_state.current_chat
        ] = []

        st.rerun()

    st.markdown("---")
    st.caption("Powered by Google Gemini")
    st.caption("Python • Streamlit • Gemini API")

    # -----------------------------
# Main Page
# -----------------------------
st.title("🤖 Gemini AI Assistant")
st.caption(
    "Ask questions, generate ideas, and get AI-powered responses."
)

# Refresh current messages
messages = st.session_state.all_chats[
    st.session_state.current_chat
]

# -----------------------------
# Display Messages
# -----------------------------
for message in messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Chat Input
# -----------------------------
prompt = st.chat_input("Ask anything...")

if prompt:

    # Save User Message
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # -----------------------------
    # Auto Rename New Chat
    # -----------------------------
    if (
        st.session_state.current_chat.startswith("New Chat")
        and len(messages) == 1
    ):

        new_title = prompt[:25].strip()

        if len(prompt) > 25:
            new_title += "..."

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

    # Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)

    # -----------------------------
    # Build Conversation History
    # -----------------------------
    conversation = ""

    for msg in messages:

        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"

        else:
            conversation += f"Assistant: {msg['content']}\n"

    # -----------------------------
    # Gemini Response
    # -----------------------------
    with st.chat_message("assistant"):

        with st.spinner("Gemini is thinking..."):

            try:
                response = client.models.generate_content(
                    model="models/gemini-3.6-flash",
                    contents=conversation
                )

                reply = response.text

            except Exception as e:
                st.error(e)

                reply = (
                    "⚠️ Gemini is currently unavailable. "
                    "Please try again later."
                )

            st.markdown(reply)

# Save AI Response
    messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    st.rerun()