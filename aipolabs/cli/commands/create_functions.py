import json
from pathlib import Path
from uuid import UUID

import click

from aipolabs.cli import config
from aipolabs.common import embeddings, utils
from aipolabs.common.db import crud
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.function import FunctionCreate

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
def create_functions(functions_file: Path, skip_dry_run: bool) -> list[UUID]:
    """Create Functions in db from file."""
    return create_functions_helper(functions_file, skip_dry_run)


def create_functions_helper(functions_file: Path, skip_dry_run: bool) -> list[UUID]:
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        with open(functions_file, "r") as f:
            functions: list[FunctionCreate] = [
                FunctionCreate.model_validate(function) for function in json.load(f)
            ]

        function_embeddings = embeddings.generate_function_embeddings(functions, openai_service)

        db_functions = crud.create_functions(db_session, functions, function_embeddings)
        if not skip_dry_run:
            click.echo(
                f"\n\n============ will create {len(functions)} functions ============\n\n"
                "============ provide --skip-dry-run to commit changes ============="
            )
            db_session.rollback()
        else:
            click.echo(
                f"\n\n============ committing creation of {len(functions)} functions ============\n\n"
            )
            db_session.commit()
            click.echo("============ success! =============")

        return [db_function.id for db_function in db_functions]
