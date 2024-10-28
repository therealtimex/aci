import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aipolabs.common.schemas.app_auth import SupportedAuthSchemes
from aipolabs.common.schemas.function import FunctionFileModel


# validation model for app file
# TODO: consolidate with model in app and abstract to a common module
class AppFileModel(BaseModel):
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
    functions: list[FunctionFileModel] = Field(..., min_length=1)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("name must be uppercase and contain only letters and underscores")
        return v


# TODO: remove app.id and function.id from the response?
class AppBasicPublic(BaseModel):
    name: str
    description: str
    similarity_score: float | None = None

    model_config = ConfigDict(from_attributes=True)
