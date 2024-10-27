import logging
from typing import Any

from fastapi.testclient import TestClient

from aipolabs.common import sql_models
from aipolabs.server import schemas

logger = logging.getLogger(__name__)

AIPOLABS_TEST = "AIPOLABS_TEST"
GITHUB = "GITHUB"
GOOGLE = "GOOGLE"


def test_search_apps_with_intent(
    test_client: TestClient, dummy_apps: list[sql_models.App], dummy_api_key: str
) -> None:
    # try with intent to find GITHUB app
    filter_params = {
        "intent": "i want to create a new code repo for my project",
        "categories": [],
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/apps/search",
        params=filter_params,
        headers={"x-api-key": dummy_api_key},
    )

    assert response.status_code == 200, response.json()
    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == len(dummy_apps)
    assert apps[0].name == GITHUB

    # try with intent to find GOOGLE app
    filter_params["intent"] = "i want to search the web"
    response = test_client.get(
        "/v1/apps/search",
        params=filter_params,
        headers={"x-api-key": dummy_api_key},
    )

    assert response.status_code == 200, response.json()
    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == len(dummy_apps)
    assert apps[0].name == GOOGLE


def test_search_apps_without_intent(
    test_client: TestClient, dummy_apps: list[sql_models.App], dummy_api_key: str
) -> None:
    response = test_client.get("/v1/apps/search", headers={"x-api-key": dummy_api_key})

    assert response.status_code == 200, response.json()
    # similarity scores should not exist
    for app in response.json():
        assert "similarity_score" not in app

    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == len(dummy_apps)


def test_search_apps_with_categories(test_client: TestClient, dummy_api_key: str) -> None:
    filter_params = {
        "intent": None,
        "categories": ["testcategory"],
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/apps/search", params=filter_params, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == 1
    assert apps[0].name == AIPOLABS_TEST


def test_search_apps_with_categories_and_intent(
    test_client: TestClient, dummy_api_key: str
) -> None:
    filter_params = {
        "intent": "i want to create a new code repo for my project",
        "categories": ["testcategory-2"],
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/apps/search", params=filter_params, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == 2
    assert apps[0].name == GITHUB
    assert apps[1].name == GOOGLE


def test_search_apps_pagination(
    test_client: TestClient, dummy_apps: list[sql_models.App], dummy_api_key: str
) -> None:
    assert len(dummy_apps) > 2

    filter_params: dict[str, Any] = {
        "intent": None,
        "categories": [],
        "limit": len(dummy_apps) - 1,
        "offset": 0,
    }

    response = test_client.get(
        "/v1/apps/search", params=filter_params, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == len(dummy_apps) - 1

    filter_params["offset"] = len(dummy_apps) - 1
    response = test_client.get(
        "/v1/apps/search", params=filter_params, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    apps = [schemas.AppBasicPublic.model_validate(response_app) for response_app in response.json()]
    assert len(apps) == 1
