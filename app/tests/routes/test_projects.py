import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from database import models


@pytest.fixture
def dummy_project() -> dict:
    return {
        "name": "Dummy Project",
        "owner_organization_id": None,
    }


def test_create_project(
    test_client: TestClient,
    db_session: Session,
    dummy_project: dict,
    dummy_user_bearer_token: str,
    dummy_user: models.User,
) -> None:
    response = test_client.post(
        "/v1/projects/",
        json=dummy_project,
        headers={"Authorization": f"Bearer {dummy_user_bearer_token}"},
    )
    assert response.status_code == 200
    project_public = schemas.ProjectPublic.model_validate(response.json())
    assert project_public.name == dummy_project["name"]
    assert project_public.owner_organization_id == dummy_project["owner_organization_id"]
    assert project_public.owner_user_id == dummy_user.id

    # Verify the project was actually created in the database and values match returned values
    db_project = db_session.execute(
        select(models.Project).filter(models.Project.id == project_public.id)
    ).scalar_one_or_none()

    assert db_project is not None
    assert (
        project_public.model_dump() == schemas.ProjectPublic.model_validate(db_project).model_dump()
    )
