from app.database import engine
from sqlalchemy.orm import Session
from typing import Generator
from fastapi import HTTPException, status, Security
import logging
import os
from authlib.jose import jwt, JoseError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
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
) -> str:
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
        return user_id

    except JoseError as e:
        logger.error("Token verification failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )
