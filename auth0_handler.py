# auth.py (No Auth0 - Optional Simple Login)

import streamlit as st

# Dummy credentials - replace with a real system if needed
USERS = {
    "admin": "admin123",
    "user": "user123"
}

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid credentials")

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.success("Logged out successfully.")

def require_login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
        st.stop()

def show_logout():
    if st.session_state.get("authenticated"):
        if st.sidebar.button("Logout"):
            logout()
