from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode
import streamlit as st
import config
import requests

AUTH_URL = f"https://{config.AUTH0_DOMAIN}/authorize"
TOKEN_URL = f"https://{config.AUTH0_DOMAIN}/oauth/token"
USERINFO_URL = f"https://{config.AUTH0_DOMAIN}/userinfo"

def build_login_url():
    return (
        f"{AUTH_URL}?"
        + urlencode({
            "response_type": "code",
            "client_id": config.AUTH0_CLIENT_ID,
            "redirect_uri": config.REDIRECT_URI,
            "scope": "openid profile email",
        })
    )

def get_token(code):
    session = OAuth2Session(
        client_id=config.AUTH0_CLIENT_ID,
        client_secret=config.AUTH0_CLIENT_SECRET,
    )
    token = session.fetch_token(
        TOKEN_URL,
        code=code,
        grant_type="authorization_code",
        redirect_uri=config.REDIRECT_URI
    )
    return token

def get_user_info(token):
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    res = requests.get(USERINFO_URL, headers=headers)
    return res.json()

def login():
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        token = get_token(code)
        user = get_user_info(token)
        st.session_state["user"] = user
        st.query_params()  # clean URL
        return user

    if "user" in st.session_state:
        return st.session_state["user"]

    st.markdown("### 🔐 Please log in to continue:")
    st.markdown(f"[Login with Auth0]({build_login_url()})")
    st.stop()
