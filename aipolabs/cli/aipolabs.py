import click

from aipolabs.cli.commands import (
    create_agent,
    create_app,
    create_functions,
    create_project,
    create_user,
)
from aipolabs.common.logging import setup_logging


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """AIPO CLI Tool"""
    pass


# Add commands to the group
cli.add_command(create_user.create_user)
cli.add_command(create_project.create_project)
cli.add_command(create_agent.create_agent)
cli.add_command(create_app.create_app)
cli.add_command(create_functions.create_functions)

if __name__ == "__main__":
    setup_logging()
    cli()
