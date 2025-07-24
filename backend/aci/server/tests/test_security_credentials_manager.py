import pytest
from unittest.mock import patch

from aci.common.db.sql_models import App, AppConfiguration, LinkedAccount
from aci.common.enums import SecurityScheme
from aci.common.exceptions import NoImplementationFound
from aci.common.schemas.security_scheme import (
    APIKeyScheme,
    APIKeySchemeCredentials,
    APIKeySchemeOverride,
    SecuritySchemeOverrides,
)
from aci.server.security_credentials_manager import (
    get_app_configuration_api_key_scheme,
    _get_api_key_credentials,
    SecurityCredentialsResponse,
)


class TestGetAppConfigurationApiKeyScheme:
    """Test cases for get_app_configuration_api_key_scheme function."""

    def test_get_api_key_scheme_without_overrides(self):
        """Test getting API key scheme when no overrides are configured."""
        # Create mock app with API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }

        # Create mock app configuration without overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Call the function
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify the result
        assert isinstance(result, APIKeyScheme)
        assert result.location.value == "header"
        assert result.name == "X-API-Key"
        assert result.prefix is None
        assert result.api_host_url is None

    def test_get_api_key_scheme_with_host_override(self):
        """Test getting API key scheme with api_host_url override."""
        # Create mock app with API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": "Bearer",
                "api_host_url": None,
            }
        }

        # Create mock app configuration with API key overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {
            "api_key": {
                "api_host_url": "https://custom-api.example.com"
            }
        }

        # Call the function
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify the result
        assert isinstance(result, APIKeyScheme)
        assert result.location.value == "header"
        assert result.name == "X-API-Key"
        assert result.prefix == "Bearer"
        assert result.api_host_url == "https://custom-api.example.com"

    def test_get_api_key_scheme_with_oauth2_overrides_only(self):
        """Test getting API key scheme when only OAuth2 overrides are present."""
        # Create mock app with API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "Authorization",
                "prefix": "Bearer",
                "api_host_url": None,
            }
        }

        # Create mock app configuration with OAuth2 overrides only
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {
            "oauth2": {
                "client_id": "custom_client_id",
                "client_secret": "custom_client_secret",
            }
        }

        # Call the function
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify the result (should be unchanged since no API key overrides)
        assert isinstance(result, APIKeyScheme)
        assert result.location.value == "header"
        assert result.name == "Authorization"
        assert result.prefix == "Bearer"
        assert result.api_host_url is None

    def test_get_api_key_scheme_invalid_app_scheme(self):
        """Test error handling when app has invalid API key scheme."""
        # Create mock app with invalid API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "invalid_location",  # Invalid location
                "name": "X-API-Key",
            }
        }

        # Create mock app configuration
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Call the function and expect ValueError
        with pytest.raises(ValueError, match="Invalid API key scheme configuration"):
            get_app_configuration_api_key_scheme(mock_app, mock_app_config)

    def test_get_api_key_scheme_malformed_overrides(self):
        """Test error handling when security scheme overrides are malformed."""
        # Create mock app with valid API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }

        # Create mock app configuration with malformed overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = "invalid_json"  # Should be dict

        # Call the function - should return base scheme without overrides
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify the result (should be base scheme without overrides)
        assert isinstance(result, APIKeyScheme)
        assert result.location.value == "header"
        assert result.name == "X-API-Key"
        assert result.prefix is None
        assert result.api_host_url is None

    def test_get_api_key_scheme_invalid_override_data(self):
        """Test error handling when API key override data is invalid."""
        # Create mock app with valid API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }

        # Create mock app configuration with invalid API key override
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {
            "api_key": {
                "api_host_url": "invalid-url-without-protocol"  # Invalid URL
            }
        }

        # Call the function - should return base scheme without overrides
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify the result (should be base scheme without overrides due to invalid override)
        assert isinstance(result, APIKeyScheme)
        assert result.location.value == "header"
        assert result.name == "X-API-Key"
        assert result.prefix is None
        assert result.api_host_url is None

    @patch('aci.server.security_credentials_manager.logger')
    def test_logging_on_successful_override_application(self, mock_logger):
        """Test that successful override application is logged."""
        # Create mock app with API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }

        # Create mock app configuration with API key overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {
            "api_key": {
                "api_host_url": "https://custom-api.example.com"
            }
        }

        # Call the function
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify logging was called
        mock_logger.info.assert_called_once()
        log_call_args = mock_logger.info.call_args[0][0]
        assert "Applied API key overrides" in log_call_args
        assert "test_app" in log_call_args
        assert "https://custom-api.example.com" in log_call_args

    @patch('aci.server.security_credentials_manager.logger')
    def test_logging_on_invalid_app_scheme(self, mock_logger):
        """Test that errors with invalid app scheme are logged."""
        # Create mock app with invalid API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "invalid_location",
                "name": "X-API-Key",
            }
        }

        # Create mock app configuration
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Call the function and expect ValueError
        with pytest.raises(ValueError):
            get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        log_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to validate API key scheme" in log_call_args
        assert "test_app" in log_call_args

    @patch('aci.server.security_credentials_manager.logger')
    def test_logging_on_malformed_overrides(self, mock_logger):
        """Test that errors with malformed overrides are logged."""
        # Create mock app with valid API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }

        # Create mock app configuration with malformed overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = "invalid_json"

        # Call the function
        result = get_app_configuration_api_key_scheme(mock_app, mock_app_config)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        log_call_args = mock_logger.error.call_args[0][0]
        assert "Failed to parse security scheme overrides" in log_call_args
        assert "test_app" in log_call_args


class TestGetApiKeyCredentials:
    """Test cases for _get_api_key_credentials function."""

    def test_get_api_key_credentials_with_linked_account_credentials(self):
        """Test getting API key credentials when linked account has credentials."""
        # Create mock app with API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }
        mock_app.default_security_credentials_by_scheme = {}

        # Create mock app configuration without overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Create mock linked account with credentials
        mock_linked_account = LinkedAccount()
        mock_linked_account.id = 1
        mock_linked_account.security_scheme = SecurityScheme.API_KEY
        mock_linked_account.security_credentials = {"secret_key": "test_api_key"}
        mock_linked_account.linked_account_owner_id = "user123"

        # Call the function
        result = _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)

        # Verify the result
        assert isinstance(result, SecurityCredentialsResponse)
        assert isinstance(result.scheme, APIKeyScheme)
        assert result.scheme.location.value == "header"
        assert result.scheme.name == "X-API-Key"
        assert result.scheme.prefix is None
        assert result.scheme.api_host_url is None
        assert isinstance(result.credentials, APIKeySchemeCredentials)
        assert result.credentials.secret_key == "test_api_key"
        assert result.is_app_default_credentials is False
        assert result.is_updated is False

    def test_get_api_key_credentials_with_app_default_credentials(self):
        """Test getting API key credentials when using app default credentials."""
        # Create mock app with API key scheme and default credentials
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "Authorization",
                "prefix": "Bearer",
                "api_host_url": None,
            }
        }
        mock_app.default_security_credentials_by_scheme = {
            SecurityScheme.API_KEY: {"secret_key": "default_api_key"}
        }

        # Create mock app configuration without overrides
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Create mock linked account without credentials
        mock_linked_account = LinkedAccount()
        mock_linked_account.id = 1
        mock_linked_account.security_scheme = SecurityScheme.API_KEY
        mock_linked_account.security_credentials = None
        mock_linked_account.linked_account_owner_id = "user123"

        # Call the function
        result = _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)

        # Verify the result
        assert isinstance(result, SecurityCredentialsResponse)
        assert isinstance(result.scheme, APIKeyScheme)
        assert result.scheme.location.value == "header"
        assert result.scheme.name == "Authorization"
        assert result.scheme.prefix == "Bearer"
        assert result.scheme.api_host_url is None
        assert isinstance(result.credentials, APIKeySchemeCredentials)
        assert result.credentials.secret_key == "default_api_key"
        assert result.is_app_default_credentials is True
        assert result.is_updated is False

    def test_get_api_key_credentials_with_host_override(self):
        """Test getting API key credentials with api_host_url override."""
        # Create mock app with API key scheme
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }
        mock_app.default_security_credentials_by_scheme = {}

        # Create mock app configuration with API key host override
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {
            "api_key": {
                "api_host_url": "https://custom-api.example.com"
            }
        }

        # Create mock linked account with credentials
        mock_linked_account = LinkedAccount()
        mock_linked_account.id = 1
        mock_linked_account.security_scheme = SecurityScheme.API_KEY
        mock_linked_account.security_credentials = {"secret_key": "test_api_key"}
        mock_linked_account.linked_account_owner_id = "user123"

        # Call the function
        result = _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)

        # Verify the result
        assert isinstance(result, SecurityCredentialsResponse)
        assert isinstance(result.scheme, APIKeyScheme)
        assert result.scheme.location.value == "header"
        assert result.scheme.name == "X-API-Key"
        assert result.scheme.prefix is None
        assert result.scheme.api_host_url == "https://custom-api.example.com"
        assert isinstance(result.credentials, APIKeySchemeCredentials)
        assert result.credentials.secret_key == "test_api_key"
        assert result.is_app_default_credentials is False
        assert result.is_updated is False

    def test_get_api_key_credentials_no_credentials_available(self):
        """Test error handling when no credentials are available."""
        # Create mock app with API key scheme but no default credentials
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }
        mock_app.default_security_credentials_by_scheme = {}

        # Create mock app configuration
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Create mock linked account without credentials
        mock_linked_account = LinkedAccount()
        mock_linked_account.id = 1
        mock_linked_account.security_scheme = SecurityScheme.API_KEY
        mock_linked_account.security_credentials = None
        mock_linked_account.linked_account_owner_id = "user123"

        # Call the function and expect NoImplementationFound
        with pytest.raises(NoImplementationFound, match="No API key credentials usable"):
            _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)

    def test_get_api_key_credentials_empty_credentials_dict(self):
        """Test error handling when credentials are empty dict."""
        # Create mock app with API key scheme but no default credentials
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.security_schemes = {
            SecurityScheme.API_KEY: {
                "location": "header",
                "name": "X-API-Key",
                "prefix": None,
                "api_host_url": None,
            }
        }
        mock_app.default_security_credentials_by_scheme = {}

        # Create mock app configuration
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1
        mock_app_config.security_scheme_overrides = {}

        # Create mock linked account with empty credentials dict
        mock_linked_account = LinkedAccount()
        mock_linked_account.id = 1
        mock_linked_account.security_scheme = SecurityScheme.API_KEY
        mock_linked_account.security_credentials = {}  # Empty dict
        mock_linked_account.linked_account_owner_id = "user123"

        # Call the function and expect NoImplementationFound
        with pytest.raises(NoImplementationFound, match="No API key credentials usable"):
            _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)

    @patch('aci.server.security_credentials_manager.get_app_configuration_api_key_scheme')
    def test_get_api_key_credentials_uses_scheme_function(self, mock_get_scheme):
        """Test that _get_api_key_credentials uses get_app_configuration_api_key_scheme."""
        # Setup mock return value
        mock_scheme = APIKeyScheme(
            location="header",
            name="X-API-Key",
            prefix=None,
            api_host_url="https://custom-api.example.com"
        )
        mock_get_scheme.return_value = mock_scheme

        # Create mock app
        mock_app = App()
        mock_app.name = "test_app"
        mock_app.default_security_credentials_by_scheme = {}

        # Create mock app configuration
        mock_app_config = AppConfiguration()
        mock_app_config.id = 1

        # Create mock linked account with credentials
        mock_linked_account = LinkedAccount()
        mock_linked_account.id = 1
        mock_linked_account.security_scheme = SecurityScheme.API_KEY
        mock_linked_account.security_credentials = {"secret_key": "test_api_key"}
        mock_linked_account.linked_account_owner_id = "user123"

        # Call the function
        result = _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)

        # Verify that get_app_configuration_api_key_scheme was called
        mock_get_scheme.assert_called_once_with(mock_app, mock_app_config)

        # Verify the result uses the mocked scheme
        assert result.scheme == mock_scheme
        assert result.scheme.api_host_url == "https://custom-api.example.com"