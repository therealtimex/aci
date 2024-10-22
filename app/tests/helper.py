import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.openai_service import OpenAIService
from database import models

# TODO: move log setup to conftest
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
openai_service = OpenAIService()


# TODO: duplicate code with cli's upsert_app command (to avoid dependency on cli module)
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


class SupportedAuthSchemes(BaseModel):
    api_key: ApiKeyAuthScheme | None = None
    http_basic: HttpBasicAuthScheme | None = None
    http_bearer: HttpBearerAuthScheme | None = None
    oauth2: OAuth2AuthScheme | None = None
    open_id: OpenIDAuthScheme | None = None


class FunctionModel(BaseModel):
    name: str
    description: str
    parameters: dict


# validation model for app file
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
    supported_auth_schemes: SupportedAuthSchemes | None = None
    functions: list[FunctionModel] = Field(..., min_length=1)


# TODO: duplicate code with cli's upsert_app command
def create_dummy_apps(db_session: Session) -> list[models.App]:
    # for each json file in the dummy_apps directory, create an app using cli's upsert_app command
    dummy_apps: list[models.App] = []
    for file in Path("app/tests/routes/dummy_apps").glob("*.json"):
        logger.info(f"creating app and functionsfrom file: {file}")
        dummy_apps.append(insert_app(db_session, file))
    return dummy_apps


def insert_app(db_session: Session, app_file: Path) -> models.App:
    """Upsert App and Functions to db from a json file."""
    # Parse files
    with open(app_file, "r") as f:
        app_model: AppModel = AppModel.model_validate(json.load(f))
        # make sure app and functions are upserted together
        db_app = insert_app_to_db(db_session, app_model)
        insert_functions_to_db(db_session, db_app, app_model)
        db_session.commit()

        return db_app


def insert_app_to_db(db_session: Session, app_model: AppModel) -> models.App:
    logger.info(f"Upserting app: {app_model.name}...")
    if app_model.supported_auth_schemes is None:
        supported_auth_types = []
    else:
        supported_auth_types = [
            models.App.AuthType(auth_type)
            for auth_type, auth_config in vars(app_model.supported_auth_schemes).items()
            if auth_config is not None
        ]

    db_app = models.App(
        name=app_model.name,
        display_name=app_model.display_name,
        version=app_model.version,
        provider=app_model.provider,
        description=app_model.description,
        server_url=app_model.server_url,
        logo=app_model.logo,
        categories=app_model.categories,
        tags=app_model.tags,
        supported_auth_types=supported_auth_types,
        auth_configs=(
            app_model.supported_auth_schemes.model_dump(mode="json")
            if app_model.supported_auth_schemes is not None
            else None
        ),
        embedding=generate_app_embedding(app_model),
    )

    db_session.add(db_app)
    db_session.flush()

    return db_app


def insert_functions_to_db(db_session: Session, db_app: models.App, app_model: AppModel) -> None:
    logger.info(f"Upserting functions for app: {db_app.name}...")

    for function in app_model.functions:
        db_function = models.Function(
            name=function.name,
            description=function.description,
            parameters=function.parameters,
            app_id=db_app.id,
            response={},
            embedding=generate_function_embedding(function),
        )

        db_session.add(db_function)

    db_session.flush()


def generate_app_embedding(app_model: AppModel) -> list[float]:
    logger.info(f"Generating embedding for app: {app_model.name}...")
    # generate app embeddings based on app config's name, display_name, provider, description, categories, and tags
    text_for_embedding = (
        f"{app_model.name}\n"
        f"{app_model.display_name}\n"
        f"{app_model.provider}\n"
        f"{app_model.description}\n"
        f"{' '.join(app_model.categories)}\n"
        f"{' '.join(app_model.tags)}"
    )
    return openai_service.generate_embedding(text_for_embedding)


def generate_function_embedding(function: FunctionModel) -> list[float]:
    logger.info(f"Generating embedding for function: {function.name}...")
    text_for_embedding = f"{function.name}\n{function.description}\n{function.parameters}"

    return openai_service.generate_embedding(text_for_embedding)
