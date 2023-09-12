# STL
import logging

# PDM
import click
from dotenv import load_dotenv

# LOCAL
from gmailautomater.cli.email import email

LOG = logging.getLogger()


@click.group
def cli():
    """CLI for interacting with the GmailAutomater."""
    pass


cli.add_command(email)


def main():
    load_dotenv()
    cli()


if __name__ == "__main__":
    main()
