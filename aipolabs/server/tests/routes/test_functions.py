from fastapi.testclient import TestClient

from aipolabs.common import sql_models
from aipolabs.server import schemas

GOOGLE__CALENDAR_CREATE_EVENT = "GOOGLE__CALENDAR_CREATE_EVENT"
GITHUB__CREATE_REPOSITORY = "GITHUB__CREATE_REPOSITORY"
AIPOLABS_TEST__HELLO_WORLD = "AIPOLABS_TEST__HELLO_WORLD"
AIPOLABS_TEST__HELLO_WORLD_NESTED_ARGS = "AIPOLABS_TEST__HELLO_WORLD_NESTED_ARGS"
AIPOLABS_TEST__HELLO_WORLD_NO_ARGS = "AIPOLABS_TEST__HELLO_WORLD_NO_ARGS"
GITHUB = "GITHUB"
GOOGLE = "GOOGLE"


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
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
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
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
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
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
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
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
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
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
    ]
    assert len(functions) == len(dummy_functions) - 1

    search_param["offset"] = len(dummy_functions) - 1
    response = test_client.get(
        "/v1/functions/search", params=search_param, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    functions = [
        schemas.FunctionBasicPublic.model_validate(response_function)
        for response_function in response.json()
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
    function = schemas.FunctionPublic.model_validate(response.json())
    assert function.name == function_name
    # check if parameters and description are the same as the same function from dummy_functions
    dummy_function = next(
        function for function in dummy_functions if function.name == function_name
    )
    assert function.parameters == dummy_function.parameters
    assert function.description == dummy_function.description


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
    function_definition = schemas.OpenAIFunctionDefinition.model_validate(response_json)
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
    function_definition = schemas.AnthropicFunctionDefinition.model_validate(response.json())
    assert function_definition.name == function_name
    # check if parameters and description are the same as the same function from dummy_functions
    dummy_function = next(
        function for function in dummy_functions if function.name == function_name
    )
    assert function_definition.input_schema == dummy_function.parameters
    assert function_definition.description == dummy_function.description


def test_execute_function(test_client: TestClient, dummy_api_key: str) -> None:
    function_name = AIPOLABS_TEST__HELLO_WORLD
    body = {"function_input": {"name": "John", "greeting": "Hello"}}
    response = test_client.post(
        f"/v1/functions/{function_name}/execute", json=body, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    assert "error" not in response.json()
    function_execution_response = schemas.FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == {"message": "Hello, John!"}


def test_execute_function_with_invalid_input(test_client: TestClient, dummy_api_key: str) -> None:
    function_name = AIPOLABS_TEST__HELLO_WORLD
    body = {"function_input": {"name": "John"}}
    response = test_client.post(
        f"/v1/functions/{function_name}/execute", json=body, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 400, response.json()


def test_execute_function_with_nested_args(test_client: TestClient, dummy_api_key: str) -> None:
    function_name = AIPOLABS_TEST__HELLO_WORLD_NESTED_ARGS
    body = {
        "function_input": {
            "person": {"name": "John", "title": "Mr"},
            "greeting": "Hello",
            "location": {"city": "New York", "country": "USA"},
        }
    }
    response = test_client.post(
        f"/v1/functions/{function_name}/execute", json=body, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    assert "error" not in response.json()
    function_execution_response = schemas.FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == {"message": "Hello, Mr John in New York, USA!"}


def test_execute_function_with_no_args(test_client: TestClient, dummy_api_key: str) -> None:
    # empty body
    function_name = AIPOLABS_TEST__HELLO_WORLD_NO_ARGS
    response = test_client.post(
        f"/v1/functions/{function_name}/execute", json={}, headers={"x-api-key": dummy_api_key}
    )
    assert response.status_code == 200, response.json()
    function_execution_response = schemas.FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == {"message": "Hello, world!"}

    # empty function_input
    response = test_client.post(
        f"/v1/functions/{function_name}/execute",
        json={"function_input": {}},
        headers={"x-api-key": dummy_api_key},
    )
    assert response.status_code == 200, response.json()
    function_execution_response = schemas.FunctionExecutionResponse.model_validate(response.json())
    assert function_execution_response.success
    assert function_execution_response.data == {"message": "Hello, world!"}
