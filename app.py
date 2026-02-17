import streamlit as st
import warnings
import os
import re

warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

st.set_page_config(page_title="Host Review AI", page_icon="🏡")

GREEK_RE = re.compile(r"[Α-Ωα-ωάέήίόύώϊϋΐΰ]")

def detect_lang(text: str) -> str:
    return "GR" if GREEK_RE.search(text or "") else "EN"

def reply_text(lang: str, en: str, gr: str) -> str:
    return gr if lang == "GR" else en

def light_analyze(review: str):
    """Fallback: simple keyword heuristics to avoid any ML downloads."""
    text = (review or "").lower()

    positive_words = ["amazing", "great", "excellent", "perfect", "wonderful", "fantastic", "clean", "nice", "best", "love"]
    negative_words = ["dirty", "noise", "noisy", "bad", "terrible", "awful", "broken", "smell", "cold", "hot", "problem", "issue", "late"]

    pos = sum(w in text for w in positive_words)
    neg = sum(w in text for w in negative_words)

    if neg == 0 and pos > 0:
        sentiment = "POSITIVE"
        score = 0.95
    elif neg > 0 and pos == 0:
        sentiment = "NEGATIVE"
        score = 0.80
    else:
        sentiment = "MIXED"
        score = 0.65

    # crude topic
    topics = {
        "cleanliness": ["clean", "dirty", "smell", "stain"],
        "noise": ["noise", "noisy", "loud"],
        "comfort": ["bed", "mattress", "pillow", "cold", "hot", "ac"],
        "location": ["location", "area", "near", "close", "far"],
        "value": ["value", "price", "worth"],
        "staff": ["host", "staff", "service", "communication"],
    }
    main_issue = None
    for t, kws in topics.items():
        if any(k in text for k in kws) and sentiment != "POSITIVE":
            main_issue = t
            break

    return sentiment, score, main_issue

@st.cache_resource
def try_load_models():
    """
    Try to load HuggingFace pipelines.
    If blocked by corporate network/firewall, return None and use Light Mode.
    """
    try:
        from transformers import pipeline
        sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        topic_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        return sentiment_model, topic_model
    except Exception as e:
        return None, None

st.title("🏡 Host Review AI Assistant (Cloud Edition)")
st.write("Airbnb + Booking review analyzer & smart host replies. Designed to work reliably in corporate networks.")

platform = st.selectbox("Platform:", ["Airbnb", "Booking.com"])
tone = st.selectbox("Reply style:", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])
language_mode = st.selectbox("Reply language:", ["Auto 🤖", "English 🇬🇧", "Ελληνικά 🇬🇷"])

review = st.text_area("✍️ Paste guest review here:", height=160)

sentiment_model, topic_model = try_load_models()

mode = "AI Mode ✅" if sentiment_model and topic_model else "Light Mode 🛟 (always works)"
st.caption(f"Mode: **{mode}**")

labels = ["cleanliness", "location", "staff", "comfort", "value", "noise"]

if st.button("Analyze & Generate Reply", type="primary"):

    if not review.strip():
        st.warning("⚠️ Please paste a review first.")
    else:
        # language
        if language_mode.startswith("Auto"):
            lang = detect_lang(review)
        elif language_mode.startswith("English"):
            lang = "EN"
        else:
            lang = "GR"

        # analysis
        if sentiment_model and topic_model:
            s = sentiment_model(review)[0]
            s_label = s["label"]
            s_score = float(s["score"])
            t = topic_model(review, labels)
            main_issue = t["labels"][0]

            if s_label == "POSITIVE" and s_score > 0.90:
                main_issue = None
        else:
            s_label, s_score, main_issue = light_analyze(review)
            if s_label == "POSITIVE" and s_score > 0.90:
                main_issue = None

        booking_formal = (platform == "Booking.com")

        # replies
        if main_issue is None:
            if tone == "Friendly 😊":
                reply = reply_text(
                    lang,
                    "Thank you so much for your wonderful review! 😊 We’re truly happy you enjoyed your stay. Hope to welcome you back soon!",
                    "Σας ευχαριστούμε πάρα πολύ για την υπέροχη κριτική σας! 😊 Χαιρόμαστε πραγματικά που απολαύσατε τη διαμονή σας. Θα χαρούμε να σας φιλοξενήσουμε ξανά σύντομα!"
                )
            elif tone == "Professional ⭐":
                reply = reply_text(
                    lang,
                    "Thank you very much for your kind feedback. We are delighted you had a great experience. We look forward to hosting you again.",
                    "Σας ευχαριστούμε θερμά για τα καλά σας λόγια. Χαιρόμαστε ιδιαίτερα που είχατε μια εξαιρετική εμπειρία και θα χαρούμε να σας υποδεχτούμε ξανά."
                )
            else:
                reply = reply_text(
                    lang,
                    "Thank you for sharing such a wonderful review. It was truly a pleasure hosting you, and we would be honored to welcome you back for another exceptional stay.",
                    "Σας ευχαριστούμε για την εξαιρετική σας κριτική. Ήταν πραγματική μας χαρά να σας φιλοξενήσουμε και θα ήταν τιμή μας να σας υποδεχτούμε ξανά για μια ακόμη μοναδική εμπειρία διαμονής."
                )

            if booking_formal and lang == "EN":
                reply = reply.replace("Hope to welcome you back soon!", "We would be delighted to welcome you again soon.")
            if booking_formal and lang == "GR":
                reply = reply.replace("Θα χαρούμε να σας φιλοξενήσουμε ξανά σύντομα!", "Θα χαρούμε ιδιαίτερα να σας υποδεχτούμε ξανά σύντομα.")
        else:
            if tone == "Friendly 😊":
                reply = reply_text(
                    lang,
                    f"Thank you for your review! 😊 We appreciate your feedback about {main_issue}. We will work on improving this right away. Hope to host you again!",
                    f"Σας ευχαριστούμε για την κριτική σας! 😊 Εκτιμούμε τα σχόλιά σας σχετικά με το θέμα: {main_issue}. Θα φροντίσουμε άμεσα να το βελτιώσουμε. Ελπίζουμε να σας φιλοξενήσουμε ξανά!"
                )
            elif tone == "Professional ⭐":
                reply = reply_text(
                    lang,
                    f"Thank you for your valuable feedback. We apologize for the inconvenience regarding {main_issue}. Your comments help us improve, and we will take action immediately.",
                    f"Σας ευχαριστούμε για τα πολύτιμα σχόλιά σας. Ζητούμε συγγνώμη για την ενόχληση σχετικά με το θέμα: {main_issue}. Τα σχόλιά σας μας βοηθούν να βελτιωνόμαστε και θα λάβουμε άμεσα μέτρα."
                )
            else:
                reply = reply_text(
                    lang,
                    f"Thank you for sharing your experience with us. We sincerely regret the concern related to {main_issue}. Our team is already reviewing improvements to ensure an exceptional stay in the future.",
                    f"Σας ευχαριστούμε που μοιραστήκατε την εμπειρία σας. Λυπούμαστε ειλικρινά για το ζήτημα που αφορά το θέμα: {main_issue}. Η ομάδα μας ήδη εξετάζει βελτιώσεις ώστε να διασφαλίσουμε μια άψογη διαμονή στο μέλλον."
                )

            if booking_formal and lang == "EN":
                reply = reply.replace("Hope to host you again!", "We hope to have the pleasure of welcoming you again.")
            if booking_formal and lang == "GR":
                reply = reply.replace("Ελπίζουμε να σας φιλοξενήσουμε ξανά!", "Ελπίζουμε να έχουμε τη χαρά να σας υποδεχτούμε ξανά.")

        st.subheader("📊 Results")
        st.write("Platform:", platform)
        st.write("Sentiment:", s_label)
        st.write("Confidence:", round(s_score, 2))
        st.write("Main topic:", main_issue if main_issue else "None (100% positive)")

        st.subheader("✉️ Suggested Reply")
        st.code(reply, language="text")  # has built-in copy button
