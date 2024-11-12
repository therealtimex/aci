import json
from pathlib import Path

import click

from aipolabs.cli import config
from aipolabs.common import embeddings, utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.app import AppCreate

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
    "--skip-dry-run",
    is_flag=True,
    help="provide this flag to run the command and apply changes to the database",
)
def create_app(app_file: Path, skip_dry_run: bool) -> None:
    """Create App in db from file."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        with open(app_file, "r") as f:
            app: AppCreate = AppCreate.model_validate(json.load(f))
            app_embedding = embeddings.generate_app_embedding(app, openai_service)

        db_app = crud.create_app(db_session, app, app_embedding)
        if not skip_dry_run:
            logger.info(
                f"provide --skip-dry-run to insert new app {db_app.name} with app data \n{app.model_dump_json(indent=2)}"
            )
            db_session.rollback()
        else:
            logger.info(f"committing insert of new app: {db_app.name}")
            db_session.commit()
            logger.info("success!")
