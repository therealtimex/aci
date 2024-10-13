import json

import click
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cli.models.app_file import AppModel
from cli.utils import config
from cli.utils.logging import get_logger

logger = get_logger()


SessionMaker = sessionmaker(
    autocommit=False, autoflush=False, bind=create_engine(config.DB_FULL_URL)
)
LLM_CLIENT = OpenAI(api_key=config.OPENAI_API_KEY)


def generate_app_embedding(app_config: dict) -> list[float]:
    # generate app embeddings based on app config's name, display_name, provider, description, categories, and tags
    app_text_for_embedding = (
        f"{app_config['name']}\n"
        f"{app_config['display_name']}\n"
        f"{app_config['provider']}\n"
        f"{app_config['description']}\n"
        f"{' '.join(app_config['categories'])}\n"
        f"{' '.join(app_config['tags'])}"
    )
    response = LLM_CLIENT.embeddings.create(
        input=app_text_for_embedding,
        model=config.OPENAI_EMBEDDING_MODEL,
        dimensions=config.EMBEDDING_DIMENSION,
    )
    embedding: list[float] = response.data[0].embedding
    return embedding

    # existing_app = db_session.execute(
    #     select(models.App).filter_by(name=app_config["name"])
    # ).scalar_one_or_none()

    # if existing_app:
    #     for key, value in app_attributes.items():
    #         setattr(existing_app, key, value)
    #     app = existing_app
    #     logger.info(f"Updated existing app: {app_config['name']}")
    # else:
    #     app = models.App(name=app_config["name"], **app_attributes)
    #     db_session.add(app)
    #     logger.info(f"Created new app: {app_config['name']}")

    # return app


@click.command()
@click.option(
    "--app-file",
    "app_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the complete app json file",
)
def upsert_app(app_file: str) -> None:
    # """Index App and Functions from OpenAPI spec and app definition file."""
    with open(app_file, "r") as f:

        app_file_model: AppModel = AppModel.model_validate(json.load(f))

    logger.info(app_file_model)
    # with SessionMaker() as db_session:
    #     try:
    #         # Parse files
    #         with open(app_file, "r") as f:
    #             app_file_model: AppModel = AppModel.model_validate_json(f)

    #         # prepare app and functions database records to upsert
    #         app = get_app_to_upsert(db_session, app_config, app_openapi)
    #         # ensure app id is generated
    #         db_session.add(app)
    #         db_session.flush()
    #         db_session.refresh(app)
    #         get_functions_to_upsert(app, app_openapi)

    #         # Commit all changes
    #         db_session.commit()
    #         click.echo("App and functions indexed successfully.")

    #     except Exception as e:
    #         db_session.rollback()
    #         logger.error(f"Error indexing app and functions: {e}")
    #         click.echo(f"Error indexing app and functions: {e}")
