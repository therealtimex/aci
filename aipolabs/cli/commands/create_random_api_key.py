"""
A convenience command to create a test api key for local development.
This will:
- create a new dummy user
- create a new dummy project with the new user as the owner
- create a new dummy agent in the project
"""

import uuid

import click

from aipolabs.cli import config
from aipolabs.cli.commands import create_agent, create_project, create_user
from aipolabs.common import utils
from aipolabs.common.db import crud, sql_models
from aipolabs.common.enums import Plan, ProjectOwnerType, Visibility


@click.command()
def create_random_api_key() -> str:
    """Create a random test api key for local development."""
    # can not do dry run because of the dependencies
    skip_dry_run = True

    random_id = str(uuid.uuid4())[:8]  # Get first 8 chars of UUID

    user_id = create_user.create_user_helper(
        auth_provider="google",
        auth_user_id=random_id,
        name=f"Test User {random_id}",
        email=f"test_{random_id}@example.com",
        profile_picture=f"https://example.com/profile_{random_id}.png",
        plan=Plan.FREE,
        skip_dry_run=skip_dry_run,
    )
    project_id = create_project.create_project_helper(
        project_name=f"Test Project {random_id}",
        owner_type=ProjectOwnerType.USER,
        owner_id=user_id,
        created_by=user_id,
        visibility_access=Visibility.PUBLIC,
        skip_dry_run=skip_dry_run,
    )
    agent_id = create_agent.create_agent_helper(
        agent_name=f"Test Agent {random_id}",
        description=f"Test Agent {random_id}",
        project_id=project_id,
        created_by=user_id,
        excluded_apps=[],
        excluded_functions=[],
        skip_dry_run=skip_dry_run,
    )

    # get the api key by agent id
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        db_api_key: sql_models.APIKey | None = crud.get_api_key_by_agent_id(db_session, agent_id)
        if not db_api_key:
            raise ValueError(f"API key with agent ID {agent_id} not found")
        api_key: str = db_api_key.key
        click.echo(f"\n\n============ Created Test API key: {api_key} ============\n\n")

    return api_key
