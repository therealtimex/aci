import logging

from fastapi.testclient import TestClient

from app import schemas
from database import models

logger = logging.getLogger(__name__)


def test_get_apps_with_query(test_client: TestClient, dummy_apps: list[models.App]) -> None:
    # try with intent to find github app
    filter_params = {
        "query": "i want to create a new code repo for my project",
        "categories": [],
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/apps/",
        params=filter_params,
    )

    assert response.status_code == 200
    apps = [schemas.AppPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == len(dummy_apps)
    assert apps[0].name == "github"

    # try with intent to find google app
    filter_params["query"] = "i want to search the web"
    response = test_client.get(
        "/v1/apps/",
        params=filter_params,
    )
    assert response.status_code == 200
    apps = [schemas.AppPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == len(dummy_apps)
    assert apps[0].name == "google"
