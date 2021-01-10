import os
from dotenv import load_dotenv

load_dotenv()

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET_KEY")
username = os.getenv("USER_SCREEN_NAME")
