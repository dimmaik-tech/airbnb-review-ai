import streamlit as st
import warnings
import os
from transformers import pipeline

# ----------------------------
# Hide warnings + telemetry
# ----------------------------
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Host Review AI v5", page_icon="🏠")

# ----------------------------
# Title
# ----------------------------
st.title("🏠 Host Review AI Assistant (v5)")
st.write("Airbnb + Booking smart replies — professional, luxury, multilingual.")

# ----------------------------
# Load models once
# ----------------------------
@st.cache_resource
def load_models():
    sentiment = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    translator_en_to_gr = pipeline(
        "translation_en_to_el",
        model="Helsinki-NLP/opus-mt-en-el"
    )

    translator_gr_to_en = pipeline(
        "translation_el_to_en",
        model="Helsinki-NLP/opus-mt-el-en"
    )

    return sentiment, translator_en_to_gr, translator_gr_to_en


sentiment_model, trans_en_gr, trans_gr_en = load_models()

# ----------------------------
# Language detection
# ----------------------------
def detect_language(text):
    greek_chars = sum(1 for c in text if "α" <= c.lower() <= "ω")
    return "Greek" if greek_chars > 5 else "English"

# ----------------------------
# Topic detection (simple keywords)
# ----------------------------
def detect_topic(text):
    t = text.lower()
    if "noise" in t or "θόρυβ" in t:
        return "noise"
    if "clean" in t or "dirty" in t or "καθαρι" in t:
        return "cleanliness"
    if "location" in t or "περιοχ" in t:
        return "location"
    if "bed" in t or "comfort" in t or "άνεσ" in t:
        return "comfort"
    if "price" in t or "value" in t or "τιμή" in t:
        return "value"
    return "overall experience"

# ----------------------------
# Session history
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ----------------------------
# Sidebar settings
# ----------------------------
st.sidebar.header("⚙️ Settings")

platform = st.sidebar.selectbox("Platform:", ["Airbnb", "Booking.com"])
tone = st.sidebar.selectbox("Reply Style:", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])
rating = st.sidebar.slider("Guest Rating:", 1, 5, 5)

guest_name = st.sidebar.text_input("Guest Name (optional):")
property_name = st.sidebar.text_input("Property Name (optional):")

translate_reply = st.sidebar.checkbox("Translate reply automatically")

# ----------------------------
# Review Input
# ----------------------------
review = st.text_area("✍️ Paste guest review here:")

# ----------------------------
# Generate Button
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

        # Topic
        topic = detect_topic(review)

        # Greeting personalization
        greeting = ""
        if guest_name.strip():
            greeting = f"Dear {guest_name}, "

        # Property mention
        prop_line = ""
        if property_name.strip():
            prop_line = f"at {property_name}"

        # Logic
        mixed = (label == "POSITIVE" and rating <= 4)

        # ----------------------------
        # Reply Builder
        # ----------------------------
        if label == "POSITIVE" and rating == 5:
            # Pure positive → NEVER apologize

            if lang == "English":
                if tone == "Luxury 5★ ✨":
                    reply = (
                        f"{greeting}thank you for such an outstanding review. "
                        f"We are truly honored that you enjoyed your stay {prop_line}. "
                        "It would be our absolute pleasure to welcome you back again."
                    )
                elif tone == "Professional ⭐":
                    reply = (
                        f"{greeting}thank you very much for your kind feedback. "
                        f"We’re delighted you had a wonderful experience {prop_line}. "
                        "We look forward to hosting you again."
                    )
                else:
                    reply = (
                        f"{greeting}thank you so much for your lovely review! 😊 "
                        "We’re so happy you enjoyed everything. Hope to see you again soon!"
                    )

            else:  # Greek
                if tone == "Luxury 5★ ✨":
                    reply = (
                        f"{greeting}σας ευχαριστούμε θερμά για την εξαιρετική σας κριτική. "
                        f"Είναι μεγάλη μας χαρά που απολαύσατε τη διαμονή σας {prop_line}. "
                        "Θα είναι τιμή μας να σας φιλοξενήσουμε ξανά."
                    )
                elif tone == "Professional ⭐":
                    reply = (
                        f"{greeting}σας ευχαριστούμε πολύ για τα όμορφα σχόλιά σας. "
                        "Χαιρόμαστε που είχατε μια υπέροχη εμπειρία. "
                        "Ανυπομονούμε να σας υποδεχτούμε ξανά."
                    )
                else:
                    reply = (
                        f"{greeting}σας ευχαριστούμε πάρα πολύ! 😊 "
                        "Χαιρόμαστε που όλα ήταν τέλεια. Θα χαρούμε να σας φιλοξενήσουμε ξανά!"
                    )

        elif mixed:
            # Mostly positive but improvement

            if lang == "English":
                reply = (
                    f"{greeting}thank you for your feedback. "
                    f"We’re very happy you enjoyed your stay {prop_line}. "
                    f"We will also pay attention to {topic} to make the experience even better next time."
                )
            else:
                reply = (
                    f"{greeting}σας ευχαριστούμε πολύ για την κριτική σας. "
                    "Χαιρόμαστε που μείνατε συνολικά ευχαριστημένοι. "
                    f"Θα δώσουμε προσοχή και στο θέμα: {topic}, ώστε να γίνει ακόμη καλύτερο."
                )

        else:
            # Negative review → apology only here

            if lang == "English":
                reply = (
                    f"{greeting}thank you for taking the time to share your experience. "
                    f"We sincerely regret the inconvenience regarding {topic}. "
                    "Your feedback is valuable, and we will take immediate steps to improve."
                )
            else:
                reply = (
                    f"{greeting}σας ευχαριστούμε για τα σχόλιά σας. "
                    f"Λυπούμαστε για την ταλαιπωρία σχετικά με το θέμα: {topic}. "
                    "Θα προχωρήσουμε άμεσα σε βελτιώσεις."
                )

        # ----------------------------
        # Translation Option
        # ----------------------------
        if translate_reply:
            if lang == "English":
                reply = trans_en_gr(reply)[0]["translation_text"]
            else:
                reply = trans_gr_en(reply)[0]["translation_text"]

        # Save history
        st.session_state.history.insert(0, reply)

        # ----------------------------
        # Output
        # ----------------------------
        st.subheader("📊 Analysis")
        st.write("Language:", lang)
        st.write("Sentiment:", label, "| Confidence:", confidence)
        st.write("Detected topic:", topic)

        st.subheader("✉️ Suggested Reply")
        st.code(reply)

        # Download reply
        st.download_button(
            "⬇️ Download Reply as TXT",
            reply,
            file_name="host_reply.txt"
        )

        st.success("Reply generated successfully ✅")

# ----------------------------
# History
# ----------------------------
st.subheader("🕒 Recent Replies")
if st.session_state.history:
    for i, r in enumerate(st.session_state.history[:5], 1):
        st.info(f"Reply #{i}:\n\n{r}")
else:
    st.write("No replies yet.")
