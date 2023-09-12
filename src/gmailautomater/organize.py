# STL
import os
import imaplib
import logging

# LOCAL
from gmailautomater.email_utils.utils import get_emails, organize_inbox

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()


def organize_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

    if EMAIL and PASSWORD:
        mail.login(EMAIL, PASSWORD)
    else:
        LOG.error("Email and password not defined.")

    mail.select('"[Gmail]/All Mail"')

    # only emails in the primary section
    _, email_ids = mail.search(None, 'X-GM-LABELS "inbox" SEEN NOT FLAGGED')

    email_id_list = email_ids[0].split()[::-1]
    emails = get_emails(mail, email_id_list)
    organize_inbox(mail, emails)

    mail.logout()
