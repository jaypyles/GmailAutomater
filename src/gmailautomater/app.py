# STL
import os
import imaplib

# PDM
from dotenv import load_dotenv

# LOCAL
from gmailautomater.email_utils.utils import get_emails

load_dotenv()
mail = imaplib.IMAP4_SSL("imap.gmail.com")

EMAIL, PASSWORD = os.getenv("USER_EMAIL"), os.getenv("APP_PASSWORD")

if EMAIL and PASSWORD:
    mail.login(EMAIL, PASSWORD)

mail.select("inbox")

# Search for all emails
result, email_ids = mail.search(None, "ALL")
email_id_list = email_ids[0].split()

emails = get_emails(mail, email_id_list)

print(emails)

mail.logout()
