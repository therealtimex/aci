import secrets
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from aipolabs.common.db import sql_models
from aipolabs.common.logging import get_logger
from aipolabs.common.schemas.agent import AgentCreate
from aipolabs.common.schemas.project import ProjectCreate

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
        db_session.execute(select(sql_models.User).filter_by(id=user_id)).scalar_one_or_none()
        is not None
    )


def create_project(
    db_session: Session, project: ProjectCreate, user_id: UUID
) -> sql_models.Project:
    """
    Create a new project.
    Create as personal project if owner_organization_id is not specified in ProjectCreate.
    Assume user exists, if not, the database will raise an error becuase owner_user_id
    is defined as foreign key to users.id.
    TODO: handle creating project under an organization
    """
    owner_user_id = user_id if project.owner_organization_id is None else None
    db_project = sql_models.Project(
        **project.model_dump(), owner_user_id=owner_user_id, created_by=user_id
    )
    db_session.add(db_project)
    db_session.flush()
    db_session.refresh(db_project)

    return db_project


def get_or_create_user(
    db_session: Session,
    auth_provider: str,
    auth_user_id: str,
    name: str,
    email: str,
    profile_picture: str | None = None,
) -> sql_models.User:
    # Step 1: Acquire a lock on the row to prevent race condition
    db_user: Union[sql_models.User, None] = db_session.execute(
        select(sql_models.User)
        .where(
            sql_models.User.auth_provider == auth_provider,
            sql_models.User.auth_user_id == auth_user_id,
        )
        .with_for_update()
    ).scalar_one_or_none()

    if db_user:
        return db_user  # Return the existing user if found

    # Step 2: Create the user if not found
    # TODO: compliance with PII data
    logger.info(f"Creating user: {name}")
    db_user = sql_models.User(
        auth_provider=auth_provider,
        auth_user_id=auth_user_id,
        name=name,
        email=email,
        profile_picture=profile_picture,
    )
    db_session.add(db_user)
    db_session.flush()

    db_session.refresh(db_user)
    return db_user


def create_agent(
    db_session: Session, agent: AgentCreate, project_id: UUID, user_id: UUID
) -> sql_models.Agent:
    """
    Create a new agent under a project, and create a new API key for the agent.
    Assume user's access to the project has been checked.
    TODO: a more unified way to handle access control?
    """
    # Create the agent
    db_agent = sql_models.Agent(**agent.model_dump(), project_id=project_id, created_by=user_id)
    db_session.add(db_agent)
    db_session.flush()  # Flush to get the agent's ID

    # Create the API key for the agent
    api_key = sql_models.APIKey(key=secrets.token_hex(32), agent_id=db_agent.id)
    db_session.add(api_key)
    db_session.flush()

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
        select(sql_models.Project).filter_by(id=project_id)
    ).scalar_one_or_none()
    if not db_project:
        raise ProjectNotFoundError(f"Project with ID {project_id} not found")

    return db_project.owner_user_id is not None and db_project.owner_user_id == user_id


def get_api_key(db_session: Session, key: str) -> sql_models.APIKey | None:
    db_api_key: sql_models.APIKey | None = db_session.execute(
        select(sql_models.APIKey).filter_by(key=key)
    ).scalar_one_or_none()

    return db_api_key


# TODO: return total count of apps, or return remaining count for pagination?
# TODO: combine with postgres full text search for a hybrid search? https://github.com/pgvector/pgvector?tab=readme-ov-file#hybrid-search
# TODO: filter out unnecessary columns
def search_apps(
    db_session: Session,
    categories: list[str] | None,
    intent_embedding: list[float] | None,
    limit: int,
    offset: int,
) -> list[tuple[sql_models.App, float | None]]:
    """Get a list of apps with optional filtering by categories and sorting by vector similarity to intent. and pagination."""
    statement = select(sql_models.App)

    # TODO: Is there any way to get typing for cosine_distance, label, overlap?
    if categories and len(categories) > 0:
        statement = statement.filter(sql_models.App.categories.overlap(categories))
    if intent_embedding:
        similarity_score = sql_models.App.embedding.cosine_distance(intent_embedding)
        statement = statement.add_columns(similarity_score.label("similarity_score"))
        statement = statement.order_by("similarity_score")

    statement = statement.offset(offset).limit(limit)

    logger.warning(f"Executing statement: {statement}")

    results = db_session.execute(statement).all()

    if intent_embedding:
        return [(app, score) for app, score in results]
    else:
        return [(app, None) for app, in results]


# TODO: filter out unnecessary columns like embedding if not needed?
# TODO: return total count of functions, or return remaining count for pagination?
def search_functions(
    db_session: Session,
    app_names: list[str] | None,
    intent_embedding: list[float] | None,
    limit: int,
    offset: int,
) -> list[sql_models.Function]:
    statement = select(sql_models.Function)

    if app_names and len(app_names) > 0:
        statement = statement.join(sql_models.App).filter(sql_models.App.name.in_(app_names))
    if intent_embedding:
        similarity_score = sql_models.Function.embedding.cosine_distance(intent_embedding)
        statement = statement.order_by(similarity_score)

    statement = statement.offset(offset).limit(limit)
    logger.warning(f"Executing statement: {statement}")
    results: list[sql_models.Function] = db_session.execute(statement).scalars().all()
    return results


def get_function(db_session: Session, function_name: str) -> sql_models.Function | None:

    function: sql_models.Function | None = db_session.execute(
        select(sql_models.Function).filter_by(name=function_name)
    ).scalar_one_or_none()

    return function


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
