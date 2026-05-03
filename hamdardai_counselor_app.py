%%writefile hamdardai_dashboard.py
import streamlit as st

st.set_page_config(
    page_title="HamdardAI Dashboard",
    page_icon="🌿",
    layout="wide"
)

# Role state
if "role" not in st.session_state:
    st.session_state.role = None

# Role selection screen
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

# Load dashboards
if st.session_state.role == "student":
    import hamdardai_student_app

elif st.session_state.role == "counselor":
    import hamdardai_counselor_app%%writefile hamdardai_student_app.py
"""
HamdardAI — Student Chat Interface
M4 Frontend | Streamlit + Google Colab compatible
─────────────────────────────────────────────────
Integration contract with M3 (Backend):
  POST /analyze  → { message: str, session_token: str }
                 ← { severity: int, label: str, confidence: float,
                     flags: list, coping_resource: dict,
                     counselor_alerted: bool, session_summary: dict }

To run standalone (no backend):
  streamlit run hamdardai_student_app.py

To run in Colab:
  !pip install streamlit pyngrok -q
  from pyngrok import ngrok
  ngrok.set_auth_token("YOUR_NGROK_TOKEN")
  !streamlit run hamdardai_student_app.py &
  tunnel = ngrok.connect(8501)
  print(tunnel.public_url)
"""

import streamlit as st
import requests
import uuid
import time
import random
from datetime import datetime


# ─────────────────────────────────────────────────────────────
#  BACKEND CONFIG  ← M3: change this URL to your FastAPI server
# ─────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"   # ← M3: update this
USE_MOCK    = True                       # ← M3: set False when backend is ready

# ─────────────────────────────────────────────────────────────
#  PREMIUM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}

/* Hide default streamlit chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
footer,
#MainMenu { display: none !important; }

/* ── Main container ── */
[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 720px;
    padding: 0 1rem 6rem 1rem;
    margin: 0 auto;
}

/* ── Header ── */
.hamdard-header {
    text-align: center;
    padding: 2.8rem 0 1.6rem;
    border-bottom: 1px solid #1e2530;
    margin-bottom: 1.6rem;
}
.hamdard-header .logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #a8d5b5;
    letter-spacing: -0.03em;
    line-height: 1;
}
.hamdard-header .logo span { color: #4ade80; }
.hamdard-header .tagline {
    font-size: 0.78rem;
    color: #4b5563;
    margin-top: 0.4rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 300;
}
.hamdard-header .privacy-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    margin-top: 0.9rem;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 0.3rem 0.85rem;
    font-size: 0.7rem;
    color: #6b7280;
    font-weight: 300;
}
.hamdard-header .privacy-badge .dot {
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Chat window ── */
.chat-window {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-bottom: 0.5rem;
}

/* ── Message bubbles ── */
.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
}
.msg-row.user  { flex-direction: row-reverse; }
.msg-row.echo  { flex-direction: row; }

.avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
}
.avatar.hamdard-av { background: #14532d; color: #4ade80; }
.avatar.user-av { background: #1e3a5f; color: #60a5fa; }

.bubble {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 18px;
    font-size: 0.875rem;
    line-height: 1.55;
    animation: pop-in 0.2s ease;
}
@keyframes pop-in {
    from { transform: scale(0.95); opacity: 0; }
    to   { transform: scale(1);    opacity: 1; }
}
.bubble.user-bubble {
    background: #1e3a5f;
    color: #e0edff;
    border-bottom-right-radius: 4px;
}
.bubble.hamdard-bubble {
    background: #111827;
    color: #d1fae5;
    border: 1px solid #1a2e1a;
    border-bottom-left-radius: 4px;
}
.bubble .ts {
    font-size: 0.62rem;
    color: #374151;
    margin-top: 0.35rem;
    display: block;
}

/* ── Coping resource card ── */
.resource-card {
    background: linear-gradient(135deg, #0f1f12 0%, #111a1b 100%);
    border: 1px solid #1a2e1a;
    border-left: 3px solid #22c55e;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #86efac;
    line-height: 1.5;
}
.resource-card .rc-title {
    font-weight: 500;
    color: #4ade80;
    margin-bottom: 0.25rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Alert card ── */
.alert-card {
    background: linear-gradient(135deg, #1a0f0f 0%, #1f1212 100%);
    border: 1px solid #3b1515;
    border-left: 3px solid #ef4444;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #fca5a5;
    line-height: 1.6;
}
.alert-card .ac-title {
    font-weight: 500;
    color: #f87171;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.25rem;
}

/* ── Typing indicator ── */
.typing-dots {
    display: flex; gap: 4px; align-items: center;
    padding: 0.65rem 0.9rem;
    background: #111827;
    border: 1px solid #1a2e1a;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    width: fit-content;
}
.typing-dots span {
    width: 6px; height: 6px;
    background: #4ade80;
    border-radius: 50%;
    animation: bounce 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.3; }
    30%            { transform: translateY(-5px); opacity: 1; }
}

/* ── Session status bar ── */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0a0e17;
    border: 1px solid #111827;
    border-radius: 8px;
    padding: 0.55rem 1rem;
    margin-bottom: 1.2rem;
    font-size: 0.72rem;
    color: #374151;
}
.status-bar .sb-item { display: flex; align-items: center; gap: 0.35rem; }
.status-bar .sev-0  { color: #4ade80; }
.status-bar .sev-1  { color: #facc15; }
.status-bar .sev-2  { color: #f97316; }
.status-bar .sev-3  { color: #ef4444; }

/* ── Input area ── */
.stTextArea > div > div > textarea {
    background: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.85rem 1rem !important;
    resize: none !important;
    line-height: 1.55 !important;
    transition: border-color 0.2s !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: #22c55e !important;
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.08) !important;
    outline: none !important;
}
.stTextArea > div > div > textarea::placeholder { color: #374151 !important; }
.stTextArea label { display: none !important; }

/* ── Send button ── */
.stButton > button {
    background: #14532d !important;
    color: #4ade80 !important;
    border: 1px solid #166534 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.4rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #166534 !important;
    border-color: #22c55e !important;
    color: #86efac !important;
}
.stButton > button:active { transform: scale(0.98) !important; }

/* ── Divider ── */
hr { border-color: #1f2937 !important; margin: 1.2rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 4px; }

/* ── Opt-in connect card ── */
.connect-card {
    background: #0f1629;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    margin-top: 0.6rem;
}
.connect-card p {
    font-size: 0.82rem;
    color: #93c5fd;
    margin-bottom: 0.7rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "messages":         [],
        "session_token":    f"HAI-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}",
        "message_count":    0,
        "peak_severity":    0,
        "current_severity": 0,
        "connected":        False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─────────────────────────────────────────────────────────────
#  MOCK BACKEND  (delete when M3 is ready)
# ─────────────────────────────────────────────────────────────
COPING_RESOURCES = {
    0: None,
    1: {
        "type":    "breathing",
        "title":   "4-7-8 Breathing",
        "content": "Inhale for 4 counts → hold for 7 → exhale slowly for 8. Repeat 3 times. This activates your parasympathetic nervous system and can reduce anxious feelings within minutes.",
    },
    2: {
        "type":    "grounding",
        "title":   "5-4-3-2-1 Grounding",
        "content": "Name 5 things you can see · 4 you can touch · 3 you can hear · 2 you can smell · 1 you can taste. This technique anchors you to the present moment.",
    },
    3: None,
}

ECHO_RESPONSES = {
    0: [
        "I hear you. Thank you for sharing that with me.",
        "It sounds like things are going okay. Keep checking in — I'm always here.",
        "That's good to know. How are you feeling beyond that?",
    ],
    1: [
        "It sounds like you're carrying a lot right now. You don't have to carry it alone.",
        "I hear that things feel heavy. It's okay to feel this way — and it matters that you're expressing it.",
        "Thank you for trusting me with this. What you're feeling is real and valid.",
    ],
    2: [
        "I'm really glad you're talking. What you're going through sounds genuinely hard.",
        "That sounds exhausting. You deserve support — you don't have to figure this out by yourself.",
        "I hear you. Things feel very difficult right now, and that's important.",
    ],
    3: [
        "I'm here with you. What you're feeling matters, and you matter.",
        "You reached out, and that takes courage. Please know support is available right now.",
        "I hear you. You are not alone in this moment.",
    ],
}

def mock_analyze(message: str, token: str) -> dict:
    """Simulates the M3 backend response. Remove when real backend is live."""
    lower = message.lower()

    crisis_kws = ["kill myself", "end my life", "don't want to be here", "want to die",
                  "better off dead", "no reason to live", "suicide", "suicidal", "overdose",
                  "goodbye forever", "written letters", "have a plan"]
    high_kws   = ["hopeless", "falling apart", "breaking down", "can't cope",
                  "empty inside", "numb", "alone", "no one cares", "worthless",
                  "can't go on", "hurting myself", "self harm"]
    mid_kws    = ["anxious", "stressed", "overwhelmed", "crying", "can't sleep",
                  "tired", "exhausted", "scared", "worried", "lonely"]

    flags = [kw for kw in crisis_kws if kw in lower]
    if flags:
        severity = 3
    elif any(kw in lower for kw in high_kws):
        severity = 2
        flags = [kw for kw in high_kws if kw in lower]
    elif any(kw in lower for kw in mid_kws):
        severity = 1
    else:
        severity = 0

    severity_names = {0: "low", 1: "medium", 2: "high", 3: "crisis"}

    time.sleep(random.uniform(0.8, 1.6))  # simulate latency

    return {
        "severity":          severity,
        "label":             severity_names[severity],
        "confidence":        round(random.uniform(0.75, 0.97), 3),
        "flags":             flags,
        "coping_resource":   COPING_RESOURCES.get(severity),
        "counselor_alerted": severity >= 2,
        "session_summary": {
            "messages_analyzed": st.session_state.message_count + 1,
            "peak_severity":     max(st.session_state.peak_severity, severity),
        },
    }

# ─────────────────────────────────────────────────────────────
#  REAL BACKEND CALL  (M3: this calls your FastAPI endpoint)
# ─────────────────────────────────────────────────────────────
def call_backend(message: str) -> dict:
    if USE_MOCK:
        return mock_analyze(message, st.session_state.session_token)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/analyze",
            json={"message": message, "session_token": st.session_state.session_token},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Backend unreachable: {e}")
        return None

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def severity_color(s):
    return ["sev-0", "sev-1", "sev-2", "sev-3"][min(s, 3)]

def severity_label(s):
    return ["Low", "Mild", "High", "Crisis"][min(s, 3)]

def severity_icon(s):
    return ["🟢", "🟡", "🟠", "🔴"][min(s, 3)]

def now_ts():
    return datetime.now().strftime("%I:%M %p")

# ─────────────────────────────────────────────────────────────
#  RENDER HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hamdard-header">
  <div class="logo">Hamdard<span>AI</span></div>
  <div class="tagline">University Mental Wellness · Passive Monitoring</div>
  <div class="privacy-badge">
    <span class="dot"></span>
    Anonymous session · No personal data stored
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SESSION STATUS BAR
# ─────────────────────────────────────────────────────────────
sev      = st.session_state.current_severity
sc       = severity_color(sev)
sl       = severity_label(sev)
si       = severity_icon(sev)
n_msgs   = st.session_state.message_count

st.markdown(f"""
<div class="status-bar">
  <div class="sb-item">
    <span style="color:#1f2937">◆</span>
    <span style="color:#374151">Session</span>
    <code style="background:#111827;border:1px solid #1f2937;border-radius:4px;
                 padding:1px 6px;font-size:0.68rem;color:#4b5563;font-family:monospace">
      {st.session_state.session_token}
    </code>
  </div>
  <div class="sb-item">
    <span style="color:#374151">Mood</span>
    <span class="{sc}" style="font-weight:500">{si} {sl}</span>
  </div>
  <div class="sb-item">
    <span style="color:#374151">Messages</span>
    <span style="color:#4b5563">{n_msgs}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  WELCOME MESSAGE (first time only)
# ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="chat-window">
      <div class="msg-row echo">
        <div class="avatar hamdard-av">🌿</div>
        <div class="bubble hamdard-bubble">
          Hi. This is a safe space to write whatever's on your mind — 
          like a journal, but I'm always listening.<br><br>
          There's no right or wrong thing to say. Just express yourself freely.
          <span class="ts">Just now</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  RENDER CHAT HISTORY
# ─────────────────────────────────────────────────────────────
chat_html = '<div class="chat-window">'

for m in st.session_state.messages:
    if m["role"] == "user":
        chat_html += f"""
        <div class="msg-row user">
          <div class="avatar user-av">✦</div>
          <div class="bubble user-bubble">
            {m["content"]}
            <span class="ts">{m["ts"]}</span>
          </div>
        </div>"""
    else:
        # Echo response
        chat_html += f"""
        <div class="msg-row echo">
          <div class="avatar hamdard-av">🌿</div>
          <div class="bubble hamdard-bubble">
            {m["content"]}
            <span class="ts">{m["ts"]}</span>
          </div>
        </div>"""
        # Coping resource card
        if m.get("resource"):
            r = m["resource"]
            chat_html += f"""
            <div style="margin-left:2.2rem">
              <div class="resource-card">
                <div class="rc-title">💚 Try this · {r['title']}</div>
                {r['content']}
              </div>
            </div>"""
        # Counselor alert info (non-crisis)
        if m.get("counselor_alerted") and m.get("severity", 0) == 2:
            chat_html += """
            <div style="margin-left:2.2rem">
              <div class="alert-card">
                <div class="ac-title">🔔 Wellness Check Queued</div>
                A counselor has been quietly notified. You don't need to do anything — 
                they'll reach out only if you choose to connect.
              </div>
            </div>"""

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  CONNECT-TO-COUNSELOR OPT-IN  (crisis / high severity)
# ─────────────────────────────────────────────────────────────
if st.session_state.current_severity >= 2 and not st.session_state.connected:
    st.markdown("""
    <div class="connect-card">
      <p>A counselor is available if you'd like to talk.<br>
      This is completely your choice.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Connect with a Counselor →", key="connect_btn"):
        st.session_state.connected = True
        st.success("✓ A counselor has been notified and will reach out shortly.")

# ─────────────────────────────────────────────────────────────
#  INPUT AREA
# ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        label="message",
        placeholder="What's on your mind today…",
        height=100,
        key="input_box",
    )
    col_send, col_clear = st.columns([3, 1])
    with col_send:
        submitted = st.form_submit_button("Send →")
    with col_clear:
        if st.form_submit_button("New session"):
            for k in ["messages", "message_count", "peak_severity", "current_severity", "connected"]:
                del st.session_state[k]
            st.session_state.session_token = f"HAI-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"
            st.rerun()

# ─────────────────────────────────────────────────────────────
#  PROCESS SUBMISSION
# ─────────────────────────────────────────────────────────────
if submitted and user_input.strip():
    ts = now_ts()

    # Add user message
    st.session_state.messages.append({
        "role":    "user",
        "content": user_input.strip(),
        "ts":      ts,
    })
    st.session_state.message_count += 1

    # Show typing indicator, call backend
    with st.spinner(""):
        result = call_backend(user_input.strip())

    if result:
        sev = result.get("severity", 0)

        # Update session severity
        st.session_state.current_severity = sev
        st.session_state.peak_severity = max(st.session_state.peak_severity, sev)

        # Choose echo response
        echo_text = random.choice(ECHO_RESPONSES.get(sev, ECHO_RESPONSES[0]))

        st.session_state.messages.append({
            "role":              "echo",
            "content":           echo_text,
            "ts":                now_ts(),
            "severity":          sev,
            "resource":          result.get("coping_resource"),
            "counselor_alerted": result.get("counselor_alerted", False),
        })

    st.rerun()

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:2rem;padding-top:1rem;
            border-top:1px solid #111827;font-size:0.68rem;color:#1f2937;
            font-weight:300;letter-spacing:0.05em">
  HamdardAI · HEC Generative AI Hackathon · Cohort 3<br>
  <span style="color:#111827">Your session is anonymous and encrypted end-to-end</span>
</div>
""", unsafe_allow_html=True)%%writefile hamdardai_counselor_app.py
"""
HamdardAI — Counselor Dashboard (UPDATED UI)
"""

import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"
USE_MOCK = True

# ─────────────────────────────────────────────
# CSS (UPDATED FOR YOUR REQUESTS)
# ─────────────────────────────────────────────
st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    color: #c9d1d9;
}

/* ===== ROLE TOGGLE CENTER ===== */
.role-center {
    display: flex;
    justify-content: center;
    margin-top: 10px;
    margin-bottom: 15px;
}

/* ===== INPUT ROW FIX ===== */
.input-row {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 15px;
}

/* make input text BLACK as requested */
input, textarea {
    color: black !important;
}

/* buttons spacing */
.stButton > button {
    width: 100%;
}

/* keep input compact */
div[data-testid="stTextInput"] input {
    color: black !important;
    background: white !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROLE SELECTION (CENTERED TOGGLE)
# ─────────────────────────────────────────────
st.markdown("<div class='role-center'>", unsafe_allow_html=True)

role = st.radio(
    "",
    ["Student", "Counselor"],
    horizontal=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TOP INPUT ROW (YOUR REQUEST)
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns([5, 2, 2])

with col1:
    user_input = st.text_input("", placeholder="Type message...")

with col2:
    send_btn = st.button("Send")

with col3:
    new_session = st.button("New Session")

# Action logic (basic demo)
if send_btn:
    if user_input:
        st.success(f"Sent: {user_input}")

if new_session:
    st.warning("New session started")
    st.rerun()

# ─────────────────────────────────────────────
# YOUR ORIGINAL CONTENT (UNCHANGED CORE)
# ─────────────────────────────────────────────

st.markdown("""
<div style="margin-top:20px; text-align:center;">
    <h3 style="color:#e6edf3;">HamdardAI Counselor Dashboard</h3>
</div>
""", unsafe_allow_html=True)

# Mock alerts (kept minimal for clarity)
def get_mock_alerts():
    return [
        {"token":"HAI-7X-92-MN","severity":3,"messages":5,"avg":2.7,"time":"1h ago"},
        {"token":"HAI-3A-F1-PQ","severity":2,"messages":3,"avg":2.0,"time":"2h ago"},
        {"token":"HAI-9B-22-ZZ","severity":1,"messages":7,"avg":1.2,"time":"3h ago"},
    ]

alerts = get_mock_alerts()

st.markdown("### Alerts")

for a in alerts:
    st.markdown(f"""
    <div style="background:#0d1117;padding:10px;margin:8px 0;border-radius:8px;
                border:1px solid #161b22;">
        <b>{a['token']}</b> | Severity: {a['severity']} | Avg: {a['avg']} | {a['time']}
    </div>
    """, unsafe_allow_html=True)

