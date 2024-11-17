import json
from pathlib import Path
from uuid import UUID

import click

from aipolabs.cli import config
from aipolabs.common import embeddings, utils
from aipolabs.common.db import crud
from aipolabs.common.logging import create_headline
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.app import AppCreate

openai_service = OpenAIService(config.OPENAI_API_KEY)


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
def create_app(app_file: Path, skip_dry_run: bool) -> UUID:
    """Create App in db from file."""
    return create_app_helper(app_file, skip_dry_run)


def create_app_helper(app_file: Path, skip_dry_run: bool) -> UUID:
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        with open(app_file, "r") as f:
            app: AppCreate = AppCreate.model_validate(json.load(f))
            app_embedding = embeddings.generate_app_embedding(
                app,
                openai_service,
                config.OPENAI_EMBEDDING_MODEL,
                config.OPENAI_EMBEDDING_DIMENSION,
            )

        db_app = crud.create_app(db_session, app, app_embedding)
        if not skip_dry_run:
            click.echo(create_headline(f"will create new app {db_app.name}"))
            click.echo(db_app)
            click.echo(create_headline("provide --skip-dry-run to commit changes"))
            db_session.rollback()
        else:
            click.echo(create_headline(f"committing creation of app {db_app.name}"))
            click.echo(db_app)
            db_session.commit()

        return db_app.id  # type: ignore
