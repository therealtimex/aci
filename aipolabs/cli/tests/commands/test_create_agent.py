from uuid import UUID

import pytest
from click.testing import CliRunner
from sqlalchemy import select
from sqlalchemy.orm import Session

from aipolabs.cli.commands.create_agent import create_agent
from aipolabs.cli.commands.create_project import create_project
from aipolabs.cli.commands.create_user import create_user
from aipolabs.common.db import sql_models
from aipolabs.common.schemas.project import ProjectOwnerType


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


@pytest.fixture
def created_user_id(cli_runner: CliRunner, db_session: Session, dummy_user: dict) -> UUID:
    # Create the user first
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

    return db_user.id  # type: ignore


@pytest.fixture
def dummy_project(created_user_id: UUID) -> dict:
    return {
        "project_name": "Test Project",
        "owner_type": ProjectOwnerType.USER,
        "owner_id": str(created_user_id),
        "created_by": str(created_user_id),
        "visibility_access": sql_models.Visibility.PRIVATE,
    }


@pytest.fixture
def created_project_id(cli_runner: CliRunner, db_session: Session, dummy_project: dict) -> UUID:
    result = cli_runner.invoke(
        create_project,
        [
            "--project-name",
            dummy_project["project_name"],
            "--owner-type",
            dummy_project["owner_type"],
            "--owner-id",
            dummy_project["owner_id"],
            "--created-by",
            dummy_project["created_by"],
            "--visibility-access",
            dummy_project["visibility_access"],
            "--skip-dry-run",
        ],
        catch_exceptions=False,
        standalone_mode=False,
    )

    # Assert the command exited successfully
    assert result.exit_code == 0

    db_project: sql_models.Project | None = db_session.execute(
        select(sql_models.Project).filter_by(id=result.return_value)
    ).scalar_one_or_none()

    assert db_project is not None

    return db_project.id  # type: ignore


@pytest.fixture
def dummy_agent(created_project_id: UUID, created_user_id: UUID) -> dict:
    return {
        "agent_name": "Test Agent",
        "description": "Test agent description",
        "project_id": str(created_project_id),
        "created_by": str(created_user_id),
        "excluded_apps": [],
        "excluded_functions": [],
    }


def test_create_agent_dry_run(
    cli_runner: CliRunner, db_session: Session, dummy_agent: dict
) -> None:
    result = cli_runner.invoke(
        create_agent,
        [
            "--agent-name",
            dummy_agent["agent_name"],
            "--description",
            dummy_agent["description"],
            "--project-id",
            dummy_agent["project_id"],
            "--created-by",
            dummy_agent["created_by"],
        ],
        catch_exceptions=False,
        standalone_mode=False,
    )

    # Assert the command exited successfully
    assert result.exit_code == 0
    agent_id: UUID = result.return_value
    # Verify agent was not created in DB (dry run)
    agent = db_session.execute(select(sql_models.Agent).filter_by(id=agent_id)).scalar_one_or_none()

    assert agent is None


def test_create_agent_skip_dry_run(
    cli_runner: CliRunner, db_session: Session, dummy_agent: dict
) -> None:
    result = cli_runner.invoke(
        create_agent,
        [
            "--agent-name",
            dummy_agent["agent_name"],
            "--description",
            dummy_agent["description"],
            "--project-id",
            dummy_agent["project_id"],
            "--created-by",
            dummy_agent["created_by"],
            "--skip-dry-run",
        ],
        catch_exceptions=False,
        standalone_mode=False,
    )

    # Assert the command exited successfully
    assert result.exit_code == 0
    agent_id: UUID = result.return_value
    db_agent = db_session.execute(select(sql_models.Agent).filter_by(id=agent_id)).scalar_one()

    assert db_agent is not None
    assert db_agent.name == dummy_agent["agent_name"]
    assert db_agent.description == dummy_agent["description"]
    assert str(db_agent.project_id) == dummy_agent["project_id"]
    assert str(db_agent.created_by) == dummy_agent["created_by"]
    assert db_agent.excluded_apps == dummy_agent["excluded_apps"]
    assert db_agent.excluded_functions == dummy_agent["excluded_functions"]
