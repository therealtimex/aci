# Aipolabs CLI
Internal admin CLI tool for Aipolabs to manage apps, functions, users, etc.

## Setup
Follow the [setup instructions](../README.md) for the project.

## Commands
For commands that require database connection, make sure the database you are connecting to is running and the `CLI_DB_` variables in `.env` file is set up correctly.

<details>
  <summary>Upsert App</summary>
  This command will create or update an app and its functions in the database, based on the app json file provided.

  Example json file: [`cli/assets/apps/aipolabs_test.json`](assets/apps/aipolabs_test.json)

  Make sure the database where the records are upserted to is running and the `CLI_DB_` variables in `.env` file is set up correctly.


  ```bash
  python -m cli.aipocli upsert-app --app-file ./cli/assets/apps/aipolabs_test.json
  ```
</details>


## Testing
Follow all guidelines below for setting up the development environment, running services and testing locally
