import streamlit as st
import os
import streamlit as st
from auth import require_login, show_logout_button

require_login("Host Reply Pro")
show_logout_button()



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

