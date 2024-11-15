def validate_function_parameters_schema_common(parameters_schema: dict, path: str) -> None:
    """
    Validate a function parameters schema based on a set of common rules.
    These rules should be true for all types of protocols. (rest, graphql, etc.)
    """
    # Skip if not an object type schema
    if not isinstance(parameters_schema, dict) or parameters_schema.get("type") != "object":
        return

    # Ensure required field exists
    if "required" not in parameters_schema:
        raise ValueError(f"Missing 'required' field at {path}")

    # Ensure visible field exists
    if "visible" not in parameters_schema:
        raise ValueError(f"Missing 'visible' field at {path}")

    properties = parameters_schema.get("properties", {})
    required = parameters_schema.get("required", [])
    visible = parameters_schema.get("visible", [])

    # Check that all required properties actually exist
    for prop in required:
        if prop not in properties:
            raise ValueError(f"Required property '{prop}' at {path} not found in properties")

    # Check that all visible properties actually exist
    for prop in visible:
        if prop not in properties:
            raise ValueError(f"Visible property '{prop}' at {path} not found in properties")

    # Check that non-visible properties have defaults (except for objects)
    for prop_name, prop_schema in properties.items():
        if prop_name not in visible:
            is_object = prop_schema.get("type") == "object"
            if not is_object and "default" not in prop_schema:
                raise ValueError(
                    f"Non-visible property '{prop_name}' at {path} must have a default value"
                )

    # Recursively validate nested objects
    for prop_name, prop_schema in properties.items():
        if isinstance(prop_schema, dict) and prop_schema.get("type") == "object":
            validate_function_parameters_schema_common(prop_schema, f"{path}/{prop_name}")

            # Check if parent should be visible based on children
            child_visible = prop_schema.get("visible", [])
            if not child_visible and prop_name in visible:
                raise ValueError(
                    f"Property '{prop_name}' at {path} cannot be visible when all its children are non-visible"
                )


def validate_function_parameters_schema_rest_protocol(
    parameters_schema: dict, path: str, allowed_top_level_keys: list[str]
) -> None:
    """
    Validate a function parameters schema for the REST protocol, for rules that are not covered by the common rules.
    """
    # Skip if empty schema (happens in some cases, e.g. when function has no parameters)
    if not parameters_schema:
        return

    # type must be "object"
    if parameters_schema.get("type") != "object":
        raise ValueError("top level type must be 'object' for REST protocol's parameters")
    # properties must be a dict and can only have "path", "query", "header", "cookie", "body" keys
    properties = parameters_schema["properties"]
    if not isinstance(properties, dict):
        raise ValueError("'properties' must be a dict for REST protocol's parameters")
    for key in properties.keys():
        if key not in allowed_top_level_keys:
            raise ValueError(
                f"invalid key '{key}' for REST protocol's parameters's top level 'properties'"
            )
    # required must be present and must be a list and can only have keys in "properties"
    required = parameters_schema["required"]
    if not isinstance(required, list):
        raise ValueError("'required' must be a list for REST protocol's parameters")
    for key in required:
        if key not in properties:
            raise ValueError(
                f"key '{key}' in 'required' must be in 'properties' for REST protocol's parameters"
            )
    # additionalProperties must be present and must be false
    if "additionalProperties" not in parameters_schema or not isinstance(
        parameters_schema["additionalProperties"], bool
    ):
        raise ValueError(
            "'additionalProperties' must be present and must be a boolean for REST protocol's parameters"
        )
    if parameters_schema["additionalProperties"]:
        raise ValueError("'additionalProperties' must be false for REST protocol's parameters")
