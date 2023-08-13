# STL
import os
import email
import imaplib
from email.header import decode_header

# PDM
from dotenv import load_dotenv

# LOCAL
from gmailautomater.email_utils.utils import decode_email_from

load_dotenv()
mail = imaplib.IMAP4_SSL("imap.gmail.com")

EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

if EMAIL and PASSWORD:
    mail.login(EMAIL, PASSWORD)

mail.select("inbox")

# Search for all emails
result, email_ids = mail.search(None, "ALL")

# Get a list of email IDs
email_id_list = email_ids[0].split()

# Loop through each email id and fetch email content
for email_id in email_id_list[0:1]:
    status, email_data = mail.fetch(email_id, "(RFC822)")
    raw_email = email_data[0][1]

    # Parse the raw email data
    msg = email.message_from_bytes(raw_email)

    # Decode the email subject
    subject, _ = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode()

    # Get the sender's email address
    from_email = msg.get("From")

    # Initialize the email body
    email_body = ""

    # Check if the message is multipart
    if msg.is_multipart():
        # Loop through each part of the email
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                email_body += part.get_payload(decode=True).decode("utf-8")
    else:
        email_body = msg.get_payload(decode=True).decode("utf-8")

    # Print the extracted information

    from_email = decode_email_from(from_email)

    print("Subject:", subject)
    print("From:", from_email)
    print("Body:", email_body)
    print("-" * 50)

    decision = input("Do you want to delete this?")

    if decision:
        mail.store(email_id, "+FLAGS", "\\Deleted")
        mail.expunge()

# Logout from the email server
mail.logout()
