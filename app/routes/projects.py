import logging
from fastapi import APIRouter, Depends, HTTPException
from app import schemas
from sqlalchemy.orm import Session
from app.database import crud
from typing import Any

from app import dependencies as deps

# Create router instance
router = APIRouter()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@router.post("/", response_model=schemas.Project)
async def create_project(
    project: schemas.ProjectCreate,
    user_id: str = Depends(deps.verify_user),
    db_session: Session = Depends(deps.get_db_session),
) -> Any:
    try:
        logger.info(f"Creating project: {project}, user_id: {user_id}")
        db_project = crud.create_project(
            db_session,
            project,
            user_id,
        )
        logger.info(f"Created project: {schemas.Project.model_validate(db_project)}")
        return db_project
    except Exception:
        logger.error("Error in creating project", exc_info=True)
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create project")
