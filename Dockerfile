
FROM python:3.12


WORKDIR /backend

# Install Poetry, make sure poetry is in the PATH, and configure poetry to not create virtual environments
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -
RUN cd /usr/local/bin && ln -s /opt/poetry/bin/poetry
RUN poetry config virtualenvs.create false


# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /backend/

# COPY ./requirements.txt /backend/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

# ENV PYTHONPATH=${PYTHONPATH}:${PWD} 

# TODO: remove this and use either AWS Secrets Manager or container definition on fargate
# COPY .env /backend/.env
COPY ./alembic.ini /backend/

COPY ./app /backend/app


CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]