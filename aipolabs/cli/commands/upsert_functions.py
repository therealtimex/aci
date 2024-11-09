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
    "--functions-file",
    "functions_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the function json file",
)
@click.option(
    "--skip-dry-run",
    is_flag=True,
    help="provide this flag to run the command and make changes to the system",
)
def upsert_functions(functions_file: Path, skip_dry_run: bool) -> None:
    """Upsert Functions to db from file."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            functions, function_embeddings = utils.generate_functions_from_file(
                functions_file, openai_service
            )

            app_names = set(
                [utils.parse_app_name_from_function_name(function.name) for function in functions]
            )
            if len(app_names) != 1:
                raise ValueError("All functions must belong to the same app")
            app_name = app_names.pop()

            db_app = crud.get_app_by_name(db_session, app_name)
            if not db_app:
                raise ValueError(f"App {app_name} does not exist")

            if not skip_dry_run:
                # for each function, check if it already exists, if exists, log "function already exists, will update", if not, log "function does not exist, will insert"
                for function in functions:
                    db_function = crud.get_function_by_name(db_session, function.name)
                    if db_function:
                        logger.warning(
                            f"Function {function.name} already exists, will update, provide --skip-dry-run to proceed"
                        )
                    else:
                        logger.info(
                            f"Function {function.name} does not exist, will insert, provide --skip-dry-run to proceed"
                        )
            else:
                logger.info(f"Upserting {len(functions)} functions for app: {app_name}")
                crud.upsert_functions(db_session, functions, function_embeddings, db_app.id)
                db_session.commit()
                logger.info("success!")
        except Exception:
            db_session.rollback()
            logger.exception("Error upserting functions")
