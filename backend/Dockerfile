
FROM python:3.12


WORKDIR /backend


COPY ./requirements.txt /backend/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

# TODO: remove this and use either AWS Secrets Manager or container definition on fargate
# COPY .env /backend/.env
COPY ./alembic.ini /backend/

COPY ./app /backend/app


CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]