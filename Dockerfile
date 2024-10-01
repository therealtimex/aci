
FROM python:3.12


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# TODO: remove this and use either AWS Secrets Manager or container definition on fargate
COPY .env /code/.env

COPY ./server /code/server


CMD ["fastapi", "run", "server/main.py", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]