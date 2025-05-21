import os
import streamlit as st
from dotenv import load_dotenv

# Detect environment
if "auth0" in st.secrets:
    # ✅ Streamlit Cloud mode
    AUTH0_CLIENT_ID = st.secrets.get("auth0", {}).get("client_id", os.getenv("AUTH0_CLIENT_ID"))
    AUTH0_CLIENT_SECRET = st.secrets.get("auth0", {}).get("client_secret", os.getenv("AUTH0_CLIENT_SECRET"))
    AUTH0_DOMAIN = st.secrets.get("auth0", {}).get("domain", os.getenv("AUTH0_DOMAIN"))
    REDIRECT_URI = st.secrets.get("auth0", {}).get("redirect_uri", os.getenv("REDIRECT_URI"))
else:
    # ✅ Local dev mode
    load_dotenv()
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
