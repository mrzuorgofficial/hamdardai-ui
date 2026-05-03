import streamlit as st
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
