import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Host Review AI", page_icon="🏡", layout="wide")

st.title("🏡 Host Review AI")
st.caption("Airbnb + Booking review → smart host reply generator (GPT).")

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not api_key:
    st.error("Missing OPENAI_API_KEY in Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

platform = st.selectbox("Platform", ["Airbnb", "Booking.com", "Other"])
tone = st.selectbox("Reply style", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])
lang = st.selectbox("Language", ["English", "Greek"])

review = st.text_area("✍️ Paste guest review here:")

if st.button("Generate Reply"):
    if not review.strip():
        st.warning("Paste a review first.")
        st.stop()

    prompt = f"""
You are a professional Airbnb host assistant.

Platform: {platform}
Tone: {tone}
Language: {lang}

Write a perfect host reply.
Guest review:
{review}

Reply only with the final message.
"""

    with st.spinner("Generating..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )

    reply = resp.choices[0].message.content.strip()

    st.subheader("✉️ Suggested Reply")
    st.text_area("Copy:", reply, height=180)
