import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Airbnb AI Reviews", layout="wide")

st.title("🏡 Airbnb AI Review Generator")

# API KEY
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ Missing OpenAI API Key in Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

guest_name = st.text_input("Guest Name", "Guest")

notes = st.text_area(
    "Notes about the guest",
    placeholder="Very clean, polite, great communication..."
)

style = st.selectbox(
    "Review Style",
    ["Warm & Friendly", "Luxury 5★", "Short & Simple", "Professional Host"]
)

if st.button("✨ Generate Review"):
    with st.spinner("Generating..."):

        prompt = f"""
Write a perfect Airbnb host review.

Guest: {guest_name}
Style: {style}
Notes: {notes}

Short, warm, professional, 5-star tone.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert Airbnb host assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        review = response.choices[0].message.content

        st.success("✅ Review Ready!")
        st.text_area("Review", review, height=200)
