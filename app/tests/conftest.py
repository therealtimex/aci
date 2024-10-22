import logging
from datetime import timedelta
from typing import Generator, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Session

from app import schemas
from app.db import crud
from app.db.engine import SessionMaker
from app.main import app as fastapi_app
from app.routes.auth import create_access_token
from app.tests import helper
from database import models

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def db_setup_and_cleanup() -> Generator[None, None, None]:
    # Use 'with' to manage the session context
    with SessionMaker() as session:
        inspector = cast(Inspector, inspect(session.bind))

        # Check if all tables defined in models are created in the db
        for table in models.Base.metadata.tables.values():
            if not inspector.has_table(table.name):
                pytest.exit(f"Table {table} does not exist in the database.")

        # Go through all tables and make sure there are no records in the table
        # (skip alembic_version table)
        for table in models.Base.metadata.tables.values():
            if table.name != "alembic_version" and session.query(table).count() > 0:
                pytest.exit(f"Table {table} is not empty.")

        yield  # This allows the test to run

        # Clean up: Empty all tables after tests in reverse order of creation
        for table in reversed(models.Base.metadata.sorted_tables):
            if table.name != "alembic_version" and session.query(table).count() > 0:
                logger.warning(f"Deleting all records from table {table.name}")
                session.execute(table.delete())
        session.commit()


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    # disable following redirects for testing login
    with TestClient(fastapi_app, follow_redirects=False) as c:
        yield c


@pytest.fixture(scope="module")
def db_session() -> Generator[Session, None, None]:
    with SessionMaker() as db_session:
        yield db_session


@pytest.fixture(scope="module", autouse=True)
def dummy_user(db_session: Session) -> Generator[models.User, None, None]:
    dummy_user = crud.get_or_create_user(
        db_session, "dummy_auth_provider", "dummy_user_id", "Dummy User", "dummy@example.com"
    )
    db_session.commit()
    yield dummy_user
    db_session.delete(dummy_user)
    db_session.commit()


@pytest.fixture(scope="module", autouse=True)
def dummy_user_bearer_token(dummy_user: models.User) -> str:
    return create_access_token(str(dummy_user.id), timedelta(minutes=15))


@pytest.fixture(scope="module", autouse=True)
def dummy_project(
    db_session: Session, dummy_user: models.User
) -> Generator[models.Project, None, None]:
    dummy_project = crud.create_project(
        db_session,
        schemas.ProjectCreate(name="Dummy Project", owner_organization_id=None),
        dummy_user.id,
    )
    db_session.commit()
    yield dummy_project
    db_session.delete(dummy_project)
    db_session.commit()


@pytest.fixture(scope="module", autouse=True)
def dummy_apps(db_session: Session) -> Generator[list[models.App], None, None]:
    dummy_apps = helper.create_dummy_apps(db_session)
    db_session.commit()
    yield dummy_apps
    for dummy_app in dummy_apps:
        db_session.delete(dummy_app)
    db_session.commit()
