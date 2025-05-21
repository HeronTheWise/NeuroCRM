from dotenv import load_dotenv
import os

load_dotenv()

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
REDIRECT_URI = os.getenv("REDIRECT_URI")
