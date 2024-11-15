from enum import Enum
from typing import Annotated, Any
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
    FunctionExecution,
    FunctionExecutionResult,
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
        logger.debug(f"Getting functions with params: {search_params}")
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


class InferenceProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# TODO: have "structured_outputs" flag ("structured_outputs_if_possible") to support openai's structured outputs function calling?
# which need "strict: true" and only support a subset of json schema and a bunch of other restrictions like "All fields must be required"
# If you turn on Structured Outputs by supplying strict: true and call the API with an unsupported JSON Schema, you will receive an error.
# TODO: client sdk can use pydantic to validate model output for parameters used for function execution
# TODO: "flatten" flag to make sure nested parameters are flattened?
@router.get(
    "/{function_name}",
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
    response_model=FunctionExecutionResult,
    response_model_exclude_none=True,
)
async def execute(
    db_session: Annotated[Session, Depends(yield_db_session)],
    api_key_id: Annotated[UUID, Depends(validate_api_key)],
    function_name: str,
    function_execution_params: FunctionExecutionParams,
) -> FunctionExecutionResult:
    try:
        # Fetch function definition
        db_function = crud.get_function(db_session, api_key_id, function_name)
        if not db_function:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Function not found.")

        return _execute(
            db_function.app,
            FunctionExecution.model_validate(db_function),
            function_execution_params.function_input,
        )

    except ValueError as e:
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
    db_app: sql_models.App, function_execution: FunctionExecution, function_input: dict
) -> FunctionExecutionResult:
    try:
        logger.info(f"validating function input for {function_execution.name}")
        jsonschema.validate(instance=function_input, schema=function_execution.parameters)
    except jsonschema.ValidationError as e:
        logger.error(f"Invalid input: {e.message}")
        raise ValueError(f"Invalid input: {e.message}") from e
    if function_execution.protocol == Protocol.REST:
        # remove None values from the input
        # TODO: better way to remove None values? and if it's ok to remove all of them?
        function_input = _remove_none_values(function_input)
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

        # get default api key and header name for the app
        default_api_key_data = _get_default_api_key_and_header_name(db_app)
        if default_api_key_data:
            headers[default_api_key_data[1]] = default_api_key_data[0]
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
        # TODO: remove logging
        logger.info(
            "======================== FUNCTION EXECUTION HTTP REQUEST ========================"
        )
        logger.info(
            f"method: {prepared_request.method}, url: {prepared_request.url}, headers: {prepared_request.headers}, body: {prepared_request.body}"
        )
        # execute request
        response = requests.Session().send(prepared_request)
        # try to parse response as json, if failed, use the raw response content
        try:
            response_data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            # TODO: can this fail?
            response_data = _get_response_data(response)
            logger.error(f"Raw response content: {response_data}")

        if response.status_code >= 400:
            logger.error(
                f"Function execution failed for {function_execution.name}, response: {response_data}"
            )
            return FunctionExecutionResult(success=False, error=response_data)
        else:
            logger.info(
                f"Function execution succeeded for {function_execution.name}, response: {response_data}"
            )
            return FunctionExecutionResult(success=True, data=response_data)


# get the default api key and header name for an app if exists, for example
# "api_key": {
#   "in": "header",
#   "name": "X-Subscription-Token",
#   "default": ["BSAnf8MFuERsHzyYzNPjOdX5lFc9zXv"]
# },
# and put it in the header of the request
# TODO: the right way for auth is to get from the connected account first (need app & project integration),
# and if not found, then use the app's default
def _get_default_api_key_and_header_name(db_app: sql_models.App) -> tuple[str, str] | None:
    if (
        db_app.security_schemes
        and "api_key" in db_app.security_schemes
        and db_app.security_schemes["api_key"]["default"]
    ):
        return (
            db_app.security_schemes["api_key"]["default"][0],
            db_app.security_schemes["api_key"]["name"],
        )
    return None


def _remove_none_values(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _remove_none_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [_remove_none_values(item) for item in data if item is not None]
    else:
        return data


def _get_response_data(response: requests.Response) -> Any:
    response_data: Any = None
    try:
        if response.content:
            response_data = response.content.decode("utf-8", errors="replace")
    except Exception as e:
        logger.error(f"Failed to decode response content: {str(e)}")
        response_data = "Invalid response content"

    return response_data
