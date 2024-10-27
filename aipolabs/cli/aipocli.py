import click

from aipolabs.cli.commands import upsert_app
from aipolabs.common.logging import setup_logging


@click.group()
def cli() -> None:
    """AIPO CLI Tool"""
    pass


# Add commands to the group
cli.add_command(upsert_app.upsert_app)

if __name__ == "__main__":
    setup_logging()
    cli()
