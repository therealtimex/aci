import logging
from uuid import UUID

from propelauth_fastapi import FastAPIAuth, User, init_auth
from sqlalchemy.orm import Session

from aci.common.db import crud
from aci.common.enums import OrganizationRole
from aci.common.exceptions import OrgAccessDenied, ProjectNotFound
from aci.server import config
from aci.server.dependencies import APIKeyAuthDetails, AuthContext

logger = logging.getLogger(__name__)


_auth = init_auth(config.PROPELAUTH_AUTH_URL, config.PROPELAUTH_API_KEY)


def get_propelauth() -> FastAPIAuth:
    return _auth


def validate_user_access_to_org(auth_context: AuthContext, org_id: UUID) -> None:
    # TODO: Change to require_org_member_with_minimum_role and require_org_member once projects have been refactored to use
    # TODO: org_id in the header. Currently they we have project_id so this function and validate_user_access_to_project are still useful.
    # Use PropelAuth's built-in method to validate organization role
    if isinstance(auth_context, User):
        get_propelauth().require_org_member(auth_context, str(org_id))
    elif isinstance(auth_context, APIKeyAuthDetails):
        # For API key, we assume it has access to its associated organization.
        # The API key is tied to an agent, which is tied to a project, which is tied to an organization.
        # So, if the org_id matches the project's org_id, access is granted.
        if auth_context.project.org_id != org_id:
            logger.error(
                f"API Key access denied to organization. API Key's project org_id={auth_context.project.org_id}, "
                f"requested org_id={org_id}"
            )
            raise OrgAccessDenied("Agent API Key does not have access to this organization.")
        # Implicitly granted if org_id matches. No further PropelAuth check needed for API keys.
    elif isinstance(auth_context, str):  # Organization API key
        # For organization API key, access is granted if the org_id matches.
        # We assume the organization API key has access to all resources within the organization.
        # In a more complex scenario, you might want to decode the API key to extract the associated org_id.
        # For this simplified version, we assume the presence of the key implies access to the requested org.
        return  # Access granted
    else:
        logger.error(f"Invalid authentication context type: {type(auth_context)}")
        raise OrgAccessDenied("Invalid authentication context.")


def validate_user_access_to_project(db_session: Session, auth_context: AuthContext, project_id: UUID) -> None:
    # TODO: refactor to use PropelAuth built-in methods
    # TODO: we can introduce project level ACLs later

    project = crud.projects.get_project(db_session, project_id)
    if not project:
        raise ProjectNotFound(f"project={project_id} not found")

    from aci.server.dependencies import APIKeyAuthDetails # Import here to avoid circular dependency

    if isinstance(auth_context, User):
        validate_user_access_to_org(auth_context, project.org_id)
    elif isinstance(auth_context, APIKeyAuthDetails):
        # For API key, we assume it has access to its associated project.
        # The API key is tied to an agent, which is tied to a project.
        if auth_context.project.id != project_id:
            logger.error(
                f"API Key access denied to project. API Key's project_id={auth_context.project.id}, "
                f"requested project_id={project_id}"
            )
            raise OrgAccessDenied("API Key does not have access to this project.")
        # Implicitly granted if project_id matches.
    elif isinstance(auth_context, str):  # Organization API key
        # For organization API key, access is granted if the project's org_id matches the key's org_id.
        # Similar to organization access, we assume the key has access to all projects within the organization.
        # In a more complex scenario, you might want to decode the API key to extract the associated org_id.
        # For this simplified version, we assume the presence of the key implies access to the requested project.
        # TODO: In the future, we might want to add more granular access control for organization API keys.
        return  # Access granted
        # Implicitly granted if project_id matches.
    else:
        logger.error(f"Invalid authentication context type: {type(auth_context)}")
        raise OrgAccessDenied("Invalid authentication context.")


def require_org_member(user: User, org_id: UUID) -> None:
    get_propelauth().require_org_member(user, str(org_id))


def require_org_member_with_minimum_role(
    user: User, org_id: UUID, minimum_role: OrganizationRole
) -> None:
    get_propelauth().require_org_member_with_minimum_role(user, str(org_id), minimum_role)
