# STL
import logging

# PDM
import click
from dotenv import load_dotenv

# LOCAL
from gmailautomater.cli.email import email
from gmailautomater.sqlite.DatabaseFunctions import initalize_db

LOG = logging.getLogger()


@click.group
def cli():
    """CLI for interacting with the GmailAutomater."""
    pass


cli.add_command(email)


def main():
    load_dotenv(dotenv_path=".env")
    if initalize_db():  # WILL fail if db does not exist
        cli()
    else:
        LOG.error("DB is not initalized. Ensure `init-emails` has been ran.")


if __name__ == "__main__":
    main()
