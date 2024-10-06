from pydantic import BaseModel
import uuid
from .database import models
import datetime
from pydantic import ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# User models
class UserBase(BaseModel):
    auth_provider: str
    auth_user_id: str
    name: str
    email: str | None = None
    profile_picture: str | None = None


class UserCreate(UserBase):
    pass


# TODO: check UUID behavtior in response
class User(UserBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    organization_role: models.User.OrgRole
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyBase(BaseModel):
    project_id: uuid.UUID
    creator_id: uuid.UUID
    status: models.APIKey.Status = models.APIKey.Status.ACTIVE
    plan: models.APIKey.Plan


class APIKeyCreate(APIKeyBase):
    pass


# TODO: should we hide api key and only show one it time when creating?
class APIKey(APIKeyBase):
    id: uuid.UUID
    key: str
    daily_quota_used: int
    daily_quota_reset_at: datetime.datetime
    total_quota_used: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    api_keys: list[APIKey]

    model_config = ConfigDict(from_attributes=True)
