import logging

from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


def test_health_check(test_client: TestClient) -> None:
    # TODO: /v1/health will result in a redirect to /v1/health/
    response = test_client.get("/v1/health/")
    assert response.status_code == 200
    assert response.json() is True
