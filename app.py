import streamlit as st

st.set_page_config(page_title="Airbnb Review AI", page_icon="🏠")

st.title("🏠 Airbnb Review AI Assistant")
st.write("Generate the perfect host reply instantly ✨")

tone = st.selectbox(
    "Choose reply style:",
    ["Friendly 😊", "Professional ⭐", "Luxury 5★ ✨"]
)

review = st.text_area("✍️ Paste a guest review here:")

if st.button("Generate Reply"):

    if review.strip() == "":
        st.warning("Please enter a review first.")
    else:
        if tone == "Friendly 😊":
            reply = (
                "Thank you so much for your wonderful review! 😊 "
                "We’re truly happy you enjoyed your stay. "
                "Hope to welcome you again soon!"
            )

        elif tone == "Professional ⭐":
            reply = (
                "Thank you very much for your kind feedback. "
                "We truly appreciate your comments and would be delighted "
                "to host you again in the future."
            )

        else:
            reply = (
                "Thank you for sharing such a wonderful experience. "
                "It was an absolute pleasure hosting you, and we look forward "
                "to welcoming you back for another exceptional stay."
            )

        st.subheader("✉️ Suggested Host Reply")
        st.text_area("Copy your reply:", reply, height=140)
