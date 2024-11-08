import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from aipolabs.common.db import sql_models


class APIKeyPublic(BaseModel):
    id: UUID
    key: str
    agent_id: UUID
    status: sql_models.APIKey.Status

    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
