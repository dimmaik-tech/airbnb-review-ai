import streamlit as st
import os

# =========================================
# ✅ PAGE CONFIG (MUST BE FIRST)
# =========================================
st.set_page_config(
    page_title="Host Reply Pro",
    page_icon="🏡",
    layout="wide"
)

# =========================================
# 🔒 PASSWORD PROTECTION
# =========================================
PASSWORD = st.secrets.get("APP_PASSWORD", "1234")

pw = st.text_input("🔑 Enter Password", type="password")

if pw != PASSWORD:
    st.warning("🔒 Access denied")
    st.stop()

# =========================================
# ✅ MAIN APP STARTS HERE
# =========================================

st.title("🏡 Host Reply Pro")
st.caption("Airbnb/Booking review → smart analysis + premium host reply (GPT).")

st.markdown(
    """
### Τι κάνει
- ✅ Auto language (Greek/English)
- ✅ Issue detection (cleanliness, noise, check-in, value κλπ)
- ✅ Reply styles (Friendly / Professional / Luxury 5★)
- ✅ History (κρατάει τις τελευταίες απαντήσεις)
- ✅ PDF Export report

➡️ Άνοιξε αριστερά το **Review Generator** για να ξεκινήσεις.
"""
)

st.info("Tip: Το OpenAI key μπαίνει μόνο στα Secrets (δεν φαίνεται ποτέ δημόσια).")
