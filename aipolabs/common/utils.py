import json
import os
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.app import AppCreate
from aipolabs.common.schemas.function import FunctionCreate

logger = get_logger(__name__)


def check_and_get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    if value == "":
        raise ValueError(f"Environment variable '{name}' is empty string")
    return value


def construct_db_url(
    scheme: str, user: str, password: str, host: str, port: str, db_name: str
) -> str:
    return f"{scheme}://{user}:{password}@{host}:{port}/{db_name}"


def format_to_screaming_snake_case(name: str) -> str:
    """
    Convert a string with spaces, hyphens, slashes, camel case etc. to screaming snake case.
    e.g., "GitHub Create Repository" -> "GITHUB_CREATE_REPOSITORY"
    e.g., "GitHub/Create Repository" -> "GITHUB_CREATE_REPOSITORY"
    e.g., "github-create-repository" -> "GITHUB_CREATE_REPOSITORY"
    """
    name = re.sub(r"[\W]+", "_", name)  # Replace non-alphanumeric characters with underscore
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    s3 = s2.replace("-", "_").replace("/", "_").replace(" ", "_")
    s3 = re.sub("_+", "_", s3)  # Replace multiple underscores with single underscore
    s4 = s3.upper().strip("_")

    return s4


def create_db_session(db_url: str) -> Session:
    SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(db_url))
    return SessionMaker()


# TODO: include response schema in the embedding if added
def generate_function_embedding(
    function: FunctionCreate, openai_service: OpenAIService
) -> list[float]:
    logger.debug(f"Generating embedding for function: {function.name}...")
    text_for_embedding = f"{function.name}\n{function.description}\n{function.parameters}"

    return openai_service.generate_embedding(text_for_embedding)


def generate_app_embedding(app: AppCreate, openai_service: OpenAIService) -> list[float]:
    logger.debug(f"Generating embedding for app: {app.name}...")
    # generate app embeddings based on app config's name, display_name, provider, description, categories
    text_for_embedding = (
        f"{app.name}\n"
        f"{app.display_name}\n"
        f"{app.provider}\n"
        f"{app.description}\n"
        f"{' '.join(app.categories)}"
    )
    return openai_service.generate_embedding(text_for_embedding)


def generate_app_and_functions_from_files(
    app_file: Path, functions_file: Path, openai_service: OpenAIService
) -> tuple[AppCreate, list[float], list[FunctionCreate], list[list[float]]]:
    with open(app_file, "r") as f:
        app: AppCreate = AppCreate.model_validate(json.load(f))
    with open(functions_file, "r") as f:
        functions: list[FunctionCreate] = [
            FunctionCreate.model_validate(function) for function in json.load(f)
        ]

    # TODO: validate app and function name match and function name uniqueness?

    app_embedding = generate_app_embedding(app, openai_service)
    # TODO: generate embeddings in batch
    function_embeddings: list[list[float]] = []
    for function in functions:
        function_embeddings.append(generate_function_embedding(function, openai_service))
    return app, app_embedding, functions, function_embeddings
