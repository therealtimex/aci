from pydantic import BaseModel

from aipolabs.common.db.sql_models import Plan


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    auth_provider: str
    auth_user_id: str
    name: str
    email: str
    profile_picture: str | None = None
    plan: Plan = Plan.FREE
