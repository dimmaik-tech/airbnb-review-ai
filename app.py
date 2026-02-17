import re
import streamlit as st

st.set_page_config(page_title="Host Reply Pro", page_icon="🏨")

# ----------------------------
# Lexicons (light + stable)
# ----------------------------
TOPICS = {
    "cleanliness": ["clean", "dirty", "dust", "smell", "hygiene", "towel", "towels", "sheets", "linen", "bathroom", "mold", "stain"],
    "noise": ["noise", "noisy", "loud", "street", "neighbors", "party", "construction", "thin walls"],
    "location": ["location", "close", "far", "near", "walk", "metro", "bus", "center", "beach", "restaurants", "shops", "parking"],
    "comfort": ["comfortable", "comfort", "bed", "pillow", "mattress", "sofa", "ac", "air conditioning", "heating", "shower", "water pressure"],
    "value": ["value", "price", "worth", "expensive", "cheap", "overpriced", "cost"],
    "communication": ["host", "helpful", "friendly", "communication", "check-in", "check in", "support", "kind", "responsive", "instructions"],
}

POS_PHRASES = [
    "highly recommend", "would recommend", "would stay again", "perfectly equipped",
    "exceptional", "everything is available", "very kind", "very helpful"
]

POS_WORDS = set([
    "excellent","amazing","perfect","great","fantastic","wonderful","comfortable","clean",
    "helpful","friendly","recommend","exceptional","lovely","nice","super","awesome",
    "beautiful","spacious","quiet","modern","spotless","convenient"
])

NEG_WORDS = set([
    "dirty","bad","terrible","awful","poor","worst","noisy","loud","smell","broken",
    "cold","hot","problem","issue","uncomfortable","disappointed","rude","slow",
    "missing","leak","mold","stain","bugs","cockroach","unsafe","dangerous"
])

COMPLAINT_PHRASES = [
    "we were disappointed", "i was disappointed", "not as expected", "didn't work", "did not work",
    "was broken", "was dirty", "there was a problem", "there was an issue", "not clean",
    "too noisy", "no hot water", "no warm water", "couldn't sleep", "could not sleep"
]

NEGATION = {"not","no","never","hardly","without"}

def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t

def tokenize(text: str):
    return re.findall(r"[a-z']+", normalize(text))

def phrase_hits(text: str, phrases: list[str]) -> int:
    t = normalize(text)
    return sum(1 for p in phrases if p in t)

def sentiment_score(text: str):
    """
    Returns:
      score: int (pos - neg with negation handling)
      pos_hits, neg_hits: ints
    """
    words = tokenize(text)
    pos = 0
    neg = 0

    for i, w in enumerate(words):
        window = words[max(0, i-2):i]
        negated = any(n in window for n in NEGATION)

        if w in POS_WORDS:
            if negated:
                neg += 1
            else:
                pos += 1

        if w in NEG_WORDS:
            if negated:
                pos += 1
            else:
                neg += 1

    # phrase boosts
    pos += phrase_hits(text, POS_PHRASES) * 2
    neg += phrase_hits(text, COMPLAINT_PHRASES) * 3

    return (pos - neg), pos, neg

def detect_topic(text: str):
    t = normalize(text)
    counts = {}
    for topic, kws in TOPICS.items():
        c = 0
        for kw in kws:
            if kw in t:
                c += 1
        counts[topic] = c

    best = max(counts, key=counts.get)
    if counts[best] == 0:
        return None, counts
    return best, counts

def classify_review(text: str):
    """
    Output:
      label: POSITIVE / MIXED / NEGATIVE
      complaint: bool (controls whether we apologize)
      confidence: 0..1
    """
    score, pos_hits, neg_hits = sentiment_score(text)

    # complaint rule: either complaint phrases OR enough negative hits
    complaint = (phrase_hits(text, COMPLAINT_PHRASES) > 0) or (neg_hits >= 2 and score < 0)

    if score >= 3 and not complaint:
        label = "POSITIVE"
    elif score <= -2 and complaint:
        label = "NEGATIVE"
    else:
        label = "MIXED" if complaint else "POSITIVE"

    total = max(1, pos_hits + neg_hits)
    confidence = min(0.99, 0.60 + (abs(score) / total) * 0.35)
    return label, complaint, round(confidence, 2), score, pos_hits, neg_hits

def format_reply(platform: str, tone: str, length: str, language: str,
                 complaint: bool, topic: str | None, highlights: list[str]) -> str:
    issue = topic or "the points you mentioned"

    # Optional highlight sentence
    hi = ""
    if highlights:
        # keep it short & professional
        if language == "English":
            hi = " We’re glad you especially enjoyed " + ", ".join(highlights[:2]) + "."
        else:
            hi = " Χαιρόμαστε ιδιαίτερα που σας άρεσαν " + ", ".join(highlights[:2]) + "."

    # Base templates
    if language == "English":
        if not complaint:
            if platform == "Airbnb":
                base = "Thank you for your wonderful review and for choosing to stay with us."
            else:
                base = "Thank you for taking the time to share your experience."

            if tone == "Professional":
                mid = " We’re delighted everything met your expectations."
            elif tone == "Luxury":
                mid = " We’re delighted you enjoyed an exceptional stay with us."
            else:
                mid = " We’re so happy you enjoyed your stay!"

            close = " We’d be happy to host you again anytime."
            if platform == "Booking":
                close = " We truly appreciate your recommendation and hope to welcome you back soon."

            text = base + mid + hi + close

        else:
            if platform == "Airbnb":
                base = "Thank you for your feedback and for staying with us."
            else:
                base = "Thank you for your feedback. We appreciate you letting us know."

            if tone == "Professional":
                mid = f" We’re sorry for the inconvenience regarding {issue}."
            elif tone == "Luxury":
                mid = f" We sincerely regret the concern related to {issue}."
            else:
                mid = f" We’re sorry about the issue with {issue}."

            close = " We’re already reviewing this to improve, and we hope to welcome you back for a better experience."
            text = base + mid + close
    else:
        # Greek
        if not complaint:
            if platform == "Airbnb":
                base = "Σας ευχαριστούμε θερμά για την υπέροχη κριτική και που επιλέξατε να μείνετε μαζί μας."
            else:
                base = "Σας ευχαριστούμε που αφιερώσατε χρόνο να μοιραστείτε την εμπειρία σας."

            if tone == "Professional":
                mid = " Χαιρόμαστε που όλα ανταποκρίθηκαν στις προσδοκίες σας."
            elif tone == "Luxury":
                mid = " Χαιρόμαστε που απολαύσατε μια πραγματικά εξαιρετική διαμονή."
            else:
                mid = " Χαιρόμαστε πολύ που απολαύσατε τη διαμονή σας!"

            close = " Θα χαρούμε να σας φιλοξενήσουμε ξανά."
            if platform == "Booking":
                close = " Σας ευχαριστούμε για τη σύστασή σας και θα χαρούμε να σας υποδεχτούμε ξανά σύντομα."

            text = base + mid + hi + close

        else:
            if platform == "Airbnb":
                base = "Σας ευχαριστούμε για τα σχόλιά σας και που μείνατε μαζί μας."
            else:
                base = "Σας ευχαριστούμε για την ενημέρωση. Εκτιμούμε τα σχόλιά σας."

            if tone == "Professional":
                mid = f" Λυπούμαστε για την αναστάτωση σχετικά με {issue}."
            elif tone == "Luxury":
                mid = f" Λυπούμαστε ειλικρινά για το ζήτημα που αφορά {issue}."
            else:
                mid = f" Λυπούμαστε για το θέμα με {issue}."

            close = " Το εξετάζουμε ήδη ώστε να βελτιωθούμε, και ελπίζουμε να σας φιλοξενήσουμε ξανά με καλύτερη εμπειρία."
            text = base + mid + close

    # Length control
    if length == "Short":
        # keep first 1-2 sentences
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(parts[:2]).strip()
    if length == "Long":
        # add an extra pro sentence
        if language == "English":
            extra = " If there’s anything we can do to make your next stay even better, please let us know."
        else:
            extra = " Αν υπάρχει κάτι που θα θέλατε στην επόμενη διαμονή σας, θα χαρούμε να το γνωρίζουμε."
        return (text + extra).strip()

    return text.strip()

def extract_highlights(text: str):
    t = normalize(text)
    candidates = [
        ("the view", ["view", "terrace", "balcony", "sea"]),
        ("the cleanliness", ["clean", "spotless"]),
        ("the location", ["location", "beach", "restaurants", "shops", "center"]),
        ("the comfort", ["comfortable", "bed", "mattress", "pillow"]),
        ("the communication", ["host", "helpful", "friendly", "responsive", "communication"]),
    ]
    hits = []
    for label, kws in candidates:
        if any(k in t for k in kws):
            hits.append(label)
    # dedupe
    out = []
    for h in hits:
        if h not in out:
            out.append(h)
    return out

# ----------------------------
# UI
# ----------------------------
col1, col2, col3 = st.columns(3)
with col1:
    platform = st.selectbox("Platform", ["Airbnb", "Booking"])
with col2:
    language = st.selectbox("Language", ["English", "Greek"])
with col3:
    length = st.selectbox("Length", ["Short", "Medium", "Long"])

tone = st.selectbox("Tone", ["Friendly", "Professional", "Luxury"])
review = st.text_area("✍️ Paste a guest review here:", height=170)

if st.button("Analyze Review"):
    if not review.strip():
        st.warning("⚠️ Please enter a review first.")
    else:
        label, complaint, confidence, score, pos_hits, neg_hits = classify_review(review)
        topic, topic_counts = detect_topic(review)
        highlights = extract_highlights(review)

        reply = format_reply(platform, tone, length, language, complaint, topic, highlights)

        st.subheader("📊 Analysis Results")
        st.write("Sentiment:", label)
        st.write("Confidence:", confidence)
        st.write("Complaint detected:", "YES" if complaint else "NO")
        st.write("Main topic:", topic if topic else "No clear topic")
        if highlights:
            st.write("Highlights:", ", ".join(highlights[:3]))

        with st.expander("Debug (optional)"):
            st.write({"score": score, "pos_hits": pos_hits, "neg_hits": neg_hits, "topic_counts": topic_counts})

        st.subheader("✉️ Suggested Host Reply")
        st.text_area("Copy your reply:", reply, height=140)
