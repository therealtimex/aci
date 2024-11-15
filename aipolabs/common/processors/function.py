import copy


def filter_visible_properties(parameters: dict) -> dict:
    """
    Filter the schema to include only visible properties and remove the 'visible' field itself.
    """
    # Create a deep copy of the schema to avoid modifying the original input
    filtered_parameters = copy.deepcopy(parameters)
    if filtered_parameters.get("type") != "object":
        return filtered_parameters

    # Get the visible list
    visible = filtered_parameters.pop("visible", [])

    # Filter properties to include only visible properties
    properties = filtered_parameters.get("properties", {})
    filtered_properties = {key: value for key, value in properties.items() if key in visible}

    # Recursively filter nested properties
    for key, value in filtered_properties.items():
        if value.get("type") == "object":
            filtered_properties[key] = filter_visible_properties(value)

    # Update the schema with filtered properties
    filtered_parameters["properties"] = filtered_properties

    return filtered_parameters
