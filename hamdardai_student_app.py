import streamlit as st
import uuid
import random
from datetime import datetime

# CONFIG
USE_MOCK = True

def run_student_app():

    st.title("🌿 HamdardAI Student Support")

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.session_token = f"HAI-{uuid.uuid4().hex[:6].upper()}"
        st.session_state.severity = 0

    def analyze_message(msg):
        msg = msg.lower()
        if any(x in msg for x in ["suicide", "kill myself", "die"]):
            return 3
        elif any(x in msg for x in ["hopeless", "alone", "worthless"]):
            return 2
        elif any(x in msg for x in ["stress", "anxious", "tired"]):
            return 1
        return 0

    def bot_reply(sev):
        responses = {
            0: ["I’m here for you. Tell me more."],
            1: ["That sounds stressful. Want to talk about it?"],
            2: ["That sounds really hard. You’re not alone."],
            3: ["I’m really glad you spoke up. You matter."],
        }
        return random.choice(responses[sev])

    # Chat display
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    # Input
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        sev = analyze_message(prompt)
        st.session_state.severity = sev

        reply = bot_reply(sev)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()

    st.caption(f"Session: {st.session_state.session_token}")
