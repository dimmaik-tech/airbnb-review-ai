import re
import streamlit as st

st.set_page_config(page_title="Airbnb Review AI", page_icon="🏠")

st.title("🏠 Airbnb Review AI Assistant")
st.write("Analyze guest reviews & generate the perfect host reply (light + stable).")

# ----------------------------
# Config
# ----------------------------
TOPICS = {
    "cleanliness": ["clean", "dirty", "dust", "smell", "hygiene", "towel", "sheets", "linen", "bathroom", "mold"],
    "noise": ["noise", "noisy", "loud", "street", "neighbors", "party", "construction"],
    "location": ["location", "close", "far", "near", "walk", "metro", "bus", "center", "beach", "restaurants", "shops"],
    "comfort": ["comfortable", "comfort", "bed", "pillow", "mattress", "sofa", "ac", "air conditioning", "heating"],
    "value": ["value", "price", "worth", "expensive", "cheap", "overpriced"],
    "staff": ["host", "helpful", "friendly", "communication", "check-in", "check in", "support", "kind"],
}

POS_WORDS = [
    "excellent","amazing","perfect","great","fantastic","wonderful","comfortable","clean",
    "helpful","friendly","recommend","exceptional","lovely","nice","super","awesome"
]

NEG_WORDS = [
    "dirty","bad","terrible","awful","poor","worst","noisy","loud","smell","broken",
    "cold","hot","problem","issue","uncomfortable","disappointed","rude","slow"
]

NEGATION = ["not", "no", "never", "hardly", "without"]

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def score_sentiment(text: str):
    """
    Simple, stable sentiment scoring (rule-based).
    Returns: label, confidence-ish (0..1), pos_hits, neg_hits
    """
    t = normalize(text)

    # Token-ish split
    words = re.findall(r"[a-z']+", t)

    pos = 0
    neg = 0

    for i, w in enumerate(words):
        window = words[max(0, i-2):i]  # small negation window

        # handle negations: "not clean" => negative, "not bad" => positive
        is_negated = any(n in window for n in NEGATION)

        if w in POS_WORDS:
            if is_negated:
                neg += 1
            else:
                pos += 1

        if w in NEG_WORDS:
            if is_negated:
                pos += 1
            else:
                neg += 1

    # fallback if no hits: neutral-positive bias for Airbnb-style reviews
    total = pos + neg
    if total == 0:
        return "NEUTRAL", 0.55, pos, neg

    score = pos - neg
    if score >= 2:
        label = "POSITIVE"
    elif score <= -2:
        label = "NEGATIVE"
    else:
        label = "MIXED"

    confidence = min(0.99, 0.55 + (abs(score) / max(1, total)) * 0.44)
    return label, round(confidence, 2), pos, neg

def detect_topic(text: str):
    t = normalize(text)
    counts = {}
    for topic, kws in TOPICS.items():
        c = 0
        for kw in kws:
            if kw in t:
                c += 1
        counts[topic] = c

    best_topic = max(counts, key=counts.get)
    best_score = counts[best_topic]

    if best_score == 0:
        return None, counts
    return best_topic, counts

def generate_reply(review: str, tone: str, sentiment_label: str, topic: str | None):
    # If it's positive/neutral, do NOT apologize.
    if sentiment_label in ["POSITIVE", "NEUTRAL"]:
        if tone == "Friendly 😊":
            return (
                "Thank you so much for your wonderful review! 😊 "
                "We’re really happy you enjoyed your stay and appreciated the home. "
                "You’re always welcome back!"
            )
        if tone == "Professional ⭐":
            return (
                "Thank you for your kind feedback. "
                "We’re delighted you enjoyed your stay, and we truly appreciate your recommendation. "
                "We’d be happy to host you again."
            )
        # Luxury
        return (
            "Thank you for sharing such a lovely review. "
            "We’re delighted you enjoyed the comfort and the overall experience. "
            "It would be our pleasure to welcome you back for another exceptional stay."
        )

    # MIXED / NEGATIVE: apology only then
    issue = topic or "your experience"

    if tone == "Friendly 😊":
        return (
            f"Thank you for your feedback! 😊 "
            f"We’re sorry to hear about the issue related to {issue}. "
            "We’ll address it right away and would love the chance to host you again with an improved experience."
        )

    if tone == "Professional ⭐":
        return (
            "Thank you for your feedback. "
            f"We apologize for the inconvenience regarding {issue}. "
            "We appreciate your comments and will take corrective action to improve."
        )

    return (
        "Thank you for sharing your experience with us. "
        f"We sincerely regret the concern related to {issue}. "
        "Our team is reviewing improvements to ensure an exceptional stay going forward."
    )

# ----------------------------
# UI
# ----------------------------
tone = st.selectbox("Choose reply style:", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"])
review = st.text_area("✍️ Paste a guest review here:", height=160)

if st.button("Analyze Review"):
    if not review.strip():
        st.warning("⚠️ Please enter a review first.")
    else:
        sentiment_label, confidence, pos_hits, neg_hits = score_sentiment(review)
        topic, topic_counts = detect_topic(review)

        reply = generate_reply(review, tone, sentiment_label, topic)

        st.subheader("📊 Analysis Results")
        st.write("😊 Sentiment:", sentiment_label)
        st.write("Confidence:", confidence)
        st.write("🔎 Positive hits:", pos_hits, "| Negative hits:", neg_hits)
        st.write("🏷️ Main Topic:", topic if topic else "No clear topic detected")

        st.subheader("✉️ Suggested Host Reply")
        st.text_area("Copy your reply:", reply, height=130)
