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
        st.experimental_set_query_params()  # clean URL
        return user

    if "user" in st.session_state:
        return st.session_state["user"]

    # Not logged in (or after logout)
    st.markdown("### 🔐 You must log in to continue")
    st.markdown(f'''
        <a href="{build_login_url()}" target="_self" style="text-decoration:none;font-weight:bold;">
            🔓 Login with Auth0
        </a>
    ''', unsafe_allow_html=True)
    st.stop()
    
def logout_button():
    import streamlit as st
    logout_url = f"https://{config.AUTH0_DOMAIN}/v2/logout?returnTo={config.REDIRECT_URI}&client_id={config.AUTH0_CLIENT_ID}"
    
    # Clear user session for Streamlit (acts locally)
    if "user" in st.session_state:
        del st.session_state["user"]

    # Show Logout link (still needed to log out of Auth0)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'''
        <a href="{logout_url}" target="_self" style="text-decoration:none;">
            🔓 Logout
        </a>
    ''', unsafe_allow_html=True)

