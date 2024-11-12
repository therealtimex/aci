import json
from pathlib import Path

import click

from aipolabs.cli import config
from aipolabs.common import embeddings, utils
from aipolabs.common.db import crud
from aipolabs.common.logging import get_logger
from aipolabs.common.openai_service import OpenAIService
from aipolabs.common.schemas.app import AppCreate

logger = get_logger(__name__)
openai_service = OpenAIService(
    config.OPENAI_API_KEY, config.OPENAI_EMBEDDING_MODEL, config.OPENAI_EMBEDDING_DIMENSION
)


@click.command()
@click.option(
    "--app-file",
    "app_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the app json file",
)
@click.option(
    "--skip-dry-run",
    is_flag=True,
    help="provide this flag to run the command and apply changes to the database",
)
def create_app(app_file: Path, skip_dry_run: bool) -> None:
    """Create App in db from file."""
    with utils.create_db_session(config.DB_FULL_URL) as db_session:
        with open(app_file, "r") as f:
            app: AppCreate = AppCreate.model_validate(json.load(f))
            app_embedding = embeddings.generate_app_embedding(app, openai_service)

        db_app = crud.create_app(db_session, app, app_embedding)
        if not skip_dry_run:
            logger.info(
                f"provide --skip-dry-run to insert new app {db_app.name} with app data \n{app.model_dump_json(indent=2)}"
            )
            db_session.rollback()
        else:
            logger.info(f"committing insert of new app: {db_app.name}")
            db_session.commit()
            logger.info("success!")


# def construct_request(base_url: str, path: str, method: str, parameters: dict) -> requests.Request:
#     """Construct a request object based on function parameters."""
#     parameters = {
#         "path": {
#             "userId": "user_12345",
#         },
#         "query": {
#             "verbose": True,
#             "freeForm": {
#                 "search_term_1": 1,
#                 "search_term_2": 2,
#             },
#         },
#         "header": {
#             "token": [987654321],
#             "X-Custom-Header": "MyCustomHeaderValue",
#         },
#         "cookie": {
#             "session_id": "session_67890",
#         },
#         "body": {
#             "id": "123",
#             "item": "Laptop",
#             "quantity": 1,
#             "price": 999.99,
#         },
#     }

#     # Extract parameters by location
#     path_params = parameters.get("path", {})
#     query_params = parameters.get("query", {})
#     headers = parameters.get("header", {})
#     cookies = parameters.get("cookie", {})
#     body = parameters.get("body")

#     # Construct URL with path parameters
#     url = f"{base_url}/{path}"
#     if path_params:
#         # Replace path parameters in URL
#         for param_name, param_value in path_params.items():
#             url = url.replace(f"{{{param_name}}}", str(param_value))

#     # Create request object
#     request = requests.Request(
#         method=method,
#         url=url,
#         params=query_params,
#         headers=headers,
#         cookies=cookies,
#         json=body if body else None,
#     )

#     # print request in nice format
#     logger.info(f"======================== REQUEST ========================")
#     logger.info(request.prepare())
#     return request


# def execute_function(base_url: str, schema: dict) -> requests.Response:
#     """Execute a function based on its schema."""
#     function_name = schema["function"]["name"]
#     parameters = schema["function"]["parameters"]

#     # Construct request
#     request = construct_request(base_url, function_name, parameters)

#     # Prepare and send request
#     session = requests.Session()
#     prepped = session.prepare_request(request)

#     # For debugging
#     logger.info(f"URL: {prepped.url}")
#     logger.info(f"Headers: {prepped.headers}")
#     logger.info(f"Body: {prepped.body}")

#     return session.send(prepped)
