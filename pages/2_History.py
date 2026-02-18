import json
import streamlit as st

from db import init_db, list_history, clear_history

init_db()

st.set_page_config(page_title="History", page_icon="🕘", layout="wide")
st.title("🕘 History")
st.caption("Ό,τι έφτιαξες αποθηκεύεται μόνιμα εδώ (SQLite).")

top = st.columns([1, 1, 2])
with top[0]:
    limit = st.selectbox("Show last", [10, 20, 50, 100], index=2)
with top[1]:
    if st.button("🗑️ Clear ALL history", type="secondary"):
        clear_history()
        st.rerun()

items = list_history(limit=limit)

if not items:
    st.info("Δεν υπάρχει ιστορικό ακόμα. Πήγαινε στο Review Generator.")
    st.stop()

for it in items:
    issues = json.loads(it["issues_json"]) if it.get("issues_json") else []
    highlights = json.loads(it["highlights_json"]) if it.get("highlights_json") else []
    prop = it.get("property_name") or "—"

    with st.expander(f"#{it['id']} • {it['created_at'][:19]} • {it['platform']} • {it['sentiment']} • {prop}"):
        st.write("**Tone:**", it["tone"])
        st.write("**Language:**", it["language"])
        st.write("**Length:**", it["length"])
        st.write("**Summary:**", it["summary"])
        st.write("**Highlights:**", ", ".join(highlights) if highlights else "—")
        st.write("**Issues:**")
        if issues:
            for x in issues:
                st.write(f"- {x.get('label')} (sev {x.get('severity')}): {x.get('note')}")
        else:
            st.write("—")

        st.divider()
        st.write("**Review:**")
        st.text_area("Review", it["review"], height=120, key=f"rev_{it['id']}")

        st.write("**Reply:**")
        st.text_area("Reply", it["reply"], height=140, key=f"rep_{it['id']}")
        st.code(it["reply"])
