# Aipolabs Core Components

## OpenAPI Specification
TODO

## Requirements

- Python ^3.12
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

## Development

### Run database migrations
- `alembic current`: show the current revision
- `alembic check`: detect if there are any new upgrade operations.
- `alembic revision --autogenerate -m "xxx"`: generate a new revision
- change the generated file in `alembic/versions/` to add the necessary changes, e.g.,:
  - import `pgvector` library for `Vector` type
  - create and drop necessary indexes
  - create and drop vector extension
  - ...

- `alembic upgrade head`: apply the changes to the database
- `alembic downgrade -1`: undo the last change

### Run postgreSQL and server in Docker locally
- `docker-compose up --build`: build server and start the database and server
- DATABASE_URL = "postgresql://test_user:password@localhost:5432/test_db"
- (optional) Download a GUI client like `DBeaver` to connect to the database
