from uuid import UUID

import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.enums import ProjectOwnerType, Visibility
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.project import ProjectCreate

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
    help="user id of the creator of the project, should be the same as owner_id if owner_type is user",
)
@click.option(
    "--visibility-access",
    "visibility_access",
    required=True,
    type=Visibility,
    help="visibility access of the project, if 'public', the project can only access public apps and functions",
)
@click.option(
    "--skip-dry-run",
    is_flag=True,
    help="provide this flag to run the command and apply changes to the database",
)
def create_project(
    project_name: str,
    owner_type: ProjectOwnerType,
    owner_id: UUID,
    created_by: UUID,
    visibility_access: Visibility,
    skip_dry_run: bool,
) -> UUID:
    """
    Create a project in db.
    Note this is a privileged command, as it can create projects under any user or organization.
    """
    return create_project_helper(
        project_name, owner_type, owner_id, created_by, visibility_access, skip_dry_run
    )


def create_project_helper(
    project_name: str,
    owner_type: ProjectOwnerType,
    owner_id: UUID,
    created_by: UUID,
    visibility_access: Visibility,
    skip_dry_run: bool,
) -> UUID:
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        project_create = ProjectCreate(
            name=project_name, owner_type=owner_type, owner_id=owner_id, created_by=created_by
        )

        db_project = crud.create_project(db_session, project_create, visibility_access)
        if not skip_dry_run:
            click.echo(
                f"\n\n============ will create new project {db_project.name} ============\n\n"
                f"{db_project}\n\n"
                "============ provide --skip-dry-run to commit changes ============="
            )
            db_session.rollback()
        else:
            click.echo(
                f"\n\n============ committing creation of project {db_project.name} ============\n\n"
                f"{db_project}\n\n"
            )
            db_session.commit()
            click.echo("============ success! =============")
        return db_project.id  # type: ignore
