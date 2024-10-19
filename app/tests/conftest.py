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
from app.main import app
from app.routes.auth import create_access_token
from database import models


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
            if table.name != "alembic_version":
                session.execute(table.delete())
        session.commit()


@pytest.fixture(scope="module")
def db_session() -> Generator[Session, None, None]:
    with SessionMaker() as db_session:
        yield db_session


@pytest.fixture(scope="module")
def dummy_user(db_session: Session) -> models.User:
    return crud.get_or_create_user(
        db_session, "dummy_auth_provider", "dummy_user_id", "Dummy User", "dummy@example.com"
    )


@pytest.fixture(scope="module")
def dummy_user_bearer_token(dummy_user: models.User) -> str:
    return create_access_token(str(dummy_user.id), timedelta(minutes=15))


@pytest.fixture(scope="module")
def dummy_project(db_session: Session, dummy_user: models.User) -> models.Project:
    return crud.create_project(
        db_session,
        schemas.ProjectCreate(name="Dummy Project", owner_organization_id=None),
        dummy_user.id,
    )


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    # disable following redirects for testing login
    with TestClient(app, follow_redirects=False) as c:
        yield c
