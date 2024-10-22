from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app import schemas
from app.db import crud
from app.dependencies import get_db_session
from app.logging import get_logger
from app.openai_service import OpenAIService
from database import models

logger = get_logger(__name__)
router = APIRouter()
openai_service = OpenAIService()


class AppFilterParams(BaseModel):
    """
    Parameters for filtering applications.
    TODO: add sorted_by field?
    TODO: category enum?
    TODO: add tags field?
    TODO: filter by similarity score?
    """

    query: str | None = Field(
        default=None,
        description="Natural language query for vector similarity search. Results will be sorted by relevance to the query.",
    )
    categories: list[str] | None = Field(
        default=None, description="List of categories for filtering."
    )
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of Apps per response."
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset.")

    # need this in case user set {"categories": None} which will translate to [''] in the query params
    @field_validator("categories")
    def validate_categories(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            # Remove any empty strings from the list
            v = [category for category in v if category.strip()]
            # If after removing empty strings the list is empty, set it to None
            if not v:
                return None
        return v


# TODO: implement api key validation and project quota checks
# (middleware or dependency? and for mvp can probably just use memory for daily quota limit instead of checking and updating db every time)
# TODO: implement app category filtering
# TODO: filter out disabled apps first before doing any other filtering
# TODO: more efficient pagination?
@router.get("/", response_model=list[schemas.AppPublic])
async def get_apps(
    filter_params: Annotated[AppFilterParams, Query()],
    db_session: Session = Depends(get_db_session),
) -> list[models.App]:
    """
    Returns a list of applications (name and description).
    """
    try:
        logger.info(f"Getting apps with filter params: {filter_params}")
        query_embedding = (
            openai_service.generate_embedding(filter_params.query) if filter_params.query else None
        )
        logger.debug(f"Generated query embedding: {query_embedding}")
        apps = crud.get_apps(
            db_session,
            filter_params.categories,
            query_embedding,
            filter_params.limit,
            filter_params.offset,
        )
        return apps

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
