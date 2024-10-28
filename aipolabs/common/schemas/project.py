import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from aipolabs.common.schemas.agent import AgentPublic


class ProjectCreate(BaseModel):
    name: str
    owner_organization_id: UUID | None = None


class ProjectPublic(BaseModel):
    id: UUID
    name: str
    owner_user_id: UUID | None = None
    owner_organization_id: UUID | None = None
    daily_quota_used: int
    daily_quota_reset_at: datetime.datetime
    total_quota_used: int

    created_at: datetime.datetime
    updated_at: datetime.datetime

    agents: list[AgentPublic]

    model_config = ConfigDict(from_attributes=True)
