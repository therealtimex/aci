import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from aipolabs.common import sql_models

# TODO: add Field to validate fields like str length as defined in database models


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# TODO: should we hide api key and only show one it time when creating?
class APIKeyPublic(BaseModel):
    id: UUID
    key: str
    agent_id: UUID
    status: sql_models.APIKey.Status = sql_models.APIKey.Status.ACTIVE

    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str
    owner_organization_id: UUID | None = None


class ProjectPublic(BaseModel):
    id: UUID
    name: str
    owner_user_id: UUID | None = None
    owner_organization_id: UUID | None = None
    plan: sql_models.Project.Plan
    daily_quota_used: int
    daily_quota_reset_at: datetime.datetime
    total_quota_used: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

    agents: list["AgentPublic"]

    model_config = ConfigDict(from_attributes=True)


class AgentCreate(BaseModel):
    name: str
    description: str
    excluded_apps: list[UUID] = []
    excluded_functions: list[UUID] = []


class AgentPublic(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    description: str
    excluded_apps: list[UUID] = []
    excluded_functions: list[UUID] = []
    created_by: UUID

    created_at: datetime.datetime
    updated_at: datetime.datetime

    api_keys: list["APIKeyPublic"]

    model_config = ConfigDict(from_attributes=True)


# TODO: remove app.id and function.id from the response?
class AppBasicPublic(BaseModel):
    name: str
    description: str
    similarity_score: float | None = None

    model_config = ConfigDict(from_attributes=True)


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


# TODO: data could be None even if success is True?
class FunctionExecutionResponse(BaseModel):
    success: bool
    data: Any | None = None  # adding "| None" just for clarity
    error: str | None = None
