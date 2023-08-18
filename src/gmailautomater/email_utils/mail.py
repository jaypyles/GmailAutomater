# STL
import os
import imaplib
import logging

LOG = logging.getLogger()


def connect_to_mail():
    """Login and return mail object."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

    if EMAIL and PASSWORD:
        mail.login(EMAIL, PASSWORD)
        if mail == None:
            LOG.error(f"Failed to login. Email: {EMAIL}, Password: {PASSWORD}.")
    else:
        LOG.error("Login credentials not defined.")
        return

    return mail
