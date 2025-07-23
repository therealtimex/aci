#!/usr/bin/env python3
"""
Simple test script to verify the API key credentials functionality.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from aci.common.db.sql_models import App, AppConfiguration, LinkedAccount
from aci.common.enums import SecurityScheme, HttpLocation
from aci.server.security_credentials_manager import _get_api_key_credentials


def test_api_key_credentials_with_override():
    """Test API key credentials with host URL override."""
    print("Testing API key credentials with host URL override...")
    
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

    try:
        # Call the function
        result = _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)
        
        # Verify the result
        print(f"✓ Function returned SecurityCredentialsResponse")
        print(f"✓ Scheme type: {type(result.scheme).__name__}")
        print(f"✓ API host URL: {result.scheme.api_host_url}")
        print(f"✓ Credentials secret key: {result.credentials.secret_key}")
        print(f"✓ Is app default credentials: {result.is_app_default_credentials}")
        
        # Verify the override was applied
        assert result.scheme.api_host_url == "https://custom-api.example.com"
        print("✓ Host URL override correctly applied")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_key_credentials_without_override():
    """Test API key credentials without host URL override."""
    print("\nTesting API key credentials without host URL override...")
    
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

    try:
        # Call the function
        result = _get_api_key_credentials(mock_app, mock_app_config, mock_linked_account)
        
        # Verify the result
        print(f"✓ Function returned SecurityCredentialsResponse")
        print(f"✓ Scheme type: {type(result.scheme).__name__}")
        print(f"✓ API host URL: {result.scheme.api_host_url}")
        print(f"✓ Credentials secret key: {result.credentials.secret_key}")
        
        # Verify no override was applied
        assert result.scheme.api_host_url is None
        print("✓ No host URL override (as expected)")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_api_key_credentials_with_override()
    success2 = test_api_key_credentials_without_override()
    
    if success1 and success2:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)