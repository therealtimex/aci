# Aipolabs Core Components

## OpenAPI Specification
TODO

## Local Development
Guidelines for setting up the local development environment.

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

### Run postgreSQL and backend in Docker locally
- create a `.env` file in the root directory based on `.env.example`
  - Note that we don't use the `.env` file in the production environment
  - `.env` is provided to docker compose to set up the environment variables in the container, not loaded by the backend directly
- `docker-compose up --build`: build backend and start the database and backend

### Run database migrations
In local development the backend directory is mounted as a volume inside the container,you can run the migrations with `alembic` commands inside the container and the migration code (`versions` folder) will be in your local directory (instead of being only inside the container).
- Get a bash shell inside the backend container for running commands
  - `docker-compose exec backend bash`
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

### Type checking
- `mypy backend/ --ignore-missing-imports`: run type checking for the backend module
- `mypy backend/crud.py  --ignore-missing-imports`: run type checking for the `crud.py` file with ignoring missing imports
