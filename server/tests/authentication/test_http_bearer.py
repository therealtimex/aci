from fastapi import status
from fastapi.testclient import TestClient

from server import schemas


# sending a request without a valid jwt token in Authorization header to /projects route should fail
def test_without_bearer_token(test_client: TestClient) -> None:
    project_create = schemas.ProjectCreate(name="new test project", owner_organization_id=None)

    response = test_client.post("/v1/projects/", json=project_create.model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN


# sending a request with an invalid bearer token should fail
def test_with_invalid_bearer_token(test_client: TestClient) -> None:
    project_create = schemas.ProjectCreate(name="new test project", owner_organization_id=None)

    response = test_client.post(
        "/v1/projects/",
        json=project_create.model_dump(),
        headers={"Authorization": "Bearer xxx"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
