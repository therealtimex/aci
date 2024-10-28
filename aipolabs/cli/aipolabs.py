import click

from aipolabs.cli.commands import create_project, create_user, upsert_app_and_functions
from aipolabs.common.logging import setup_logging


@click.group()
def cli() -> None:
    """AIPO CLI Tool"""
    pass


# Add commands to the group
cli.add_command(upsert_app_and_functions.upsert_app_and_functions)
cli.add_command(create_user.create_user)
cli.add_command(create_project.create_project)
if __name__ == "__main__":
    setup_logging()
    cli()
