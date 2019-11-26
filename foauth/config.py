import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from file
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID')
TWITTER_CLIENT_SECRET = os.environ.get('TWITTER_CLIENT_SECRET')
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
DEV_FRONT_URL = os.environ.get("DEV_FRONT_URL", "https://localhost:3000")
