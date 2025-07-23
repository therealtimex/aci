import pytest
from unittest.mock import patch

from aci.common.db.sql_models import App, AppConfiguration
from aci.common.enums import SecurityScheme
from aci.common.schemas.security_scheme import (
    APIKeyScheme,
    APIKeySchemeOverride,
    SecuritySchemeOverrides,
)
from aci.server.security_credentials_manager import get_app_configuration_api_key_scheme


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