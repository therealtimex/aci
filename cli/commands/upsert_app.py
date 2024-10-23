import json

import click
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from cli.models.app_file import AppModel, FunctionModel
from cli.utils import config
from cli.utils.helper import get_db_session
from cli.utils.logging import get_logger
from database import models

logger = get_logger(__name__)
LLM_CLIENT = OpenAI(api_key=config.OPENAI_API_KEY)


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
    with get_db_session() as db_session:
        try:
            # Parse files
            with open(app_file, "r") as f:
                app_model: AppModel = AppModel.model_validate(json.load(f))

            # make sure app and functions are upserted together
            db_app = upsert_app_to_db(db_session, app_model)
            upsert_functions_to_db(db_session, db_app, app_model)
            db_session.commit()

        except Exception as e:
            db_session.rollback()
            logger.error(f"Error indexing app and functions: {e}")
            click.echo(f"Error indexing app and functions: {e}")


# TODO: check for changes before updating? if no changes just skip?
def upsert_functions_to_db(db_session: Session, db_app: models.App, app_model: AppModel) -> None:
    logger.info(f"Upserting functions for app: {db_app.name}...")
    # Retrieve all existing functions for the app in one query
    existing_functions = (
        (db_session.execute(select(models.Function).filter_by(app_id=db_app.id).with_for_update()))
        .scalars()
        .all()
    )
    # Create a dictionary of existing functions by name for easy lookup
    existing_function_dict = {f.name: f for f in existing_functions}

    for function in app_model.functions:
        db_function = models.Function(
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
def generate_function_embedding(function: FunctionModel) -> list[float]:
    logger.debug(f"Generating embedding for function: {function.name}...")
    text_for_embedding = f"{function.name}\n{function.description}\n{function.parameters}"
    response = LLM_CLIENT.embeddings.create(
        input=text_for_embedding,
        model=config.OPENAI_EMBEDDING_MODEL,
        dimensions=config.EMBEDDING_DIMENSION,
    )
    embedding: list[float] = response.data[0].embedding
    return embedding


def upsert_app_to_db(db_session: Session, app_model: AppModel) -> models.App:
    logger.info(f"Upserting app: {app_model.name}...")
    if app_model.supported_auth_schemes is None:
        supported_auth_types = []
    else:
        supported_auth_types = [
            models.App.AuthType(auth_type)
            for auth_type, auth_config in vars(app_model.supported_auth_schemes).items()
            if auth_config is not None
        ]

    db_app = models.App(
        name=app_model.name,
        display_name=app_model.display_name,
        version=app_model.version,
        provider=app_model.provider,
        description=app_model.description,
        server_url=app_model.server_url,
        logo=app_model.logo,
        categories=app_model.categories,
        tags=app_model.tags,
        supported_auth_types=supported_auth_types,
        auth_configs=(
            app_model.supported_auth_schemes.model_dump(mode="json")
            if app_model.supported_auth_schemes is not None
            else None
        ),
        embedding=generate_app_embedding(app_model),
    )

    # check if the app already exists
    existing_app = db_session.execute(
        select(models.App).filter_by(name=app_model.name).with_for_update()
    ).scalar_one_or_none()
    if existing_app:
        logger.info(f"App {app_model.name} already exists, will perform update")
        db_app.id = existing_app.id
        db_app = db_session.merge(db_app)
    else:
        logger.info(f"App {app_model.name} does not exist, will perform insert")
        db_session.add(db_app)
        db_session.flush()

    return db_app


def generate_app_embedding(app_model: AppModel) -> list[float]:
    logger.debug(f"Generating embedding for app: {app_model.name}...")
    # generate app embeddings based on app config's name, display_name, provider, description, categories, and tags
    text_for_embedding = (
        f"{app_model.name}\n"
        f"{app_model.display_name}\n"
        f"{app_model.provider}\n"
        f"{app_model.description}\n"
        f"{' '.join(app_model.categories)}\n"
        f"{' '.join(app_model.tags)}"
    )
    response = LLM_CLIENT.embeddings.create(
        input=text_for_embedding,
        model=config.OPENAI_EMBEDDING_MODEL,
        dimensions=config.EMBEDDING_DIMENSION,
    )
    embedding: list[float] = response.data[0].embedding
    return embedding
