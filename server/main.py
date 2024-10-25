# import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from server import config
from server.logging import get_logger, setup_logging

from .routes import apps, auth, functions, projects


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
#     sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# Configure logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Aipolabs",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


# Set all CORS enabled origins
# if settings.all_cors_origins:
# TODO: configure CORS properly
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.all_cors_origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.error(f"Validation error, request: {request}, error: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Internal validation error"},
    )


# Include routers with prefixes
# app.include_router(client.router, prefix="/v1/client", tags=["client"])
# app.include_router(team.router, prefix="/v1/team", tags=["team"])
# app.include_router(apps.router, prefix="/v1/apps", tags=["apps"])
# app.include_router(actions.router, prefix="/v1/actions", tags=["actions"])

app.add_middleware(SessionMiddleware, secret_key=config.SESSION_SECRET_KEY)

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/v1/projects", tags=["projects"])
app.include_router(apps.router, prefix="/v1/apps", tags=["apps"])
app.include_router(functions.router, prefix="/v1/functions", tags=["functions"])
