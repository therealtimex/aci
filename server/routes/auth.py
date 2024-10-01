import logging
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from datetime import datetime, timedelta, timezone
import os
from authlib.jose import jwt, JoseError
from server.schemas import TokenResponse

# Create router instance
router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

# OAuth setup
oauth = OAuth()

# Register Google OAuth
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url=os.getenv("GOOGLE_ACCESS_TOKEN_URL"),
    authorize_url=os.getenv("GOOGLE_AUTHORIZE_URL"),
    api_base_url=os.getenv("GOOGLE_API_BASE_URL"),
    client_kwargs={"scope": "openid email profile"},
)


# Function to generate JWT using Authlib
def create_access_token(user_id: str, expires_delta: timedelta):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + expires_delta,
    }

    # Authlib expects a header, payload, and key
    header = {"alg": JWT_ALGORITHM}
    try:
        encoded_jwt = jwt.encode(header, payload, JWT_SECRET_KEY)
        logger.info(f"JWT successfully created for user {user_id}, payload: {payload}")
        return encoded_jwt.decode("utf-8")  # Decode to convert bytes to string
    except JoseError as e:
        logger.error(f"JWT generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="JWT generation failed")


# login route for different auth providers
@router.get("/login/{provider}")
async def login(request: Request, provider: str):
    if provider not in oauth._registry:
        logger.error(f"Unsupported provider: {provider}")
        raise HTTPException(status_code=400, detail="Unsupported provider")

    redirect_uri = request.url_for("auth_callback", provider=provider)
    logger.info(f"Initiating OAuth login for provider: {provider}, redirecting to: {redirect_uri}")
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


# callback route for different auth providers
# TODO: decision between long-lived JWT v.s session based v.s refresh token based auth
@router.get("/callback/{provider}", name="auth_callback", response_model=TokenResponse)
async def auth_callback(request: Request, provider: str):
    if provider not in oauth._registry:
        logger.error(f"Unsupported provider during callback: {provider}")
        raise HTTPException(status_code=400, detail="Unsupported provider")

    oauth_client = oauth.create_client(provider)

    try:
        logger.info(f"Retrieving access token for provider: {provider}")
        token = await oauth_client.authorize_access_token(request)
        logger.info(f"Access token retrieved successfully for provider: {provider}, token: {token}")
    except Exception as e:
        logger.error(f"Failed to retrieve access token for provider {provider}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to retrieve access token: {str(e)}")

    try:
        if provider == "google":
            logger.info("Parsing ID token from Google")
            user_info = await oauth_client.parse_id_token(request, token)
            logger.info(f"User information retrieved from Google: {user_info}")
        else:
            logger.error(f"Unsupported provider during user info retrieval: {provider}")
            raise HTTPException(status_code=400, detail="Unsupported provider")
    except Exception as e:
        logger.error(f"Failed to retrieve user information for provider {provider}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to retrieve user information: {str(e)}")

    if not user_info["sub"]:
        logger.error(f"User ID not found in user information for provider {provider}")
        raise HTTPException(status_code=400, detail="User ID not found in user information")

    # Create a unique user identifier
    user_id = f"{provider}-{user_info["sub"]}"
    logger.info(f"Unique user identifier generated: {user_id}")

    # TODO: If this is a new user, save the user information to a database
    
    # Generate JWT token for the user
    try:
        jwt_token = create_access_token(
            user_id,
            timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        logger.info(f"JWT generated successfully for user: {user_id}, jwt_token: {jwt_token}")
    except JoseError as e:
        logger.error(f"JWT generation failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="JWT generation failed")

    return {"access_token": jwt_token, "token_type": "bearer"}
