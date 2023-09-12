# STL
import os
import imaplib
import logging
from datetime import datetime

# LOCAL
from gmailautomater.email_utils.utils import get_emails, organize_inbox
from gmailautomater.sqlite.DatabaseFunctions import get_last_checked

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

ALL_QUERY = 'X-GM-LABELS "inbox" SEEN NOT FLAGGED'


def organize_mail(all: bool):
    # TODO: add dynamic query building
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    last_checked = get_last_checked()

    if not all:
        today = datetime.now().strftime("%d-%b-%Y")
        if last_checked:
            QUERY = f'X-GM-LABELS "inbox" SEEN NOT FLAGGED SINCE {last_checked} BEFORE {today}'
        else:
            QUERY = ALL_QUERY
    else:
        QUERY = ALL_QUERY

    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

    if EMAIL and PASSWORD:
        mail.login(EMAIL, PASSWORD)
    else:
        LOG.error("Email and password not defined.")

    mail.select('"[Gmail]/All Mail"')

    _, email_ids = mail.search(None, QUERY)

    email_id_list = email_ids[0].split()
    emails = get_emails(mail, email_id_list, last_checked)
    organize_inbox(mail, emails)

    mail.logout()
