from pathlib import Path

import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.app import AppCreate
from aipolabs.common.schemas.function import FunctionCreate

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
@click.option(
    "--skip-dry-run",
    is_flag=True,
    help="provide this flag to run the command and apply changes to the database",
)
def upsert_app_and_functions(app_file: Path, functions_file: Path, skip_dry_run: bool) -> None:
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            app_create, app_embedding = utils.generate_app_from_file(app_file, openai_service)
            functions, function_embeddings = utils.generate_functions_from_file(
                functions_file, openai_service
            )
            db_app = crud.get_app_by_name(db_session, app_create.name)

            _validate(functions, app_create)

            # upsert app
            if not skip_dry_run:
                if db_app:
                    logger.info(
                        f"App {app_create.name} already exists, \n {AppCreate.model_validate(db_app).model_dump_json(indent=2, exclude_none=True)} \n provide --skip-dry-run to update existing app with data \n {app_create.model_dump_json(indent=2, exclude_none=True)}"
                    )
                else:
                    logger.info(
                        f"App {app_create.name} does not exist, provide --skip-dry-run to insert new app with data \n{app_create.model_dump_json(indent=2, exclude_none=True)}"
                    )
                for function in functions:
                    db_function = crud.get_function_by_name(db_session, function.name)
                    if db_function:
                        logger.info(
                            f"Function {function.name} already exists, will update. Provide --skip-dry-run to proceed."
                        )
                    else:
                        logger.info(
                            f"Function {function.name} does not exist, will insert. Provide --skip-dry-run to proceed."
                        )
            else:
                logger.info(
                    f"{'updating existing' if db_app else 'inserting new'} app: {app_create.name}"
                )
                db_app = crud.upsert_app(db_session, app_create, app_embedding)

                logger.info(f"Upserting {len(functions)} functions for app: {db_app.name}")
                crud.upsert_functions(db_session, functions, function_embeddings, db_app.id)

                db_session.commit()
                logger.info("success!")

        except Exception:
            logger.exception("Error upserting app and functions")


def _validate(functions: list[FunctionCreate], app_create: AppCreate) -> None:
    # each function name must be unique
    if len(functions) != len(set(function.name for function in functions)):
        raise ValueError("Function names must be unique")

    # all functions must belong to the same app
    app_names = set(
        [utils.parse_app_name_from_function_name(function.name) for function in functions]
    )
    if len(app_names) != 1:
        raise ValueError("All functions must belong to the same app")
    app_name = app_names.pop()

    # functions must belong to the app provided in the app file
    if app_name != app_create.name:
        raise ValueError("functions and app doesn't match")
