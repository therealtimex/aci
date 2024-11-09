from pathlib import Path

import click

from aipolabs.cli import config
from aipolabs.common import utils
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
    help="provide this flag to run the command and make changes to the system",
)
def upsert_app(app_file: Path, skip_dry_run: bool) -> None:
    """Upsert App to db from file."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            app_create, app_embedding = utils.generate_app_from_file(app_file, openai_service)
            db_app = crud.get_app_by_name(db_session, app_create.name)

            if not skip_dry_run:
                if db_app:
                    logger.warning(
                        f"App {app_create.name} already exists, \n {AppCreate.model_validate(db_app).model_dump_json(indent=2, exclude_none=True)} \n provide --skip-dry-run to update existing app with data \n {app_create.model_dump_json(indent=2, exclude_none=True)}"
                    )
                else:
                    logger.info(
                        f"App {app_create.name} does not exist, provide --skip-dry-run to insert new app with data \n{app_create.model_dump_json(indent=2, exclude_none=True)}"
                    )
            else:
                if db_app:
                    logger.info(f"updating existing app: {app_create.name}")
                else:
                    logger.info(f"inserting new app: {app_create.name}")

                crud.upsert_app(db_session, app_create, app_embedding)
                db_session.commit()
                logger.info("success!")

        except Exception:
            db_session.rollback()
            logger.exception("Error upserting app")
