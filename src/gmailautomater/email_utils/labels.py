# STL
import logging
from imaplib import IMAP4_SSL

# LOCAL
from gmailautomater.mail.Email import Email, EmailName

LOG = logging.getLogger()


def check_email_for_move(email: Email, label_email_list: list[EmailName]):
    """Check if the email is in the list of emails for a label, to move."""
    return email.sender in label_email_list


def move_email_to_label(mail: IMAP4_SSL, email: Email, label):
    """Move email from main inbox to a label."""
    copy_result = mail.copy(str(email.id), label)
    if copy_result[0] != "OK":
        LOG.warning("Failed to move email to label.")
        return
    else:
        LOG.info(f"Email: {str(email.id)}, moved to label: {label}")

    mail.store(str(email.id), "+FLAGS", "\\Deleted")
    mail.expunge()
