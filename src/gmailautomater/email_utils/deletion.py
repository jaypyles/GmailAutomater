# STL
from imaplib import IMAP4_SSL

# LOCAL
from gmailautomater.mail.Email import Email, EmailName


def check_email_for_deletion(email: Email, delete_list: list[EmailName]) -> bool:
    """Check if an email sender is meant to be deleted."""
    return email.sender in delete_list


def mark_email_for_deletion(mail: IMAP4_SSL, email: Email) -> None:
    """Mark an email for deletion."""
    _ = mail.store(email.id, "+X-GM-LABELS", "\\Trash")
    _ = mail.store(email.id, "-X-GM-LABELS", "\\All Mail")


def delete_emails(
    mail: IMAP4_SSL, emails: list[Email], delete_list: list[EmailName]
) -> None:
    """From a list of emails and the delete emails list. Store for deletion and expunge."""
    for email in emails:
        if email.sender in delete_list:
            _ = mail.store(str(email.id), "+FLAGS", "\\Deleted")

    _ = mail.expunge()
