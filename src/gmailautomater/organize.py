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
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    last_checked = get_last_checked()

    query = ALL_QUERY

    if not all:
        today = datetime.now().strftime("%d-%b-%Y")

        if last_checked:
            query = f'X-GM-LABELS "inbox" SEEN NOT FLAGGED SINCE {last_checked} BEFORE {today}'

    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

    if not (EMAIL and PASSWORD):
        raise EnvironmentError("USER_EMAIL and APP_PASSWORD are not set.")

    _ = mail.login(EMAIL, PASSWORD)

    _ = mail.select('"[Gmail]/All Mail"')

    _, email_ids = mail.search(None, query)

    email_id_list = email_ids[0].split()
    emails = get_emails(mail, email_id_list, all)
    organize_inbox(mail, emails)

    _ = mail.logout()
