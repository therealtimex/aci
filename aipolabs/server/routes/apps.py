from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from aipolabs.common.db import crud
from aipolabs.common.enums import Visibility
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.app import AppDetails, AppPublic
from aipolabs.common.schemas.function import FunctionPublic
from aipolabs.server import config
from aipolabs.server.dependencies import validate_api_key, yield_db_session

logger = get_logger(__name__)
router = APIRouter()
openai_service = OpenAIService(config.OPENAI_API_KEY)


class SearchAppsParams(BaseModel):
    """
    Parameters for filtering applications.
    TODO: add flag to include detailed app info? (e.g., dev portal will need this)
    TODO: add sorted_by field?
    TODO: category enum?
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


@router.get("/search", response_model=list[AppPublic])
async def search_apps(
    search_params: Annotated[SearchAppsParams, Query()],
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
) -> list[AppPublic]:
    """
    Returns a list of applications (name and description).
    """
    try:
        logger.info(f"Getting apps with filter params: {search_params}")
        intent_embedding = (
            openai_service.generate_embedding(
                search_params.intent,
                config.OPENAI_EMBEDDING_MODEL,
                config.OPENAI_EMBEDDING_DIMENSION,
            )
            if search_params.intent
            else None
        )
        logger.debug(f"Generated intent embedding: {intent_embedding}")
        apps_with_scores = crud.search_apps(
            db_session,
            api_key_id,
            search_params.categories,
            intent_embedding,
            search_params.limit,
            search_params.offset,
        )
        # build apps list with similarity scores if they exist
        apps: list[AppPublic] = []
        for app, _ in apps_with_scores:
            app = AppPublic.model_validate(app)
            apps.append(app)

        return apps
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error getting apps with filter params: {search_params}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{app_name}", response_model=AppDetails)
async def get_app(
    app_name: str,
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
) -> AppDetails:
    """
    Returns an application (name, description, and functions).
    """
    try:
        db_app = crud.get_app_by_name(db_session, app_name)
        if not db_app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found.")

        if not db_app.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="App is currently disabled."
            )

        db_project = crud.get_project_by_api_key_id(db_session, api_key_id)
        # TODO: unify access control logic
        if (
            db_project.visibility_access == Visibility.PUBLIC
            and db_app.visibility != Visibility.PUBLIC
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this app.",
            )
        # filter functions by project visibility and enabled status
        # TODO: better way and place for this logic?
        db_functions = [
            function
            for function in db_app.functions
            if function.enabled
            and not (
                db_project.visibility_access == Visibility.PUBLIC
                and function.visibility != Visibility.PUBLIC
            )
        ]

        app_details: AppDetails = AppDetails(
            name=db_app.name,
            description=db_app.description,
            functions=[FunctionPublic.model_validate(function) for function in db_functions],
        )

        return app_details
    except HTTPException as e:
        raise e
    # TODO: is catching Exception here necessary?
    except Exception as e:
        logger.exception(f"Error getting app: {app_name}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
