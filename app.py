import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Host Review AI", page_icon="🏡", layout="wide")

st.title("🏡 Host Review AI")
st.caption("Airbnb/Booking review → ανάλυση + έτοιμη απάντηση host (GPT).")

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not api_key:
    st.error('Λείπει OPENAI_API_KEY στα Secrets. Βάλε: OPENAI_API_KEY="sk-..."')
    st.stop()

client = OpenAI(api_key=api_key)

col1, col2, col3 = st.columns(3)
with col1:
    platform = st.selectbox("Platform", ["Airbnb", "Booking.com", "Other"])
with col2:
    tone = st.selectbox("Reply style", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])
with col3:
    lang = st.selectbox("Language", ["English", "Greek"])

review = st.text_area("✍️ Paste guest review here:", height=220)

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
- Output ONLY the reply text.

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
    st.download_button("⬇️ Download reply.txt", reply, file_name="host_reply.txt")
