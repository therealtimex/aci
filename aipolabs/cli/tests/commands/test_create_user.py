from uuid import UUID

import pytest
from click.testing import CliRunner
from sqlalchemy import select
from sqlalchemy.orm import Session

from aipolabs.cli.commands.create_user import create_user
from aipolabs.common.db import sql_models


@pytest.fixture
def dummy_user() -> dict:
    return {
        "auth_provider": "google",
        "auth_user_id": "123",
        "name": "Test User",
        "email": "test@example.com",
        "profile_picture": "https://example.com/pic.jpg",
        "plan": sql_models.Plan.FREE,
    }


def test_create_user_dry_run(cli_runner: CliRunner, db_session: Session, dummy_user: dict) -> None:
    result = cli_runner.invoke(
        create_user,
        [
            "--auth-provider",
            dummy_user["auth_provider"],
            "--auth-user-id",
            dummy_user["auth_user_id"],
            "--name",
            dummy_user["name"],
            "--email",
            dummy_user["email"],
            "--profile-picture",
            dummy_user["profile_picture"],
            "--plan",
            dummy_user["plan"],
        ],
        catch_exceptions=False,
        standalone_mode=False,
    )

    # Assert the command exited successfully
    assert result.exit_code == 0
    assert isinstance(result.return_value, UUID)
    # Verify user was not created in DB (dry run)
    db_user: sql_models.User | None = db_session.execute(
        select(sql_models.User).filter_by(id=result.return_value)
    ).scalar_one_or_none()

    assert db_user is None


def test_create_user_skip_dry_run(
    cli_runner: CliRunner, db_session: Session, dummy_user: dict
) -> None:
    result = cli_runner.invoke(
        create_user,
        [
            "--auth-provider",
            dummy_user["auth_provider"],
            "--auth-user-id",
            dummy_user["auth_user_id"],
            "--name",
            dummy_user["name"],
            "--email",
            dummy_user["email"],
            "--profile-picture",
            dummy_user["profile_picture"],
            "--plan",
            dummy_user["plan"],
            "--skip-dry-run",
        ],
        catch_exceptions=False,
        standalone_mode=False,
    )

    # Assert the command exited successfully
    assert result.exit_code == 0
    assert isinstance(result.return_value, UUID)
    # Verify user was created in DB
    db_user: sql_models.User | None = db_session.execute(
        select(sql_models.User).filter_by(id=result.return_value)
    ).scalar_one_or_none()

    assert db_user is not None
    assert db_user.auth_provider == dummy_user["auth_provider"]
    assert db_user.auth_user_id == dummy_user["auth_user_id"]
    assert db_user.name == dummy_user["name"]
    assert db_user.email == dummy_user["email"]
    assert db_user.profile_picture == dummy_user["profile_picture"]
    assert db_user.plan == dummy_user["plan"]
