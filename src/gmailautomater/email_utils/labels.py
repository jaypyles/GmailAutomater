# STL
import re
import email
import logging
from time import sleep
from typing import List
from imaplib import IMAP4_SSL

# LOCAL
from gmailautomater.mail.Email import Email, EmailName
from gmailautomater.email_utils.mail import connect_to_mail
from gmailautomater.sqlite.DatabaseFunctions import retrieve_emails_from_db

LOG = logging.getLogger()


def get_emails_by_label(label: str):
    """Get a list of Email objects by label."""
    email_ids = []
    if mail := connect_to_mail():
        status, _ = mail.select(label)
        if status == "OK":
            # Search for emails within the selected folder (you can specify search criteria)
            search_criteria = (
                "ALL"  # You can use different criteria (e.g., 'UNSEEN', 'FROM', etc.)
            )
            status, message_ids = mail.search(None, search_criteria)

            if status == "OK":
                # The variable message_ids contains a space-separated list of email message IDs
                email_ids = message_ids[0].split()

    # LOCAL
    from gmailautomater.email_utils.utils import get_emails

    return get_emails(mail, email_ids, all=True)


def get_labels():
    """Get all current custom labels in Gmail."""
    l = []
    if mail := connect_to_mail():
        _, labels = mail.list()
        for label in labels:
            if isinstance(label, bytes):
                if "Gmail" not in str(label):
                    l.append(label.decode())
        l = [label.split()[-1] for label in l]
        l.remove('"INBOX"')
        return l
    return l


def remove_label_from_email(label: str):
    """Remove label from Gmail."""
    if mail := connect_to_mail():
        result, _ = mail.delete(label)
        if result == "OK":
            LOG.info(f"Label deleted from inbox: {label}.")
        else:
            LOG.error(f"Failed to delete label: {label}.")

        mail.logout()


def add_label_to_email(label: str):
    """Add label to email."""
    if mail := connect_to_mail():
        result, _ = mail.create(label)
        if result == "OK":
            LOG.debug(f"Label created in inbox: {label}.")
        else:
            LOG.debug(f"Failed to create label: {label}.")

        mail.logout()


def check_if_label_exists(label: str):
    """Check if a label exists in a mailbox."""
    if mail := connect_to_mail():
        response, labels = mail.list()
        if response == "OK":
            for lbl in labels:
                if isinstance(lbl, bytes):
                    if label in lbl.decode():
                        return True
            return False
        else:
            return False


def check_email_for_move(email: Email, label_email_list: list[EmailName]):
    """Check if the email is in the list of emails for a label, to move."""
    return email.sender in label_email_list


def move_email_to_label(mail: IMAP4_SSL, e: Email, label):
    """Move email from main inbox to a label."""

    _, email_data = mail.fetch(str(e.id), "(RFC822)")
    LOG.debug(f"Email Data: {email_data.__class__}")
    raw_email = email_data[0][1]

    if isinstance(raw_email, bytes):
        msg = email.message_from_bytes(raw_email)
    else:
        return

    sender = msg.get("From")
    email_address = re.search(r"<(.*?)>", str(sender))
    if email_address:
        sender = email_address[1]

    # Remove the "Inbox" label
    if e.sender == sender:
        mail.store(str(e.id), "+X-GM-LABELS", label)
        sleep(
            1
        )  # Fix weird error where the server wouldn't update and it would move the wrong id
        mail.store(str(e.id), "-X-GM-LABELS", "\\Inbox")
        mail.expunge()
    else:
        pass


def build_label_map(labels: list):
    """From a list of labels, build a map emails to label."""
    label_map = {}
    for label in labels:
        emails = retrieve_emails_from_db(label)
        label_map[label] = emails

    return label_map


class TrieLabelNode:
    def __init__(self) -> None:
        self.children = {}
        self.label = None


def build_email_label_trie(label_map: dict):
    """Build a trie where each node is a char of an email, with the final node having a `label` attribute."""
    root = TrieLabelNode()
    for label, addresses in label_map.items():
        for address in addresses:
            node = root
            components = address.split("@")
            local = components[0]
            domain = components[1]
            for char in local:
                if char not in node.children:
                    node.children[char] = TrieLabelNode()
                node = node.children[char]
            if domain not in node.children:
                node.children[domain] = TrieLabelNode()
            node = node.children[domain]
            node.label = label
    return root


def categorize_emails(emails: list[Email], trie: TrieLabelNode, labels):
    """Categorize a list of emails based on a trie."""
    categorized_emails = {label: [] for label in labels}
    for email in emails:
        components = email.sender.split("@")
        local = components[0]
        domain = components[1]
        node = trie
        for char in local:
            if char not in node.children:
                break
            node = node.children[char]
            if domain in node.children:
                node = node.children[domain]
                if node.label:
                    categorized_emails[node.label].append(email)
    return categorized_emails
