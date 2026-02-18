import streamlit as st

def _get_password() -> str:
    # Πρέπει να υπάρχει στα Streamlit Secrets ως APP_PASSWORD
    return str(st.secrets.get("APP_PASSWORD", "")).strip()

def logout():
    st.session_state["auth_ok"] = False
    st.session_state.pop("auth_ok", None)

def require_login(app_name: str = "Host Reply Pro"):
    """
    Call this at the TOP of app.py and at the TOP of every page in /pages.
    Blocks access unless password is correct.
    """
    pw = _get_password()

    # Αν δεν έχεις βάλει APP_PASSWORD στα Secrets → κόβει πρόσβαση (ασφάλεια)
    if not pw:
        st.error("🔒 Private app: Missing APP_PASSWORD in Streamlit Secrets.")
        st.stop()

    # Already logged in
    if st.session_state.get("auth_ok", False):
        return

    # ---- Private Access Screen ----
    st.set_page_config(page_title=f"{app_name} – Private Access", page_icon="🔒", layout="centered")
    st.title("🔒 Host Reply Pro – Private Access")
    st.caption("This app is private. Enter the password to continue.")

    with st.form("login_form", clear_on_submit=False):
        entered = st.text_input("Password", type="password", placeholder="Enter password…")
        ok = st.form_submit_button("Login")

    if ok:
        if entered == pw:
            st.session_state["auth_ok"] = True
            st.success("✅ Access granted")
            st.rerun()
        else:
            st.error("❌ Wrong password")

    st.stop()

def show_logout_button():
    """Put this in sidebar/top bar wherever you want."""
    if st.session_state.get("auth_ok", False):
        if st.sidebar.button("🚪 Logout"):
            logout()
            st.rerun()
