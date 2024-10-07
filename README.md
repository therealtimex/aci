# Aipolabs Core Components

## Project Structure
Currently only contains the app server code (and associated database).
But can be extended to include more services (e.g., separate admin server, sdk, cli, etc.) as a monorepo if needed.

## Local Development
Follow all guidelines below for setting up the development environment, running services and testing locally


<details>
  <summary>Setup</summary>

  - Git clone the repo
  - Python ^3.12
  - Install `docker`
  - Install `poetry`
  - Activate virtual env: `poetry shell`
    - We use docker and docker compose to run components in a container, so using a virtual env is more for development purposes. (IDE, pytest, dev dependencies, etc.)
  - Install dependencies: `poetry install`
  - Set up `.env` file according to `.env.example`, these should be parameters for testing and loaded from env variables in docker compose instead of being loaded by the app server directly
  - Coding style
    - all the following tools are part of `pyproject.toml` dev dependencies, and are automatically installed when running `poetry install`
    - use `black` to format the code
    - use `flake8` to lint the code
    - use `mypy` to type check the code
    - use `isort` to sort the imports
    - use `pre-commit` to run the above tools as pre-commit hooks
  - Install `pre-commit` hooks: `pre-commit install`
  - Setup you preferred editor to use `Black` formatter
    - e.g., you might need to install `Black` formatter extension in VS Code, and configure the setting as below
      ```json
      {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter"
      }
      ```
</details>

<details>
  <summary>Run postgreSQL and app server in Docker locally</summary>

  - `docker-compose up --build`: build app server and start the database and app server
  - You can access the `Swagger UI` at `http://localhost:8000/v1/docs`
</details>

<details>
  <summary>Set up or update database for testing locally</summary>

  - In local development the `app` directory is mounted as a volume inside the container, you can run the migrations with `alembic` commands inside the container and the migration code (`versions` folder) will be in your local directory (instead of being only inside the container).
  - Get a bash shell inside the app server container for running commands
    - `docker-compose exec app bash`
  - Set up the database (running in docker) with the latest migration 
    - `alembic upgrade head`
  - (Optional) Connect to the database using a GUI client like `DBeaver`
    - Parameters for the db connection can be found in the `docker-compose.yml` file
  - (If any changes are made to the models) After changing any tables or models, generate a new migration
    - Check if a new migration is needed: `alembic check`
    - Generate a new migration if a new migration is needed: `alembic revision --autogenerate -m "<some message>"`
    - (If needed) Change the generated file in `alembic/versions/` to add the necessary changes (that are not auto-generated), e.g.,:
      - import `pgvector` library for `Vector` type
      - create and drop necessary indexes
      - create and drop vector extension
      - ...  
    - Apply the changes to the database: `alembic upgrade head`
    - (If needed) you can undo the last change to the database: `alembic downgrade -1`
</details>

<details>
  <summary>Testing</summary>

  - Make sure services and database are running, as instructed previously
    - We will read and write to the `db` instance running in docker
    - We will **NOT** send and receive requests to the `app` server instance running in docker because we use `TestClient` (but still need to make sure it's running in order to apply database migrations and run `pytest`, and all `env` variables are only available in the container of `app` server)
  - Make sure you have applied the latest migrations, and all tables are empty
    - `docker-compose exec app alembic upgrade head`
  - Run tests
    - `docker-compose exec app pytest -vv -s`
  - Apart from running `pytest`, you should also manually do integration tests by sending requests to the endpoints (the `app` server instance running in docker) and checking the behaviors
</details>
