import re

from pydantic import BaseModel, ConfigDict, field_validator

from aipolabs.common.schemas.app_auth import SupportedAuthSchemes


class AppCreate(BaseModel):
    """Used to load and validate app data from a file."""

    name: str
    display_name: str
    version: str
    provider: str
    description: str
    server_url: str
    logo: str | None = None
    categories: list[str]
    tags: list[str]
    supported_auth_schemes: SupportedAuthSchemes | None = None

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("name must be uppercase and contain only letters and underscores")
        return v


class AppBasicPublic(BaseModel):
    name: str
    description: str
    similarity_score: float | None = None

    model_config = ConfigDict(from_attributes=True)
