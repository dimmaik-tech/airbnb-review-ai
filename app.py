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

st.set_page_config(page_title="Airbnb Review AI", page_icon="🏠")

# ----------------------------
# Title
# ----------------------------
st.title("🏠 Airbnb Review AI Assistant")
st.write("Analyze guest reviews & generate the perfect host reply.")

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
labels = ["noise", "cleanliness", "location", "staff", "comfort", "value"]

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
        # Sentiment
        sent_result = sentiment(review)[0]

        # Main issue detection
        topic_result = topics(review, labels)
        main_issue = topic_result["labels"][0]

        # Reply generator
        if tone == "Friendly 😊":
            reply = (
                f"Thank you so much for your review! 😊 "
                f"We're sorry about the issue with {main_issue}. "
                "We will do our best to improve. Hope to host you again!"
            )

        elif tone == "Professional ⭐":
            reply = (
                f"Thank you for your feedback. "
                f"We apologize for the inconvenience regarding {main_issue}. "
                "We appreciate your comments and will take action to improve."
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

        st.write("😊 Sentiment:", sent_result["label"])
        st.write("Confidence:", round(sent_result["score"], 2))
        st.write("⚠️ Main Issue:", main_issue)

        st.subheader("✉️ Suggested Host Reply")

        st.text_area("Copy your reply:", reply, height=120)
