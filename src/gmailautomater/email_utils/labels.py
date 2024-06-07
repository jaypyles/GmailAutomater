# STL
import re
import email as emaillib
import imaplib
import logging
from time import sleep
from typing import cast

# LOCAL
from gmailautomater.utils import DEFAULT_LABEL
from gmailautomater.mail.Email import Email, EmailName
from gmailautomater.mail.Label import Label
from gmailautomater.email_utils.mail import connect_to_mail
from gmailautomater.sqlite.DatabaseFunctions import retrieve_emails_from_db

LOG = logging.getLogger()


def get_emails_by_label(mail: imaplib.IMAP4_SSL, label: Label) -> list[Email]:
    """Get a list of Email objects by label."""
    email_ids: list[bytes] = list()

    status, _ = mail.select(label)

    if status == "OK":
        search_criteria = "ALL"
        status, message_ids = mail.search(None, search_criteria)

        if status == "OK":
            message_ids = cast(list[bytes], message_ids)
            email_ids = message_ids[0].split()

    # LOCAL
    from gmailautomater.email_utils.utils import get_emails

    return get_emails(email_ids, all=True, label=label)


def get_labels(mail: imaplib.IMAP4_SSL) -> list[Label]:
    """Get all current custom labels in Gmail."""

    _, response = mail.list()
    labels: list[Label] = list()

    for label in response:
        if not isinstance(label, bytes):
            continue

        if "Gmail" not in str(label):
            labels.append(Label(label.decode()))

    labels = [Label(label.split()[-1].replace('"', "")) for label in labels]
    labels.remove(Label("INBOX"))

    return labels


def remove_label_from_email(label: Label) -> None:
    """Remove label from Gmail."""
    if not (mail := connect_to_mail()):
        return

    result, _ = mail.delete(label)

    if result != "OK":
        LOG.error(f"Failed to delete label: {label}.")

    LOG.info(f"Label deleted from inbox: {label}.")
    _ = mail.logout()


def add_label_to_email(mail: imaplib.IMAP4_SSL, label: str) -> None:
    """Add label to email."""
    result, _ = mail.create(label)
    _ = mail.logout()

    if result != "OK":
        raise Exception("Failed to create label.")

    return


def check_if_label_exists(mail: imaplib.IMAP4_SSL, label: str):
    """Check if a label exists in a mailbox."""
    response, labels = mail.list()

    if response == "OK":
        for lbl in labels:
            if isinstance(lbl, bytes):
                if label in lbl.decode():
                    return True
        return False

    return False


def check_email_for_move(email: Email, label_email_list: list[EmailName]):
    """Check if the email is in the list of emails for a label, to move."""
    return email.sender in label_email_list


def move_email_to_label(e: Email, label: Label):
    """Move email from main inbox to a label."""
    mail = connect_to_mail()
    mail.select(DEFAULT_LABEL)

    _, email_data = mail.fetch(e.id, "(RFC822)")
    raw_email = email_data[0][1]

    if isinstance(raw_email, bytes):
        msg = emaillib.message_from_bytes(raw_email)
    else:
        return

    sender = msg.get("From")
    email_address = re.search(r"<(.*?)>", str(sender))
    if email_address:
        sender = email_address[1]

    # Remove the "Inbox" label
    if e.sender == sender:
        res = mail.store(e.id, "+X-GM-LABELS", label)
        print(f"RES: {res}")
        sleep(
            1
        )  # Fix weird error where the server wouldn't update and it would move the wrong id
        mail.store(e.id, "-X-GM-LABELS", "\\Inbox")
        mail.expunge()
    else:
        pass


def build_label_map(labels: list[Label]):
    """From a list of labels, build a map emails to label."""
    label_map: dict[EmailName, Label] = {}

    for label in labels:
        emails = retrieve_emails_from_db(label)

        for e in emails:
            label_map[e] = label

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


def categorize_emails(
    emails: list[Email],
    labels: list[Label],
    label_map: dict[EmailName, Label],
):
    """Categorize a list of emails based on a trie."""
    categorized_emails: dict[Label, list[Email]] = {label: list() for label in labels}

    for email in emails:
        if email.sender:
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
