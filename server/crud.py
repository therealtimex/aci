from .db import APIKey
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Tuple
from sqlalchemy import select, update
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# CRUD
# TODO: try catch execption handling somewhere
def soft_delete_api_key(session: Session, id: str):
    api_key = session.query(APIKey).filter(APIKey.id == id).first()
    api_key.status = APIKey.Status.DELETED
    session.commit()


def increment_api_key_usage(session: Session, id: str):
    statement = (
        update(APIKey)
        .where(APIKey.id == id)
        .values(daily_quota_used=APIKey.daily_quota_used + 1, total_requests_made=APIKey.total_quota_used + 1)
    )
    session.execute(statement)
    session.commit()


# TODO: error handling and logging
def handle_api_request(session: Session, api_key_str: str, daily_limit: int) -> Tuple[bool, str]:
    """
    Handles the incoming API request, validates the API key, checks quotas, and increments them.

    Parameters:
    - session: SQLAlchemy session object
    - api_key_str: The API key provided by the user
    - daily_limit: The maximum number of daily requests allowed per API key

    Returns:
    - Tuple[bool, str]: success (True if the request is successful, False otherwise),
                        and an error or success message as a string.
    """

    statement = select(APIKey).where(APIKey.key == api_key_str)
    result = session.execute(statement)
    api_key = result.scalar_one_or_none()

    if api_key is None:
        return False, "Invalid API key"

    if api_key.status != "active":
        return False, "API key is not active"

    now: datetime = datetime.now(datetime.timezone.utc)
    need_reset = now >= api_key.daily_quota_reset_at + timedelta(days=1)

    if not need_reset and api_key.daily_quota_used >= daily_limit:
        return False, "Daily quota exceeded"

    if need_reset:
        # Reset the daily quota
        statement = (
            update(APIKey)
            .where(APIKey.id == api_key.id)
            .values(daily_quota_used=1, daily_quota_reset_at=now, total_requests_made=APIKey.total_quota_used + 1)
        )
    else:
        # Increment the daily quota
        statement = (
            update(APIKey)
            .where(APIKey.id == api_key.id)
            .values(daily_quota_used=APIKey.daily_quota_used + 1, total_requests_made=APIKey.total_quota_used + 1)
        )

    try:
        session.execute(statement)
        session.commit()
        return True, "Valid API key"
    except Exception as e:
        logger.error(f"Failed to update API key quotas: {str(e)}")
        session.rollback()
        return False, "Internal database error"
