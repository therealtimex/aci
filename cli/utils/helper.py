import re

from cli.utils.logging import get_logger

logger = get_logger()


# convert a string with spaces, hyphens, slashes, camel case etc. to screaming snake case
def format_to_screaming_snake_case(name: str) -> str:
    name = re.sub(r"[\W]+", "_", name)  # Replace non-alphanumeric characters with underscore
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    s3 = s2.replace("-", "_").replace("/", "_").replace(" ", "_")
    s3 = re.sub("_+", "_", s3)  # Replace multiple underscores with single underscore
    s4 = s3.upper().strip("_")

    logger.info(f"Formatted {name} to {s4}")

    return s4
