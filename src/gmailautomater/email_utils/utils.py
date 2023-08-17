# STL
import re
import email
import logging
from typing import List
from imaplib import IMAP4_SSL
from email.header import decode_header

# LOCAL
from gmailautomater.mail.Email import Email, EmailName
from gmailautomater.email_utils.labels import check_email_for_move
from gmailautomater.email_utils.deletion import (
    mark_email_for_deletion,
    check_email_for_deletion,
)
from gmailautomater.sqlite.DatabaseFunctions import (
    retrieve_emails_from_db,
    retrieve_labels_from_db,
)

LOG = logging.getLogger()


def organize_inbox(mail: IMAP4_SSL, emails: list[Email], delete_list: list[EmailName]):
    labels = retrieve_labels_from_db()
    for email in emails:
        if check_email_for_deletion(email, delete_list):
            mark_email_for_deletion(mail, email)
        # Move emails where they go based on their sender
    mail.expunge()


def decode_email_from(header):
    "Convert a utf-8 encoded header, into a string representing the email address sender."
    if isinstance(header, list):
        decoded_header = str(decode_header(header)[1][0])
        email_address = re.search(r"<(.*?)>", decoded_header)[1]
        return email_address
    else:
        email_address = re.search(r"<(.*?)>", str(header))
        if email_address:
            return email_address[1]
    return header


def get_emails(mail, email_id_list: list) -> List[Email]:
    "From a list of email ids, return a list of emails."
    emails = []
    for email_id in email_id_list[0:20]:
        _, email_data = mail.fetch(email_id, "(RFC822)")
        raw_email = email_data[0][1]

        # Parse the raw email data
        msg = email.message_from_bytes(raw_email)

        # Decode the email subject
        subject, _ = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        # Get the sender's email address
        from_email = msg.get("From")

        from_email = decode_email_from(from_email)

        e = Email(subject, from_email, email_id.decode("utf-8"))

        emails.append((e))

    return emails
