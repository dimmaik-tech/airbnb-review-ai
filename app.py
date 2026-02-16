import streamlit as st
from transformers import pipeline
import warnings
import os

# ----------------------------
# Hide warnings + HF noise
# ----------------------------
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

st.set_page_config(page_title="Host Review AI", page_icon="🏡")

# ----------------------------
# Title
# ----------------------------
st.title("🏡 Host Review AI Assistant")
st.write("Airbnb + Booking review analyzer & smart host reply generator.")

# ----------------------------
# Load models once
# ----------------------------
@st.cache_resource
def load_models():
    sentiment_model = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    topic_model = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

    return sentiment_model, topic_model


sentiment, topics = load_models()

# ----------------------------
# Options
# ----------------------------
labels = ["cleanliness", "location", "staff", "comfort", "value", "noise"]

platform = st.selectbox(
    "Platform:",
    ["Airbnb", "Booking.com", "Other"]
)

tone = st.selectbox(
    "Reply style:",
    ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"]
)

# ----------------------------
# Input
# ----------------------------
review = st.text_area("✍️ Paste guest review here:")

# ----------------------------
# Analyze Button
# ----------------------------
if st.button("Analyze & Generate Reply"):

    if review.strip() == "":
        st.warning("⚠️ Please enter a review first.")

    else:
        # Sentiment Analysis
        sent_result = sentiment(review)[0]
        label = sent_result["label"]
        score = sent_result["score"]

        # Topic Detection
        topic_result = topics(review, labels)
        main_issue = topic_result["labels"][0]

        # ----------------------------
        # Smart Positive Review Check
        # ----------------------------
        if label == "POSITIVE" and score > 0.90:
            main_issue = None

        # ----------------------------
        # Reply Generator
        # ----------------------------
        if main_issue is None:
            # Pure positive review reply
            if tone == "Friendly 😊":
                reply = (
                    "Thank you so much for your wonderful review! 😊 "
                    "We’re truly happy you enjoyed your stay. "
                    "Hope to welcome you back again soon!"
                )

            elif tone == "Professional ⭐":
                reply = (
                    "Thank you very much for your kind feedback. "
                    "We are delighted to hear you had a great experience. "
                    "We look forward to hosting you again."
                )

            else:  # Luxury
                reply = (
                    "Thank you for sharing such a wonderful review. "
                    "It was truly a pleasure hosting you, and we are delighted "
                    "that everything met your expectations. "
                    "We would be honored to welcome you back for another exceptional stay."
                )

        else:
            # Mixed/Negative review reply
            if tone == "Friendly 😊":
                reply = (
                    f"Thank you for your review! 😊 "
                    f"We appreciate your feedback about {main_issue}. "
                    "We will work on improving this right away. "
                    "Hope to host you again!"
                )

            elif tone == "Professional ⭐":
                reply = (
                    f"Thank you for your valuable feedback. "
                    f"We apologize for the inconvenience regarding {main_issue}. "
                    "Your comments help us improve, and we will take action immediately."
                )

            else:  # Luxury
                reply = (
                    f"Thank you for sharing your experience with us. "
                    f"We sincerely regret the concern related to {main_issue}. "
                    "Our team is already reviewing improvements to ensure an exceptional stay in the future."
                )

        # ----------------------------
        # Results
        # ----------------------------
        st.subheader("📊 Analysis Results")

        st.write("Platform:", platform)
        st.write("Sentiment:", label)
        st.write("Confidence:", round(score, 2))

        if main_issue:
            st.write("⚠️ Main Topic Detected:", main_issue)
        else:
            st.write("✅ Review is fully positive (no issues detected).")

        st.subheader("✉️ Suggested Host Reply")

        st.text_area("Copy your reply:", reply, height=150)
