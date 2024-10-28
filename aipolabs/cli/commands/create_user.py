import click

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import crud
from aipolabs.common.db.sql_models import Plan
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.user import UserCreate

logger = get_logger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


@click.command()
@click.option(
    "--auth-provider",
    "auth_provider",
    required=True,
    type=click.Choice(
        ["google", "github", "email"]
    ),  # TODO: update according to auth provider when db finalized
    help="Auth provider",
)
@click.option(
    "--auth-user-id",
    "auth_user_id",
    required=True,
    help="Auth user id",
)
@click.option(
    "--name",
    "name",
    required=True,
    help="user name",
)
@click.option(
    "--email",
    "email",
    required=True,
    help="user email",
)
@click.option(
    "--profile-picture",
    "profile_picture",
    help="url to user profile picture",
)
@click.option(
    "--plan",
    "plan",
    type=click.Choice(list(Plan)),
    help="subscription plan, default is free",
    default=Plan.FREE,
)
def create_user(
    auth_provider: str,
    auth_user_id: str,
    name: str,
    email: str,
    profile_picture: str | None,
    plan: Plan,
) -> None:
    """Create a user in db."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        try:
            # no need to check if user exists, db will raise an error if user already exists
            # with same auth_provider and auth_user_id
            user_create = UserCreate(
                auth_provider=auth_provider,
                auth_user_id=auth_user_id,
                name=name,
                email=email,
                profile_picture=profile_picture,
                plan=plan,
            )
            # make sure app and functions are upserted in one transaction
            logger.info(f"creating user: {user_create.name}...")
            db_user = crud.create_user(db_session, user_create)
            db_session.commit()

            logger.info(f"user created: {db_user}...")

        except Exception as e:
            db_session.rollback()
            logger.error(f"Error upserting app and functions: {e}")
