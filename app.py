import streamlit as st
import warnings
import os
from transformers import pipeline

# ----------------------------
# Hide warnings + HF noise
# ----------------------------
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Airbnb Review AI", page_icon="🏠")

# ----------------------------
# Title
# ----------------------------
st.title("🏠 Airbnb Review AI Assistant")
st.write("Analyze guest reviews & generate the perfect host reply.")

# ----------------------------
# Load ONLY Sentiment Model (Lightweight)
# ----------------------------
@st.cache_resource
def load_sentiment_model():
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

sentiment_model = load_sentiment_model()

# ----------------------------
# Simple Topic Detection (No AI, No RAM)
# ----------------------------
def detect_topic(text):
    text = text.lower()

    if "noise" in text or "loud" in text:
        return "noise"
    if "dirty" in text or "clean" in text or "cleanliness" in text:
        return "cleanliness"
    if "location" in text or "close" in text or "area" in text:
        return "location"
    if "host" in text or "staff" in text or "friendly" in text:
        return "hospitality"
    if "bed" in text or "comfort" in text:
        return "comfort"
    if "price" in text or "value" in text:
        return "value"

    return "overall experience"

# ----------------------------
# Options
# ----------------------------
tone = st.selectbox(
    "Choose reply style:",
    ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"]
)

# ----------------------------
# Input
# ----------------------------
review = st.text_area("✍️ Paste a guest review here:")

# ----------------------------
# Analyze Button
# ----------------------------
if st.button("Analyze Review"):

    if review.strip() == "":
        st.warning("⚠️ Please enter a review first.")

    else:
        # ----------------------------
        # Sentiment Analysis
        # ----------------------------
        sent_result = sentiment_model(review)[0]
        sentiment_label = sent_result["label"]
        confidence = round(sent_result["score"], 2)

        # Topic detection (light)
        main_topic = detect_topic(review)

        # ----------------------------
        # Reply Generator
        # ----------------------------
        if sentiment_label == "POSITIVE":

            if tone == "Friendly 😊":
                reply = (
                    "Thank you so much for your wonderful review! 😊 "
                    "We’re truly happy you enjoyed your stay. "
                    "Hope to welcome you back again soon!"
                )

            elif tone == "Professional ⭐":
                reply = (
                    "Thank you very much for your kind feedback. "
                    "We are delighted that you had a great experience. "
                    "We look forward to hosting you again in the future."
                )

            else:  # Luxury
                reply = (
                    "Thank you for sharing such a wonderful review. "
                    "It was a pleasure hosting you, and we are delighted "
                    "that you enjoyed the comfort and overall experience. "
                    "We would be honored to welcome you back again."
                )

        else:
            # Negative or mixed review → apology
            if tone == "Friendly 😊":
                reply = (
                    f"Thank you for your feedback! 😊 "
                    f"We’re sorry about the issue regarding {main_topic}. "
                    "We will do our best to improve. Hope to host you again!"
                )

            elif tone == "Professional ⭐":
                reply = (
                    f"Thank you for sharing your experience. "
                    f"We apologize for the inconvenience related to {main_topic}. "
                    "Your feedback helps us improve, and we appreciate it."
                )

            else:  # Luxury
                reply = (
                    f"Thank you for your valuable feedback. "
                    f"We sincerely regret the concern regarding {main_topic}. "
                    "Our team is already reviewing improvements to ensure "
                    "an exceptional stay in the future."
                )

        # ----------------------------
        # Results
        # ----------------------------
        st.subheader("📊 Analysis Results")
        st.write("😊 Sentiment:", sentiment_label)
        st.write("Confidence:", confidence)
        st.write("Topic detected:", main_topic)

        st.subheader("✉️ Suggested Host Reply")
        st.text_area("Copy your reply:", reply, height=120)
