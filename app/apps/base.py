import importlib
from abc import ABC
from typing import Type

from jsonschema import ValidationError, validate

from app import schemas
from app.logging import get_logger

logger = get_logger(__name__)


# custom exception
class InvalidFunctionNameException(Exception):
    pass


def parse_function_name(function_name: str) -> tuple[str, str, str]:
    """
    Parse function name to get module name, class name and method name.
    e.g. "AIPOLABS_TEST__HELLO_WORLD" -> "app.apps.aipolabs_test", "AipolabsTest", "hello_world"
    """
    try:
        app_name, method_name = function_name.split("__", 1)
        module_name = f"app.apps.{app_name.lower()}"
        class_name = "".join(word.capitalize() for word in app_name.split("_"))
        method_name = method_name.lower()

        return module_name, class_name, method_name
    except Exception as e:
        logger.exception(f"failed to parse function name: {function_name}")
        raise InvalidFunctionNameException(f"failed to parse function name: {function_name}") from e


class AppBase(ABC):
    # TODO: init with end user account credentials

    # TODO: retry?
    def execute(self, function_name: str, args: dict) -> schemas.FunctionExecutionResponse:
        _, _, method_name = parse_function_name(function_name)
        method = getattr(self, method_name, None)
        if not method:
            raise ValueError(f"Method '{method_name}' not found in {self.__class__.__name__}.")

        try:
            logger.info(
                f"executing method {method_name} in {self.__class__.__name__} with args: {args}"
            )
            result = method(**args)
            logger.info(f"execution result: \n {result}")
            return schemas.FunctionExecutionResponse(success=True, data=result)
        except Exception as e:
            logger.exception(f"error executing method {method_name} in {self.__class__.__name__}")
            return schemas.FunctionExecutionResponse(success=False, error=str(e))

    @staticmethod
    def validate_input(function_parameters_schema: dict, function_input: dict) -> None:
        try:
            validate(instance=function_input, schema=function_parameters_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid input: {e.message}") from e


class AppFactory:
    # TODO: caching? singleton per app per enduser account? executing in a thread pool?

    def get_app_instance(self, function_name: str) -> AppBase:

        module_name, class_name, _ = parse_function_name(function_name)

        try:
            app_class: Type[AppBase] = getattr(importlib.import_module(module_name), class_name)
            logger.info(f"found app class for {function_name}: {app_class}")
            app_instance: AppBase = app_class()
            return app_instance
        except (ModuleNotFoundError, AttributeError) as e:
            logger.exception(f"failed to find app class for {function_name}")
            raise InvalidFunctionNameException(
                f"failed to find app class for {function_name}"
            ) from e
