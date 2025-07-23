#!/usr/bin/env python3
"""Manual test script to verify the security scheme models work correctly"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pydantic import ValidationError
from aci.common.enums import HttpLocation, SecurityScheme
from aci.common.schemas.app_configurations import AppConfigurationCreate
from aci.common.schemas.security_scheme import (
    APIKeyScheme,
    APIKeySchemeOverride,
    SecuritySchemeOverrides,
)

def test_api_key_scheme_basic():
    """Test basic APIKeyScheme creation without api_host_url"""
    print("Testing basic APIKeyScheme...")
    scheme = APIKeyScheme(
        location=HttpLocation.HEADER,
        name="X-API-Key",
        prefix="Bearer"
    )
    assert scheme.location == HttpLocation.HEADER
    assert scheme.name == "X-API-Key"
    assert scheme.prefix == "Bearer"
    assert scheme.api_host_url is None
    print("✓ Basic APIKeyScheme test passed")

def test_api_key_scheme_with_valid_host_url():
    """Test APIKeyScheme with valid api_host_url"""
    print("Testing APIKeyScheme with valid host URL...")
    scheme = APIKeyScheme(
        location=HttpLocation.HEADER,
        name="X-API-Key",
        api_host_url="https://api.example.com"
    )
    assert scheme.api_host_url == "https://api.example.com"
    print("✓ APIKeyScheme with valid host URL test passed")

def test_api_key_scheme_strips_trailing_slash():
    """Test that trailing slash is removed from api_host_url"""
    print("Testing trailing slash removal...")
    scheme = APIKeyScheme(
        location=HttpLocation.HEADER,
        name="X-API-Key",
        api_host_url="https://api.example.com/"
    )
    assert scheme.api_host_url == "https://api.example.com"
    print("✓ Trailing slash removal test passed")

def test_api_key_scheme_invalid_host_url():
    """Test APIKeyScheme with invalid api_host_url"""
    print("Testing invalid host URL...")
    try:
        APIKeyScheme(
            location=HttpLocation.HEADER,
            name="X-API-Key",
            api_host_url="api.example.com"
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "API host URL must start with http:// or https://" in str(e)
        print("✓ Invalid host URL test passed")

def test_api_key_scheme_override():
    """Test APIKeySchemeOverride"""
    print("Testing APIKeySchemeOverride...")
    override = APIKeySchemeOverride(api_host_url="https://custom.example.com")
    assert override.api_host_url == "https://custom.example.com"
    print("✓ APIKeySchemeOverride test passed")

def test_security_scheme_overrides():
    """Test SecuritySchemeOverrides with api_key field"""
    print("Testing SecuritySchemeOverrides with api_key...")
    overrides = SecuritySchemeOverrides(
        api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
    )
    assert overrides.api_key is not None
    assert overrides.api_key.api_host_url == "https://custom.example.com"
    assert overrides.oauth2 is None
    print("✓ SecuritySchemeOverrides test passed")

def test_app_configuration_validation():
    """Test AppConfigurationCreate validation"""
    print("Testing AppConfigurationCreate with API key override...")
    config = AppConfigurationCreate(
        app_name="test-app",
        security_scheme=SecurityScheme.API_KEY,
        security_scheme_overrides=SecuritySchemeOverrides(
            api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
        )
    )
    assert config.security_scheme == SecurityScheme.API_KEY
    assert config.security_scheme_overrides.api_key is not None
    print("✓ AppConfigurationCreate validation test passed")

def test_app_configuration_wrong_scheme():
    """Test AppConfigurationCreate with wrong security scheme"""
    print("Testing AppConfigurationCreate with wrong security scheme...")
    try:
        AppConfigurationCreate(
            app_name="test-app",
            security_scheme=SecurityScheme.OAUTH2,
            security_scheme_overrides=SecuritySchemeOverrides(
                api_key=APIKeySchemeOverride(api_host_url="https://custom.example.com")
            )
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "API key overrides not supported for security scheme SecurityScheme.OAUTH2" in str(e)
        print("✓ Wrong security scheme validation test passed")

if __name__ == "__main__":
    print("Running manual tests for security scheme models...")
    print("=" * 50)
    
    try:
        test_api_key_scheme_basic()
        test_api_key_scheme_with_valid_host_url()
        test_api_key_scheme_strips_trailing_slash()
        test_api_key_scheme_invalid_host_url()
        test_api_key_scheme_override()
        test_security_scheme_overrides()
        test_app_configuration_validation()
        test_app_configuration_wrong_scheme()
        
        print("=" * 50)
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)