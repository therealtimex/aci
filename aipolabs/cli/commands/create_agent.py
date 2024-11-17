from uuid import UUID

import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.agent import AgentCreate

openai_service = OpenAIService(config.OPENAI_API_KEY)


@click.command()
@click.option(
    "--project-id",
    "project_id",
    required=True,
    type=UUID,
    help="project id under which the agent is created",
)
@click.option(
    "--created-by",
    "created_by",
    required=True,
    type=UUID,
    help="user id of the creator of the agent",
)
@click.option(
    "--agent-name",
    "agent_name",
    required=True,
    help="agent name",
)
@click.option(
    "--description",
    "description",
    required=True,
    help="agent description",
)
@click.option(
    "--excluded-apps",
    "excluded_apps",
    required=False,
    default=[],
    type=list[UUID],
    help="list of app ids to exclude from the agent",
)
@click.option(
    "--excluded-functions",
    "excluded_functions",
    required=False,
    default=[],
    type=list[UUID],
    help="list of function ids to exclude from the agent",
)
@click.option(
    "--skip-dry-run",
    is_flag=True,
    help="provide this flag to run the command and apply changes to the database",
)
def create_agent(
    agent_name: str,
    description: str,
    project_id: UUID,
    created_by: UUID,
    excluded_apps: list[UUID],
    excluded_functions: list[UUID],
    skip_dry_run: bool,
) -> UUID:
    """
    Create an agent in db.
    """
    return create_agent_helper(
        agent_name,
        description,
        project_id,
        created_by,
        excluded_apps,
        excluded_functions,
        skip_dry_run,
    )


def create_agent_helper(
    agent_name: str,
    description: str,
    project_id: UUID,
    created_by: UUID,
    excluded_apps: list[UUID],
    excluded_functions: list[UUID],
    skip_dry_run: bool,
) -> UUID:
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        agent_create = AgentCreate(
            name=agent_name,
            description=description,
            project_id=project_id,
            created_by=created_by,
            excluded_apps=excluded_apps,
            excluded_functions=excluded_functions,
        )

        db_agent = crud.create_agent(db_session, agent_create)

        if not skip_dry_run:
            click.echo(
                f"\n\n============ will create new agent {db_agent.name} ============\n\n"
                f"{db_agent}\n\n"
                "============ provide --skip-dry-run to commit changes ============="
            )
            db_session.rollback()
        else:
            click.echo(
                f"\n\n============ committing creation of agent {db_agent.name} ============\n\n"
                f"{db_agent}\n\n"
            )
            db_session.commit()
            click.echo("============ success! =============")

        return db_agent.id  # type: ignore
