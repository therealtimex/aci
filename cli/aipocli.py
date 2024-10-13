import click

from cli.commands import upsert_app
from cli.utils.logging import get_logger

# Initialize logging
logger = get_logger()


@click.group()
def cli() -> None:
    """AIPO CLI Tool"""
    pass


# Add commands to the group
cli.add_command(upsert_app.upsert_app)

if __name__ == "__main__":
    cli()
