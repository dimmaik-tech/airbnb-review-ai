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
st.set_page_config(page_title="Host Review AI v4", page_icon="🏠")

# ----------------------------
# Title
# ----------------------------
st.title("🏠 Host Review AI Assistant (v4)")
st.write("Smart replies for Airbnb & Booking — fast, elegant, professional.")

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
# Detect language automatically
# ----------------------------
def detect_language(text):
    greek_chars = sum(1 for c in text if "α" <= c.lower() <= "ω")
    if greek_chars > 5:
        return "Greek"
    return "English"

# ----------------------------
# Topic detection (keywords)
# ----------------------------
def detect_topic(text):
    text = text.lower()

    if "noise" in text or "loud" in text or "θόρυβ" in text:
        return "noise"
    if "dirty" in text or "clean" in text or "καθαρι" in text:
        return "cleanliness"
    if "location" in text or "close" in text or "περιοχ" in text:
        return "location"
    if "host" in text or "staff" in text or "φιλοξ" in text:
        return "hospitality"
    if "bed" in text or "comfort" in text or "άνεσ" in text:
        return "comfort"
    if "price" in text or "value" in text or "τιμή" in text:
        return "value"

    return "overall experience"

# ----------------------------
# Session history
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ----------------------------
# Controls
# ----------------------------
platform = st.selectbox("Platform:", ["Airbnb", "Booking.com"])
rating = st.slider("Guest Rating (Stars):", 1, 5, 5)
tone = st.selectbox("Reply Style:", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])

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
        # Detect language
        lang = detect_language(review)

        # Sentiment
        sent = sentiment_model(review)[0]
        label = sent["label"]
        confidence = round(sent["score"], 2)

        topic = detect_topic(review)

        # Mixed review logic
        mixed = (label == "POSITIVE" and rating <= 4)

        # ----------------------------
        # Reply Templates
        # ----------------------------
        if label == "POSITIVE" and rating == 5:
            # Pure positive

            if lang == "English":

                if tone == "Luxury 5★ ✨":
                    reply = (
                        "Thank you for such an exceptional review. "
                        "We are truly honored that you enjoyed your stay. "
                        "It would be our pleasure to welcome you back again."
                    )
                elif tone == "Professional ⭐":
                    reply = (
                        "Thank you very much for your kind feedback. "
                        "We are delighted you had a wonderful stay. "
                        "We look forward to hosting you again."
                    )
                else:
                    reply = (
                        "Thank you so much for your lovely review! 😊 "
                        "We’re so happy you enjoyed everything. "
                        "Hope to see you again soon!"
                    )

            else:  # Greek

                if tone == "Luxury 5★ ✨":
                    reply = (
                        "Σας ευχαριστούμε θερμά για την εξαιρετική σας κριτική. "
                        "Είναι μεγάλη μας χαρά που απολαύσατε τη διαμονή σας. "
                        "Θα είναι τιμή μας να σας φιλοξενήσουμε ξανά."
                    )
                elif tone == "Professional ⭐":
                    reply = (
                        "Σας ευχαριστούμε πολύ για τα όμορφα σχόλιά σας. "
                        "Χαιρόμαστε που είχατε μια υπέροχη εμπειρία. "
                        "Ανυπομονούμε να σας υποδεχτούμε ξανά."
                    )
                else:
                    reply = (
                        "Σας ευχαριστούμε πάρα πολύ! 😊 "
                        "Χαιρόμαστε που όλα ήταν τέλεια. "
                        "Θα χαρούμε να σας φιλοξενήσουμε ξανά!"
                    )

        elif mixed:
            # Positive but small improvement

            if lang == "English":
                reply = (
                    "Thank you for your feedback. "
                    "We’re very happy you enjoyed your stay overall. "
                    f"We will also pay attention to the area of {topic} to make it even better next time."
                )
            else:
                reply = (
                    "Σας ευχαριστούμε πολύ για την κριτική σας. "
                    "Χαιρόμαστε που μείνατε συνολικά ευχαριστημένοι. "
                    f"Θα δώσουμε ιδιαίτερη προσοχή και στο θέμα: {topic}, ώστε να γίνει ακόμη καλύτερο."
                )

        else:
            # Negative review

            if lang == "English":
                if platform == "Booking.com":
                    reply = (
                        "Thank you for taking the time to share your experience. "
                        f"We regret the inconvenience regarding {topic}. "
                        "Your feedback is valuable, and we will take immediate steps to improve."
                    )
                else:
                    reply = (
                        f"Thank you for your feedback. We’re sorry about the issue with {topic}. "
                        "We will work on improvements right away and hope to host you again."
                    )

            else:
                reply = (
                    "Σας ευχαριστούμε για τα σχόλιά σας. "
                    f"Λυπούμαστε για την ταλαιπωρία σχετικά με το θέμα: {topic}. "
                    "Θα προχωρήσουμε άμεσα σε βελτιώσεις."
                )

        # Save to history
        st.session_state.history.insert(0, reply)

        # ----------------------------
        # Display Results
        # ----------------------------
        st.subheader("📊 Analysis Results")
        st.write("Language:", lang)
        st.write("Sentiment:", label)
        st.write("Confidence:", confidence)
        st.write("Topic detected:", topic)
        st.write("Rating:", f"{rating} ⭐")

        st.subheader("✉️ Suggested Reply")
        st.code(reply)

        st.success("Reply generated successfully ✅")

# ----------------------------
# Reply History
# ----------------------------
st.subheader("🕒 Recent Replies")
if st.session_state.history:
    for i, r in enumerate(st.session_state.history[:3], 1):
        st.write(f"Reply #{i}:")
        st.info(r)
else:
    st.write("No replies generated yet.")
