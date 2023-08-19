# STL
import os

# PDM
from dotenv import set_key


def store_email(email: str):
    """Store the email in the .env file"""
    set_key(".env", "USER_EMAIL", email)


def store_app_password(password: str):
    """Store the password in the .env file"""
    set_key(".env", "APP_PASSWORD", password)


def create_env():
    """Used to create the .env file if it does not exist."""
    if not os.path.exists(".env"):
        open(".env", "w").close()
