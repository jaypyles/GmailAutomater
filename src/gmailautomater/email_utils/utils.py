# STL
import re
import email
import logging
from typing import List
from imaplib import IMAP4_SSL
from email.header import decode_header

# LOCAL
from gmailautomater.mail.Email import Email
from gmailautomater.email_utils.labels import (
    build_label_map,
    categorize_emails,
    move_email_to_label,
    build_email_label_trie,
)
from gmailautomater.email_utils.deletion import mark_email_for_deletion
from gmailautomater.sqlite.DatabaseFunctions import retrieve_labels_from_db

LOG = logging.getLogger()


def organize_inbox(mail: IMAP4_SSL, emails: list[Email]):
    """Move emails to their respective labels along with deleting emails when needed."""
    labels = retrieve_labels_from_db()
    label_map = build_label_map(labels)
    label_trie = build_email_label_trie(label_map)
    categorized_emails = categorize_emails(emails, label_trie, labels)

    for label, email_list in categorized_emails.items():
        if label == "deletion":
            for email in email_list:
                mark_email_for_deletion(mail, email)
        else:
            for email in email_list:
                move_email_to_label(mail, email, label)
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
    for email_id in email_id_list[0:1000]:
        _, email_data = mail.fetch(email_id, "(RFC822)")
        raw_email = email_data[0][1]

        # Parse the raw email data
        msg = email.message_from_bytes(raw_email)

        # Decode the email subject
        subject, charset = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(charset if charset else "utf-8", errors="replace")

        # Get the sender's email address
        from_email = msg.get("From")
        from_email = decode_email_from(from_email)

        e = Email(subject, from_email, email_id.decode("utf-8"))
        LOG.info(e)

        emails.append(e)

    return emails
