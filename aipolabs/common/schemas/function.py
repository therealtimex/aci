import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# TODO: validate against json schema
class FunctionCreate(BaseModel):
    name: str
    description: str
    # use empty dict for function definition that doesn't take any args (doesn't have parameters field)
    parameters: dict = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("name must be uppercase and contain only letters and underscores")
        return v


class FunctionBasicPublic(BaseModel):
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class FunctionPublic(BaseModel):
    name: str
    description: str
    parameters: dict

    model_config = ConfigDict(from_attributes=True)


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


class FunctionExecutionResponse(BaseModel):
    success: bool
    data: Any | None = None  # adding "| None" just for clarity
    error: str | None = None
