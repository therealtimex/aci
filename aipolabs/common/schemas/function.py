from enum import Enum
from typing import Any, Literal

import jsonschema as js
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
    parameters: dict = Field(default_factory=dict)
    response: dict = Field(default_factory=dict)

    # validate parameters json schema
    # TODO: validate parameters must have "description"
    @model_validator(mode="after")
    def validate_parameters(self) -> "FunctionCreate":
        # Validate that parameters schema itself is a valid JSON Schema
        try:
            js.validate(instance=self.parameters, schema=js.Draft7Validator.META_SCHEMA)
        except Exception as e:
            raise ValueError(f"Invalid JSON Schema: {str(e)}")
        # validate parameters for REST protocol
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
            # required must be present and must be a list and can only have keys in "properties"
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

        def validate_object_level(schema: dict, path: str) -> None:
            # Skip if not an object type schema
            if not isinstance(schema, dict) or schema.get("type") != "object":
                return

            # Ensure required field exists
            if "required" not in schema:
                raise ValueError(f"Missing 'required' field at {path}")

            # Ensure visible field exists
            if "visible" not in schema:
                raise ValueError(f"Missing 'visible' field at {path}")

            properties = schema.get("properties", {})
            required = schema.get("required", [])
            visible = schema.get("visible", [])

            # Check that all required properties actually exist
            for prop in required:
                if prop not in properties:
                    raise ValueError(
                        f"Required property '{prop}' at {path} not found in properties"
                    )

            # Check that all visible properties actually exist
            for prop in visible:
                if prop not in properties:
                    raise ValueError(f"Visible property '{prop}' at {path} not found in properties")

            # Check that non-visible properties have defaults (except for objects)
            for prop_name, prop_schema in properties.items():
                if prop_name not in visible:
                    is_object = prop_schema.get("type") == "object"
                    if not is_object and "default" not in prop_schema:
                        raise ValueError(
                            f"Non-visible property '{prop_name}' at {path} must have a default value"
                        )

            # Recursively validate nested objects
            for prop_name, prop_schema in properties.items():
                if isinstance(prop_schema, dict) and prop_schema.get("type") == "object":
                    validate_object_level(prop_schema, f"{path}/{prop_name}")

                    # Check if parent should be visible based on children
                    child_visible = prop_schema.get("visible", [])
                    if not child_visible and prop_name in visible:
                        raise ValueError(
                            f"Property '{prop_name}' at {path} cannot be visible when all its children are non-visible"
                        )

        validate_object_level(self.parameters, "parameters")

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
