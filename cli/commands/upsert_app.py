import json

import click
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.orm import Session

from cli.models.app_file import AppModel
from cli.utils import config
from cli.utils.helper import get_db_session
from cli.utils.logging import get_logger
from database import models

logger = get_logger()


LLM_CLIENT = OpenAI(api_key=config.OPENAI_API_KEY)


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
    """Upsert App and Functions to db from a json file."""
    with get_db_session() as db_session:
        try:
            # Parse files
            with open(app_file, "r") as f:
                app_model: AppModel = AppModel.model_validate(json.load(f))

            # make sure app and functions are upserted together
            with db_session.begin():
                upsert_app_to_db(db_session, app_model)
                # upsert_functions_to_db(db_session, app_model)

                db_session.commit()
                # db_session.refresh(app)

                # # prepare app and functions database records to upsert
                # app = get_app_to_upsert(db_session, app_config, app_openapi)
                # # ensure app id is generated
                # db_session.add(app)
                # db_session.flush()
                # db_session.refresh(app)
                # get_functions_to_upsert(app, app_openapi)

                # # Commit all changes
                # db_session.commit()
                # click.echo("App and functions indexed successfully.")

        except Exception as e:
            db_session.rollback()
            logger.error(f"Error indexing app and functions: {e}")
            click.echo(f"Error indexing app and functions: {e}")


def upsert_functions_to_db(db_session: Session, app_model: AppModel) -> None:
    pass


def upsert_app_to_db(db_session: Session, app_model: AppModel) -> models.App:
    app_embedding = generate_app_embedding(app_model)

    if app_model.supported_auth_schemes is None:
        supported_auth_types = []
    else:
        supported_auth_types = [
            models.App.AuthType(auth_type)
            for auth_type, auth_config in vars(app_model.supported_auth_schemes).items()
            if auth_config is not None
        ]
    auth_required = len(supported_auth_types) > 0

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
        auth_required=auth_required,
        supported_auth_types=supported_auth_types,
        auth_configs=(
            app_model.supported_auth_schemes.model_dump(mode="json")
            if app_model.supported_auth_schemes is not None
            else None
        ),
        embedding=app_embedding,
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
