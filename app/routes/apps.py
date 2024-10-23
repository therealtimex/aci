from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app import schemas
from app.db import crud
from app.dependencies import get_db_session
from app.logging import get_logger
from app.openai_service import OpenAIService

logger = get_logger(__name__)
router = APIRouter()
openai_service = OpenAIService()


class AppFilterParams(BaseModel):
    """
    Parameters for filtering applications.
    TODO: add flag to include detailed app info? (e.g., dev portal will need this)
    TODO: add sorted_by field?
    TODO: category enum?
    TODO: add tags field?
    TODO: filter by similarity score?
    """

    intent: str | None = Field(
        default=None,
        description="Natural language intent for vector similarity sorting. Results will be sorted by relevance to the intent.",
    )
    categories: list[str] | None = Field(
        default=None, description="List of categories for filtering."
    )
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of Apps per response."
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset.")

    # need this in case user set {"categories": None} which will translate to [''] in the params
    @field_validator("categories")
    def validate_categories(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            # Remove any empty strings from the list
            v = [category for category in v if category.strip()]
            # If after removing empty strings the list is empty, set it to None
            if not v:
                return None
        return v

    # empty intent or string with spaces should be treated as None
    @field_validator("intent")
    def validate_intent(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            return None
        return v


# TODO: implement api key validation and project quota checks
# (middleware or dependency? and for mvp can probably just use memory for daily quota limit instead of checking and updating db every time)
# TODO: filter out disabled apps first before doing any other filtering
@router.get(
    "/search", response_model=list[schemas.AppBasicPublic], response_model_exclude_unset=True
)
async def search_apps(
    filter_params: Annotated[AppFilterParams, Query()],
    db_session: Session = Depends(get_db_session),
) -> list[schemas.AppBasicPublic]:
    """
    Returns a list of applications (name and description).
    """
    try:
        logger.info(f"Getting apps with filter params: {filter_params}")
        intent_embedding = (
            openai_service.generate_embedding(filter_params.intent)
            if filter_params.intent
            else None
        )
        logger.debug(f"Generated intent embedding: {intent_embedding}")
        apps_with_scores = crud.search_apps(
            db_session,
            filter_params.categories,
            intent_embedding,
            filter_params.limit,
            filter_params.offset,
        )
        # build apps list with similarity scores if they exist
        apps: list[schemas.AppBasicPublic] = []
        for app, score in apps_with_scores:
            app = schemas.AppBasicPublic.model_validate(app)
            if score is not None:
                app.similarity_score = score
            apps.append(app)

        return apps

    except Exception as e:
        logger.error("Error getting apps", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
