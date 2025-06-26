from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Annotated, Union
from uuid import UUID

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader, HTTPBearer
from sqlalchemy.orm import Session

from aci.common import utils
from aci.common.db import crud
from aci.common.db.sql_models import Agent, Project, APIKey as SQLAPIKey
from aci.common.enums import APIKeyStatus
from aci.common.exceptions import (
    AgentNotFound,
    DailyQuotaExceeded,
    InvalidAPIKey,
    AuthenticationError,
    ProjectNotFound,
)
from aci.common.logging_setup import get_logger
from aci.server import billing, config

logger = get_logger(__name__)
http_bearer = HTTPBearer(auto_error=True, description="login to receive a JWT token")
api_key_header = APIKeyHeader(
    # Changed: Use a different header for agent API keys
    name=config.ACI_API_KEY_HEADER,
    description="API key for authentication",
    auto_error=True,
)

# New type for API Key authentication details
class APIKeyAuthDetails:
    def __init__(self, api_key_id: UUID, project: Project, agent: Agent):
        self.api_key_id = api_key_id
        self.project = project
        self.agent = agent


class RequestContext:
    def __init__(self, db_session: Session, api_key_auth_details: APIKeyAuthDetails, project: Project, agent: Agent):
        self.db_session = db_session
        # Store the full APIKeyAuthDetails object
        # This will be populated by get_api_key_details
        self.api_key_auth_details = api_key_auth_details
        self.project = project
        self.agent = agent


def yield_db_session() -> Generator[Session, None, None]:
    db_session = utils.create_db_session(config.DB_FULL_URL)
    try:
        yield db_session
    finally:
        db_session.close()


# Modified: This dependency now specifically validates agent-associated API keys
def get_agent_api_key_details(
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_key: Annotated[str, Security(api_key_header)],  # Use agent API key header
) -> APIKeyAuthDetails:
    """Validate API key and return the API key ID. (not the actual API key string)"""
    api_key = crud.projects.get_api_key(db_session, api_key_key)
    if api_key is None:
        logger.error(f"API key not found, partial_api_key={api_key_key[:4]}****{api_key_key[-4:]}")
        raise InvalidAPIKey("api key not found")

    elif api_key.status == APIKeyStatus.DISABLED:
        logger.error(f"API key is disabled, api_key_id={api_key.id}")
        raise InvalidAPIKey("API key is disabled")

    elif api_key.status == APIKeyStatus.DELETED:
        logger.error(f"API key is deleted, api_key_id={api_key.id}")
        raise InvalidAPIKey("API key is deleted")

    agent = crud.projects.get_agent_by_api_key_id(db_session, api_key.id)
    if not agent:
        logger.error(f"Agent not found for API key, api_key_id={api_key.id}")
        raise AgentNotFound(f"Agent not found for api_key_id={api_key.id}")

    project = crud.projects.get_project_by_api_key_id(db_session, api_key.id)
    if not project:
        logger.error(f"Project not found for API key, api_key_id={api_key.id}")
        raise ProjectNotFound(f"Project not found for api_key_id={api_key.id}")

    logger.info(f"API key validation successful, api_key_id={api_key.id}")
    return APIKeyAuthDetails(api_key_id=api_key.id, project=project, agent=agent)


# New dependency for organization-level API key
def get_org_api_key(
    org_api_key: Annotated[str, Security(APIKeyHeader(name="X-ORG-API-KEY", auto_error=True))]
) -> str:
    """Validates the organization-level API key from the environment."""
    if org_api_key != config.ACI_ORG_API_KEY:
        logger.error("Invalid organization API key provided.")
        raise AuthenticationError("Invalid organization API key")
    return org_api_key


def get_projects_auth_context(
    propelauth_user: Annotated[User | None, Depends(acl.get_propelauth().require_user)] = None,
    org_api_key: Annotated[str | None, Depends(get_org_api_key)] = None,
) -> Union[User, str]:  # Return the API key string if valid
    """
    Authenticates the request for /projects endpoints using either PropelAuth (Bearer token)
    or an organization-level API Key.
    Prioritizes PropelAuth, then Org API Key.
    """
    if propelauth_user:
        return propelauth_user
    elif org_api_key:
        return org_api_key  # Return the validated API key string
    else:
        raise AuthenticationError(
            "Authentication required: Provide a valid Bearer token or Organization API Key."
        )


def validate_project_quota(
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_auth_details: Annotated[APIKeyAuthDetails, Depends(get_api_key_details)],
) -> Project:
    logger.debug(f"Validating project quota, api_key_id={api_key_auth_details.api_key_id}")

    project = api_key_auth_details.project
    if not project:
        logger.error(f"Project not found, api_key_id={api_key_auth_details.api_key_id}")
        raise ProjectNotFound(f"Project not found, api_key_id={api_key_auth_details.api_key_id}")

    now: datetime = datetime.now(UTC)
    need_reset = now >= project.daily_quota_reset_at.replace(tzinfo=UTC) + timedelta(days=1)

    if not need_reset and project.daily_quota_used >= config.PROJECT_DAILY_QUOTA:
        logger.warning(
            f"Daily quota exceeded, "
            f"project_id={project.id} "
            f"daily_quota_used={project.daily_quota_used} "
            f"daily_quota={config.PROJECT_DAILY_QUOTA}"
        )
        raise DailyQuotaExceeded(
            f"Daily quota exceeded for project={project.id}, "
            f"daily_quota_used={project.daily_quota_used} "
            f"daily quota={config.PROJECT_DAILY_QUOTA}"
        )

    crud.projects.increase_project_quota_usage(db_session, project)
    # TODO: commit here with the same db_session or should create a separate db_session?
    db_session.commit()

    logger.info(f"Project quota validation successful, project_id={project.id}")
    return project


def validate_monthly_api_quota(
    request: Request,
    db_session: Annotated[Session, Depends(yield_db_session)],
    project: Annotated[Project, Depends(validate_project_quota)],
) -> None:
    """
    Use quota for a project operation.

    1. Only check and manage quota for certain endpoints
    2. Reset quota if it's a new month
    3. Increment usage or raise error if exceeded
    """
    # Only check quota for app search and function search/execute endpoints
    path = request.url.path
    is_quota_limited_endpoint = path.startswith(f"{config.ROUTER_PREFIX_APPS}/search") or (
        path.startswith(f"{config.ROUTER_PREFIX_FUNCTIONS}/")
        and (path.endswith("/execute") or path.endswith("/search"))
    )
    if not is_quota_limited_endpoint:
        return

    last_reset = project.api_quota_last_reset.replace(tzinfo=UTC)
    cur_first_day_of_month = datetime.now(UTC).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    if cur_first_day_of_month > last_reset:
        logger.info(
            f"resetting monthly quota, last_reset={last_reset}, cur_first_day_of_month={cur_first_day_of_month}",
        )
        crud.projects.reset_api_monthly_quota_for_org(
            db_session, project.org_id, cur_first_day_of_month
        )

    plan = billing.get_active_plan_by_org_id(db_session, project.org_id)
    billing.increment_quota(db_session, project, plan.features["api_calls_monthly"])
    db_session.commit()

    logger.info("monthly api quota validation successful", extra={"project_id": project.id})


def get_request_context(
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_auth_details: Annotated[APIKeyAuthDetails, Depends(get_api_key_details)],
    project: Annotated[Project, Depends(validate_project_quota)],
    _: Annotated[None, Depends(validate_monthly_api_quota)],
) -> RequestContext:
    """
    Returns a RequestContext object containing the DB session,
    the validated API key ID, and the project ID.
    """
    logger.info(f"Populating request context, api_key_id={api_key_auth_details.api_key_id}, "
                f"project_id={project.id}, agent_id={api_key_auth_details.agent.id}")
    return RequestContext(db_session=db_session,
        api_key_auth_details=api_key_auth_details,
        project=project,
        agent=api_key_auth_details.agent,
    )
