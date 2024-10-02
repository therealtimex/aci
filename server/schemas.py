from pydantic import BaseModel
import uuid
from . import db


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
    organization_role: db.User.OrgRole

    class Config:
        from_attributes = True
