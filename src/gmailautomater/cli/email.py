# STL
import logging

# PDM
import click
from rich import print

# LOCAL
from gmailautomater.organize import organize_mail
from gmailautomater.mail.Label import Label
from gmailautomater.email_utils.mail import connect_to_mail
from gmailautomater.email_utils.login import create_env, store_email, store_app_password
from gmailautomater.email_utils.utils import find_top_emails
from gmailautomater.email_utils.labels import (
    get_labels,
    add_label_to_email,
    get_emails_by_label,
    check_if_label_exists,
    remove_label_from_email,
)
from gmailautomater.sqlite.DatabaseFunctions import (
    add_label_to_db,
    add_email_to_label,
    retrieve_labels_from_db,
    remove_label_from_labels,
)

LOG = logging.getLogger()


@click.group()
def email():
    pass


@email.command()
@click.option("--all", is_flag=True)
def organize(all: bool):
    """Run the organize_inbox command."""
    organize_mail(all=all)


@email.command()
@click.argument("email", required=True)
@click.argument("app_password", required=True)
def set_credentials(email: str, app_password: str):
    """Set email to be used, along with Gmail 2FA App Password."""
    create_env()
    store_email(email)
    store_app_password(app_password)


@email.command()
@click.argument("label", required=True)
def add_label(label: str):
    """Add a label to Gmail."""
    mail = connect_to_mail()
    if check_if_label_exists(mail, label):
        LOG.debug(f"Label already existed: {label}")

    add_label_to_email(mail, label)
    _ = add_label_to_db(Label(label))
    print(
        f"[bold green]Label added: [/bold green][bold italic yellow]{label}[/bold italic yellow][bold green]."
    )


@email.command()
@click.argument("label", required=True)
def remove_label(label: str):
    """Remove a label from Gmail."""
    mail = connect_to_mail()

    if not (check_if_label_exists(mail, label)):
        print(f"[bold red]Label did not exist: {label}.")
        LOG.debug(f"Label did not exist: {label}")
        return

    remove_label_from_email(Label(label))
    remove_label_from_labels(label)
    print(f"[bold green]Label: {label} deleted.")


@email.command()
@click.option("--email", "email", required=True)
@click.option("--label", "label", required=True)
def add_email(email: str, label: str):
    """Add an email to be sorted into a label."""
    mail = connect_to_mail()

    if check_if_label_exists(mail, label) or label == "deletion":
        _ = add_email_to_label(Label(label), email)
        print(f"[bold green]Email: {email}, added to label: {label}.")
        return

    print(f"[bold red]Email: {email}, not added to label: {label}.")
    LOG.debug(f"Label not found: {label}")


@email.command()
def init_emails():
    """Initialize all email senders and labels from current folders."""
    mail = connect_to_mail()

    labels = get_labels(mail)

    db_labels = retrieve_labels_from_db()

    for label in labels:
        if label not in db_labels:
            _ = add_label_to_db(label)

        emails = get_emails_by_label(mail, label)
        emails = set(email.sender for email in emails)

        for email in emails:
            _ = add_email_to_label(Label(label), email)
            print(f"[bold green]Email: {email}, added to label: {label}.")


@email.command()
def top_emails():
    """Find what email senders have sent the most emails."""
    if top := find_top_emails():
        count = 0
        for key, value in top.items():
            print(f"{key}: {value}")
            count += 1
            if count == 20:
                break


@email.command()
def list_labels():
    """List all currently stored labels"""
    mail = connect_to_mail()
    get_labels(mail)
