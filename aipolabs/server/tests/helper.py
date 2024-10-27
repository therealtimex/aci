import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from aipolabs.common import sql_models
from aipolabs.common.schemas import AppFileModel, FunctionFileModel
from aipolabs.server.openai_service import OpenAIService

logger = logging.getLogger(__name__)
openai_service = OpenAIService()


# TODO: duplicate code with cli's upsert_app command
def create_dummy_apps(db_session: Session) -> list[sql_models.App]:
    # for each json file in the dummy_apps directory, create an app using cli's upsert_app command
    dummy_apps: list[sql_models.App] = []
    for file in Path("aipolabs/server/tests/routes/dummy_apps").glob("*.json"):
        logger.info(f"creating app and functionsfrom file: {file}")
        dummy_apps.append(insert_app(db_session, file))
    return dummy_apps


def insert_app(db_session: Session, app_file: Path) -> sql_models.App:
    """Upsert App and Functions to db from a json file."""
    # Parse files
    with open(app_file, "r") as f:
        app: AppFileModel = AppFileModel.model_validate(json.load(f))
        # make sure app and functions are upserted together
        db_app = insert_app_to_db(db_session, app)
        insert_functions_to_db(db_session, db_app, app)
        db_session.commit()

        return db_app


def insert_app_to_db(db_session: Session, app: AppFileModel) -> sql_models.App:
    logger.info(f"Upserting app: {app.name}...")
    if app.supported_auth_schemes is None:
        supported_auth_types = []
    else:
        supported_auth_types = [
            sql_models.App.AuthType(auth_type)
            for auth_type, auth_config in vars(app.supported_auth_schemes).items()
            if auth_config is not None
        ]

    db_app = sql_models.App(
        name=app.name,
        display_name=app.display_name,
        version=app.version,
        provider=app.provider,
        description=app.description,
        server_url=app.server_url,
        logo=app.logo,
        categories=app.categories,
        tags=app.tags,
        supported_auth_types=supported_auth_types,
        auth_configs=(
            app.supported_auth_schemes.model_dump(mode="json")
            if app.supported_auth_schemes is not None
            else None
        ),
        embedding=generate_app_embedding(app),
    )

    db_session.add(db_app)
    db_session.flush()

    return db_app


def insert_functions_to_db(db_session: Session, db_app: sql_models.App, app: AppFileModel) -> None:
    logger.info(f"Upserting functions for app: {db_app.name}...")

    for function in app.functions:
        db_function = sql_models.Function(
            name=function.name,
            description=function.description,
            parameters=function.parameters,
            app_id=db_app.id,
            response={},
            embedding=generate_function_embedding(function),
        )

        db_session.add(db_function)

    db_session.flush()


def generate_app_embedding(app: AppFileModel) -> list[float]:
    logger.debug(f"Generating embedding for app: {app.name}...")
    # generate app embeddings based on app config's name, display_name, provider, description, categories, and tags
    text_for_embedding = (
        f"{app.name}\n"
        f"{app.display_name}\n"
        f"{app.provider}\n"
        f"{app.description}\n"
        f"{' '.join(app.categories)}\n"
        f"{' '.join(app.tags)}"
    )
    return openai_service.generate_embedding(text_for_embedding)


def generate_function_embedding(function: FunctionFileModel) -> list[float]:
    logger.debug(f"Generating embedding for function: {function.name}...")
    text_for_embedding = f"{function.name}\n{function.description}\n{function.parameters}"

    return openai_service.generate_embedding(text_for_embedding)
