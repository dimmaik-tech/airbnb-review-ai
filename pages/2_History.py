import streamlit as st

st.set_page_config(page_title="History", page_icon="🕘", layout="wide")
st.title("🕘 History")

hist = st.session_state.get("history", [])
if not hist:
    st.info("Δεν υπάρχει history ακόμα. Πήγαινε στο Review Generator και δημιούργησε 1 απάντηση.")
    st.stop()

for i, item in enumerate(hist, start=1):
    with st.expander(f"{i}) {item['platform']} • {item['tone']} • {item['language']} • {item['sentiment']}"):
        st.write("**Review:**")
        st.text_area("review", item["review"], height=120, key=f"r{i}")
        st.write("**Reply:**")
        st.text_area("reply", item["reply"], height=120, key=f"p{i}")
        st.code(item["reply"])
