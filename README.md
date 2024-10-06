# Aipolabs Core Components

## Project Structure
Currently only contains the app server code (and associated database).
But can be extended to include more services (e.g., separate admin server, sdk, cli, etc.) as a monorepo if needed.

## OpenAPI Specification
TODO

## Local Development
Guidelines for setting up the containerized development environment locally

### Requirements
- Python ^3.12
- Install docker
- Install virtualenv: `pip install virtualenv`
- Create a virtual env: `cd /path/to/your/project && python -m venv venv`
- Activate virtual env: `source venv/bin/activate`
- Install dependencies
  - `pip install -r requirements.txt`
- Formatter: `Black`
  - Install `Black Formatter` extension in VS Code
  - It should respect the settings in `.vscode/settings.json`
- Linter: `Flake8`
  - Install `Flake8` extension in VS Code
  - It should work out of box and respect the settings in `.vscode/settings.json` if any

### Virtual Environment
Because we use docker and docker compose to run components in a container, installing the dependencies here locally is more for development purposes.
- Activate virtual environemnt
  - `poetry shell`
- Install dependencies
  - `poetry install`

### Run postgreSQL and app server in Docker locally
- create a `.env` file in the root directory based on `.env.example`
  - Note that we don't use the `.env` file in the production environment
  - `.env` is provided to docker compose to set up the environment variables in the container, not loaded by the app server directly
- `docker-compose up --build`: build app server and start the database and app server

### Run database migrations
In local development the `app` directory is mounted as a volume inside the container,you can run the migrations with `alembic` commands inside the container and the migration code (`versions` folder) will be in your local directory (instead of being only inside the container).
- Get a bash shell inside the app server container for running commands
  - `docker-compose exec app bash`
- Set up the database (running in docker) with the latest migration 
  - `alembic upgrade head`
- (Optional) Connect to the database using a GUI client like `DBeaver`
  - parameters for the db connection can be found in the `docker-compose.yml` file
- After (if any) changing any tables or models, generate a new migration
  - `alembic check`: check if a new migration is needed
  - `alembic revision --autogenerate -m "<some message>"`: generate a new migration if a new migration is needed
  - change the generated file in `alembic/versions/` to add the necessary changes (that are not auto-generated), e.g.,:
    - import `pgvector` library for `Vector` type
    - create and drop necessary indexes
    - create and drop vector extension
    - ...  
  - `alembic upgrade head`: apply the changes to the database
  - `alembic downgrade -1`: you can undo the last change to the database

### Testing
- make sure services and database are running, if not, run 
  - `docker-compose up --build`
  - we will read and write to the `db` running in docker
  - we will NOT send and receive requests to the `app` server running in docker because we use `TestClient` (but still need to make sure it's running in order to apply database migrations and run `pytest`, e.g., all env variables are only available in the container of `app` server)
- make sure you have applied the latest migrations, and all tables are empty
  - `docker-compose exec app alembic upgrade head`
- run tests
  - `docker-compose exec app pytest -vv -s`

### Type checking
- `mypy app/ `: run (outside of the container) type checking for the app module
  - configure mypy in `mypy.ini`

