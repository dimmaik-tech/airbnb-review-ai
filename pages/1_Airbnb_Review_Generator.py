import json
from datetime import datetime, timezone

import streamlit as st

from db import init_db, add_history, list_properties, kv_get
from utils import get_client_from_secrets, detect_language, analyze_review, build_reply_prompt, generate_text

init_db()
client = get_client_from_secrets(st)

# ---- Load settings (persistent) ----
def get_setting(key: str, default: str) -> str:
    v = kv_get(key)
    return v if v is not None else default

MODEL = get_setting("model", "gpt-4o-mini")
TEMP = float(get_setting("temperature", "0.6"))
DEFAULT_PLATFORM = get_setting("default_platform", "Airbnb")
DEFAULT_TONE = get_setting("default_tone", "Professional ⭐")
AUTO_LANG = get_setting("auto_language", "1") == "1"
DEFAULT_LENGTH = get_setting("default_length", "Normal")
DEFAULT_PROPERTY = get_setting("default_property", "")

st.set_page_config(page_title="Review Generator", page_icon="✍️", layout="wide")
st.title("✍️ Review Generator")
st.caption("Paste review → Analyze → Premium reply. (GPT)")

props = list_properties()
prop_names = ["(No property)"] + [p["name"] for p in props]
default_prop_index = 0
if DEFAULT_PROPERTY and DEFAULT_PROPERTY in prop_names:
    default_prop_index = prop_names.index(DEFAULT_PROPERTY)

c0, c1, c2, c3 = st.columns([1.2, 1, 1, 1])
with c0:
    property_name = st.selectbox("Property", prop_names, index=default_prop_index)
with c1:
    platform = st.selectbox("Platform", ["Airbnb", "Booking.com", "Other"],
                            index=["Airbnb","Booking.com","Other"].index(DEFAULT_PLATFORM))
with c2:
    tone = st.selectbox("Reply style", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"],
                        index=["Friendly 😊","Professional ⭐","Luxury 5★ ✨"].index(DEFAULT_TONE))
with c3:
    length = st.selectbox("Reply length", ["Short", "Normal", "Premium"],
                          index=["Short","Normal","Premium"].index(DEFAULT_LENGTH))

if AUTO_LANG:
    lang_mode = st.selectbox("Language", ["Auto (detect)", "English", "Greek"], index=0)
else:
    lang_mode = st.selectbox("Language", ["English", "Greek"], index=0)

review = st.text_area("📝 Paste guest review here", height=220, placeholder="Paste the guest review text here...")

colA, colB = st.columns([1, 1])
with colA:
    go = st.button("✅ Analyze & Generate Reply", type="primary")
with colB:
    clear = st.button("🧹 Clear")

if clear:
    st.rerun()

def get_selected_property():
    if property_name == "(No property)":
        return None
    for p in props:
        if p["name"] == property_name:
            return p
    return None

# --- Copy button (JS) ---
def copy_button(text: str):
    safe = json.dumps(text)  # proper JS string
    st.components.v1.html(
        f"""
        <button style="
            padding:10px 14px;border-radius:10px;border:1px solid #ddd;
            background:#fff;cursor:pointer;font-weight:600;"
            onclick='navigator.clipboard.writeText({safe});
                     this.innerText="✅ Copied"; setTimeout(()=>this.innerText="📋 Copy Reply", 1400);'>
            📋 Copy Reply
        </button>
        """,
        height=55
    )

if go:
    if not review.strip():
        st.warning("Κάνε paste ένα review πρώτα.")
        st.stop()

    with st.spinner("Analyzing..."):
        # Language
        if lang_mode == "Auto (detect)":
            detected = detect_language(client, MODEL, review)
            language = "Greek" if detected == "Greek" else "English"
        else:
            language = lang_mode

        analysis = analyze_review(client, MODEL, review)

    with st.spinner("Generating reply..."):
        prop = get_selected_property()
        prompt = build_reply_prompt(platform, tone, language, length, analysis, review, prop)
        reply = generate_text(client, MODEL, TEMP, prompt)

    st.success("Done ✅")

    # ---- Show analysis ----
    st.subheader("📊 Analysis")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write("**Summary:**", analysis.get("summary", ""))
        hi = analysis.get("highlights", [])
        st.write("**Highlights:**", ", ".join(hi) if hi else "—")
    with c2:
        st.metric("Sentiment", str(analysis.get("sentiment", "mixed")).title())
        st.metric("Language", language)

    issues = analysis.get("issues", [])
    if issues:
        st.write("**Issues detected:**")
        for it in issues:
            st.write(f"- **{it.get('label','other')}** (severity {it.get('severity',3)}): {it.get('note','')}")
    else:
        st.write("**Issues detected:** — (fully positive / no clear issues)")

    # ---- Reply ----
    st.subheader("✉️ Suggested Host Reply")
    copy_button(reply)
    st.text_area("Reply", reply, height=170)
    st.code(reply)

    st.download_button("⬇️ Download reply.txt", reply, file_name="host_reply.txt")

    # Save to DB history
    add_history({
        "created_at": datetime.now(timezone.utc).isoformat(),
        "property_name": "" if property_name == "(No property)" else property_name,
        "platform": platform,
        "tone": tone,
        "language": language,
        "length": length,
        "sentiment": analysis.get("sentiment", "mixed"),
        "issues_json": json.dumps(issues, ensure_ascii=False),
        "summary": analysis.get("summary", ""),
        "highlights_json": json.dumps(analysis.get("highlights", []), ensure_ascii=False),
        "review": review,
        "reply": reply,
    })
