import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from aipolabs.common.enums import APIKeyStatus


class APIKeyPublic(BaseModel):
    id: UUID
    key: str
    agent_id: UUID
    status: APIKeyStatus

    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
