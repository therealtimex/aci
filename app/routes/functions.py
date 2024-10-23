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

router = APIRouter()
logger = get_logger(__name__)
openai_service = OpenAIService()


# TODO: convert app names to lowercase (in crud or here) to avoid case sensitivity issues?
# TODO: add flag (e.g., verbose=true) to include detailed function info? (e.g., dev portal will need this)
class FunctionSearchParams(BaseModel):
    app_names: list[str] | None = Field(
        default=None, description="List of app names for filtering functions."
    )
    intent: str | None = Field(
        default=None,
        description="Natural language intent for vector similarity sorting. Results will be sorted by relevance to the intent.",
    )
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of Apps per response."
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset.")

    # need this in case user set {"app_names": None} which will translate to [''] in the params
    # TODO: convert to uppercase?
    @field_validator("app_names")
    def validate_app_names(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            # Remove any empty strings from the list
            v = [app_name for app_name in v if app_name.strip()]
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


@router.get("/search", response_model=list[schemas.FunctionBasicPublic])
async def search_functions(
    search_params: Annotated[FunctionSearchParams, Query()],
    db_session: Session = Depends(get_db_session),
) -> list[models.Function]:
    """
    Returns the basic information of a list of functions.
    """
    try:
        logger.info(f"Getting functions with params: {search_params}")
        intent_embedding = (
            openai_service.generate_embedding(search_params.intent)
            if search_params.intent
            else None
        )
        logger.debug(f"Generated intent embedding: {intent_embedding}")
        functions = crud.search_functions(
            db_session,
            search_params.app_names,
            intent_embedding,
            search_params.limit,
            search_params.offset,
        )
        logger.debug(f"functions: \n {functions}")
        return functions
    except Exception as e:
        logger.error("Error searching functions", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{function_name}", response_model=schemas.FunctionPublic)
async def get_function(
    function_name: str,
    db_session: Session = Depends(get_db_session),
) -> models.Function:
    """
    Returns the full function signature to be used for LLM function call.
    """
    try:
        function = crud.get_function(db_session, function_name)
        if not function:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found.")
        return function
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# @router.post("/{function_id}/execute", response_model=FunctionExecutionResponse)
# async def execute_function(
#     function_id: UUID = Path(..., description="Unique identifier of the function."),
#     request: FunctionExecutionRequest = None,
#     api_key: str = Depends(get_api_key),
# ):
#     """
#     Executes the function and returns the execution result.
#     """
#     try:
#         function_signature = get_function_signature_data(function_id)
#         if not function_signature:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found.")

#         parameters = request.parameters

#         # Validate required parameters
#         missing_params = [
#             param.name for param in function_signature.parameters
#             if param.required and param.name not in parameters
#         ]
#         if missing_params:
#             return FunctionExecutionResponse(
#                 success=False,
#                 error=f"Missing required parameters: {', '.join(missing_params)}"
#             )

#         # Simulate function execution
#         if function_signature.name == "resizeImage":
#             # Simulate a successful execution
#             return FunctionExecutionResponse(
#                 success=True,
#                 result={"outputPath": "/path/to/resized_image.jpg"}
#             )
#         else:
#             # Function execution not implemented
#             return FunctionExecutionResponse(
#                 success=False,
#                 error="Function execution not implemented."
#             )

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
