from enum import Enum
from typing import Any, Literal

import jsonschema
from pydantic import BaseModel, ConfigDict, Field, model_validator

from aipolabs.common.db.sql_models import Protocol, Visibility
from aipolabs.common.validators.function import (
    validate_function_parameters_schema_common,
    validate_function_parameters_schema_rest_protocol,
)


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
    protocol_data: HttpMetadata | GraphQLMetadata = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)
    response: dict = Field(default_factory=dict)

    # validate parameters json schema
    @model_validator(mode="after")
    def validate_parameters(self) -> "FunctionCreate":

        # Validate that parameters schema itself is a valid JSON Schema
        jsonschema.validate(instance=self.parameters, schema=jsonschema.Draft7Validator.META_SCHEMA)

        # common validation
        validate_function_parameters_schema_common(self.parameters, f"{self.name}.parameters")

        # specific validation per protocol
        if self.protocol == Protocol.REST:
            validate_function_parameters_schema_rest_protocol(
                self.parameters,
                f"{self.name}.parameters",
                [location.value for location in HttpLocation],
            )
        else:
            pass

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


class FunctionVerbosePublic(FunctionPublic):
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
