import os

from dotenv import load_dotenv

load_dotenv()


def check_and_get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not set")
    if value == "":
        raise ValueError(f"Environment variable '{name}' is empty string")
    return value


JWT_SECRET_KEY = check_and_get_env_variable("APP_JWT_SECRET_KEY")
JWT_ALGORITHM = check_and_get_env_variable("APP_JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    check_and_get_env_variable("APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
)
SESSION_SECRET_KEY = check_and_get_env_variable("APP_SESSION_SECRET_KEY")
AIPOLABS_REDIRECT_URI_BASE = check_and_get_env_variable("APP_AIPOLABS_REDIRECT_URI_BASE")

# Google Auth
GOOGLE_AUTH_CLIENT_ID = check_and_get_env_variable("APP_GOOGLE_AUTH_CLIENT_ID")
GOOGLE_AUTH_CLIENT_SECRET = check_and_get_env_variable("APP_GOOGLE_AUTH_CLIENT_SECRET")
GOOGLE_AUTH_AUTHORIZE_URL = check_and_get_env_variable("APP_GOOGLE_AUTH_AUTHORIZE_URL")
GOOGLE_AUTH_ACCESS_TOKEN_URL = check_and_get_env_variable(
    "APP_GOOGLE_AUTH_ACCESS_TOKEN_URL"
)  # refresh token (if needed in the future) link is the same
GOOGLE_AUTH_API_BASE_URL = check_and_get_env_variable("APP_GOOGLE_AUTH_API_BASE_URL")
GOOGLE_AUTH_SERVER_METADATA_URL = check_and_get_env_variable("APP_GOOGLE_AUTH_SERVER_METADATA_URL")
GOOGLE_AUTH_CLIENT_KWARGS = {
    "scope": "openid email profile",
    "prompt": "consent",  # Force the user to consent again (help if need to get the refresh token)
}
DB_SCHEME = check_and_get_env_variable("APP_DB_SCHEME")
DB_USER = check_and_get_env_variable("APP_DB_USER")
DB_PASSWORD = check_and_get_env_variable("APP_DB_PASSWORD")
DB_HOST = check_and_get_env_variable("APP_DB_HOST")
DB_PORT = check_and_get_env_variable("APP_DB_PORT")
DB_NAME = check_and_get_env_variable("APP_DB_NAME")
# need to use "+psycopg" to use psycopg3 instead of psycopg2 (default)
DB_FULL_URL = f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
