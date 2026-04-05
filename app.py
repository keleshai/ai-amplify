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

# ====================== FREE TIER ======================
CURRENT_FREE_LIMIT = 25   # generations per week

with st.sidebar:
    st.header("Settings")
    groq_api_key = st.text_input("Groq API Key (local testing only)", type="password", key="groq_key")
    
    # Use secret key from secrets.toml on the deployed app
    actual_key = st.secrets.get("GROQ_API_KEY") or groq_api_key
    
    if actual_key:
        openai.api_key = actual_key
        openai.base_url = "https://api.groq.com/openai/v1"
    
    brand_voice = st.text_area("Your Brand Voice (optional)", 
                              placeholder="Professional but witty tech marketer who loves data", 
                              height=100, key="brand_voice")

# Weekly reset logic
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now()
    st.session_state.uses_this_week = 0

if datetime.now() - st.session_state.last_reset > timedelta(days=7):
    st.session_state.uses_this_week = 0
    st.session_state.last_reset = datetime.now()

remaining = CURRENT_FREE_LIMIT - st.session_state.uses_this_week
st.info(f"🎟️ Free uses left this week: **{remaining}** out of {CURRENT_FREE_LIMIT}\n(Upgrade for Unlimited Text – only $4.99/month)")

# Upgrade button (replace with your real Stripe link later)
if st.button("🔓 Upgrade for Unlimited Text – only $4.99/month", type="primary", use_container_width=True):
    st.markdown("[Go to Stripe Checkout →](https://buy.stripe.com/your_real_link_here)", unsafe_allow_html=True)

# History file
HISTORY_FILE = "history.json"
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

def load_history():
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# Main input
input_content = st.text_area("Paste your original content here (blog, script, transcript, etc.)", 
                            height=300, placeholder="Start writing or paste...", key="input_content")

output_options = {
    "LinkedIn Post": "Professional, value-driven LinkedIn post (max 300 words)",
    "X/Twitter Thread": "Engaging Twitter thread (5-8 tweets)",
    "Instagram Caption": "Catchy Instagram caption + hashtags",
    "Email Newsletter": "Short email newsletter version",
    "YouTube Description": "SEO-optimized YouTube video description",
    "Pinterest Pin": "Pinterest title + description",
    "Blog Summary": "Compelling blog summary / TL;DR"
}

selected = st.multiselect("Choose output formats", 
                         options=list(output_options.keys()), 
                         default=["LinkedIn Post", "X/Twitter Thread"], 
                         key="selected_formats")

# ====================== GENERATE BUTTON ======================
if st.button("🚀 Generate with AI", type="primary", use_container_width=True, key="generate_button") and input_content:
    if st.session_state.uses_this_week >= CURRENT_FREE_LIMIT:
        st.error("⏰ You've used all your free generations this week!")
        st.markdown("[Upgrade for Unlimited Text – $4.99/month →](https://buy.stripe.com/your_real_link_here)", unsafe_allow_html=True)
    else:
        with st.spinner("AI is amplifying your content..."):
            results = {}
            # Use secret key from secrets.toml on deployed app
            groq_key = st.secrets.get("GROQ_API_KEY") or groq_api_key
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

            # Save to history
            entry = {
                "timestamp": datetime.now().isoformat(),
                "original": input_content[:200] + "...",
                "outputs": results
            }
            save_history(entry)

            st.session_state.uses_this_week += 1

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
history = load_history()
if history:
    for item in reversed(history[-5:]):
        st.caption(f"{item['timestamp'][:10]} • {item['original']}")
        for fmt, text in item["outputs"].items():
            st.write(f"• {fmt}")
else:
    st.info("No history yet – generate something!")

st.caption("AI Amplify • Content Creator Amplifier • Built by Naum Celesovski Aka Kelesh • Powered by Groq")