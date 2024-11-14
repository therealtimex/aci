import logging
from typing import Generator, cast

import pytest
from click.testing import CliRunner
from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Session

from aipolabs.cli import config
from aipolabs.common import utils
from aipolabs.common.db import sql_models

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
def db_setup_and_cleanup() -> Generator[None, None, None]:
    # Use 'with' to manage the session context
    with utils.create_db_session(config.DB_FULL_URL) as session:
        inspector = cast(Inspector, inspect(session.bind))

        # Check if all tables defined in models are created in the db
        for table in sql_models.Base.metadata.tables.values():
            if not inspector.has_table(table.name):
                pytest.exit(f"Table {table} does not exist in the database.")

        # Go through all tables and make sure there are no records in the table
        # (skip alembic_version table)
        for table in sql_models.Base.metadata.tables.values():
            if table.name != "alembic_version" and session.query(table).count() > 0:
                pytest.exit(f"Table {table} is not empty.")

        yield  # This allows the test to run

        # Clean up: Empty all tables after tests in reverse order of creation
        for table in reversed(sql_models.Base.metadata.sorted_tables):
            if table.name != "alembic_version" and session.query(table).count() > 0:
                logger.warning(f"Deleting all records from table {table.name}")
                session.execute(table.delete())
        session.commit()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        yield db_session


@pytest.fixture(scope="function")
def cli_runner() -> Generator[CliRunner, None, None]:
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner
