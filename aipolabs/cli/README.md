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

  ```bash
  python -m aipolabs.cli.aipolabs upsert-app-and-functions --app-file ./aipolabs/cli/assets/aipolabs_test/app.json --functions-file ./aipolabs/cli/assets/aipolabs_test/functions.json
  ```
</details>

<details>
  <summary>Create User</summary>
  This command will create a user in the database.

  ```bash
  python -m aipolabs.cli.aipolabs create-user --auth-provider google --auth-user-id 1234567890 --name "John Doe" --email "john.doe@example.com" --profile-picture "https://example.com/profile.jpg" --plan free
  ```
</details>

<details>
  <summary>Create Project</summary>
  This command will create a project in the database.
  You need to create the user first before creating a project for the user.

  ```bash
  python -m aipolabs.cli.aipolabs create-project --project-name "My Project" --owner-type user --owner-id "8341edc4-eeb6-4e90-abe3-0051a9a7b9a5" --created-by "8341edc4-eeb6-4e90-abe3-0051a9a7b9a5"
  ```
</details>

<details>
  <summary>Create Agent</summary>
  This command will create an agent in the database.
  You need to create the project first before creating an agent for the project.

  ```bash
  python -m aipolabs.cli.aipolabs create-agent --agent-name "My Agent" --description "My Agent Description" --project-id "51711368-ef40-4efc-a9ab-5d44dbe0d671" --created-by "8341edc4-eeb6-4e90-abe3-0051a9a7b9a5"
  ```
</details>

## Testing
Follow all guidelines below for setting up the development environment, running services and testing locally
