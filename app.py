import streamlit as st

st.set_page_config(page_title="Host Reply Pro", page_icon="🏡", layout="wide")

st.title("🏡 Host Reply Pro")
st.caption("Airbnb/Booking review → smart analysis + premium host reply (GPT).")

st.markdown(
    """
### Τι έχεις (Premium v1)
- ✅ **Persistent Settings** (κρατάνε μόνιμα)
- ✅ **Persistent History** (δεν χάνεται)
- ✅ **Properties profiles** (πολλά σπίτια)
- ✅ **Reply length** (Short / Normal / Premium)
- ✅ **Crisis mode** (damage control σε κακά reviews)
- ✅ **PDF export** (report)

➡️ Διάλεξε σελίδα από το αριστερό menu:
- **Airbnb Review Generator**
- **History**
- **Settings**
- **Properties**
- **PDF Export**
"""
)

st.info("Tip: Το OpenAI key μπαίνει μόνο στο Streamlit → Manage app → Settings → Secrets.")
