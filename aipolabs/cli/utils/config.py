import os

from dotenv import load_dotenv

from aipolabs.cli.utils.logging import get_logger

logger = get_logger(__name__)

load_dotenv()


def check_and_get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    if value == "":
        raise ValueError(f"Environment variable '{name}' is empty string")
    return value


# TODO: any way to unify cli and app's db config?
OPENAI_API_KEY = check_and_get_env_variable("CLI_OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = check_and_get_env_variable("CLI_OPENAI_EMBEDDING_MODEL")
EMBEDDING_DIMENSION = int(check_and_get_env_variable("CLI_EMBEDDING_DIMENSION"))
DB_SCHEME = check_and_get_env_variable("CLI_DB_SCHEME")
DB_USER = check_and_get_env_variable("CLI_DB_USER")
DB_PASSWORD = check_and_get_env_variable("CLI_DB_PASSWORD")
DB_HOST = check_and_get_env_variable("CLI_DB_HOST")
DB_PORT = check_and_get_env_variable("CLI_DB_PORT")
DB_NAME = check_and_get_env_variable("CLI_DB_NAME")
DB_FULL_URL = f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
