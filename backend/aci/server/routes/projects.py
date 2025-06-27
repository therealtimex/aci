from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from propelauth_fastapi import User
from sqlalchemy.orm import Session

from aci.common.db import crud
from aci.common.db.sql_models import Agent, Project
from aci.common.exceptions import (
    AgentNotFound,
    ProjectIsLastInOrgError,
    ProjectNotFound,
)
from aci.common.logging_setup import get_logger
from aci.common.schemas.agent import AgentCreate, AgentPublic, AgentUpdate
from aci.common.schemas.project import ProjectCreate, ProjectPublic, ProjectUpdate
from aci.server import acl, config, quota_manager
from aci.server import dependencies as deps

# Create router instance
router = APIRouter()
logger = get_logger(__name__)

auth = acl.get_propelauth()


# TODO: Once member has been introduced change the ACL to require_org_member_with_minimum_role
@router.post("", response_model=ProjectPublic, include_in_schema=True)
async def create_project(
    body: ProjectCreate,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> Project:
    if user:
        logger.info(f"Create project, user_id={user.user_id}, org_id={body.org_id}")

        acl.validate_user_access_to_org(user, body.org_id)
    else:
        logger.info(f"Create project, internal_api_key, org_id={body.org_id}")

    quota_manager.enforce_project_creation_quota(db_session, body.org_id)

    project = crud.projects.create_project(db_session, body.org_id, body.name)

    # Create a default Agent for the project
    crud.projects.create_agent(
        db_session,
        project.id,
        name="Default Agent",
        description="Default Agent",
        allowed_apps=[],
        custom_instructions={},
    )
    db_session.commit()

    if user:
        logger.info(
            f"Created project, project_id={project.id}, user_id={user.user_id}, org_id={body.org_id}"
        )
    else:
        logger.info(f"Created project, project_id={project.id}, internal_api_key, org_id={body.org_id}")
    return project


@router.get("", response_model=list[ProjectPublic], include_in_schema=True)
async def get_projects(
    org_id: Annotated[UUID, Header(alias=config.ACI_ORG_ID_HEADER)],
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> list[Project]:
    """
    Get all projects for the organization if the user is a member of the organization.
    """
    if user:
        acl.validate_user_access_to_org(user, org_id)

        logger.info(f"Get projects, user_id={user.user_id}, org_id={org_id}")
    else:
        logger.info(f"Get projects, internal_api_key, org_id={org_id}")

    projects = crud.projects.get_projects_by_org(db_session, org_id)

    return projects


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=True)
async def delete_project(
    project_id: UUID,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> None:
    """
    Delete a project by project id.

    This operation will cascade delete all related data:
    - Agents and their API keys
    - App configurations
    - Linked accounts

    All associations to the project will be removed from the database.
    """
    if user:
        logger.info(f"Delete project, project_id={project_id}, user_id={user.user_id}")

        acl.validate_user_access_to_project(db_session, user, project_id)
    else:
        logger.info(f"Delete project, project_id={project_id}, internal_api_key")

    # Get the project to check its organization
    project = crud.projects.get_project(db_session, project_id)
    if not project:
        logger.error(f"Project not found, project_id={project_id}")
        raise ProjectNotFound(f"project={project_id} not found")

    # Check if this is the last project in the organization
    org_projects = crud.projects.get_projects_by_org(db_session, project.org_id)
    if len(org_projects) <= 1:
        logger.error(
            f"Cannot delete last project, project_id={project_id}, org_id={project.org_id}"
        )
        raise ProjectIsLastInOrgError()

    crud.projects.delete_project(db_session, project_id)
    db_session.commit()


@router.patch("/{project_id}", response_model=ProjectPublic, include_in_schema=True)
async def update_project(
    project_id: UUID,
    body: ProjectUpdate,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> Project:
    """
    Update a project by project id.
    Currently supports updating the project name.
    """
    if user:
        logger.info(f"Update project, project_id={project_id}, user_id={user.user_id}")

        acl.validate_user_access_to_project(db_session, user, project_id)
    else:
        logger.info(f"Update project, project_id={project_id}, internal_api_key")

    project = crud.projects.get_project(db_session, project_id)
    if not project:
        logger.error(f"Project not found, project_id={project_id}")
        raise ProjectNotFound(f"project={project_id} not found")

    updated_project = crud.projects.update_project(db_session, project, body)
    db_session.commit()

    return updated_project


@router.post("/{project_id}/agents", response_model=AgentPublic, include_in_schema=True)
async def create_agent(
    project_id: UUID,
    body: AgentCreate,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> Agent:
    if user:
        logger.info(f"Create agent, project_id={project_id}, user_id={user.user_id}")

        acl.validate_user_access_to_project(db_session, user, project_id)
    else:
        logger.info(f"Create agent, project_id={project_id}, internal_api_key")

    quota_manager.enforce_agent_creation_quota(db_session, project_id)

    agent = crud.projects.create_agent(
        db_session,
        project_id,
        body.name,
        body.description,
        body.allowed_apps,
        body.custom_instructions,
    )
    db_session.commit()
    logger.info(f"Created agent, agent_id={agent.id}")
    return agent


@router.patch(
    "/{project_id}/agents/{agent_id}",
    response_model=AgentPublic,
    include_in_schema=True,
)
async def update_agent(
    project_id: UUID,
    agent_id: UUID,
    body: AgentUpdate,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> Agent:
    if user:
        logger.info(
            f"Update agent, agent_id={agent_id}, project_id={project_id}, user_id={user.user_id}"
        )

        acl.validate_user_access_to_project(db_session, user, project_id)
    else:
        logger.info(f"Update agent, agent_id={agent_id}, project_id={project_id}, internal_api_key")

    agent = crud.projects.get_agent_by_id(db_session, agent_id)
    if not agent:
        logger.error(f"Agent not found, agent_id={agent_id}, project_id={project_id}")
        raise AgentNotFound(f"agent={agent_id} not found in project={project_id}")
    # TODO: get project direct from agent through relationship
    project = crud.projects.get_project(db_session, project_id)
    if not project:
        logger.error(f"Project not found, project_id={project_id}")
        raise ProjectNotFound(f"project={project_id} not found")

    if agent.project_id != project_id:
        logger.error(
            f"Agent with project_id={agent.project_id} does not belong to project with project_id={project_id}"
        )
        raise AgentNotFound(f"Agent={agent_id} not found in project={project_id}")

    crud.projects.update_agent(db_session, agent, body)
    db_session.commit()

    return agent


@router.delete("/{project_id}/agents/{agent_id}", include_in_schema=True)
async def delete_agent(
    project_id: UUID,
    agent_id: UUID,
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
    user: Annotated[User | None, Depends(deps.user_or_internal_api_key)],
) -> dict[str, str]:
    """
    Delete an agent by agent id
    """
    if user:
        logger.info(
            f"Delete agent, agent_id={agent_id}, project_id={project_id}, user_id={user.user_id}"
        )

        acl.validate_user_access_to_project(db_session, user, project_id)
    else:
        logger.info(f"Delete agent, agent_id={agent_id}, project_id={project_id}, internal_api_key")

    agent = crud.projects.get_agent_by_id(db_session, agent_id)
    if not agent:
        logger.error(f"Agent not found, agent_id={agent_id}, project_id={project_id}")
        raise AgentNotFound(f"Agent={agent_id} not found")

    if agent.project_id != project_id:
        logger.error(
            f"Agent does not belong to project, agent_id={agent_id}, project_id={project_id}"
        )
        # raise 404 instead of 403 to avoid leaking information about the existence of the agent
        raise AgentNotFound(f"Agent={agent_id} not found")

    crud.projects.delete_agent(db_session, agent)
    db_session.commit()

    return {"message": f"Agent={agent.name} deleted successfully"}
