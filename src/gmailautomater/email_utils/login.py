# STL
import os

# PDM
from dotenv import set_key

HOME = os.environ.get("HOME")
assert HOME, "$HOME must be set."

ENV_PATH = os.path.join(HOME, ".config/gmailautomater/.env")


def store_email(email: str):
    """Store the email in the .env file"""
    _ = set_key(ENV_PATH, "USER_EMAIL", email)


def store_app_password(password: str):
    """Store the password in the .env file"""
    _ = set_key(ENV_PATH, "APP_PASSWORD", password)


def create_env():
    """Used to create the .env file if it does not exist."""
    if not os.path.exists(ENV_PATH):
        open(ENV_PATH, "w").close()
