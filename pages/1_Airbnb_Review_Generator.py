import os
import json
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Review Generator", page_icon="✍️", layout="wide")

# ---- Secrets / client ----
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not api_key:
    st.error('Λείπει OPENAI_API_KEY στα Secrets. (Manage app → Settings → Secrets)')
    st.stop()

client = OpenAI(api_key=api_key)

# ---- Session defaults ----
if "history" not in st.session_state:
    st.session_state.history = []

if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": "gpt-4o-mini",
        "temperature": 0.6,
        "default_platform": "Airbnb",
        "default_tone": "Professional ⭐",
        "auto_language": True,
        "auto_length": True,  # pro default
    }

S = st.session_state.settings

st.title("✍️ Review Generator")
st.caption("Paste review → Analyze → Premium reply. (GPT)")

# ---- UI ----
c1, c2, c3, c4 = st.columns(4)

with c1:
    platform = st.selectbox(
        "Platform",
        ["Airbnb", "Booking.com", "Other"],
        index=["Airbnb", "Booking.com", "Other"].index(S["default_platform"]),
    )

with c2:
    tone = st.selectbox(
        "Reply style",
        ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"],
        index=["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"].index(S["default_tone"]),
    )

with c3:
    if S.get("auto_language", True):
        lang_mode = st.selectbox("Language", ["Auto (detect)", "English", "Greek"], index=0)
    else:
        lang_mode = st.selectbox("Language", ["English", "Greek"], index=0)

with c4:
    # Pro: Auto length
    length_mode = st.selectbox(
        "Reply length",
        ["Auto", "Short", "Normal", "Detailed", "Luxury Long"],
        index=0,
        help="Auto = αποφασίζει το μήκος ανάλογα με sentiment + issues."
    )

review = st.text_area(
    "📝 Paste guest review here",
    height=220,
    placeholder="Paste the guest review text here...",
)

# ---- Helpers ----
ISSUE_LABELS = [
    "cleanliness", "noise", "check-in", "location", "comfort",
    "value", "staff/service", "communication", "amenities", "other"
]

def call_json(system: str, user: str, model: str, temperature: float) -> dict:
    """Ask GPT to return strict JSON."""
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)

def detect_language(text: str) -> str:
    data = call_json(
        system="Return JSON only.",
        user=f"""Detect the language of this text. Return JSON:
{{"language": "English" or "Greek" or "Mixed"}}.

TEXT:
{text}""",
        model=S["model"],
        temperature=0.0,
    )
    return data.get("language", "English")

def analyze_review(text: str) -> dict:
    data = call_json(
        system="You are a strict JSON generator. Output valid JSON only.",
        user=f"""
Analyze the review and return JSON with this schema:
{{
  "summary": "1-2 sentences",
  "sentiment": "positive" | "mixed" | "negative",
  "issues": [
    {{"label": one of {ISSUE_LABELS}, "severity": 1-5, "note": "short"}}
  ],
  "highlights": ["short bullet", "short bullet"]
}}

Review:
{text}
""",
        model=S["model"],
        temperature=0.2,
    )
    data.setdefault("issues", [])
    data.setdefault("highlights", [])
    data.setdefault("summary", "")
    data.setdefault("sentiment", "mixed")
    return data

def length_rules(length: str) -> dict:
    """Concrete constraints passed to prompt."""
    rules = {
        "Short":       {"paragraphs": 1, "words_max": 80,  "lines": "3–5"},
        "Normal":      {"paragraphs": 1, "words_max": 130, "lines": "5–8"},
        "Detailed":    {"paragraphs": 2, "words_max": 220, "lines": "8–12"},
        "Luxury Long": {"paragraphs": 3, "words_max": 320, "lines": "12–18"},
    }
    return rules.get(length, rules["Normal"])

def auto_length_from_analysis(analysis: dict, tone: str) -> str:
    """Auto choose length from sentiment + issues (+ luxury boost)."""
    sentiment = (analysis.get("sentiment") or "mixed").lower()
    issues = analysis.get("issues", []) or []
    sev_sum = sum(int(i.get("severity", 3)) for i in issues) if issues else 0

    if sentiment == "positive" and not issues:
        base = "Short"
    elif sentiment == "negative" or sev_sum >= 8 or len(issues) >= 2:
        base = "Detailed"
    else:
        base = "Normal"

    # Luxury boost: one step up
    if "Luxury" in tone:
        if base == "Short":
            return "Normal"
        if base == "Normal":
            return "Detailed"
        if base == "Detailed":
            return "Luxury Long"
    return base

def build_reply_prompt(platform: str, tone: str, language: str, analysis: dict, review_text: str, length_choice: str) -> str:
    issues = analysis.get("issues", [])
    sentiment = analysis.get("sentiment", "mixed")
    summary = analysis.get("summary", "")

    r = length_rules(length_choice)

    return f"""
You are a professional short-term rental host assistant.

Platform: {platform}
Tone: {tone}
Language: {language}
Target length: {length_choice} ({r["lines"]} lines, max {r["words_max"]} words, {r["paragraphs"]} paragraph(s))

Guest review (raw):
{review_text}

Analysis summary:
- Sentiment: {sentiment}
- Summary: {summary}
- Issues: {issues}

Rules:
- Respect the target length strictly (max words).
- Be polite, warm, and clear.
- If issues exist: apologize once, mention a realistic corrective action, and invite them back.
- Avoid overpromising, refunds, or admissions of liability.
- If fully positive: thank them, highlight 1–2 positives, invite them back.
- Output ONLY the final reply text (no headings, no bullets).
""".strip()

def generate_reply(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=S["model"],
        temperature=S["temperature"],
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()

# ---- Actions ----
colA, colB = st.columns([1, 1])

with colA:
    go = st.button("✅ Analyze & Generate Reply", type="primary")

with colB:
    clear = st.button("🧹 Clear")

if clear:
    st.rerun()

if go:
    if not review.strip():
        st.warning("Κάνε paste ένα review πρώτα.")
        st.stop()

    with st.spinner("Analyzing..."):
        # Language
        if lang_mode == "Auto (detect)":
            detected = detect_language(review)
            language = "Greek" if detected == "Greek" else "English"
        else:
            language = lang_mode

        analysis = analyze_review(review)

        # Length
        if length_mode == "Auto":
            final_length = auto_length_from_analysis(analysis, tone)
        else:
            final_length = length_mode

    with st.spinner("Generating reply..."):
        prompt = build_reply_prompt(platform, tone, language, analysis, review, final_length)
        reply = generate_reply(prompt)

    st.success("Done ✅")

    # ---- Show analysis ----
    st.subheader("📊 Analysis")
    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        st.write("**Summary:**", analysis.get("summary", ""))
        st.write("**Highlights:**", ", ".join(analysis.get("highlights", [])) if analysis.get("highlights") else "—")

    with c2:
        st.metric("Sentiment", str(analysis.get("sentiment", "mixed")).title())
        st.metric("Language", language)

    with c3:
        st.metric("Reply length", final_length)

    issues = analysis.get("issues", [])
    if issues:
        st.write("**Issues detected:**")
        for it in issues:
            st.write(f"- **{it.get('label','other')}** (severity {it.get('severity',3)}): {it.get('note','')}")
    else:
        st.write("**Issues detected:** — (fully positive / no clear issues)")

    # ---- Reply ----
    st.subheader("✉️ Suggested Host Reply")
    st.text_area("Reply", reply, height=170)
    st.code(reply)  # has built-in copy icon

    st.download_button("⬇️ Download reply.txt", reply, file_name="host_reply.txt")

    # Save to history
    st.session_state.history.insert(0, {
        "platform": platform,
        "tone": tone,
        "language": language,
        "sentiment": analysis.get("sentiment", "mixed"),
        "reply_length": final_length,
        "review": review,
        "reply": reply,
    })
    st.session_state.history = st.session_state.history[:10]
