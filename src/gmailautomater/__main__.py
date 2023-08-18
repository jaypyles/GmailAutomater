# PDM
import click
from dotenv import load_dotenv

# LOCAL
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
