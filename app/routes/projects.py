from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import dependencies as deps
from app import schemas
from app.db import crud
from app.logging import get_logger

# Create router instance
router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=schemas.ProjectPublic)
async def create_project(
    project: schemas.ProjectCreate,
    user_id: UUID = Depends(deps.verify_user),
    db_session: Session = Depends(deps.get_db_session),
) -> Any:
    try:
        logger.info(f"Creating project: {project}, user_id: {user_id}")

        if project.owner_organization_id is not None:
            # Assuming you have a function to check if a user has admin access to an org
            if not crud.user_has_admin_access_to_org(
                db_session, user_id, project.owner_organization_id
            ):
                raise HTTPException(
                    status_code=403, detail="User does not have admin access to the organization"
                )

        db_project = crud.create_project(
            db_session,
            project,
            user_id,
        )
        logger.info(f"Created project: {schemas.ProjectPublic.model_validate(db_project)}")
        return db_project
    except Exception:
        logger.error("Error in creating project", exc_info=True)
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create project")
