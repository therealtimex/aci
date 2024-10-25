from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import models
from server import schemas


def test_create_project(
    test_client: TestClient,
    db_session: Session,
    dummy_user_bearer_token: str,
    dummy_user: models.User,
) -> None:
    project_create = schemas.ProjectCreate(name="new test project", owner_organization_id=None)

    response = test_client.post(
        "/v1/projects/",
        json=project_create.model_dump(),
        headers={"Authorization": f"Bearer {dummy_user_bearer_token}"},
    )
    assert response.status_code == 200
    project_public = schemas.ProjectPublic.model_validate(response.json())
    assert project_public.name == project_create.name
    assert project_public.owner_organization_id == project_create.owner_organization_id
    assert project_public.owner_user_id == dummy_user.id

    # Verify the project was actually created in the database and values match returned values
    db_project = db_session.execute(
        select(models.Project).filter(models.Project.id == project_public.id)
    ).scalar_one_or_none()

    assert db_project is not None
    assert (
        project_public.model_dump() == schemas.ProjectPublic.model_validate(db_project).model_dump()
    )

    # Clean up: no need to delete project, it will be deleted when dummy_user is deleted


def test_create_agent(
    test_client: TestClient,
    db_session: Session,
    dummy_project: models.Project,
    dummy_user_bearer_token: str,
    dummy_user: models.User,
) -> None:
    agent_create = schemas.AgentCreate(
        name="new test agent", description="new test agent description"
    )

    response = test_client.post(
        f"/v1/projects/{dummy_project.id}/agents/",
        json=agent_create.model_dump(),
        headers={"Authorization": f"Bearer {dummy_user_bearer_token}"},
    )
    assert response.status_code == 200
    agent_public = schemas.AgentPublic.model_validate(response.json())
    assert agent_public.name == agent_create.name
    assert agent_public.description == agent_create.description
    assert agent_public.project_id == dummy_project.id
    assert agent_public.created_by == dummy_user.id

    # Verify the agent was actually created in the database and values match returned values
    db_agent = db_session.execute(
        select(models.Agent).filter(models.Agent.id == agent_public.id)
    ).scalar_one_or_none()

    assert db_agent is not None
    assert agent_public.model_dump() == schemas.AgentPublic.model_validate(db_agent).model_dump()

    # check api keys
    db_api_key = db_session.execute(
        select(models.APIKey).filter(models.APIKey.agent_id == db_agent.id)
    ).scalar_one_or_none()
    assert db_api_key is not None
    assert len(agent_public.api_keys) == 1
    assert agent_public.api_keys[0].key == db_api_key.key

    # Clean up: no need to delete agent and api key, it will be deleted when dummy_project is deleted
