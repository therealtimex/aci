# Implementation Plan

- [x] 1. Extend security scheme models to support API key host overrides

  - Add api_host_url field to APIKeyScheme model with validation
  - Create APIKeySchemeOverride model for security scheme overrides
  - Update SecuritySchemeOverrides to include api_key field
  - Add validation to ensure api_key overrides only work with API_KEY security scheme
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.4_

- [x] 2. Implement API key scheme configuration handler

  - Create get_app_configuration_api_key_scheme function following OAuth2 pattern
  - Integrate with existing security scheme override parsing logic
  - Add proper error handling for malformed override data
  - Write unit tests for scheme configuration with and without overrides
  - _Requirements: 2.3, 3.2, 5.3_

- [x] 3. Update security credentials manager for API key overrides

  - Modify \_get_api_key_credentials to use get_app_configuration_api_key_scheme
  - Ensure APIKeyScheme with overrides is returned in SecurityCredentialsResponse
  - Add logging for when custom API host URLs are applied
  - Write unit tests for credentials manager with host URL overrides
  - _Requirements: 2.1, 5.1, 5.4_

- [x] 4. Modify REST function executor to support custom API hosts

  - Update \_execute method in RestFunctionExecutor to check for api_host_url in security scheme
  - Implement URL construction logic that preserves path while using custom host
  - Add fallback logic to use default host if custom host is malformed
  - Add detailed logging for host URL selection decisions
  - _Requirements: 2.1, 2.2, 2.4, 5.1, 5.2_

- [x] 5. Update app configuration validation logic

  - Extend AppConfigurationCreate.check_security_scheme_matches_override validator
  - Add validation to reject api_key overrides when security_scheme is not API_KEY
  - Update AppConfigurationPublic to handle api_key overrides in security_scheme_overrides
  - Write unit tests for validation scenarios with API key overrides
  - _Requirements: 3.1, 3.4_

- [ ] 6. Add comprehensive error handling and logging

  - Implement proper error messages for invalid API host URLs
  - Add connection failure handling for unreachable custom hosts
  - Implement logging strategy for host selection and fallback scenarios
  - Add error handling for URL construction failures
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 7. Create integration tests for end-to-end functionality

  - Test creating app configuration with API key host override
  - Test function execution using custom API host URL
  - Test updating app configuration to modify host URL override
  - Test error scenarios with invalid or unreachable custom hosts
  - _Requirements: 2.1, 2.2, 4.1, 4.2, 4.3_

- [ ] 8. Add unit tests for all new components

  - Test APIKeyScheme validation with api_host_url field
  - Test APIKeySchemeOverride model validation
  - Test SecuritySchemeOverrides with api_key field
  - Test get_app_configuration_api_key_scheme function
  - Test REST function executor URL construction logic
  - _Requirements: 1.1, 1.2, 1.4, 2.2, 2.4_

- [ ] 9. Update documentation and ensure backward compatibility
  - Verify existing API key configurations continue to work unchanged
  - Add API documentation for new security_scheme_overrides.api_key field
  - Update error message documentation for new validation scenarios
  - Test that existing function executions are not affected
  - _Requirements: 2.3, 3.3, 4.4_
