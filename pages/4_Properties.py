from auth import require_login, show_logout_button
require_login("Host Reply Pro")


import streamlit as st
from db import init_db, list_properties, upsert_property, delete_property

init_db()

st.set_page_config(page_title="Properties", page_icon="🏠", layout="wide")
st.title("🏠 Properties")
st.caption("Φτιάξε profiles για τα σπίτια σου ώστε το GPT να γράφει πιο σωστά / στο context.")

props = list_properties()
names = [p["name"] for p in props]

left, right = st.columns([1, 2])

with left:
    st.subheader("📌 Select / Create")
    selected = st.selectbox("Property", ["(New)"] + names, index=0)

with right:
    st.subheader("✍️ Property details")

    if selected == "(New)":
        data = {
            "name": "",
            "description": "",
            "location": "",
            "checkin": "",
            "checkout": "",
            "house_rules": "",
            "amenities": "",
        }
    else:
        data = next(p for p in props if p["name"] == selected)

    name = st.text_input("Name (unique)", value=data["name"])
    location = st.text_input("Location", value=data.get("location",""))
    description = st.text_area("Description", value=data.get("description",""), height=110)
    checkin = st.text_input("Check-in info", value=data.get("checkin",""))
    checkout = st.text_input("Check-out info", value=data.get("checkout",""))
    amenities = st.text_area("Amenities (comma separated)", value=data.get("amenities",""), height=90)
    house_rules = st.text_area("House rules", value=data.get("house_rules",""), height=110)

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("💾 Save / Update", type="primary"):
            if not name.strip():
                st.error("Βάλε όνομα property.")
            else:
                upsert_property({
                    "name": name.strip(),
                    "location": location.strip(),
                    "description": description.strip(),
                    "checkin": checkin.strip(),
                    "checkout": checkout.strip(),
                    "amenities": amenities.strip(),
                    "house_rules": house_rules.strip(),
                })
                st.success("Saved ✅")
                st.rerun()

    with c2:
        if selected != "(New)":
            if st.button("🗑️ Delete", type="secondary"):
                delete_property(selected)
                st.warning("Deleted.")
                st.rerun()
