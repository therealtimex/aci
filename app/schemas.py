import datetime
import uuid

from pydantic import BaseModel, ConfigDict

from database import models


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


"""User models"""


class APIKeyBase(BaseModel):
    key: str
    agent_id: uuid.UUID
    status: models.APIKey.Status = models.APIKey.Status.ACTIVE


class APIKeyCreate(APIKeyBase):
    pass


# TODO: should we hide api key and only show one it time when creating?
class APIKeyPublic(APIKeyBase):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str
    owner_organization_id: uuid.UUID | None


class ProjectPublic(BaseModel):
    id: uuid.UUID
    name: str
    owner_user_id: uuid.UUID | None
    owner_organization_id: uuid.UUID | None
    plan: models.Project.Plan
    daily_quota_used: int
    daily_quota_reset_at: datetime.datetime
    total_quota_used: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

    agents: list["AgentPublic"]

    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    project_id: uuid.UUID
    name: str
    description: str
    excluded_apps: list[uuid.UUID] = []
    excluded_functions: list[uuid.UUID] = []
    created_by: uuid.UUID


class AgentCreate(AgentBase):
    pass


class AgentPublic(AgentBase):
    id: uuid.UUID

    created_at: datetime.datetime
    updated_at: datetime.datetime

    api_keys: list["APIKeyPublic"]

    model_config = ConfigDict(from_attributes=True)
