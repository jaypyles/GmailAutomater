# STL
import os
import imaplib
import logging
from typing import cast
from datetime import datetime

# LOCAL
from gmailautomater.email_utils.utils import get_emails, organize_inbox
from gmailautomater.sqlite.DatabaseFunctions import get_last_checked

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger()

ALL_QUERY = 'X-GM-LABELS "inbox" NOT FLAGGED'


def organize_mail(all: bool):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    last_checked = get_last_checked()

    query = ALL_QUERY

    if not all:
        today = datetime.now().strftime("%d-%b-%Y")

        if last_checked:
            query = (
                f'X-GM-LABELS "inbox" NOT FLAGGED SINCE {last_checked} BEFORE {today}'
            )

    EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

    if not (EMAIL and PASSWORD):
        raise EnvironmentError("USER_EMAIL and APP_PASSWORD are not set.")

    _ = mail.login(EMAIL, PASSWORD)

    _ = mail.select('"[Gmail]/All Mail"', readonly=True)

    _, email_ids = mail.search(None, query)
    email_ids = cast(list[bytes], email_ids)

    email_id_list: list[bytes] = email_ids[0].split()
    emails = get_emails(email_id_list, all)
    organize_inbox(emails)

    _ = mail.logout()
