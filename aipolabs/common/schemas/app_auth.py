from pydantic import BaseModel


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
