import streamlit as st
import openai
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF

st.set_page_config(page_title="AI Amplify", page_icon="🔎", layout="wide")

st.title("🔎 AI Amplify")
st.subheader("Content Creator Amplifier")
st.caption("🚀 Turn 1 piece of content into 10+ platform-ready posts in seconds.")

CURRENT_FREE_LIMIT = 25

with st.sidebar:
    st.header("Settings")
    groq_api_key = st.text_input("Groq API Key (local testing only)", type="password", key="groq_key")
    brand_voice = st.text_area("Your Brand Voice (optional)", placeholder="Professional but witty tech marketer who loves data", height=100, key="brand_voice")

# TEMPORARY HARDCODE FOR TESTING - REPLACE WITH YOUR REAL KEY
groq_key = "gsk_SdlX2g9xLzk6fqTaluMVWGdyb3FYXA7c31muHaCv3TekNDIEiC2"   # ←←← PASTE YOUR REAL FULL KEY HERE

# Weekly reset logic
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now()
    st.session_state.uses_this_week = 0

if datetime.now() - st.session_state.last_reset > timedelta(days=7):
    st.session_state.uses_this_week = 0
    st.session_state.last_reset = datetime.now()

remaining = CURRENT_FREE_LIMIT - st.session_state.uses_this_week
st.info(f"🎟️ Free uses left this week: **{remaining}** out of {CURRENT_FREE_LIMIT}")

input_content = st.text_area("Paste your original content here", height=300, placeholder="Start writing or paste...", key="input_content")

output_options = {
    "LinkedIn Post": "Professional, value-driven LinkedIn post (max 300 words)",
    "X/Twitter Thread": "Engaging Twitter thread (5-8 tweets)",
    "Instagram Caption": "Catchy Instagram caption + hashtags",
    "Email Newsletter": "Short email newsletter version",
    "YouTube Description": "SEO-optimized YouTube video description",
    "Pinterest Pin": "Pinterest title + description",
    "Blog Summary": "Compelling blog summary / TL;DR"
}

selected = st.multiselect("Choose output formats", options=list(output_options.keys()), default=["LinkedIn Post", "X/Twitter Thread"], key="selected_formats")

if st.button("🚀 Generate with AI", type="primary", use_container_width=True, key="generate_button") and input_content:
    with st.spinner("AI is amplifying your content..."):
        results = {}
        client = openai.OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        
        for fmt in selected:
            prompt = f"""
            You are an expert content repurposer. Rewrite the following content as a {output_options[fmt]}.
            Original content: {input_content}
            Brand voice: {brand_voice or 'Keep it natural and engaging'}
            Make it highly engaging, platform-optimized, and ready to copy-paste.
            """
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                results[fmt] = response.choices[0].message.content.strip()
            except Exception as e:
                results[fmt] = f"Error: {str(e)}"

        st.success("✅ Done! Copy any output below.")
        for fmt, text in results.items():
            with st.expander(f"📌 {fmt}", expanded=True):
                st.text_area("", text, height=250, label_visibility="collapsed", key=f"output_text_{fmt}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Copy", key=f"copy_{fmt}"):
                        st.code(text)
                with col2:
                    if st.button("Download as PDF", key=f"pdf_{fmt}"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, text)
                        pdf_bytes = pdf.output(dest="S").encode("latin1")
                        st.download_button("Download PDF", pdf_bytes, f"{fmt}.pdf", "application/pdf")

        st.balloons()

st.divider()
st.subheader("📜 Your Amplify History")
st.info("History will appear here after generations")

st.caption("AI Amplify • Content Creator Amplifier • Built by Naum Celesovski Aka Kelesh • Powered by Groq")