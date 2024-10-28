import logging
from pathlib import Path

from sqlalchemy.orm import Session

from aipolabs.common import utils
from aipolabs.common.db import crud, sql_models
from aipolabs.common.openai_service import OpenAIService
from aipolabs.server import config

logger = logging.getLogger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


def create_dummy_apps_and_functions(db_session: Session) -> list[sql_models.App]:
    dummy_apps: list[sql_models.App] = []
    # for app.json and functions.json in each dummy_apps directory, create an app and functions
    dummy_apps_dir = Path(__file__).parent / "routes/dummy_apps"
    for app_dir in dummy_apps_dir.glob("*"):
        app_file = app_dir / "app.json"
        functions_file = app_dir / "functions.json"
        logger.info(f"app_file: {app_file}, functions_file: {functions_file}")
        dummy_apps.append(_upsert_app_and_functions(db_session, app_file, functions_file))
    return dummy_apps


def _upsert_app_and_functions(
    db_session: Session, app_file: Path, functions_file: Path
) -> sql_models.App:
    """Upsert App and Functions to db from a json file."""
    app, app_embedding, functions, function_embeddings = (
        utils.generate_app_and_functions_from_files(app_file, functions_file, openai_service)
    )

    # make sure app and functions are upserted in one transaction
    logger.info(f"Upserting app: {app.name}...")
    db_app = crud.upsert_app(db_session, app, app_embedding)

    logger.info(f"Upserting functions for app: {app.name}...")
    crud.upsert_functions(db_session, functions, function_embeddings, db_app.id)

    db_session.commit()

    return db_app
