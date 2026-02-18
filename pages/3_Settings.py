import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("⚙️ Settings")

if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": "gpt-4o-mini",
        "temperature": 0.6,
        "default_platform": "Airbnb",
        "default_tone": "Professional ⭐",
        "auto_language": True,
    }

S = st.session_state.settings

S["model"] = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=["gpt-4o-mini","gpt-4o"].index(S["model"]))
S["temperature"] = st.slider("Temperature", 0.0, 1.2, float(S["temperature"]), 0.1)

S["default_platform"] = st.selectbox("Default platform", ["Airbnb", "Booking.com", "Other"],
                                     index=["Airbnb","Booking.com","Other"].index(S["default_platform"]))
S["default_tone"] = st.selectbox("Default tone", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"],
                                 index=["Friendly 😊","Professional ⭐","Luxury 5★ ✨"].index(S["default_tone"]))

S["auto_language"] = st.toggle("Auto language detect (recommended)", value=bool(S["auto_language"]))

st.success("Saved in session ✅ (applies immediately).")
st.caption("Tip: Για μόνιμο saving (ακόμα και μετά από restart) θέλει storage/db — το κάνουμε στο v2.")
