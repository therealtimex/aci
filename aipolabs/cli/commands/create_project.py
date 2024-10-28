from uuid import UUID

import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.project import ProjectCreate, ProjectOwnerType

logger = get_logger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


@click.command()
@click.option(
    "--project-name",
    "project_name",
    required=True,
    help="project name",
)
@click.option(
    "--owner-type",
    "owner_type",
    required=True,
    type=ProjectOwnerType,
    help="owner type, either 'user' or 'organization'",
)
@click.option(
    "--owner-id",
    "owner_id",
    required=True,
    type=UUID,
    help="owner id, either user id or organization id, depending on the owner type",
)
@click.option(
    "--created-by",
    "created_by",
    required=True,
    type=UUID,
    help="user id of the creator of the project, ideally the same as owner_id if owner_type is user",
)
def create_project(
    project_name: str,
    owner_type: ProjectOwnerType,
    owner_id: UUID,
    created_by: UUID,
) -> None:
    """
    Create a project in db.
    Note this is a privileged command, as it can create projects under any user or organization.
    """

    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            project_create = ProjectCreate(
                name=project_name,
                owner_type=owner_type,
                owner_id=owner_id,
                created_by=created_by,
            )

            logger.info("creating project...")
            db_project = crud.create_project(db_session, project_create)
            db_session.commit()

            logger.info(f"project created: {db_project}")

        except Exception:
            db_session.rollback()
            logger.exception("Error creating project")
