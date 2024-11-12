from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aipolabs.common.db.sql_models import Protocol, Visibility


class HttpLocation(str, Enum):
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"
    BODY = "body"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpMetadata(BaseModel):
    method: HttpMethod
    path: str
    server_url: str


class GraphQLMetadata(BaseModel):
    pass


class FunctionCreate(BaseModel):
    name: str
    description: str
    tags: list[str]
    visibility: Visibility
    enabled: bool
    protocol: Protocol
    # TODO: validate protocol_data against protocol type
    protocol_data: HttpMetadata | GraphQLMetadata = Field(default_factory=dict)
    # TODO: deep validation on parameters, for example, must have "description", must specify "required" for each parameter
    parameters: dict = Field(default_factory=dict)
    response: dict = Field(default_factory=dict)

    # top level validation for parameters for REST protocol
    @model_validator(mode="after")
    def validate_parameters(self) -> "FunctionCreate":
        if self.protocol == Protocol.REST and self.parameters:
            # type must be "object"
            if self.parameters.get("type") != "object":
                raise ValueError("top level type must be 'object' for REST protocol's parameters")
            # properties must be a dict and can only have "path", "query", "header", "cookie", "body" keys
            properties = self.parameters["properties"]
            if not isinstance(properties, dict):
                raise ValueError("'properties' must be a dict for REST protocol's parameters")
            allowed_keys = [location.value for location in HttpLocation]
            for key in properties.keys():
                if key not in allowed_keys:
                    raise ValueError(
                        f"invalid key '{key}' for REST protocol's parameters's top level 'properties'"
                    )
            # required must be a list and can only have keys in "properties"
            required = self.parameters["required"]
            if not isinstance(required, list):
                raise ValueError("'required' must be a list for REST protocol's parameters")
            for key in required:
                if key not in properties:
                    raise ValueError(
                        f"key '{key}' in 'required' must be in 'properties' for REST protocol's parameters"
                    )
            # additionalProperties must be present and must be false
            if "additionalProperties" not in self.parameters or not isinstance(
                self.parameters["additionalProperties"], bool
            ):
                raise ValueError(
                    "'additionalProperties' must be present and must be a boolean for REST protocol's parameters"
                )
            if self.parameters["additionalProperties"]:
                raise ValueError(
                    "'additionalProperties' must be false for REST protocol's parameters"
                )
        return self

    # validate protocol_data against protocol type
    @model_validator(mode="after")
    def validate_metadata_by_protocol(self) -> "FunctionCreate":
        protocol_to_class = {Protocol.REST: HttpMetadata}

        expected_class = protocol_to_class[self.protocol]
        if not isinstance(self.protocol_data, expected_class):
            raise ValueError(
                f"Protocol '{self.protocol}' requires protocol_data of type {expected_class.__name__}, "
                f"but got {type(self.protocol_data).__name__}"
            )
        return self


class FunctionPublic(BaseModel):
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class FunctionDefinitionPublic(FunctionPublic):
    parameters: dict


class OpenAIFunctionDefinition(BaseModel):
    class OpenAIFunction(BaseModel):
        name: str
        strict: bool | None = None
        description: str
        parameters: dict

    type: Literal["function"] = "function"
    function: OpenAIFunction


class AnthropicFunctionDefinition(BaseModel):
    name: str
    description: str
    # equivalent to openai's parameters
    input_schema: dict


class FunctionExecution(BaseModel):
    """essential information for executing a function"""

    name: str
    protocol: Protocol
    protocol_data: HttpMetadata | GraphQLMetadata = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)
    response: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class FunctionExecutionResult(BaseModel):
    success: bool
    data: Any | None = None  # adding "| None" just for clarity
    error: str | None = None
