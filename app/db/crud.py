import secrets
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.logging import get_logger
from database import models

logger = get_logger(__name__)


class UserNotFoundError(Exception):
    """Exception raised when a user is not found in the database."""

    pass


class ProjectNotFoundError(Exception):
    """Exception raised when a project is not found in the database."""

    pass


def user_exists(db_session: Session, user_id: UUID) -> bool:
    """Check if a user exists in the database."""
    return (
        db_session.execute(select(models.User).filter_by(id=user_id)).scalar_one_or_none()
        is not None
    )


def create_project(
    db_session: Session, project: schemas.ProjectCreate, user_id: UUID
) -> models.Project:
    """
    Create a new project.
    Create as personal project if owner_organization_id is not specified in ProjectCreate.
    Assume user exists, if not, the database will raise an error becuase owner_user_id
    is defined as foreign key to users.id.
    TODO: handle creating project under an organization
    """
    with db_session.begin():
        owner_user_id = user_id if project.owner_organization_id is None else None
        db_project = models.Project(
            **project.model_dump(), owner_user_id=owner_user_id, created_by=user_id
        )
        db_session.add(db_project)

    db_session.refresh(db_project)

    return db_project


def get_or_create_user(
    db_session: Session,
    auth_provider: str,
    auth_user_id: str,
    name: str,
    email: str,
    profile_picture: str | None = None,
) -> models.User:
    with db_session.begin():
        # Step 1: Acquire a lock on the row to prevent race condition
        db_user: Union[models.User, None] = db_session.execute(
            select(models.User)
            .where(
                models.User.auth_provider == auth_provider,
                models.User.auth_user_id == auth_user_id,
            )
            .with_for_update()
        ).scalar_one_or_none()

        if db_user:
            return db_user  # Return the existing user if found

        # Step 2: Create the user if not found
        # TODO: compliance with PII data
        logger.info(f"Creating user: {name}")
        db_user = models.User(
            auth_provider=auth_provider,
            auth_user_id=auth_user_id,
            name=name,
            email=email,
            profile_picture=profile_picture,
        )
        db_session.add(db_user)

    db_session.refresh(db_user)
    return db_user


def create_agent(
    db_session: Session, agent: schemas.AgentCreate, project_id: UUID, user_id: UUID
) -> models.Agent:
    """
    Create a new agent under a project, and create a new API key for the agent.
    Assume user's access to the project has been checked.
    TODO: a more unified way to handle access control?
    """
    with db_session.begin():
        # Create the agent
        db_agent = models.Agent(**agent.model_dump(), project_id=project_id, creator_id=user_id)
        db_session.add(db_agent)
        db_session.flush()  # Flush to get the agent's ID

        # Create the API key for the agent
        api_key = models.APIKey(key=secrets.token_hex(32), agent_id=db_agent.id)
        db_session.add(api_key)

    db_session.refresh(db_agent)
    return db_agent


def user_has_admin_access_to_org(db_session: Session, user_id: UUID, org_id: UUID) -> bool:
    """Check if a user has admin access to an organization."""
    # TODO: implement this
    return True


def user_has_admin_access_to_project(db_session: Session, user_id: UUID, project_id: UUID) -> bool:
    """Check if a user has admin access to a project."""
    # TODO: implement properly with organization and project access control
    # for now, just check if project owner is the user
    db_project = db_session.execute(
        select(models.Project).filter_by(id=project_id)
    ).scalar_one_or_none()
    if not db_project:
        raise ProjectNotFoundError(f"Project with ID {project_id} not found")
    return db_project.owner_user_id is not None and db_project.owner_user_id == user_id


# TODO: try catch execption handling somewhere
# def soft_delete_api_key(session: Session, id: str):
#     api_key = session.query(APIKey).filter(APIKey.id == id).first()
#     api_key.status = APIKey.Status.DELETED
#     session.commit()


# def create_api_key(db_session: Session, user_id: str) -> str:
#     # get user and make sure they exist
#     user = db_session.execute(select(db.User).where(db.User.id == user_id)).scalar_one_or_none()
#     if not user:
#         raise UserNotFoundError(f"User {user_id} not found")

#     # Create a new APIKey instance
#     new_api_key = db.APIKey(
#         key=secrets.token_hex(32),
#         project_id=project_id,
#         creator_id=creator_id,
#         status=APIKey.Status.ACTIVE,
#         plan=APIKey.Plan.FREE,
#         daily_quota_used=0,
#         total_quota_used=0,
#     )

#     # Add the new APIKey to the session
#     db.add(new_api_key)
#     # Commit the session to save the new APIKey to the database
#     db.commit()

#     return new_api_key


# def increment_api_key_usage(session: Session, id: str) -> None:
#     statement = (
#         update(APIKey)
#         .where(APIKey.id == id)
#         .values(daily_quota_used=APIKey.daily_quota_used + 1, total_requests_made=APIKey.total_quota_used + 1)
#     )
#     session.execute(statement)
#     session.commit()


# TODO: error handling and logging
# def handle_api_request(session: Session, api_key_str: str, daily_limit: int) -> Tuple[bool, str]:
#     """
#     Handles the incoming API request, validates the API key, checks quotas, and increments them.

#     Parameters:
#     - session: SQLAlchemy session object
#     - api_key_str: The API key provided by the user
#     - daily_limit: The maximum number of daily requests allowed per API key

#     Returns:
#     - Tuple[bool, str]: success (True if the request is successful, False otherwise),
#                         and an error or success message as a string.
#     """

#     statement: Union[Select, Update] = select(APIKey).where(APIKey.key == api_key_str)
#     result = session.execute(statement)
#     api_key = result.scalar_one_or_none()

#     if api_key is None:
#         return False, "Invalid API key"

#     if api_key.status != "active":
#         return False, "API key is not active"

#     now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
#     need_reset = now >= api_key.daily_quota_reset_at + datetime.timedelta(days=1)

#     if not need_reset and api_key.daily_quota_used >= daily_limit:
#         return False, "Daily quota exceeded"

#     if need_reset:
#         # Reset the daily quota
#         statement = (
#             update(APIKey)
#             .where(APIKey.id == api_key.id)
#             .values(daily_quota_used=1, daily_quota_reset_at=now, total_requests_made=APIKey.total_quota_used + 1)
#         )
#     else:
#         # Increment the daily quota
#         statement = (
#             update(APIKey)
#             .where(APIKey.id == api_key.id)
#             .values(daily_quota_used=APIKey.daily_quota_used + 1, total_requests_made=APIKey.total_quota_used + 1)
#         )

#     try:
#         session.execute(statement)
#         session.commit()
#         return True, "Valid API key"
#     except Exception as e:
#         logger.error(f"Failed to update API key quotas: {str(e)}")
#         session.rollback()
#         return False, "Internal database error"
