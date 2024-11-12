from enum import Enum
from typing import Annotated
from uuid import UUID

import jsonschema
import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from aipolabs.common.db import crud, sql_models
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.function import (
    AnthropicFunctionDefinition,
    FunctionDefinitionPublic,
    FunctionExecution,
    FunctionExecutionResponse,
    FunctionPublic,
    HttpMetadata,
    OpenAIFunctionDefinition,
    Protocol,
)
from aipolabs.server import config
from aipolabs.server.dependencies import validate_api_key, yield_db_session

router = APIRouter()
logger = get_logger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


# TODO: convert app names to lowercase/uppercase (in crud or here) to avoid case sensitivity issues?
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


class FunctionExecutionParams(BaseModel):
    function_input: dict = Field(
        default_factory=dict, description="The input parameters for the function."
    )
    # TODO: can add other params like account_id


@router.get("/search", response_model=list[FunctionPublic])
async def search_functions(
    search_params: Annotated[FunctionSearchParams, Query()],
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
) -> list[sql_models.Function]:
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
            api_key_id,
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


# TODO: get list of functions by list of names
@router.get("/{function_name}", response_model=FunctionDefinitionPublic)
async def get_function(
    function_name: str,
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
) -> sql_models.Function:
    """
    Returns the full function data.
    """
    try:
        function = crud.get_function(db_session, api_key_id, function_name)
        if not function:
            logger.error(f"Function {function_name} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found.")
        return function
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error getting function for {function_name}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class InferenceProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# TODO: have "structured_outputs" flag ("structured_outputs_if_possible") to support openai's structured outputs function calling?
# which need "strict: true" and only support a subset of json schema and a bunch of other restrictions like "All fields must be required"
# If you turn on Structured Outputs by supplying strict: true and call the API with an unsupported JSON Schema, you will receive an error.
# TODO: client sdk can use pydantic to validate model output for parameters used for function execution
# TODO: "flatten" flag to make sure nested parameters are flattened?
@router.get(
    "/{function_name}/definition",
    response_model=OpenAIFunctionDefinition | AnthropicFunctionDefinition,
    response_model_exclude_none=True,  # having this to exclude "strict" field in openai's function definition if not set
)
async def get_function_definition(
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
    function_name: str,
    inference_provider: InferenceProvider = Query(
        default=InferenceProvider.OPENAI,
        description="The inference provider, which determines the format of the function definition.",
    ),
) -> sql_models.Function:
    """
    Return the function definition that can be used directly by LLM.
    The actual content depends on the intended model (inference provider, e.g., OpenAI, Anthropic, etc.) and the function itself.
    """
    try:
        function = crud.get_function(db_session, api_key_id, function_name)
        if not function:
            logger.error(f"Function {function_name} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found.")

        if inference_provider == InferenceProvider.OPENAI:
            function_definition = OpenAIFunctionDefinition(
                function={
                    "name": function.name,
                    "description": function.description,
                    "parameters": function.parameters,
                }
            )
        elif inference_provider == InferenceProvider.ANTHROPIC:
            function_definition = AnthropicFunctionDefinition(
                name=function.name,
                description=function.description,
                input_schema=function.parameters,
            )
        return function_definition
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Error getting function definition for {function_name}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/{function_name}/execute",
    response_model=FunctionExecutionResponse,
    response_model_exclude_none=True,
)
async def execute(
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
    function_name: str,
    function_execution_params: FunctionExecutionParams,
) -> FunctionExecutionResponse:
    try:
        # Fetch function definition
        db_function = crud.get_function(db_session, api_key_id, function_name)
        if not db_function:
            logger.error(f"Function {function_name} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found.")

        return _execute(
            FunctionExecution.model_validate(db_function), function_execution_params.function_input
        )

    except ValueError as e:
        logger.exception(f"Error executing function {function_name}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception:
        logger.exception(
            f"An unexpected error occurred during function execution for {function_name}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error."
        )


# TODO: allow local code execution override by using AppBase.execute() e.g.,:
# app_factory = AppFactory()
# app_instance: AppBase = app_factory.get_app_instance(function_name)
# app_instance.validate_input(db_function.parameters, function_execution_params.function_input)
# return app_instance.execute(function_name, function_execution_params.function_input)
def _execute(
    function_execution: FunctionExecution, function_input: dict
) -> FunctionExecutionResponse:
    try:
        jsonschema.validate(instance=function_input, schema=function_execution.parameters)
    except jsonschema.ValidationError as e:
        logger.error(f"Invalid input: {e.message}")
        raise ValueError(f"Invalid input: {e.message}") from e

    if function_execution.protocol == Protocol.REST:
        # Extract parameters by location
        path_params = function_input.get("path", {})
        query_params = function_input.get("query", {})
        headers = function_input.get("header", {})
        cookies = function_input.get("cookie", {})
        body = function_input.get("body", {})

        # TODO: validate protocol_data is of type HttpMetadata?
        protocol_data: HttpMetadata = function_execution.protocol_data
        # Construct URL with path parameters
        url = f"{protocol_data.server_url}{protocol_data.path}"
        if path_params:
            # Replace path parameters in URL
            for path_param_name, path_param_value in path_params.items():
                url = url.replace(f"{{{path_param_name}}}", str(path_param_value))

        # Create request object
        request = requests.Request(
            method=protocol_data.method,
            url=url,
            params=query_params if query_params else None,
            headers=headers if headers else None,
            cookies=cookies if cookies else None,
            json=body if body else None,
        )

        # Prepare the request to access its components
        prepared_request = request.prepare()

        # Dump the prepared request to JSON
        request_json = {
            "method": prepared_request.method,
            "url": prepared_request.url,
            "headers": dict(prepared_request.headers),
            "body": prepared_request.body.decode("utf-8") if prepared_request.body else None,
        }
        # execute request
        response = requests.Session().send(prepared_request)
        logger.info(f"Response: {response.json()}")

        # print request in nice format
        logger.info("======================== REQUEST ========================")
        logger.info(request_json)
        if response.status_code >= 400:
            return FunctionExecutionResponse(success=False, error=response.json())
        else:
            return FunctionExecutionResponse(success=True, data=response.json())
