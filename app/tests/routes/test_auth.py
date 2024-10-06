import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from authlib.jose import jwt
from sqlalchemy.orm import Session
from app.database import models
from fastapi import Request
from fastapi import status

# disable following redirects for testing login
test_client = TestClient(app, follow_redirects=False)
AIPOLABS_REDIRECT_URI_BASE = os.getenv("AIPOLABS_REDIRECT_URI_BASE")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
MOCK_USER_GOOGLE_AUTH_DATA = {
    "sub": "123",
    "iss": "mock_google",
    "name": "Test User",
    "email": "test@example.com",
    "picture": "http://example.com/pic.jpg",
}
MOCK_GOOGLE_AUTH_REDIRECT_URI_PREFIX = (
    "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&"
    "client_id=982856172186-en95h2s8qds12pme8gjp8n49sjhdtmgg.apps.googleusercontent.com&"
    "redirect_uri"
)


@pytest.fixture
def mock_oauth_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockOAuthClient:
        async def authorize_access_token(self, request: Request) -> dict[str, dict]:
            return {"userinfo": MOCK_USER_GOOGLE_AUTH_DATA}

    # Mock the OAuth client creation
    def mock_create_client(provider: str) -> MockOAuthClient:
        return MockOAuthClient()

    # Mock the OAuth provider registry
    monkeypatch.setattr("app.routes.auth.oauth._registry", {"google": "mock_google_client"})
    monkeypatch.setattr("app.routes.auth.oauth.create_client", mock_create_client)


def test_login_google() -> None:
    # TODO configutr version prefix in setting and use constant for "auth"
    # This is a redirect response, but we are not following the redirect
    response = test_client.get("/v1/auth/login/google")
    assert response.headers["location"].startswith(MOCK_GOOGLE_AUTH_REDIRECT_URI_PREFIX)
    assert response.status_code == status.HTTP_302_FOUND


# mock_oauth_provider to mock google Oauth user info
def test_callback_google(mock_oauth_provider: None, db_session: Session) -> None:
    response = test_client.get("/v1/auth/callback/google")
    data = response.json()
    assert response.status_code == 200
    # check jwt token is generated
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"
    # check user is created
    payload = jwt.decode(data["access_token"], JWT_SECRET_KEY)
    payload.validate()
    user_id = payload.get("sub")
    # get user by id and check user is created
    user = db_session.query(models.User).filter(models.User.id == user_id).first()
    assert user is not None
    assert user.auth_provider == MOCK_USER_GOOGLE_AUTH_DATA["iss"]
    assert user.auth_user_id == MOCK_USER_GOOGLE_AUTH_DATA["sub"]
    assert user.email == MOCK_USER_GOOGLE_AUTH_DATA["email"]
    assert user.name == MOCK_USER_GOOGLE_AUTH_DATA["name"]
    assert user.profile_picture == MOCK_USER_GOOGLE_AUTH_DATA["picture"]


# def test_login_unsupported_provider():
#     response = client.get("/login/unsupported")
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Unsupported provider"}


# def test_callback_unsupported_provider():
#     response = client.get("/callback/unsupported")
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Unsupported provider"}
