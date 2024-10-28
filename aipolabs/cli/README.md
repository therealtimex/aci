# Aipolabs CLI
Internal admin CLI tool for Aipolabs to manage apps, functions, users, etc.

## Setup
Follow the [setup instructions](../README.md) for the project.

## Commands
For commands that require database connection, make sure the database you are connecting to is running and the `CLI_DB_` variables in `.env` file is set up correctly.

<details>
  <summary>Upsert App and Functions</summary>
  This command will create or update an app and its functions in the database, based on the app json file provided.

  Example files: [`aipolabs_test`](assets/aipolabs_test).

  Make sure the database where the records are upserted to is running and the `CLI_DB_` variables in `.env` file is set up correctly.

  ```bash
  python -m aipolabs.cli.aipolabs upsert-app-and-functions --app-file ./aipolabs/cli/assets/aipolabs_test/app.json --functions-file ./aipolabs/cli/assets/aipolabs_test/functions.json
  ```
</details>


## Testing
Follow all guidelines below for setting up the development environment, running services and testing locally
