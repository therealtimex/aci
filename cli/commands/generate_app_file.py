# import click
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from sqlalchemy.exc import IntegrityError
# from database import models
# from cli.utils.logging import get_logger
# from cli.utils import config
# import yaml
# import json
# import re
# import os
# from openapi_spec_validator import validate
# from openai import OpenAI
# from sqlalchemy.orm import Session
# from sqlalchemy import select
# from typing import Any, cast
# import copy


# SessionMaker = sessionmaker(
#     autocommit=False, autoflush=False, bind=create_engine(config.DB_FULL_URL)
# )
# LLM_CLIENT = OpenAI(api_key=config.OPENAI_API_KEY)


# def validate_app_config(app_config: dict):
#     required_fields = ["name", "display_name", "provider", "description", "categories", "tags"]
#     missing_fields = [field for field in required_fields if field not in app_config]
#     if missing_fields:
#         raise ValueError(f"Missing required fields in app definition: {', '.join(missing_fields)}")


# def validate_openapi_spec(app_openapi: dict[str, Any]) -> None:
#     # If no exception is raised by validate(), the spec is valid.
#     validate(app_openapi)
#     paths: dict[str, Any] = app_openapi.get("paths", {})
#     # make sure each path (and each method in each path) has an operationId
#     for path, path_item in paths.items():
#         path_item = cast(dict[str, Any], path_item)
#         for method, method_item in path_item.items():
#             if "operationId" not in method_item:
#                 raise ValueError(f"OperationId is required for method {method} in path {path}")

#     # make sure each operation has a description or summary
#     for path, path_item in paths.items():
#         path_item = cast(dict[str, Any], path_item)
#         for method, method_item in path_item.items():
#             if "description" not in method_item and "summary" not in method_item:
#                 raise ValueError(
#                     f"Description or summary is required for method {method} in path {path}"
#                 )


# def generate_app_embedding(app_config: dict):
#     # generate app embeddings based on app config's name, display_name, provider, description, categories, and tags
#     app_text_for_embedding = (
#         f"{app_config['name']}\n"
#         f"{app_config['display_name']}\n"
#         f"{app_config['provider']}\n"
#         f"{app_config['description']}\n"
#         f"{' '.join(app_config['categories'])}\n"
#         f"{' '.join(app_config['tags'])}"
#     )
#     response = LLM_CLIENT.embeddings.create(
#         input=app_text_for_embedding,
#         model=config.OPENAI_EMBEDDING_MODEL,
#         dimensions=config.EMBEDDING_DIMENSION,
#     )
#     embedding = response.data[0].embedding
#     return embedding


# def format_to_screaming_snake_case(name: str) -> str:
#     # Convert to uppercase with underscores
#     name = re.sub(r"[\W]+", "_", name)  # Replace non-alphanumeric characters with underscore
#     s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
#     s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
#     s3 = s2.replace("-", "_").replace("/", "_").replace(" ", "_")
#     s3 = re.sub("_+", "_", s3)  # Replace multiple underscores with single underscore
#     return s3.upper().strip("_")


# def get_app_to_upsert(
#     app_config: dict[str, dict[str, Any]],
#     app_openapi: dict[str, dict[str, Any]],
# ) -> models.App:
#     app_embedding = generate_app_embedding(app_config)
#     supported_auth_schemes: dict[str, dict[str, Any]] = app_config.get("supported_auth_schemes", {})
#     auth_required = bool(supported_auth_schemes)
#     server_url: str = app_openapi["servers"][0]["url"]

#     app_attributes = {
#         "name": app_config["name"],
#         "display_name": app_config["display_name"],
#         "provider": app_config["provider"],
#         "description": app_config["description"],
#         "server_url": server_url,
#         "logo": app_config.get("logo", None),
#         "categories": app_config["categories"],
#         "tags": app_config["tags"],
#         "auth_required": auth_required,
#         "supported_auth_types": list(supported_auth_schemes.keys()),
#         "auth_configs": supported_auth_schemes,
#         "embedding": app_embedding,
#     }
#     return models.App(**app_attributes)

#     # existing_app = db_session.execute(
#     #     select(models.App).filter_by(name=app_config["name"])
#     # ).scalar_one_or_none()

#     # if existing_app:
#     #     for key, value in app_attributes.items():
#     #         setattr(existing_app, key, value)
#     #     app = existing_app
#     #     logger.info(f"Updated existing app: {app_config['name']}")
#     # else:
#     #     app = models.App(name=app_config["name"], **app_attributes)
#     #     db_session.add(app)
#     #     logger.info(f"Created new app: {app_config['name']}")

#     # return app


# def resolve_ref(ref: str, spec: dict[str, Any]) -> Any:
#     if not ref.startswith("#/"):
#         raise ValueError(f"Unsupported $ref format: {ref}")
#     parts = ref.lstrip("#/").split("/")
#     obj = spec
#     for part in parts:
#         if part not in obj:
#             raise KeyError(f"Reference '{ref}' cannot be resolved: '{part}' not found.")
#         obj = obj[part]
#     if "$ref" in obj:
#         return resolve_refs(obj, spec)
#     return obj


# def resolve_refs(obj: Any, spec: dict[str, Any], visited: set[str] = None) -> Any:
#     if visited is None:
#         visited = set()
#     if isinstance(obj, dict):
#         if "$ref" in obj:
#             ref = obj["$ref"]
#             if ref in visited:
#                 raise ValueError(f"Circular reference detected: {ref}")
#             visited.add(ref)
#             resolved = resolve_ref(ref, spec)
#             # Merge the resolved object with other keys if present
#             new_obj = {k: v for k, v in obj.items() if k != "$ref"}
#             resolved = resolve_refs(resolved, spec, visited)
#             merged = {**resolved, **new_obj}
#             return merged
#         else:
#             return {k: resolve_refs(v, spec, visited.copy()) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [resolve_refs(item, spec, visited.copy()) for item in obj]
#     else:
#         return obj


# def extract_parameters(operation: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
#     params = operation.get("parameters", [])
#     resolved_params = []
#     for param in params:
#         resolved_param = resolve_refs(param, spec)
#         resolved_params.append(resolved_param)
#     return resolved_params


# def extract_request_body(operation: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
#     request_body = operation.get("requestBody")
#     if request_body:
#         return resolve_refs(request_body, spec)
#     return None


# def build_parameters_schema(
#     resolved_params: list[dict[str, Any]], resolved_body: dict[str, Any], spec: dict[str, Any]
# ) -> dict[str, Any]:

#     properties: dict[str, Any] = {}
#     required: list[str] = []

#     for param in resolved_params:
#         name = param["name"]
#         param_schema: dict[str, Any] = resolve_refs(param.get("schema", {}), spec)
#         if not param_schema:
#             continue
#         if param.get("required"):
#             required.append(name)
#         param_schema["description"] = param.get("description", "")
#         param_schema["title"] = param.get("title", name)
#         properties[name] = param_schema

#     if resolved_body:
#         content: dict[str, Any] = resolved_body.get("content", {})
#         for media_type, media_spec in content.items():
#             body_schema: dict[str, Any] = media_spec.get("schema", {})
#             body_schema_resolved: dict[str, Any] = resolve_refs(body_schema, spec)
#             if "required" in body_schema_resolved:
#                 required_fields: list[str] = body_schema_resolved["required"]
#                 required.extend(required_fields)
#             if "properties" in body_schema_resolved:
#                 properties.update(body_schema_resolved["properties"])
#             else:
#                 # For schemas that are not objects
#                 properties["body"] = body_schema_resolved
#                 required.append("body")
#             break  # Assuming only one media type

#     schema = {
#         "type": "object",
#         "properties": properties,
#         "required": required,
#     }
#     return schema


# # TODO: type casting rabit hole
# def get_functions_to_upsert(app: models.App, openapi_spec: dict[str, Any]) -> list[models.Function]:
#     logger.info(f"Processing functions for app: {app.name}")
#     paths: dict[str, Any] = openapi_spec["paths"]
#     # components: dict[str, Any] = openapi_spec.get("components", {})

#     # functions_to_upsert = []

#     for path, methods in paths.items():
#         methods = cast(dict[str, Any], methods)
#         for http_method, operation in methods.items():
#             operation = cast(dict[str, Any], operation)
#             # Skip non-standard HTTP methods
#             if http_method.lower() not in [
#                 "get",
#                 "post",
#                 "put",
#                 "delete",
#                 "patch",
#                 "options",
#                 "head",
#             ]:
#                 logger.warning(f"Skipping non-standard HTTP method: {http_method.upper()}")
#                 continue

#             operation_id: str = operation["operationId"]
#             # combine summary and description if both exist
#             description = operation.get("description", "") + "\n" + operation.get("summary", "")
#             function_name: str = format_to_screaming_snake_case(f"{app.name}_{operation_id}")

#             resolved_params = extract_parameters(operation, openapi_spec)
#             resolved_body = extract_request_body(operation, openapi_spec)
#             parameters_schema = build_parameters_schema(
#                 resolved_params, resolved_body, openapi_spec
#             )
#             logger.info(
#                 f"operation_id: {operation_id}, description: {description}, function_name: {function_name}"
#             )
#             # logger.info(f"Resolved params: {resolved_params}")
#             # logger.info(f"Resolved body: {resolved_body}")
#             logger.info(f"Parameters schema: {parameters_schema}")
#             ###########################################################################

#             # # Extract parameters and response schemas
#             # parameters_schema = extract_request_parameters(operation, components)
#             # response_schema = extract_response(operation, components)
#             # # Generate Function embedding
#             # parameters_text = json.dumps(parameters_schema)
#             # function_text_for_embedding = f"{function_name}\n{description}\n{parameters_text}"
#             # function_embedding = generate_embedding(function_text_for_embedding)

#             # # Create or update Function record
#             # create_or_update_function(
#             #     session,
#             #     app,
#             #     function_name,
#             #     description,
#             #     parameters_schema,
#             #     response_schema,
#             #     function_embedding,
#             # )


# @click.command()
# @click.option(
#     "--app-config-file",
#     "app_config_file",
#     required=True,
#     type=click.Path(exists=True),
#     help="Path to app config YAML file",
# )
# @click.option(
#     "--openapi-file",
#     "openapi_file",
#     required=True,
#     type=click.Path(exists=True),
#     help="Path to OpenAPI spec file (JSON or YAML)",
# )
# def generate_app_file(app_config_file: str, openapi_file: str):
#     with open(app_config_file, "r") as f:
#         app_config: dict[str, dict[str, Any]] = yaml.safe_load(f)

#     with open(openapi_file, "r") as f:
#         if openapi_file.endswith(".json"):
#             app_openapi: dict[str, dict[str, Any]] = json.load(f)
#         else:
#             app_openapi: dict[str, dict[str, Any]] = yaml.safe_load(f)

#     # Validations
#     validate_app_config(app_config)
#     validate_openapi_spec(app_openapi)
#     # prepare app and functions database records to upsert
#     app = get_app_to_upsert(app_config, app_openapi)
#     get_functions_to_upsert(app, app_openapi)

#     # """Index App and Functions from OpenAPI spec and app definition file."""
#     # with SessionMaker() as db_session:
#     #     try:
#     #         # Parse files
#     #         with open(app_config_file, "r") as f:
#     #             app_config: dict[str, dict[str, Any]] = yaml.safe_load(f)

#     #         with open(openapi_file, "r") as f:
#     #             if openapi_file.endswith(".json"):
#     #                 app_openapi: dict[str, dict[str, Any]] = json.load(f)
#     #             else:
#     #                 app_openapi: dict[str, dict[str, Any]] = yaml.safe_load(f)
#     #         # Validations
#     #         validate_app_config(app_config)
#     #         validate_openapi_spec(app_openapi)

#     #         # prepare app and functions database records to upsert
#     #         app = get_app_to_upsert(db_session, app_config, app_openapi)
#     #         # ensure app id is generated
#     #         db_session.add(app)
#     #         db_session.flush()
#     #         db_session.refresh(app)
#     #         get_functions_to_upsert(app, app_openapi)

#     #         # Commit all changes
#     #         db_session.commit()
#     #         click.echo("App and functions indexed successfully.")

#     #     except Exception as e:
#     #         db_session.rollback()
#     #         logger.error(f"Error indexing app and functions: {e}")
#     #         click.echo(f"Error indexing app and functions: {e}")

#     # The session is automatically closed when exiting the 'with' block


# if __name__ == "__main__":
#     main()
