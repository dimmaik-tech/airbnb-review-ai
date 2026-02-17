import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Airbnb Review Generator", page_icon="✍️", layout="wide")

st.title("✍️ Airbnb Review Generator (GPT)")
st.caption("Ανάλυση review + έτοιμη απάντηση host με tone επιλογή.")

# παίρνει το key από Streamlit Secrets (Settings → Secrets)
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not api_key:
    st.error('Λείπει OPENAI_API_KEY στα Secrets. Βάλε: OPENAI_API_KEY="sk-..."')
    st.stop()

client = OpenAI(api_key=api_key)

platform = st.selectbox("Platform", ["Airbnb", "Booking.com", "Other"])
tone = st.selectbox("Reply style", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])
lang = st.selectbox("Language", ["English", "Greek"])
review = st.text_area("✍️ Paste guest review here:")

def build_prompt(platform, tone, lang, review):
    return f"""
You are an expert short-term rental host assistant.
Task: Analyze the guest review and write a perfect host reply.

Platform: {platform}
Tone: {tone}
Language: {lang}

Rules:
- Be polite, warm, concise.
- If there is a complaint, apologize and state a corrective action.
- Avoid overpromising.
- Output only the reply text.

Guest review:
{review}
""".strip()

if st.button("Analyze & Generate Reply"):
    if not review.strip():
        st.warning("Γράψε/κάνε paste ένα review πρώτα.")
        st.stop()

    with st.spinner("Generating..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": build_prompt(platform, tone, lang, review)}],
            temperature=0.6,
        )
        reply = resp.choices[0].message.content.strip()

    st.subheader("✉️ Suggested Host Reply")
    st.text_area("Copy your reply:", reply, height=180)
    st.code(reply)
