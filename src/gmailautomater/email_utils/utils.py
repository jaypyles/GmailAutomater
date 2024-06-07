# STL
import re
import email
import imaplib
import logging
from typing import Union, Optional
from imaplib import IMAP4_SSL
from collections import defaultdict
from email.header import decode_header

# PDM
from rich.progress import Progress

# LOCAL
from gmailautomater.mail.Email import Email
from gmailautomater.email_utils.mail import connect_to_mail
from gmailautomater.email_utils.labels import (
    build_label_map,
    categorize_emails,
    move_email_to_label,
    build_email_label_trie,
)
from gmailautomater.email_utils.deletion import mark_email_for_deletion
from gmailautomater.sqlite.DatabaseFunctions import (
    insert_last_checked,
    retrieve_labels_from_db,
)

LOG = logging.getLogger()


def organize_inbox(mail: IMAP4_SSL, emails: list[Email]):
    """Move emails to their respective labels along with deleting emails when needed."""
    labels = retrieve_labels_from_db()
    label_map = build_label_map(labels)

    email_map: dict[str, list[Email]] = defaultdict(list)

    for email in emails:
        email_map[email.sender].append(email)

    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Sorting emails...", total=len(email_map.items())
        )
        pc = 0
        for email, label in label_map.items():
            if not (email_map.get(email)):
                continue

            print(f"EMAIL: {email}")
            if label == "deletion":
                for e in email_map[email]:
                    mark_email_for_deletion(mail, e)
            else:
                LOG.debug(f"Moved email: {email}")
                for e in email_map[email]:
                    move_email_to_label(mail, e, label)
            pc += 1
            progress.update(task, completed=pc)


def decode_email_from(header: bytes) -> str:
    """Convert a utf-8 encoded header into a string representing the email address sender."""

    def extract_email_address(header_str: str) -> Optional[str]:
        match = re.search(r"<(.*?)>", header_str)
        return match.group(1) if match else None

    _header = header.decode("utf-8", errors="ignore")

    decoded_fragments = decode_header(_header)
    decoded_header = "".join(
        fragment.decode(encoding or "utf-8", errors="ignore")
        if isinstance(fragment, bytes)
        else fragment
        for fragment, encoding in decoded_fragments  # type: ignore [reportAny]
    )

    email_address = extract_email_address(decoded_header)

    if email_address:
        return email_address

    raise ValueError("No valid email address found in the header.")


def get_emails(
    mail: imaplib.IMAP4_SSL, email_id_list: list[bytes], all: bool
) -> list[Email]:
    "From a list of email ids, return a list of emails."
    emails: list[Email] = list()

    with Progress() as progress:
        task = progress.add_task("[cyan]Collecting emails...", total=len(email_id_list))
        pc = 0

        for email_id in email_id_list[::-1][:]:
            _, email_data = mail.fetch(email_id, "(RFC822)")  # type: ignore [this is just wrong]
            email_response: tuple[bytes, bytes] = email_data[0]  # type: ignore[reportAssignmentType]

            raw_email: bytes = email_response[1]
            msg = email.message_from_bytes(raw_email)

            sub = msg["Subject"]

            subject = ""

            if isinstance(sub, str) or isinstance(sub, bytes):
                msg_subject = msg["Subject"]
                subject: str = decode_header(msg_subject)[0][0]

            from_email: Optional[Union[str, bytes]] = msg.get("From")

            if isinstance(from_email, bytes):
                from_email = decode_email_from(from_email)

            if not from_email:
                from_email = ""

            DATE_PATTERN = (
                r"([0-9]*\ (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\ [0-9]*)"
            )

            received: Optional[str] = msg.get("Recieved")

            if not received:
                received = ""

            search = re.search(DATE_PATTERN, received)
            date = search[0] if search else ""
            split_date = date.split()
            date = "-".join(split_date)

            assert isinstance(from_email, str)

            e = Email(subject, from_email, email_id, date)
            LOG.debug(f"Email made: {e}.")

            emails.append(e)

            pc += 1
            progress.update(task, completed=pc)

    if not all:
        insert_last_checked(emails[-1].date)

    return emails


def get_inbox_emails(mail: IMAP4_SSL) -> list[Email]:
    """Get a list of all emails from the inbox."""
    _ = mail.select('"[Gmail]/All Mail"')
    _, email_ids = mail.search(None, 'X-GM-LABELS "inbox" SEEN NOT FLAGGED')

    email_id_list: list[bytes] = email_ids[0].split()
    return get_emails(mail, email_id_list, all=True)


def find_top_emails():
    email_count = {}
    if mail := connect_to_mail():
        emails = get_inbox_emails(mail)
        for e in emails:
            if e.sender not in email_count:
                email_count[e.sender] = 1
            else:
                count = email_count[e.sender]
                email_count[e.sender] = count + 1

    return dict(reversed(sorted(email_count.items(), key=lambda item: item[1])))
