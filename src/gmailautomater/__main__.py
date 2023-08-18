# PDM
import click

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
def add_label_cmd(label_name):
    print(f"Added Label: {label_name}.")


if __name__ == "__main__":
    cli()
