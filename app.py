import streamlit as st

st.set_page_config(page_title="Host Reply Pro", page_icon="🏡", layout="wide")

st.title("🏡 Host Reply Pro")
st.caption("Airbnb/Booking review → smart analysis + premium host reply (GPT).")

st.markdown(
    """
### Τι κάνει
- **Auto language** (Greek/English)
- **Issue detection** (cleanliness, noise, check-in, value κλπ)
- **Reply styles** (Friendly / Professional / Luxury 5★)
- **History** (κρατάει τις τελευταίες απαντήσεις)

➡️ Άνοιξε αριστερά το **Review Generator**.
"""
)

col1, col2 = st.columns([1, 2])
with col1:
    st.page_link("pages/1_Review_Generator.py", label="🚀 Start: Review Generator", icon="✍️")
with col2:
    st.info("Tip: Στο αποτέλεσμα θα έχεις και code block με εικονίδιο **Copy** πάνω δεξιά.")
