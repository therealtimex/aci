from uuid import UUID

import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.agent import AgentCreate

logger = get_logger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


@click.command()
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
def create_agent(
    agent_name: str,
    description: str,
    project_id: UUID,
    created_by: UUID,
    excluded_apps: list[UUID],
    excluded_functions: list[UUID],
) -> None:
    """
    Create an agent in db.
    """

    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            agent_create = AgentCreate(
                name=agent_name,
                description=description,
                project_id=project_id,
                created_by=created_by,
                excluded_apps=excluded_apps,
                excluded_functions=excluded_functions,
            )

            logger.info("creating agent...")
            db_agent = crud.create_agent(db_session, agent_create)
            db_session.commit()

            logger.info(f"agent created: {db_agent}")

        except Exception:
            db_session.rollback()
            logger.exception("Error creating agent")
