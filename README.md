# Aipolabs Core Components

## OpenAPI Specification
TODO

## Development
Guidelines for setting up the development environment.

### Requirements
- Python ^3.12
- Install docker
- (optional) Download a GUI database client like `DBeaver`
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

### Run postgreSQL and server in Docker locally
- create a `.env` file in the root directory based on `.env.example`
  - Note that we don't use the `.env` file in the production environment
- `docker-compose up --build`: build server and start the database and server

### Run database migrations
- Required
  - `alembic upgrade head`: this will create the necessary tables in the database for the first time
- Optional
  - Connect to the database using a GUI client like `DBeaver`, parameters for the db connection can be found in the `docker-compose.yml` file 
- Below are some useful commands but should not be necessary
  - `alembic current`: show the current revision
  - `alembic check`: detect if there are any new upgrade operations.
  - `alembic revision --autogenerate -m "<some message>"`: generate a new revision if there are changes in the models
  - change the generated file in `alembic/versions/` to add the necessary changes, e.g.,:
    - import `pgvector` library for `Vector` type
    - create and drop necessary indexes
    - create and drop vector extension
    - ...
  - `alembic upgrade head`: apply the changes to the database
  - `alembic downgrade -1`: undo the last change
