# STL
import os
import imaplib
import logging

LOG = logging.getLogger()


class UnableToLoginError(Exception):
    def __init__(self, message: str = "Could not log into mail service.") -> None:
        super().__init__(message)


def connect_to_mail() -> imaplib.IMAP4_SSL:
    """Login and return mail object."""
    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    if not (EMAIL and PASSWORD):
        raise EnvironmentError("USER_EMAIL and APP_PASSWORD not set.")

    result = mail.login(EMAIL, PASSWORD)

    if not result[0] == "OK":
        raise UnableToLoginError

    return mail
