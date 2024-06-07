# STL
import logging

# PDM
import click
from dotenv import load_dotenv

# LOCAL
from gmailautomater.cli.email import email
from gmailautomater.sqlite.DatabaseFunctions import initialize_db

LOG = logging.getLogger()


@click.group
def cli():
    """CLI for interacting with the GmailAutomater."""
    pass


cli.add_command(email)


def main():
    _ = load_dotenv(dotenv_path=".env")
    _ = initialize_db()
    cli()


if __name__ == "__main__":
    main()
