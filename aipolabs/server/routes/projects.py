from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.schemas.agent import AgentCreate, AgentPublic
from aipolabs.common.schemas.project import (
    ProjectCreate,
    ProjectOwnerType,
    ProjectPublic,
)
from aipolabs.server import dependencies as deps

# Create router instance
router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=ProjectPublic)
async def create_project(
    project: ProjectCreate,
    user_id: Annotated[UUID, Depends(deps.validate_http_bearer)],
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
) -> Any:
    try:
        logger.info(f"Creating project: {project}, user_id: {user_id}")
        # creator should be the same as user_id
        if project.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not match creator",
            )
        # if owner_type is user, check if user_id matches owner_id
        if project.owner_type == ProjectOwnerType.USER:
            if user_id != project.owner_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not match owner for user owned project",
                )
        # if project is to be created under an organization, check if user has admin access to the organization
        if project.owner_type == ProjectOwnerType.ORGANIZATION:
            if not crud.user_has_admin_access_to_org(db_session, user_id, project.owner_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have admin access to the organization",
                )

        db_project = crud.create_project(db_session, project)
        db_session.commit()
        logger.info(f"Created project: {db_project}")
        return db_project
    except Exception:
        logger.error("Error in creating project", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project",
        )


@router.post("/{project_id}/agents/", response_model=AgentPublic)
async def create_agent(
    project_id: UUID,
    agent: AgentCreate,
    user_id: Annotated[UUID, Depends(deps.validate_http_bearer)],
    db_session: Annotated[Session, Depends(deps.yield_db_session)],
) -> Any:
    try:
        logger.info(f"Creating agent in project: {project_id}, user_id: {user_id}")
        # check project_id matches agent.project_id
        if project_id != agent.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID does not match agent's project ID",
            )
        # check if user_id matches agent.created_by
        if user_id != agent.created_by:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID does not match agent's creator",
            )
        # Check if the user has admin access to the project
        if not crud.user_has_admin_access_to_project(db_session, user_id, project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have admin access to the project",
            )

        db_agent = crud.create_agent(db_session, agent)
        db_session.commit()
        logger.info(f"Created agent: {AgentPublic.model_validate(db_agent)}")
        return db_agent
    except Exception:
        logger.error("Error in creating agent", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent",
        )
