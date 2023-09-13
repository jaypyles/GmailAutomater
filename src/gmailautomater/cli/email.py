# STL
import logging

# PDM
import click
from rich import print

# LOCAL
from gmailautomater.organize import organize_mail
from gmailautomater.email_utils.login import create_env, store_email, store_app_password
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
    add_label_to_table,
    delete_label_table,
    remove_label_from_labels,
)

LOG = logging.getLogger()


@click.group()
def email():
    pass


@email.command()
@click.option("--all", is_flag=True)
def organize(all):
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
    if check_if_label_exists(label):
        LOG.debug(f"Label already existed: {label}")
    else:
        add_label_to_email(label)
    add_label_to_db(label)
    add_label_to_table(label)
    print(
        f"[bold green]Label added: [/bold green][bold italic yellow]{label}[/bold italic yellow][bold green]."
    )


@email.command()
@click.argument("label", required=True)
def remove_label(label: str):
    """Remove a label from Gmail."""
    if check_if_label_exists(label):
        remove_label_from_email(label)
    else:
        print(f"[bold red]Label did not exist: {label}.")
        LOG.debug(f"Label did not exist: {label}")
        return
    remove_label_from_labels(label)
    delete_label_table(label)
    print(f"[bold green]Label: {label} deleted.")


@email.command()
@click.argument("email", required=True)
@click.argument("label", required=True)
def add_email(email: str, label: str):
    """Add an email to be sorted into a label."""
    if check_if_label_exists(label):
        add_email_to_label(label, email)
        print(f"[bold green]Email: {email}, added to label: {label}.")
    else:
        print(f"[bold red]Email: {email}, not added to label: {label}.")
        LOG.debug(f"Label not found: {label}")


@email.command()
def init_emails():
    """Initialize all email senders and labels from current folders."""
    labels = get_labels()
    for label in labels:
        if not check_if_label_exists(label):
            add_label_to_db(label)
            add_label_to_table(label)
        emails = get_emails_by_label(label)
        emails = set(email.sender for email in emails)  # avoid dupes
        for email in emails:
            add_email_to_label(label, email)
            print(f"[bold green]Email: {email}, added to label: {label}.")
