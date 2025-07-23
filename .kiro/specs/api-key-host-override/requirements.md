# Requirements Document

## Introduction

This feature enables users to configure custom API host URLs when setting up App Configurations with API key authentication, providing white-label capabilities similar to the existing OAuth2 implementation. Users will be able to override the default API host URL defined in the app's protocol_data, allowing them to route API calls to their own infrastructure while maintaining the same function interface.

## Requirements

### Requirement 1

**User Story:** As a developer integrating ACI into my application, I want to configure a custom API host URL for API key-based apps, so that I can route function calls to my own API infrastructure for white-labeling purposes.

#### Acceptance Criteria

1. WHEN creating an app configuration with security_scheme=API_KEY THEN the system SHALL accept an optional api_host_url in security_scheme_overrides
2. WHEN api_host_url is provided in security_scheme_overrides THEN the system SHALL validate that it starts with http or https
3. WHEN api_host_url is provided THEN the system SHALL store it securely in the app_configuration.security_scheme_overrides field
4. WHEN api_host_url exceeds 2048 characters THEN the system SHALL reject the configuration with a validation error

### Requirement 2

**User Story:** As a developer, I want the REST function executor to use my custom API host URL when executing functions, so that API calls are routed to my infrastructure instead of the default app host.

#### Acceptance Criteria

1. WHEN executing a REST function with API key authentication AND app configuration has api_host_url override THEN the system SHALL use the custom host URL instead of protocol_data.server_url
2. WHEN constructing the request URL THEN the system SHALL replace only the host portion while preserving the path from protocol_data.path
3. WHEN no api_host_url override is configured THEN the system SHALL use the default protocol_data.server_url as before
4. WHEN the custom host URL is malformed THEN the system SHALL log an error and fall back to the default host

### Requirement 3

**User Story:** As a system administrator, I want API host overrides to be validated and secured properly, so that the system maintains security and data integrity.

#### Acceptance Criteria

1. WHEN security_scheme_overrides contains api_key configuration THEN the system SHALL only allow it when security_scheme=API_KEY
2. WHEN displaying app configuration details THEN the system SHALL include api_host_url in the response without exposing sensitive data
3. WHEN storing api_host_url THEN the system SHALL encrypt it using the same mechanism as other security scheme overrides
4. WHEN validating security_scheme_overrides THEN the system SHALL reject configurations that don't match the selected security scheme

### Requirement 4

**User Story:** As a developer, I want to update existing app configurations to add or modify API host overrides, so that I can change my routing configuration without recreating the entire setup.

#### Acceptance Criteria

1. WHEN updating an app configuration THEN the system SHALL allow modification of security_scheme_overrides.api_key.api_host_url
2. WHEN removing api_host_url override THEN the system SHALL revert to using the default protocol_data.server_url
3. WHEN updating api_host_url THEN the system SHALL validate the new URL format
4. WHEN the update is successful THEN subsequent function executions SHALL use the new host URL

### Requirement 5

**User Story:** As a developer, I want proper error handling and logging for API host overrides, so that I can troubleshoot issues with my custom routing configuration.

#### Acceptance Criteria

1. WHEN function execution fails due to custom host URL THEN the system SHALL log detailed error information including the attempted URL
2. WHEN custom host URL is unreachable THEN the system SHALL return a clear error message indicating the connection failure
3. WHEN URL construction fails THEN the system SHALL log the error and provide meaningful feedback to the user
4. WHEN switching between default and custom hosts THEN the system SHALL log the host selection decision for debugging