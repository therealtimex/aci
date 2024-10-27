import re

from pydantic import BaseModel, Field, field_validator


class AdditionalParameter(BaseModel):
    name: str
    required: bool


class ApiKeyAuthScheme(BaseModel):
    parameter_name: str
    location: str


class HttpBasicAuthScheme(BaseModel):
    username: str
    password: str


class HttpBearerAuthScheme(BaseModel):
    header_name: str
    token_prefix: str


class OAuth2AuthScheme(BaseModel):
    authorization_url: str
    token_url: str
    refresh_url: str
    default_scopes: list[str]
    available_scopes: list[str]
    client_id: str
    client_secret: str
    additional_parameters: list[AdditionalParameter]


class OpenIDAuthScheme(BaseModel):
    issuer_url: str
    client_id: str
    client_secret: str
    default_scopes: list[str]
    additional_scopes: list[str]
    additional_parameters: list[AdditionalParameter]


# TODO: consider using App.AuthType enum for field names?
class SupportedAuthSchemes(BaseModel):
    api_key: ApiKeyAuthScheme | None = None
    http_basic: HttpBasicAuthScheme | None = None
    http_bearer: HttpBearerAuthScheme | None = None
    oauth2: OAuth2AuthScheme | None = None
    open_id: OpenIDAuthScheme | None = None


# TODO: validate against json schema
class FunctionFileModel(BaseModel):
    name: str
    description: str
    # use empty dict for function definition that doesn't take any args (doesn't have parameters field)
    parameters: dict = Field(default_factory=dict)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Z_]+$", v):
            raise ValueError("name must be uppercase and contain only letters and underscores")
        return v


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
