import re

from pydantic import BaseModel, Field, field_validator

from aipolabs.cli.models import auth


# TODO: validate against json schema
class FunctionModel(BaseModel):
    name: str
    description: str
    parameters: dict = Field(default_factory=dict)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("name must be uppercase and contain only letters and underscores")
        return v


# validation model for app file
# TODO: consolidate with model in app and abstract to a common module
class AppModel(BaseModel):
    name: str
    display_name: str
    version: str
    provider: str
    description: str
    server_url: str
    logo: str | None = None
    categories: list[str]
    tags: list[str]
    supported_auth_schemes: auth.SupportedAuthSchemes | None = None
    functions: list[FunctionModel] = Field(..., min_items=1)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("name must be uppercase and contain only letters and underscores")
        return v
