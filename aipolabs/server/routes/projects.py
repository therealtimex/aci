from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aipolabs.common.logging import get_logger
from aipolabs.server import dependencies as deps
from aipolabs.server import schemas
from aipolabs.server.db import crud

# Create router instance
router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=schemas.ProjectPublic)
async def create_project(
    project: schemas.ProjectCreate,
    user_id: Annotated[UUID, Depends(deps.validate_http_bearer)],
    db_session: Annotated[Session, Depends(deps.get_db_session)],
) -> Any:
    try:
        logger.info(f"Creating project: {project}, user_id: {user_id}")
        # if project is to be created under an organization, check if user has admin access to the organization
        if project.owner_organization_id is not None:
            if not crud.user_has_admin_access_to_org(
                db_session, user_id, project.owner_organization_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have admin access to the organization",
                )

        db_project = crud.create_project(db_session, project, user_id)
        db_session.commit()
        logger.info(f"Created project: {schemas.ProjectPublic.model_validate(db_project)}")
        return db_project
    except Exception:
        # TODO: need rollback?
        logger.error("Error in creating project", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project",
        )


@router.post("/{project_id}/agents/", response_model=schemas.AgentPublic)
async def create_agent(
    project_id: UUID,
    agent: schemas.AgentCreate,
    user_id: Annotated[UUID, Depends(deps.validate_http_bearer)],
    db_session: Annotated[Session, Depends(deps.get_db_session)],
) -> Any:
    try:
        logger.info(f"Creating agent in project: {project_id}, user_id: {user_id}")

        # Check if the user has admin access to the project
        if not crud.user_has_admin_access_to_project(db_session, user_id, project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have admin access to the project",
            )

        db_agent = crud.create_agent(
            db_session,
            agent,
            project_id,
            user_id,
        )
        db_session.commit()
        logger.info(f"Created agent: {schemas.AgentPublic.model_validate(db_agent)}")
        return db_agent
    except Exception:
        logger.error("Error in creating agent", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent",
        )
