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
st.write("Generate perfect replies for Airbnb & Booking reviews (English + Greek).")

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
# Topic detection (fast keywords)
# ----------------------------
def detect_topic(text):
    text = text.lower()

    if "noise" in text or "loud" in text:
        return "noise"
    if "dirty" in text or "clean" in text:
        return "cleanliness"
    if "location" in text or "close" in text or "area" in text:
        return "location"
    if "host" in text or "staff" in text or "service" in text:
        return "hospitality"
    if "bed" in text or "comfort" in text:
        return "comfort"
    if "price" in text or "value" in text:
        return "value"

    return "overall experience"

# ----------------------------
# Controls
# ----------------------------
platform = st.selectbox("Platform:", ["Airbnb", "Booking.com"])

language = st.selectbox("Reply Language:", ["English 🇬🇧", "Greek 🇬🇷"])

rating = st.slider("Guest Rating (Stars):", 1, 5, 5)

tone = st.selectbox(
    "Reply Style:",
    ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"]
)

# ----------------------------
# Review Input
# ----------------------------
review = st.text_area("✍️ Paste the guest review here:")

# ----------------------------
# Generate Reply
# ----------------------------
if st.button("Generate Reply 🚀"):

    if review.strip() == "":
        st.warning("⚠️ Please enter a review first.")

    else:
        # Sentiment
        sent = sentiment_model(review)[0]
        label = sent["label"]
        confidence = round(sent["score"], 2)

        topic = detect_topic(review)

        # ----------------------------
        # POSITIVE LOGIC
        # ----------------------------
        is_positive = (label == "POSITIVE" and rating >= 4)

        # ----------------------------
        # Reply Templates
        # ----------------------------
        if is_positive:
            # THANK YOU reply (no apology)

            if language == "English 🇬🇧":

                if platform == "Airbnb":
                    reply = (
                        "Thank you so much for your wonderful review! 😊 "
                        "We’re truly happy you enjoyed your stay. "
                        "You are always welcome back anytime!"
                    )
                else:  # Booking
                    reply = (
                        "Thank you for your excellent feedback. "
                        "We are delighted you enjoyed your stay. "
                        "We look forward to welcoming you again."
                    )

            else:  # Greek 🇬🇷
                if platform == "Airbnb":
                    reply = (
                        "Σας ευχαριστούμε πάρα πολύ για την υπέροχη κριτική σας! 😊 "
                        "Χαιρόμαστε πραγματικά που απολαύσατε τη διαμονή σας. "
                        "Θα είναι χαρά μας να σας φιλοξενήσουμε ξανά!"
                    )
                else:
                    reply = (
                        "Σας ευχαριστούμε για τα εξαιρετικά σχόλιά σας. "
                        "Χαιρόμαστε πολύ που μείνατε ευχαριστημένοι από τη διαμονή σας. "
                        "Ανυπομονούμε να σας υποδεχτούμε ξανά."
                    )

        else:
            # NEGATIVE or MIXED reply → apology + improvement

            if language == "English 🇬🇧":

                reply = (
                    f"Thank you for sharing your feedback. "
                    f"We are sorry for the inconvenience regarding {topic}. "
                    "We will take immediate steps to improve. "
                    "We truly hope to welcome you again in the future."
                )

            else:  # Greek
                reply = (
                    f"Σας ευχαριστούμε για τα σχόλιά σας. "
                    f"Λυπούμαστε για την ταλαιπωρία σχετικά με το θέμα: {topic}. "
                    "Θα προχωρήσουμε άμεσα σε βελτιώσεις. "
                    "Ελπίζουμε να έχουμε την ευκαιρία να σας φιλοξενήσουμε ξανά."
                )

        # ----------------------------
        # Display Results
        # ----------------------------
        st.subheader("📊 Analysis Results")
        st.write("Sentiment:", label)
        st.write("Confidence:", confidence)
        st.write("Detected topic:", topic)
        st.write("Rating:", f"{rating} ⭐")

        st.subheader("✉️ Suggested Reply")

        st.code(reply)

        # Copy button trick
        st.markdown(
            f"""
            <button onclick="navigator.clipboard.writeText(`{reply}`)"
            style="padding:10px 15px;
                   border-radius:10px;
                   background:#2E86C1;
                   color:white;
                   border:none;
                   cursor:pointer;">
            📋 Copy Reply
            </button>
            """,
            unsafe_allow_html=True
        )
