import logging
from typing import Generator
from uuid import UUID

from authlib.jose import JoseError, jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import config
from app.db import engine

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

http_bearer = HTTPBearer()


def get_db_session() -> Generator[Session, None, None]:
    db_session = engine.SessionMaker()
    try:
        yield db_session
    finally:
        db_session.close()


# dependency function to verify and decode JWT token
# used for routes that require user authentication like creating API keys
def verify_user(
    auth_data: HTTPAuthorizationCredentials = Security(http_bearer),
) -> UUID:
    token = auth_data.credentials
    try:
        logger.info("Decoding JWT token.")
        payload = jwt.decode(token, config.JWT_SECRET_KEY)
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
