# STL
import os
import imaplib
import logging

# LOCAL
from gmailautomater.email_utils.utils import get_emails

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger()


def organize_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

    if EMAIL and PASSWORD:
        mail.login(EMAIL, PASSWORD)

    mail.select("inbox")

    # Search for all emails
    _, email_ids = mail.search(None, "NOT FLAGGED")
    email_id_list = email_ids[0].split()
    emails = get_emails(mail, email_id_list)
    for email in emails:
        print(email.sender)
    # organize_inbox(mail, emails)

    mail.logout()
