import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from aipolabs.common.db import sql_models


# TODO: should we hide api key and only show one it time when creating?
class APIKeyPublic(BaseModel):
    id: UUID
    key: str
    agent_id: UUID
    status: sql_models.APIKey.Status = sql_models.APIKey.Status.ACTIVE

    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
