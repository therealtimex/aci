from pathlib import Path

import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService

logger = get_logger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


@click.command()
@click.option(
    "--app-file",
    "app_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the app json file",
)
@click.option(
    "--functions-file",
    "functions_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the function json file",
)
def upsert_app_and_functions(app_file: Path, functions_file: Path) -> None:
    """Upsert App and Functions to db from files."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            app, app_embedding, functions, function_embeddings = (
                utils.generate_app_and_functions_from_files(
                    app_file, functions_file, openai_service
                )
            )

            # make sure app and functions are upserted in one transaction
            logger.info(f"Upserting app: {app.name}...")
            db_app = crud.upsert_app(db_session, app, app_embedding)

            logger.info(f"Upserting functions for app: {app.name}...")
            crud.upsert_functions(db_session, functions, function_embeddings, db_app.id)

            db_session.commit()

        except Exception as e:
            db_session.rollback()
            logger.error(f"Error upserting app and functions: {e}")
