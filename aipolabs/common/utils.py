import os


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
