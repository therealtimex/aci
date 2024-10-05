# import pytest
# from fastapi.testclient import TestClient
# from app.main import app  # Adjust the import to your FastAPI app instance

# client = TestClient(app)


# @pytest.fixture
# def mock_oauth_provider(monkeypatch):
#     # Mock the OAuth provider registry
#     monkeypatch.setattr("app.routes.auth.oauth._registry", {"google": "mock_google_client"})

#     # Mock the OAuth client creation
#     async def mock_create_client(provider):
#         class MockOAuthClient:
#             async def authorize_redirect(self, request, redirect_uri):
#                 return {"location": redirect_uri}

#             async def authorize_access_token(self, request):
#                 return {
#                     "userinfo": {
#                         "sub": "123",
#                         "iss": "google",
#                         "name": "Test User",
#                         "email": "test@example.com",
#                         "picture": "http://example.com/pic.jpg",
#                     }
#                 }

#         return MockOAuthClient()

#     monkeypatch.setattr("app.routes.auth.oauth.create_client", mock_create_client)


# def test_login_google(mock_oauth_provider):
#     response = client.get("/login/google")
#     assert response.status_code == 200
#     assert "location" in response.json()


# def test_callback_google(mock_oauth_provider):
#     response = client.get("/callback/google")
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert response.json()["token_type"] == "bearer"


# def test_login_unsupported_provider():
#     response = client.get("/login/unsupported")
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Unsupported provider"}


# def test_callback_unsupported_provider():
#     response = client.get("/callback/unsupported")
#     assert response.status_code == 400
#     assert response.json() == {"detail": "Unsupported provider"}
