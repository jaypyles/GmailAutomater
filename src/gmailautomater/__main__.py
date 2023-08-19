# PDM
import click
from dotenv import load_dotenv

# LOCAL
from gmailautomater.email_utils.login import create_env, store_email, store_app_password
from gmailautomater.email_utils.labels import add_label_to_email

# LOCAL
from .organize import organize_mail


@click.group
def cli():
    """CLI for interacting with the GmailAutomater."""
    pass


@cli.command()
def organize():
    """Run the organize_inbox command."""
    organize_mail()


@cli.command()
@click.argument("email", required=True)
@click.argument("app_password", required=True)
def set_credentials(email: str, app_password: str):
    """Set email to be used, along with Gmail 2FA App Password."""
    create_env()
    store_email(email)
    store_app_password(app_password)


@cli.command()
@click.argument("label_name")
def add_label(label_name):
    # try an add a label to gmail inbox
    # add label table to db
    # add label to labels in db
    add_label_to_email(label_name)
    print(f"Added Label: {label_name}.")


def main():
    load_dotenv()
    cli()


if __name__ == "__main__":
    main()
