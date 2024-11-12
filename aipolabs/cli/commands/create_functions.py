import json
from pathlib import Path

import click

from aipolabs.cli import config
from aipolabs.common import embeddings, utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.function import FunctionCreate

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
    help="provide this flag to run the command and apply changes to the database",
)
def create_functions(functions_file: Path, skip_dry_run: bool) -> None:
    """Create Functions in db from file."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        with open(functions_file, "r") as f:
            functions: list[FunctionCreate] = [
                FunctionCreate.model_validate(function) for function in json.load(f)
            ]

        function_embeddings = embeddings.generate_function_embeddings(functions, openai_service)

        crud.create_functions(db_session, functions, function_embeddings)
        if not skip_dry_run:
            logger.info(f"provide --skip-dry-run to insert {len(functions)} functions")
            db_session.rollback()
        else:
            logger.info(f"committing insert of {len(functions)} functions")
            db_session.commit()
            logger.info("success!")
