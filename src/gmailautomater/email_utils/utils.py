# STL
import re
import email
from typing import List
from email.header import decode_header


def decode_email_from(header):
    "Convert a utf-8 encoded header, into a string representing the email address from"
    if isinstance(header, list):
        decoded_header = str(decode_header(header)[1][0])
        email_address = re.search(r"<(.*?)>", decoded_header)[1]
        return email_address
    else:
        email_address = re.search(r"<(.*?)>", str(header))
        if email_address:
            return email_address[1]
    return header


def get_emails(mail, email_id_list: list) -> List[tuple]:
    "From a list of email ids, return a list of tuples (subject, from, email_id)"
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

        emails.append((subject, from_email, int(email_id.decode("utf-8"))))

    return emails
