import streamlit as st
import os

# =========================================
# 🔐 PASSWORD LOGIN SYSTEM (PRO)
# =========================================

PASSWORD = st.secrets.get("APP_PASSWORD", None)

if PASSWORD is None:
    st.error("❌ Missing APP_PASSWORD in Secrets")
    st.stop()

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login_screen():
    st.title("🔒 Host Reply Pro – Private Access")
    st.write("This app is private. Please enter the password to continue.")

    pw = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if pw == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Access granted!")
            st.rerun()
        else:
            st.error("❌ Wrong password")


def logout_button():
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()


# =========================================
# 🚫 BLOCK ACCESS IF NOT LOGGED IN
# =========================================

if not st.session_state.logged_in:
    login_screen()
    st.stop()


# =========================================
# ✅ MAIN APP AFTER LOGIN
# =========================================

st.set_page_config(
    page_title="Host Reply Pro",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 Host Reply Pro")
st.caption("Airbnb/Booking review → smart analysis + premium host reply (GPT)")

st.success("✅ You are logged in!")

st.markdown(
    """
### What you can do
- ✍️ Generate professional host replies  
- 📊 Analyze guest sentiment  
- 🏠 Manage multiple properties  
- 📄 Export PDF reports  

➡️ Use the left sidebar menu to start.
"""
)

logout_button()
