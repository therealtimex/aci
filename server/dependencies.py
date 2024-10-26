from typing import Annotated, Generator
from uuid import UUID

from authlib.jose import JoseError, jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import models
from server.config import AOPOLABS_API_KEY_NAME, JWT_SECRET_KEY
from server.db import crud, engine
from server.logging import get_logger

logger = get_logger(__name__)
http_bearer = HTTPBearer(auto_error=True, description="login to receive a JWT token")
api_key_header = APIKeyHeader(
    name=AOPOLABS_API_KEY_NAME, description="API key for authentication", auto_error=True
)


def get_db_session() -> Generator[Session, None, None]:
    db_session = engine.SessionMaker()
    try:
        yield db_session
    finally:
        db_session.close()


def validate_http_bearer(
    auth_data: Annotated[HTTPAuthorizationCredentials, Security(http_bearer)],
) -> UUID:
    """
    Validate HTTP Bearer token and return user ID.
    HTTP Bearer token is generated after a user logs in to dev portal.
    Used for some routes like /projects that should not be accessed programmatically.
    """
    # TODO: remove logging
    logger.warning(f"Validating HTTP Bearer token: {auth_data.credentials}")
    token = auth_data.credentials
    try:
        logger.info("Decoding JWT token.")
        payload = jwt.decode(token, JWT_SECRET_KEY)
        logger.info(f"Decoded token payload: {payload}")
        payload.validate()  # This will raise a JoseError if validation fails

        user_id: str = payload.get("sub")
        if not user_id:
            logger.error("Token is missing 'sub' claim.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        logger.info(f"Token valid. User ID: {user_id}")
        return UUID(user_id)

    except JoseError as e:
        logger.error("Token verification failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )


def validate_api_key(
    db_session: Annotated[Session, Depends(get_db_session)],
    api_key: Annotated[str, Security(api_key_header)],
) -> UUID:
    """Validate API key and return the API key ID. (not the actual API key string)"""
    # TODO: remove logging
    logger.warning(f"Validating API key: {api_key}")
    db_api_key = crud.get_api_key(db_session, api_key)
    if db_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    if db_api_key.status == models.APIKey.Status.DISABLED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is disabled")
    elif db_api_key.status == models.APIKey.Status.DELETED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key is deleted")

    api_key_id: UUID = db_api_key.id
    return api_key_id
