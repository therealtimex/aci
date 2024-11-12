import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aipolabs.common.db.sql_models import SecuritySchemeType, Visibility


# TODO: move to common utils, and solve circular import in utils
def snake_to_camel(string: str) -> str:
    """Convert a snake case string to a camel case string."""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class AppCreate(BaseModel):
    name: str
    display_name: str
    provider: str
    version: str
    description: str
    logo: str
    categories: list[str]
    visibility: Visibility
    enabled: bool
    # TODO: consider making schema for each security scheme instead of using dict
    security_schemes: dict[SecuritySchemeType, dict] = Field(default_factory=dict)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v) or "__" in v:
            raise ValueError(
                "name must be uppercase, contain only letters and underscores, and not have consecutive underscores"
            )
        return v


class AppBasicPublic(BaseModel):
    name: str
    description: str
    similarity_score: float | None = None

    model_config = ConfigDict(from_attributes=True)
