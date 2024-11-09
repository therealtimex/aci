import re
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from aipolabs.common.db import sql_models
from aipolabs.common.logging import get_logger
from aipolabs.common.schemas.app_auth import (
    ApiKeyAuthScheme,
    HttpBasicAuthScheme,
    HttpBearerAuthScheme,
    OAuth2AuthScheme,
    OpenIDAuthScheme,
)

logger = get_logger(__name__)


class AppCreate(BaseModel):
    """Used to load app data for app creation or overwrite existing app."""

    name: str
    display_name: str
    provider: str
    description: str
    server_url: str
    logo: str | None = None
    categories: list[str]
    supported_auth_types: list[sql_models.App.AuthType]
    auth_configs: dict[sql_models.App.AuthType, Any]
    version: str
    visibility: sql_models.Visibility = sql_models.Visibility.PRIVATE
    enabled: bool = True

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v) or "__" in v:
            raise ValueError(
                "name must be uppercase, contain only letters and underscores, and not have consecutive underscores"
            )
        return v

    # key in auth_configs must be in supported_auth_types
    @field_validator("auth_configs")
    def validate_auth_configs(
        cls,
        v: dict[sql_models.App.AuthType, Any],
        info: ValidationInfo,  # Use ValidationInfo to access other fields
    ) -> dict[sql_models.App.AuthType, Any]:

        if set(v.keys()) != set(info.data["supported_auth_types"]):
            raise ValueError(
                f"auth_configs must be a dict with keys in supported_auth_types: {info.data['supported_auth_types']}"
            )

        # Validate each auth_config value against its schema
        for auth_type, config in v.items():
            if auth_type == sql_models.App.AuthType.API_KEY:
                ApiKeyAuthScheme.model_validate(config)
            elif auth_type == sql_models.App.AuthType.HTTP_BASIC:
                HttpBasicAuthScheme.model_validate(config)
            elif auth_type == sql_models.App.AuthType.HTTP_BEARER:
                HttpBearerAuthScheme.model_validate(config)
            elif auth_type == sql_models.App.AuthType.OAUTH2:
                OAuth2AuthScheme.model_validate(config)
            elif auth_type == sql_models.App.AuthType.OPEN_ID:
                OpenIDAuthScheme.model_validate(config)
            else:
                raise ValueError(f"Unsupported auth type: {auth_type}")
        return v

    # enables the model to be initialized with attributes from a SQLAlchemy object.
    model_config = ConfigDict(from_attributes=True)


class AppBasicPublic(BaseModel):
    name: str
    description: str
    similarity_score: float | None = None

    model_config = ConfigDict(from_attributes=True)
