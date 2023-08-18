# STL
import logging
from imaplib import IMAP4_SSL

# LOCAL
from gmailautomater.mail.Email import Email, EmailName
from gmailautomater.sqlite.DatabaseFunctions import retrieve_emails_from_db

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
