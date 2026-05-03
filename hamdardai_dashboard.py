import streamlit as st

st.set_page_config(
    page_title="HamdardAI Dashboard",
    page_icon="🌿",
    layout="wide"
)

# Session state
if "role" not in st.session_state:
    st.session_state.role = None

# Role selection UI
if not st.session_state.role:
    st.markdown("<h1 style='text-align:center'>HamdardAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>Choose your role</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎓 Student"):
            st.session_state.role = "student"
            st.rerun()

    with col2:
        if st.button("🛡️ Counselor"):
            st.session_state.role = "counselor"
            st.rerun()

# Load selected app
if st.session_state.role == "student":
    from hamdardai_student_app import run_student_app
    run_student_app()

elif st.session_state.role == "counselor":
    from hamdardai_counselor_app import run_counselor_app
    run_counselor_app()
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

    st.caption(f"Session: {st.session_state.session_token}")import streamlit as st
import random

def run_counselor_app():

    st.title("🛡️ Counselor Dashboard")

    st.subheader("Active Alerts")

    alerts = [
        {"id": "HAI-A12", "severity": 3},
        {"id": "HAI-B34", "severity": 2},
        {"id": "HAI-C56", "severity": 1},
    ]

    for a in alerts:
        color = ["green", "yellow", "orange", "red"][a["severity"]]
        st.markdown(
            f"""
            <div style="padding:10px;border-radius:8px;margin:8px 0;
                        background:#111;border-left:5px solid {color};">
                <b>{a['id']}</b> — Severity: {a['severity']}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Send Message")

    msg = st.text_input("Message to student")
    if st.button("Send"):
        if msg:
            st.success("Message sent")
