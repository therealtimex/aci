# Aipolabs CLI
Internal admin CLI tool for Aipolabs to manage apps, functions, users, etc.

## Commands
For commands that require database connection, make sure the database you are connecting to is running and the `CLI_DB_` variables in `.env` file is set up correctly.

<details>
  <summary>Upsert App</summary>
 
  ```bash
  # Generate app file from app config and OpenAPI spec
  aipocli generate-app-file --app-config-file <path/to/app/config> --openapi-file <path/to/openapi/spec>
  ```
</details>


## Local Development
Follow all guidelines below for setting up the development environment, running services and testing locally



<details>
  <summary>Run pytest</summary>
  - Run tests
    - `pytest -vv -s`
</details>
