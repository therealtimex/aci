import logging

from fastapi.testclient import TestClient

from app import schemas
from database import models

logger = logging.getLogger(__name__)


def test_search_functions_with_app_names(
    test_client: TestClient, dummy_functions: list[models.Function]
) -> None:
    search_param = {
        "app_names": ["GITHUB", "GOOGLE"],
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get("/v1/functions/search", params=search_param)

    assert response.status_code == 200
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    # only github and google functions should be returned
    for function in functions:
        assert function.name.startswith("GITHUB") or function.name.startswith("GOOGLE")
    # total number of functions should be the sum of functions of GITHUB and GOOGLE from dummy_functions
    assert len(functions) == sum(
        function.name.startswith("GITHUB") or function.name.startswith("GOOGLE")
        for function in dummy_functions
    )


def test_search_functions_with_intent(
    test_client: TestClient, dummy_functions: list[models.Function]
) -> None:

    # intent1: create repo
    search_param = {
        "intent": "i want to create a new code repo for my project",
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get("/v1/functions/search", params=search_param)
    logger.info(f"response: \n {response.json()}")

    assert response.status_code == 200
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions)
    assert functions[0].name == "GITHUB_CREATE_REPOSITORY"

    # intent2: upload file
    search_param["intent"] = "add this meeting to my calendar"
    response = test_client.get("/v1/functions/search", params=search_param)
    assert response.status_code == 200
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions)
    assert functions[0].name == "GOOGLE_CALENDAR_CREATE_EVENT"


def test_search_functions_with_app_names_and_intent(
    test_client: TestClient, dummy_functions: list[models.Function]
) -> None:
    search_param = {
        "app_names": ["GITHUB"],
        "intent": "i want to create a new code repo for my project",
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get("/v1/functions/search", params=search_param)

    assert response.status_code == 200
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    # only github functions should be returned
    for function in functions:
        assert function.name.startswith("GITHUB")
    # total number of functions should be the sum of functions of GITHUB from dummy_functions
    assert len(functions) == sum(function.name.startswith("GITHUB") for function in dummy_functions)
    assert functions[0].name == "GITHUB_CREATE_REPOSITORY"


def test_search_functions_pagination(
    test_client: TestClient, dummy_functions: list[models.Function]
) -> None:
    assert len(dummy_functions) > 2

    search_param = {
        "limit": len(dummy_functions) - 1,
        "offset": 0,
    }

    response = test_client.get("/v1/functions/search", params=search_param)
    assert response.status_code == 200
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions) - 1

    search_param["offset"] = len(dummy_functions) - 1
    response = test_client.get("/v1/functions/search", params=search_param)
    assert response.status_code == 200
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    assert len(functions) == 1


def test_get_function(test_client: TestClient, dummy_functions: list[models.Function]) -> None:
    function_name = "GITHUB__CREATE_REPOSITORY"
    response = test_client.get(f"/v1/functions/{function_name}")

    assert response.status_code == 200
    function = schemas.FunctionPublic.model_validate(response.json())
    assert function.name == function_name
    # check if parameters and description are the same as the same function from dummy_functions
    dummy_function = next(
        function for function in dummy_functions if function.name == function_name
    )
    assert function.parameters == dummy_function.parameters
    assert function.description == dummy_function.description
