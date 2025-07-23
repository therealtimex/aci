import pytest
from pydantic import ValidationError

from aci.common.enums import HttpLocation, SecurityScheme
from aci.common.schemas.app_configurations import AppConfigurationCreate
from aci.common.schemas.security_scheme import (
    APIKeyScheme,
    APIKeySchemeOverride,
    SecuritySchemeOverrides,
)


class TestAPIKeyScheme:
    def test_api_key_scheme_basic(self):
        """Test basic APIKeyScheme creation without api_host_url"""
        scheme = APIKeyScheme(
            location=HttpLocation.HEADER,
            name="X-API-Key",
            prefix="Bearer"
        )
        assert scheme.location == HttpLocation.HEADER
        assert scheme.name == "X-API-Key"
        assert scheme.prefix == "Bearer"
        assert scheme.api_host_url is None

    def test_api_key_scheme_with_valid_host_url(self):
        """Test APIKeyScheme with valid api_host_url"""
        scheme = APIKeyScheme(
            location=HttpLocation.HEADER,
            name="X-API-Key",
            api_host_url="https://api.example.com"
        )
        assert scheme.api_host_url == "https://api.example.com"

    def test_api_key_scheme_with_http_host_url(self):
        """Test APIKeyScheme with http api_host_url"""
        scheme = APIKeyScheme(
            location=HttpLocation.HEADER,
            name="X-API-Key",
            api_host_url="http://localhost:8080"
        )
        assert scheme.api_host_url == "http://localhost:8080"

    def test_api_key_scheme_strips_trailing_slash(self):
        """Test that trailing slash is removed from api_host_url"""
        scheme = APIKeyScheme(
            location=HttpLocation.HEADER,
            name="X-API-Key",
            api_host_url="https://api.example.com/"
        )
        assert scheme.api_host_url == "https://api.example.com"

    def test_api_key_scheme_invalid_host_url_no_protocol(self):
        """Test APIKeyScheme with invalid api_host_url (no protocol)"""
        with pytest.raises(ValidationError) as exc_info:
            APIKeyScheme(
                location=HttpLocation.HEADER,
                name="X-API-Key",
                api_host_url="api.example.com"
            )
        assert "API host URL must start with http:// or https://" in str(exc_info.value)

    def test_api_key_scheme_invalid_host_url_wrong_protocol(self):
        """Test APIKeyScheme with invalid api_host_url (wrong protocol)"""
        with pytest.raises(ValidationError) as exc_info:
            APIKeyScheme(
                location=HttpLocation.HEADER,
                name="X-API-Key",
                api_host_url="ftp://api.example.com"
            )
        assert "API host URL must start with http:// or https://" in str(exc_info.value)

    def test_api_key_scheme_host_url_too_long(self):
        """Test APIKeyScheme with api_host_url exceeding max length"""
        long_url = "https://" + "a" * 2050 + ".com"
        with pytest.raises(ValidationError) as exc_info:
            APIKeyScheme(
                location=HttpLocation.HEADER,
                name="X-API-Key",
                api_host_url=long_url
            )
        assert "String should have at most 2048 characters" in str(exc_info.value)


class TestAPIKeySchemeOverride:
    def test_api_key_scheme_override_valid(self):
        """Test valid APIKeySchemeOverride creation"""
        override = APIKeySchemeOverride(api_host_url="https://custom.example.com")
        assert override.api_host_url == "https://custom.example.com"

    def test_api_key_scheme_override_strips_trailing_slash(self):
        """Test that trailing slash is removed from api_host_url in override"""
        override = APIKeySchemeOverride(api_host_url="https://custom.example.com/")
        assert override.api_host_url == "https://custom.example.com"

    def test_api_key_scheme_override_invalid_url(self):
        """Test APIKeySchemeOverride with invalid URL"""
        with pytest.raises(ValidationError) as exc_info:
            APIKeySchemeOverride(api_host_url="invalid-url")
        assert "API host URL must start with http:// or https://" in str(exc_info.value)

    def test_api_key_scheme_override_required_field(self):
        """Test that api_host_url is required in APIKeySchemeOverride"""
        with pytest.raises(ValidationError) as exc_info:
            APIKeySchemeOverride()
        assert "Field required" in str(exc_info.value)


class TestSecuritySchemeOverrides:
    def test_security_scheme_overrides_with_api_key(self):
        """Test SecuritySchemeOverrides with api_key field"""
        overrides = SecuritySchemeOverrides(
            api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
        )
        assert overrides.api_key is not None
        assert overrides.api_key.api_host_url == "https://custom.example.com"
        assert overrides.oauth2 is None

    def test_security_scheme_overrides_empty(self):
        """Test empty SecuritySchemeOverrides"""
        overrides = SecuritySchemeOverrides()
        assert overrides.api_key is None
        assert overrides.oauth2 is None


class TestAppConfigurationValidation:
    def test_app_configuration_api_key_override_valid(self):
        """Test AppConfigurationCreate with valid API key override"""
        config = AppConfigurationCreate(
            app_name="test-app",
            security_scheme=SecurityScheme.API_KEY,
            security_scheme_overrides=SecuritySchemeOverrides(
                api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
            )
        )
        assert config.security_scheme == SecurityScheme.API_KEY
        assert config.security_scheme_overrides.api_key is not None
        assert config.security_scheme_overrides.api_key.api_host_url == "https://custom.example.com"

    def test_app_configuration_api_key_override_wrong_scheme(self):
        """Test AppConfigurationCreate with API key override but wrong security scheme"""
        with pytest.raises(ValidationError) as exc_info:
            AppConfigurationCreate(
                app_name="test-app",
                security_scheme=SecurityScheme.OAUTH2,
                security_scheme_overrides=SecuritySchemeOverrides(
                    api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
                )
            )
        assert "API key overrides not supported for security scheme SecurityScheme.OAUTH2" in str(exc_info.value)

    def test_app_configuration_no_auth_with_api_key_override(self):
        """Test AppConfigurationCreate with API key override but NO_AUTH security scheme"""
        with pytest.raises(ValidationError) as exc_info:
            AppConfigurationCreate(
                app_name="test-app",
                security_scheme=SecurityScheme.NO_AUTH,
                security_scheme_overrides=SecuritySchemeOverrides(
                    api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
                )
            )
        assert "API key overrides not supported for security scheme SecurityScheme.NO_AUTH" in str(exc_info.value)