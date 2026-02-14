import streamlit as st
import warnings
import os
from transformers import pipeline

# ----------------------------
# Hide warnings
# ----------------------------
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Host Review AI", page_icon="🏠")

# ----------------------------
# Title
# ----------------------------
st.title("🏠 Host Review AI Assistant")
st.write("Generate perfect replies for Airbnb & Booking reviews.")

# ----------------------------
# Load Sentiment Model (Lightweight)
# ----------------------------
@st.cache_resource
def load_sentiment():
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

sentiment_model = load_sentiment()

# ----------------------------
# Detect Topic (simple + fast)
# ----------------------------
def detect_topic(text):
    text = text.lower()

    if "noise" in text or "loud" in text:
        return "noise"
    if "dirty" in text or "clean" in text:
        return "cleanliness"
    if "location" in text or "close" in text:
        return "location"
    if "host" in text or "staff" in text:
        return "hospitality"
    if "bed" in text or "comfort" in text:
        return "comfort"
    if "price" in text or "value" in text:
        return "value"

    return "overall experience"

# ----------------------------
# Platform selector
# ----------------------------
platform = st.selectbox(
    "Select platform:",
    ["Airbnb", "Booking.com"]
)

# ----------------------------
# Tone selector
# ----------------------------
tone = st.selectbox(
    "Choose reply style:",
    ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"]
)

# ----------------------------
# Input review
# ----------------------------
review = st.text_area("✍️ Paste the guest review here:")

# ----------------------------
# Analyze Button
# ----------------------------
if st.button("Generate Reply"):

    if review.strip() == "":
        st.warning("⚠️ Please enter a review first.")

    else:
        # Sentiment
        sent = sentiment_model(review)[0]
        label = sent["label"]
        confidence = round(sent["score"], 2)

        topic = detect_topic(review)

        # ----------------------------
        # POSITIVE REVIEW → Always Thank
        # ----------------------------
        if label == "POSITIVE":

            if platform == "Airbnb":
                reply = (
                    "Thank you so much for your wonderful review! 😊 "
                    "We’re truly happy you enjoyed your stay and appreciated "
                    "the comfort and location. "
                    "You are always welcome back anytime!"
                )

            else:  # Booking
                reply = (
                    "Thank you for your excellent feedback. "
                    "We are delighted you enjoyed your stay. "
                    "We look forward to welcoming you again."
                )

        # ----------------------------
        # NEGATIVE REVIEW → Apology + Improvement
        # ----------------------------
        else:

            if platform == "Airbnb":
                reply = (
                    f"Thank you for your feedback. "
                    f"We’re sorry about the issue regarding {topic}. "
                    "We will work on improvements immediately. "
                    "Hope we can host you again in the future."
                )

            else:  # Booking
                reply = (
                    f"Thank you for sharing your experience. "
                    f"We regret the inconvenience related to {topic}. "
                    "Your comments help us improve, and we appreciate them."
                )

        # ----------------------------
        # Display Results
        # ----------------------------
        st.subheader("📊 Analysis Results")
        st.write("Sentiment:", label)
        st.write("Confidence:", confidence)
        st.write("Topic detected:", topic)

        st.subheader("✉️ Suggested Reply")
        st.text_area("Copy your reply:", reply, height=140)
