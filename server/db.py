from sqlalchemy import (
    create_engine,
    Boolean,
    ForeignKey,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    Enum,
    func,
    Text,
    ARRAY,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pgvector.sqlalchemy import Vector
import uuid
import enum
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


EMBEDDING_DIMENTION = 1024
APP_DEFAULT_VERSION = "1.0.0"


class Base(DeclarativeBase):
    pass


# TODO: add indexes for frequently used fields for all tables, including embedding fields. Note we might need to set up index for embedding manually
# for customizing the similarity search algorithm (https://github.com/pgvector/pgvector)
# TODO: use incrementing integer as primary key for simplicity and performance
# TODO: limit auth_provider to a set of values?
class User(Base):
    __tablename__ = "users"

    class OrgRole(enum.Enum):
        BASIC = "basic"
        ADMIN = "admin"
        OWNER = "owner"

    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_provider = mapped_column(String(255), nullable=False)  # google, github, email, etc
    auth_user_id = mapped_column(String(255), nullable=False)  # google id, github id, email, etc
    name = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), nullable=True)
    profile_picture = mapped_column(Text, nullable=True)
    # TODO: might need a Organization table in the future
    organization_id = mapped_column(PGUUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    organization_role = mapped_column(Enum(OrgRole), nullable=False, default=OrgRole.OWNER)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("auth_provider", "auth_user_id", name="uc_auth_provider_user"),)


# logical container for isolating and managing API keys, selected apps, and other data
# each project can have multiple API keys
# TODO: might need to limit number of projects a user can create
# TODO: might need to assign projects to organizations
class Project(Base):
    __tablename__ = "projects"
    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(255), nullable=False)
    creator_id = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class APIKey(Base):
    __tablename__ = "api_keys"

    class Status(enum.Enum):
        ACTIVE = "active"
        # can only be disabled by aipolabs
        DISABLED = "disabled"
        # TODO: this is soft delete (requested by user), in the future might consider hard delete and keep audit logs somewhere else
        DELETED = "deleted"

    class Plan(enum.Enum):
        FREE = "free"
        BASIC = "basic"
        PRO = "pro"
        ENTERPRISE = "enterprise"

    # id is not the actual API key, it's just a unique identifier to easily reference each API key entry without depending
    # on the API key string itself.
    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # TODO: the actual API key string that the user will use to authenticate, consider encrypting it
    key = mapped_column(String(100), nullable=False, unique=True)
    # TODO: each project only allow one api key to make quota management easier, in the future might allow multiple api keys
    project_id = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id"), unique=True, nullable=False)
    creator_id = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = mapped_column(Enum(Status), default=Status.ACTIVE, nullable=False)
    plan = mapped_column(Enum(Plan), default=Plan.FREE, nullable=False)
    daily_quota_used = mapped_column(Integer, default=0, nullable=False)
    daily_quota_reset_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_quota_used = mapped_column(Integer, default=0, nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# TODO: filtering by tags and categories should be manageable because the App table will be very small
# in the unlikely event that it grows too large, we can consider using a separate table for tags and categories
# TODO: consider using enum for categories in the future
# TODO: create index on embedding and other fields that are frequently used for filtering
class App(Base):
    __tablename__ = "apps"

    class AuthType(enum.Enum):
        API_KEY = "api_key"
        OPEN_ID = "open_id"
        OAUTH2 = "oauth2"
        BASIC_AUTH = "basic_auth"
        BRERAR_TOKEN = "bearer_token"

    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # e.g., "github", "google". Note there can be another app also named "github" but from a different company,
    # in this case we need to make sure the name is unique by adding some kind of provider field or version or random string.
    # Need it to be unique to support both sdk (where user can specify apps by name) and globally unique function name.
    name = mapped_column(String(50), nullable=False, unique=True)
    display_name = mapped_column(String(50), nullable=False)
    version = mapped_column(String(50), nullable=False, default=APP_DEFAULT_VERSION)
    # provider (or company) of the app, e.g., google, github, or aipolabs or user (if allow user to create custom apps)
    provider = mapped_column(String(255), nullable=False)
    description = mapped_column(Text, nullable=False)
    website = mapped_column(String(255), nullable=True)
    logo = mapped_column(Text, nullable=True)
    categories = mapped_column(ARRAY(String), nullable=False)
    tags = mapped_column(ARRAY(String), nullable=False)
    # false if the app does not require customer authentication, e.g., scrapers API
    auth_required = mapped_column(Boolean, default=True, nullable=False)
    supported_auth_types = mapped_column(ARRAY(Enum(AuthType)), nullable=False)
    # controlled by aipolabs
    enabled = mapped_column(Boolean, default=True, nullable=False)
    # TODO: currently created with name, description, categories, tags
    embedding = mapped_column(Vector(EMBEDDING_DIMENTION), nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    functions = relationship("Function", back_populates="app", lazy="select", cascade="all, delete-orphan")


# TODO: how to do versioning for app and funcitons to allow backward compatibility, or we don't actually need to
# because function schema is loaded dynamically from the database to user
# TODO: do we need auth_required on function level?
class Function(Base):
    __tablename__ = "functions"

    # TODO: I don't see a reason yet to have a separate id for function as primary key instead of just using function name,
    # but keep it for now for potential future use
    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Note: the function name is unique across the platform and should have app information, e.g., "github_clone_repo"
    # ideally this should just be <app name>_<function name>
    name = mapped_column(String(255), nullable=False, unique=True)
    app_id = mapped_column(PGUUID(as_uuid=True), ForeignKey("apps.id"), nullable=False)
    description = mapped_column(Text, nullable=False)
    parameters = mapped_column(JSON, nullable=False)
    # TODO: should response schema be generic (data + execution success of not + optional error) or specific to the function
    response = mapped_column(JSON, nullable=False)
    # TODO: currently created with name, description, parameters, response
    embedding = mapped_column(Vector(EMBEDDING_DIMENTION), nullable=False)
    # controlled by aipolabs
    enabled = mapped_column(Boolean, default=True, nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    app = relationship("App", back_populates="functions", lazy="select")


# A user can have multiple projects, a project can integrate multiple apps, an app can have multiple connected accounts.
# Same app in different projects need to authenticate user accounts separately.
# When a user first create a project, there is no record for that project in this table,
# the record is created when the user select (enable) an app to the project.
# When user disable an app from the project, the record is not deleted, just the status is changed to disabled
# TODO: table can get large if there are too many users and each has many projects, need to keep an eye out on performance
# TODO: will it be necessary to store user selected auth type for the app here?
# TODO: will there be performance issue if we offer a button in dev portal to enable all apps at once?
class ProjectAppIntegration(Base):
    __tablename__ = "project_app_integrations"

    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    app_id = mapped_column(PGUUID(as_uuid=True), ForeignKey("apps.id"), nullable=False)
    # controlled by users
    enabled = mapped_column(Boolean, default=True, nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # unique constraint
    __table_args__ = (UniqueConstraint("project_id", "app_id", name="uc_project_app"),)


# a connected account is specific to an app in a project.
class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_app_integration_id = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("project_app_integrations.id"), nullable=False
    )
    # account_owner should be unique per app per project (or just per ProjectAppIntegration), it identifies the end user, not the project owner.
    # ideally this should be some user id in client's system that uniquely identify this account owner.
    account_owner_id = mapped_column(String(255), nullable=False)
    # TODO: here we assume it's possible to have connected account but no auth is required, in which case auth_type and auth_data will be null
    auth_type = mapped_column(Enum(App.AuthType), nullable=True)
    # auth_data is different for each auth type, e.g., API key, OAuth2 etc
    auth_data = mapped_column(JSON, nullable=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("project_app_integration_id", "account_owner_id", name="uc_project_app_account_owner"),
    )
