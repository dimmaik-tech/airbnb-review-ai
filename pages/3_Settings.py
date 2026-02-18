from auth import require_login, show_logout_button
require_login("Host Reply Pro")
show_logout_button()

import streamlit as st
from db import init_db, kv_set, kv_get

init_db()

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("⚙️ Settings")

def get_setting(key: str, default: str) -> str:
    v = kv_get(key)
    return v if v is not None else default

model = st.selectbox("Model", ["gpt-4o-mini"], index=0)

temperature = st.slider("Temperature", 0.0, 1.2, float(get_setting("temperature", "0.6")), 0.05)

default_platform = st.selectbox("Default platform", ["Airbnb", "Booking.com", "Other"],
                                index=["Airbnb","Booking.com","Other"].index(get_setting("default_platform", "Airbnb")))

default_tone = st.selectbox("Default tone", ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"],
                            index=["Friendly 😊","Professional ⭐","Luxury 5★ ✨"].index(get_setting("default_tone", "Professional ⭐")))

default_length = st.selectbox("Default reply length", ["Short", "Normal", "Premium"],
                              index=["Short","Normal","Premium"].index(get_setting("default_length", "Normal")))

auto_language = st.toggle("Auto language detect (recommended)", value=(get_setting("auto_language", "1") == "1"))

default_property = st.text_input("Default property name (optional)", value=get_setting("default_property", ""))

if st.button("💾 Save settings", type="primary"):
    kv_set("model", model)
    kv_set("temperature", str(temperature))
    kv_set("default_platform", default_platform)
    kv_set("default_tone", default_tone)
    kv_set("default_length", default_length)
    kv_set("auto_language", "1" if auto_language else "0")
    kv_set("default_property", default_property.strip())
    st.success("Saved ✅ (persistent)")

st.info("Tip: Τα settings πλέον σώζονται μόνιμα (SQLite).")
