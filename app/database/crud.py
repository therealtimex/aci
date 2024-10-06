from sqlalchemy.orm import Session
import datetime
from typing import Tuple
from sqlalchemy import select, update
import logging
from app.database import models
from app import schemas
from typing import Union
from sqlalchemy.sql import Select, Update
import secrets

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """Exception raised when a user is not found in the database."""

    pass


# create a new project and automatically generate an api key
def create_project(db_session: Session, project: schemas.ProjectCreate, user_id: str) -> models.Project:
    # Start a new transaction
    db_session.begin()

    # Retrieve the user's organization ID
    db_user = db_session.execute(select(models.User).filter_by(id=user_id)).scalar_one_or_none()
    if not db_user:
        raise UserNotFoundError(f"User with ID {user_id} not found")

    # Create a new project instance
    db_project = models.Project(
        name=project.name,
        creator_id=user_id,
        organization_id=db_user.organization_id,
    )
    db_session.add(db_project)
    db_session.flush()  # Ensure the project ID is generated
    db_session.refresh(db_project)

    # Create a new API key instance
    db_api_key = models.APIKey(
        key=secrets.token_hex(32),
        project_id=db_project.id,
        creator_id=user_id,
        plan=models.APIKey.Plan.FREE,  # TODO: decide by user or org
        daily_quota_used=0,
        total_quota_used=0,
    )
    db_session.add(db_api_key)

    # Commit the transaction
    db_session.commit()

    db_session.refresh(db_project)

    return db_project


def create_or_get_user(db_session: Session, user: schemas.UserCreate) -> models.User:
    """Use SELECT FOR UPDATE to handle concurrent access."""
    # Step 1: Acquire a lock on the row to prevent race condition
    db_user = db_session.execute(
        select(models.User)
        .where(models.User.auth_provider == user.auth_provider, models.User.auth_user_id == user.auth_user_id)
        .with_for_update()
    ).scalar_one_or_none()

    if db_user:
        return db_user  # Return the existing user if found

    # Step 2: Create the user if not found
    # TODO: compliance with PII data
    logger.info(f"Creating user: {user}")
    db_user = models.User(**user.model_dump())
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    return db_user


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
