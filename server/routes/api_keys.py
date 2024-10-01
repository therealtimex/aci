import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from authlib.jose import jwt, JoseError
from uuid import uuid4
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.security.utils import get_authorization_scheme_param

# Create router instance
router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory store for API keys (use a DB in production)
api_keys = []

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


# Use OAuth2PasswordBearer without needing tokenUrl since you're not using the password grant flow
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl="", authorizationUrl=""
)  # Leave tokenUrl empty or omit it entirely


def get_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# Function to verify and decode JWT token
def get_current_user(
    token: str = Depends(get_bearer_token),
) -> str:
    try:
        logger.info("Decoding JWT token.")
        payload = jwt.decode(token, JWT_SECRET_KEY)  # Use your secret key to decode JWT
        logger.info("Validating token claims.")
        payload.validate()  # This will raise a JoseError if validation fails

        user_id: str = payload.get("sub")  # Extract the user ID (subject)
        if not user_id:
            logger.error("Token is missing 'sub' claim.")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        logger.info(f"Token valid. User ID: {user_id}")
        return user_id  # Return the user ID for further processing

    except JoseError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# Model for API key
class APIKey(BaseModel):
    key: str
    user_email: str


# Function to generate API key
def generate_api_key(user_email: str) -> str:
    try:
        logger.info(f"Generating API key for user: {user_email}")
        api_key = str(uuid4())  # Generate a unique API key
        api_keys.append(APIKey(key=api_key, user_email=user_email))
        logger.info(f"API key generated successfully for user: {user_email}")
        return api_key
    except Exception as e:
        logger.error(f"Failed to generate API key for user {user_email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate API key")


# Route to generate API key (requires login via JWT)
@router.post("/")
async def create_api_key(user_id: str = Depends(get_current_user)):
    try:
        api_key = generate_api_key(user_id)  # Generate API key for the logged-in user
        logger.info(f"API key created for user: {user_id}")
        return {"api_key": api_key}
    except Exception as e:
        logger.error(f"Error in API key creation route: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create API key")


# Example protected route (requires valid API key)
@router.get("/main_service")
async def main_service(api_key: str):
    try:
        logger.info("Checking API key for access to the main service.")
        if any(key.key == api_key for key in api_keys):
            logger.info("API key is valid. Access granted.")
            return {"message": "Access granted to main service"}
        else:
            logger.warning("Invalid API key attempted.")
            raise HTTPException(status_code=403, detail="Invalid API key")
    except Exception as e:
        logger.error(f"Error in accessing main service: {str(e)}")
        raise HTTPException(status_code=500, detail="Service access error")
