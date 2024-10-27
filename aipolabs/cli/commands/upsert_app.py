import json

import click
from sqlalchemy import select
from sqlalchemy.orm import Session

from aipolabs.cli import config
from aipolabs.common import sql_models, utils
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas import AppFileModel, FunctionFileModel

logger = get_logger(__name__)
openai_service = OpenAIService()


# TODO: funciton name is prefixed with app name and double underscores, e.g., GITHUB__CREATE_REPOSITORY (force this check when validating)
@click.command()
@click.option(
    "--app-file",
    "app_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the complete app json file",
)
def upsert_app(app_file: str) -> None:
    """Upsert App and Functions to db from a json file."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            # Parse files
            with open(app_file, "r") as f:
                app: AppFileModel = AppFileModel.model_validate(json.load(f))

            # make sure app and functions are upserted together
            db_app = upsert_app_to_db(db_session, app)
            upsert_functions_to_db(db_session, db_app, app)
            db_session.commit()

        except Exception as e:
            db_session.rollback()
            logger.error(f"Error indexing app and functions: {e}")
            click.echo(f"Error indexing app and functions: {e}")


# TODO: check for changes before updating? if no changes just skip?
def upsert_functions_to_db(db_session: Session, db_app: sql_models.App, app: AppFileModel) -> None:
    logger.info(f"Upserting functions for app: {db_app.name}...")
    # Retrieve all existing functions for the app in one query
    existing_functions = (
        (
            db_session.execute(
                select(sql_models.Function).filter_by(app_id=db_app.id).with_for_update()
            )
        )
        .scalars()
        .all()
    )
    # Create a dictionary of existing functions by name for easy lookup
    existing_function_dict = {f.name: f for f in existing_functions}

    for function in app.functions:
        db_function = sql_models.Function(
            name=function.name,
            description=function.description,
            parameters=function.parameters,
            app_id=db_app.id,
            response={},  # TODO: add response schema
            embedding=generate_function_embedding(function),
        )
        if db_function.name in existing_function_dict:
            logger.info(f"Function {function.name} already exists, will update")
            # Update existing function
            db_function.id = existing_function_dict[function.name].id
            db_function = db_session.merge(db_function)
        else:
            logger.info(f"Function {function.name} does not exist, will insert")
            # Insert new function
            db_session.add(db_function)

    db_session.flush()


# TODO: include response schema in the embedding if added
# TODO: bacth generate function embeddings
def generate_function_embedding(function: FunctionFileModel) -> list[float]:
    logger.debug(f"Generating embedding for function: {function.name}...")
    text_for_embedding = f"{function.name}\n{function.description}\n{function.parameters}"

    return openai_service.generate_embedding(text_for_embedding)


def upsert_app_to_db(db_session: Session, app: AppFileModel) -> sql_models.App:
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

    # check if the app already exists
    existing_app = db_session.execute(
        select(sql_models.App).filter_by(name=app.name).with_for_update()
    ).scalar_one_or_none()
    if existing_app:
        logger.info(f"App {app.name} already exists, will perform update")
        db_app.id = existing_app.id
        db_app = db_session.merge(db_app)
    else:
        logger.info(f"App {app.name} does not exist, will perform insert")
        db_session.add(db_app)
        db_session.flush()

    return db_app


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
