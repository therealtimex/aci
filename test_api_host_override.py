#!/usr/bin/env python3
"""
Simple test to verify API host override functionality in REST function executor.
"""

import logging
from unittest.mock import Mock, patch

from aci.common.db.sql_models import Function
from aci.common.schemas.function import RestMetadata
from aci.common.schemas.security_scheme import APIKeyScheme, APIKeySchemeCredentials
from aci.server.function_executors.rest_api_key_function_executor import RestAPIKeyFunctionExecutor

# Set up logging to see our debug messages
logging.basicConfig(level=logging.DEBUG)

def test_api_host_override():
    """Test that custom API host URL is used when provided in security scheme."""
    
    # Create a mock function with protocol data
    function = Mock(spec=Function)
    function.name = "test_function"
    function.protocol_data = {
        "server_url": "https://api.default.com",
        "path": "/v1/test",
        "method": "GET"
    }
    
    # Create security scheme with custom API host URL
    security_scheme = APIKeyScheme(
        location="header",
        name="X-API-Key",
        prefix="Bearer",
        api_host_url="https://custom.api.com"
    )
    
    # Create security credentials
    security_credentials = APIKeySchemeCredentials(
        secret_key="test-api-key"
    )
    
    # Create function executor
    executor = RestAPIKeyFunctionExecutor()
    
    # Mock the _send_request method to capture the URL
    captured_url = None
    def mock_send_request(request):
        nonlocal captured_url
        captured_url = str(request.url)
        return Mock(success=True, data={})
    
    with patch.object(executor, '_send_request', side_effect=mock_send_request):
        # Execute the function
        result = executor._execute(
            function=function,
            function_input={},
            security_scheme=security_scheme,
            security_credentials=security_credentials
        )
    
    # Verify that custom host URL was used
    expected_url = "https://custom.api.com/v1/test"
    print(f"Expected URL: {expected_url}")
    print(f"Actual URL: {captured_url}")
    
    assert captured_url == expected_url, f"Expected {expected_url}, got {captured_url}"
    print("✅ Test passed: Custom API host URL was used correctly")


def test_fallback_to_default_host():
    """Test that default host is used when custom host is malformed."""
    
    # Create a mock function with protocol data
    function = Mock(spec=Function)
    function.name = "test_function"
    function.protocol_data = {
        "server_url": "https://api.default.com",
        "path": "/v1/test",
        "method": "GET"
    }
    
    # Create security scheme with malformed API host URL
    security_scheme = APIKeyScheme(
        location="header",
        name="X-API-Key",
        prefix="Bearer",
        api_host_url="invalid-url-format"
    )
    
    # Create security credentials
    security_credentials = APIKeySchemeCredentials(
        secret_key="test-api-key"
    )
    
    # Create function executor
    executor = RestAPIKeyFunctionExecutor()
    
    # Mock the _send_request method to capture the URL
    captured_url = None
    def mock_send_request(request):
        nonlocal captured_url
        captured_url = str(request.url)
        return Mock(success=True, data={})
    
    with patch.object(executor, '_send_request', side_effect=mock_send_request):
        # Execute the function
        result = executor._execute(
            function=function,
            function_input={},
            security_scheme=security_scheme,
            security_credentials=security_credentials
        )
    
    # Verify that default host URL was used as fallback
    expected_url = "https://api.default.com/v1/test"
    print(f"Expected URL (fallback): {expected_url}")
    print(f"Actual URL: {captured_url}")
    
    assert captured_url == expected_url, f"Expected {expected_url}, got {captured_url}"
    print("✅ Test passed: Fallback to default host URL works correctly")


def test_no_custom_host():
    """Test that default host is used when no custom host is provided."""
    
    # Create a mock function with protocol data
    function = Mock(spec=Function)
    function.name = "test_function"
    function.protocol_data = {
        "server_url": "https://api.default.com",
        "path": "/v1/test",
        "method": "GET"
    }
    
    # Create security scheme without custom API host URL
    security_scheme = APIKeyScheme(
        location="header",
        name="X-API-Key",
        prefix="Bearer"
        # api_host_url is None by default
    )
    
    # Create security credentials
    security_credentials = APIKeySchemeCredentials(
        secret_key="test-api-key"
    )
    
    # Create function executor
    executor = RestAPIKeyFunctionExecutor()
    
    # Mock the _send_request method to capture the URL
    captured_url = None
    def mock_send_request(request):
        nonlocal captured_url
        captured_url = str(request.url)
        return Mock(success=True, data={})
    
    with patch.object(executor, '_send_request', side_effect=mock_send_request):
        # Execute the function
        result = executor._execute(
            function=function,
            function_input={},
            security_scheme=security_scheme,
            security_credentials=security_credentials
        )
    
    # Verify that default host URL was used
    expected_url = "https://api.default.com/v1/test"
    print(f"Expected URL (default): {expected_url}")
    print(f"Actual URL: {captured_url}")
    
    assert captured_url == expected_url, f"Expected {expected_url}, got {captured_url}"
    print("✅ Test passed: Default host URL is used when no custom host provided")


if __name__ == "__main__":
    print("Testing API host override functionality...")
    test_api_host_override()
    test_fallback_to_default_host()
    test_no_custom_host()
    print("🎉 All tests passed!")