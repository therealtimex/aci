from fastapi import status
from fastapi.testclient import TestClient

from aipolabs.common.db import sql_models
from aipolabs.common.enums import ProjectOwnerType
from aipolabs.common.schemas.project import ProjectCreate


# sending a request without a valid jwt token in Authorization header to /projects route should fail
def test_without_bearer_token(test_client: TestClient, dummy_user: sql_models.User) -> None:
    project_create = ProjectCreate(
        name="project test_without_bearer_token",
        owner_type=ProjectOwnerType.USER,
        owner_id=dummy_user.id,
        created_by=dummy_user.id,
    )

    response = test_client.post("/v1/projects/", json=project_create.model_dump(mode="json"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


# sending a request with an invalid bearer token should fail
def test_with_invalid_bearer_token(test_client: TestClient, dummy_user: sql_models.User) -> None:
    project_create = ProjectCreate(
        name="project test_with_invalid_bearer_token",
        owner_type=ProjectOwnerType.USER,
        owner_id=dummy_user.id,
        created_by=dummy_user.id,
    )

    response = test_client.post(
        "/v1/projects/",
        json=project_create.model_dump(mode="json"),
        headers={"Authorization": "Bearer xxx"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# sending a request with a valid bearer token should succeed
def test_with_valid_bearer_token(
    test_client: TestClient, dummy_user: sql_models.User, dummy_user_bearer_token: str
) -> None:
    project_create = ProjectCreate(
        name="project test_with_valid_bearer_token",
        owner_type=ProjectOwnerType.USER,
        owner_id=dummy_user.id,
        created_by=dummy_user.id,
    )

    response = test_client.post(
        "/v1/projects/",
        json=project_create.model_dump(mode="json"),
        headers={"Authorization": f"Bearer {dummy_user_bearer_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
