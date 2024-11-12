import json
from urllib.parse import parse_qs, urlparse

import responses
from fastapi.testclient import TestClient
from requests import PreparedRequest
from sqlalchemy.orm import Session

from aipolabs.common.db import crud, sql_models
from aipolabs.common.schemas.function import (
    AnthropicFunctionDefinition,
    FunctionDefinitionPublic,
    FunctionExecutionResponse,
    FunctionPublic,
    OpenAIFunctionDefinition,
)

GOOGLE__CALENDAR_CREATE_EVENT = "GOOGLE__CALENDAR_CREATE_EVENT"
GITHUB__CREATE_REPOSITORY = "GITHUB__CREATE_REPOSITORY"
AIPOLABS_TEST__HELLO_WORLD_WITH_ARGS = "AIPOLABS_TEST__HELLO_WORLD_WITH_ARGS"
AIPOLABS_TEST__HELLO_WORLD_NESTED_ARGS = "AIPOLABS_TEST__HELLO_WORLD_NESTED_ARGS"
AIPOLABS_TEST__HELLO_WORLD_NO_ARGS = "AIPOLABS_TEST__HELLO_WORLD_NO_ARGS"
GITHUB = "GITHUB"
GOOGLE = "GOOGLE"


def test_search_functions_with_disabled_functions(
    db_session: Session,
    test_client: TestClient,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
) -> None:
    # disabled functions should not be returned
    crud.set_function_enabled_status(db_session, dummy_functions[0].id, False)
    db_session.commit()

    response = test_client.get(
        "/v1/functions/search", params={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions) - 1

    # revert changes
    crud.set_function_enabled_status(db_session, dummy_functions[0].id, True)
    db_session.commit()


def test_search_functions_with_disabled_apps(
    db_session: Session,
    test_client: TestClient,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
) -> None:
    # all functions (enabled or not) under disabled apps should not be returned
    crud.set_app_enabled_status(db_session, dummy_functions[0].app_id, False)
    db_session.commit()

    response = test_client.get(
        "/v1/functions/search", params={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]

    disabled_functions_count = sum(
        function.app_id == dummy_functions[0].app_id for function in dummy_functions
    )
    assert disabled_functions_count > 0, "there should be at least one disabled function"
    assert (
        len(functions) == len(dummy_functions) - disabled_functions_count
    ), "all functions under disabled apps should not be returned"

    # revert changes
    crud.set_app_enabled_status(db_session, dummy_functions[0].app_id, True)
    db_session.commit()


def test_search_functions_with_private_functions(
    db_session: Session,
    test_client: TestClient,
    dummy_project: sql_models.Project,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
) -> None:
    # private functions should not be reachable for project with only public access
    crud.set_function_visibility(db_session, dummy_functions[0].id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        "/v1/functions/search", params={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions) - 1

    # private functions should be reachable for project with private access
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        "/v1/functions/search", params={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions)

    # revert changes
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PUBLIC)
    crud.set_function_visibility(db_session, dummy_functions[0].id, sql_models.Visibility.PUBLIC)
    db_session.commit()


def test_search_functions_with_private_apps(
    db_session: Session,
    test_client: TestClient,
    dummy_project: sql_models.Project,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
) -> None:
    # all functions (public and private) under private apps should not be reachable for project with only public access
    crud.set_app_visibility(db_session, dummy_functions[0].app_id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        "/v1/functions/search", params={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]

    private_functions_count = sum(
        function.app_id == dummy_functions[0].app_id for function in dummy_functions
    )
    assert private_functions_count > 0, "there should be at least one private function"
    assert (
        len(functions) == len(dummy_functions) - private_functions_count
    ), "all functions under private apps should not be returned"

    # all functions (public and private) under private apps should be reachable for project with private access
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        "/v1/functions/search", params={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions)

    # revert changes
    crud.set_app_visibility(db_session, dummy_functions[0].app_id, sql_models.Visibility.PUBLIC)
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PUBLIC)
    db_session.commit()


def test_search_functions_with_app_names(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:
    search_param = {
        "app_names": [GITHUB, GOOGLE],
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    # only github and google functions should be returned
    for function in functions:
        assert function.name.startswith(GITHUB) or function.name.startswith(GOOGLE)
    # total number of functions should be the sum of functions of GITHUB and GOOGLE from dummy_functions
    assert len(functions) == sum(
        function.name.startswith(GITHUB) or function.name.startswith(GOOGLE)
        for function in dummy_functions
    )


def test_search_functions_with_intent(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:

    # intent1: create repo
    search_param = {
        "intent": "i want to create a new code repo for my project",
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions)
    assert functions[0].name == GITHUB__CREATE_REPOSITORY

    # intent2: upload file
    search_param["intent"] = "add this meeting to my calendar"
    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions)
    assert functions[0].name == GOOGLE__CALENDAR_CREATE_EVENT


def test_search_functions_with_app_names_and_intent(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:
    search_param = {
        "app_names": [GITHUB],
        "intent": "i want to create a new code repo for my project",
        "limit": 100,
        "offset": 0,
    }
    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    # only github functions should be returned
    for function in functions:
        assert function.name.startswith(GITHUB)
    # total number of functions should be the sum of functions of GITHUB from dummy_functions
    assert len(functions) == sum(function.name.startswith(GITHUB) for function in dummy_functions)
    assert functions[0].name == GITHUB__CREATE_REPOSITORY


def test_search_functions_pagination(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:
    assert len(dummy_functions) > 2

    search_param = {
        "limit": len(dummy_functions) - 1,
        "offset": 0,
    }

    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions) - 1

    search_param["offset"] = len(dummy_functions) - 1
    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        FunctionPublic.model_validate(response_function) for response_function in response.json()
    ]
    assert len(functions) == 1


def test_get_function(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:
    function_name = GITHUB__CREATE_REPOSITORY
    response = test_client.get(
        f"/v1/functions/{function_name}", headers={"x-api-key": dummy_api_key}
    )

    assert response.status_code == 200, response.json()
    function = FunctionDefinitionPublic.model_validate(response.json())
    assert function.name == function_name
    # check if parameters and description are the same as the same function from dummy_functions
    dummy_function = next(
        function for function in dummy_functions if function.name == function_name
    )
    assert function.parameters == dummy_function.parameters
    assert function.description == dummy_function.description


def test_get_function_with_private_function(
    db_session: Session,
    test_client: TestClient,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
    dummy_project: sql_models.Project,
) -> None:
    # private function should not be reachable for project with only public access
    crud.set_function_visibility(db_session, dummy_functions[0].id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        f"/v1/functions/{dummy_functions[0].name}", headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 404, response.json()

    # should be reachable for project with private access
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        f"/v1/functions/{dummy_functions[0].name}", headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()

    # revert changes
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PUBLIC)
    crud.set_function_visibility(db_session, dummy_functions[0].id, sql_models.Visibility.PUBLIC)
    db_session.commit()


def test_get_function_with_private_app(
    db_session: Session,
    test_client: TestClient,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
    dummy_project: sql_models.Project,
) -> None:
    # public function under private app should not be reachable for project with only public access
    crud.set_app_visibility(db_session, dummy_functions[0].app_id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        f"/v1/functions/{dummy_functions[0].name}", headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 404, response.json()

    # should be reachable for project with private access
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PRIVATE)
    db_session.commit()

    response = test_client.get(
        f"/v1/functions/{dummy_functions[0].name}", headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()

    # revert changes
    crud.set_app_visibility(db_session, dummy_functions[0].app_id, sql_models.Visibility.PUBLIC)
    crud.set_project_visibility_access(db_session, dummy_project.id, sql_models.Visibility.PUBLIC)
    db_session.commit()


def test_get_function_with_disabled_function(
    db_session: Session,
    test_client: TestClient,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
) -> None:
    # disabled function should not be reachable
    crud.set_function_enabled_status(db_session, dummy_functions[0].id, False)
    db_session.commit()

    response = test_client.get(
        f"/v1/functions/{dummy_functions[0].name}", headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 404, response.json()

    # revert changes
    crud.set_function_enabled_status(db_session, dummy_functions[0].id, True)
    db_session.commit()


def test_get_function_with_disabled_app(
    db_session: Session,
    test_client: TestClient,
    dummy_functions: list[sql_models.Function],
    dummy_api_key: str,
) -> None:
    # functions (public or private) under disabled app should not be reachable
    crud.set_app_enabled_status(db_session, dummy_functions[0].app_id, False)
    db_session.commit()

    response = test_client.get(
        f"/v1/functions/{dummy_functions[0].name}", headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 404, response.json()

    # revert changes
    crud.set_app_enabled_status(db_session, dummy_functions[0].app_id, True)
    db_session.commit()


def test_get_function_definition_openai(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:
    function_name = GITHUB__CREATE_REPOSITORY
    response = test_client.get(
        f"/v1/functions/{function_name}/definition",
        params={"inference_provider": "openai"},
        headers={"x-api-key": dummy_api_key},
    )
    assert response.status_code == 200, response.json()
    response_json = response.json()
    # "strict" field should not be set unless structured outputs are enabled
    assert "strict" not in response_json["function"]
    function_definition = OpenAIFunctionDefinition.model_validate(response_json)
    assert function_definition.type == "function"
    assert function_definition.function.name == function_name
    # check if content is the same as the same function from dummy_functions
    dummy_function = next(
        function for function in dummy_functions if function.name == function_name
    )
    assert function_definition.function.parameters == dummy_function.parameters
    assert function_definition.function.description == dummy_function.description


def test_get_function_definition_anthropic(
    test_client: TestClient, dummy_functions: list[sql_models.Function], dummy_api_key: str
) -> None:
    function_name = GOOGLE__CALENDAR_CREATE_EVENT
    response = test_client.get(
        f"/v1/functions/{function_name}/definition",
        params={"inference_provider": "anthropic"},
        headers={"x-api-key": dummy_api_key},
    )
    assert response.status_code == 200, response.json()
    function_definition = AnthropicFunctionDefinition.model_validate(response.json())
    assert function_definition.name == function_name
    # check if parameters and description are the same as the same function from dummy_functions
    dummy_function = next(
        function for function in dummy_functions if function.name == function_name
    )
    assert function_definition.input_schema == dummy_function.parameters
    assert function_definition.description == dummy_function.description


def test_execute_function_with_invalid_input(test_client: TestClient, dummy_api_key: str) -> None:
    function_name = AIPOLABS_TEST__HELLO_WORLD_WITH_ARGS
    body = {"function_input": {"name": "John"}}
    response = test_client.post(
        f"/v1/functions/{function_name}/execute", json=body, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 400, response.json()


@responses.activate
def test_mock_execute_function_with_no_args(test_client: TestClient, dummy_api_key: str) -> None:
    # Mock the HTTP endpoint
    response_data = {"message": "Hello, test_mock_execute_function_with_no_args!"}
    responses.add(
        responses.GET,
        "https://api.mock.aipolabs.com/v1/hello_world_no_args",
        json=response_data,
        status=200,
    )

    function_name = AIPOLABS_TEST__HELLO_WORLD_NO_ARGS
    response = test_client.post(
        f"/v1/functions/{function_name}/execute", json={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    assert "error" not in response.json()
    function_execution_response = FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == response_data


@responses.activate
def test_execute_function_with_args(test_client: TestClient, dummy_api_key: str) -> None:
    # Mock the HTTP endpoint
    mock_response_data = {"message": "Hello, test_execute_function_with_args!"}

    # Create a callback to verify request details
    def request_callback(request: PreparedRequest) -> tuple[int, dict, str]:
        # Parse URL to verify components separately
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)

        # Verify base URL and path
        assert (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            == "https://api.mock.aipolabs.com/v1/greet/John"
        )

        # Verify query parameters
        assert query_params == {"lang": ["en"]}

        # Verify body
        assert request.body == b'{"name": "John", "greeting": "Hello"}'

        # Verify headers
        assert request.headers["X-CUSTOM-HEADER"] == "header123"

        # Verify cookies
        assert request.headers["Cookie"] == "sessionId=session123"

        return (200, {}, json.dumps(mock_response_data))

    responses.add_callback(
        method=responses.POST,
        url="https://api.mock.aipolabs.com/v1/greet/John",
        callback=request_callback,
    )

    function_name = AIPOLABS_TEST__HELLO_WORLD_WITH_ARGS
    function_execution_request_body = {
        "function_input": {
            "path": {"userId": "John"},
            "query": {"lang": "en"},
            "body": {"name": "John", "greeting": "Hello"},
            "header": {"X-CUSTOM-HEADER": "header123"},
            "cookie": {"sessionId": "session123"},
        }
    }
    response = test_client.post(
        f"/v1/functions/{function_name}/execute",
        json=function_execution_request_body,
        headers={"x-api-key": dummy_api_key},
    )
    assert response.status_code == 200, response.json()
    assert "error" not in response.json()
    function_execution_response = FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == mock_response_data


@responses.activate
def test_execute_function_with_nested_args(test_client: TestClient, dummy_api_key: str) -> None:
    # Mock the HTTP endpoint
    mock_response_data = {"message": "Hello, test_execute_function_with_args!"}

    # Create a callback to verify request details
    def request_callback(request: PreparedRequest) -> tuple[int, dict, str]:
        # Parse URL to verify components separately
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)

        # Verify base URL and path
        assert (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            == "https://api.mock.aipolabs.com/v1/greet/John"
        )

        # Verify query parameters
        assert query_params == {"lang": ["cn"]}

        # Verify body
        assert (
            request.body
            == b'{"person": {"name": "John", "title": "Mr"}, "greeting": "Hello", "location": {"city": "New York", "country": "USA"}}'
        )

        return (200, {}, json.dumps(mock_response_data))

    responses.add_callback(
        method=responses.POST,
        url="https://api.mock.aipolabs.com/v1/greet/John",
        callback=request_callback,
    )

    function_name = AIPOLABS_TEST__HELLO_WORLD_NESTED_ARGS
    function_execution_request_body = {
        "function_input": {
            "path": {"userId": "John"},
            "query": {"lang": "cn"},
            "body": {
                "person": {"name": "John", "title": "Mr"},
                "greeting": "Hello",
                "location": {"city": "New York", "country": "USA"},
            },
        }
    }
    response = test_client.post(
        f"/v1/functions/{function_name}/execute",
        json=function_execution_request_body,
        headers={"x-api-key": dummy_api_key},
    )
    assert response.status_code == 200, response.json()
    assert "error" not in response.json()
    function_execution_response = FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == mock_response_data
