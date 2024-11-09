"""Note: try to keep dependencies on other internal packages to a minimum."""

# TODO: ideally shouldn't need it in python 3.12 for forward reference?
from __future__ import annotations

import datetime
import enum
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

# Note: need to use postgresqlr ARRAY in order to use overlap operator
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

EMBEDDING_DIMENTION = 1024
APP_DEFAULT_VERSION = "1.0.0"
SHORT_STRING_LENGTH = 100
NORMAL_STRING_LENGTH = 255


class Plan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Visibility(str, enum.Enum):
    # public to all users
    PUBLIC = "public"
    # only visible to project that has visibility access set to private, useful for internal testing, A/B testing and phased rollout
    PRIVATE = "private"


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    name: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


# TODO: add indexes for frequently used fields for all tables, including embedding fields. Note we might need to set up index for embedding manually
# for customizing the similarity search algorithm (https://github.com/pgvector/pgvector)
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    auth_provider: Mapped[str] = mapped_column(
        String(NORMAL_STRING_LENGTH), nullable=False
    )  # google, github, email, etc
    auth_user_id: Mapped[str] = mapped_column(
        String(NORMAL_STRING_LENGTH), nullable=False
    )  # google id, github id, email, etc
    name: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    # deleting user will delete all projects owned by the user
    owned_projects: Mapped[list[Project]] = relationship(
        "Project",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="Project.owner_user_id",
        init=False,
    )

    __table_args__ = (
        UniqueConstraint("auth_provider", "auth_user_id", name="uc_auth_provider_user"),
    )


# logical container for isolating and managing API keys, selected apps, and other data
# each project can have multiple API keys
# TODO: might need to limit number of projects a user can create
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    name: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)

    # owner of the project can be a user or an organization, here we have both fields as ForeignKey instead of (owner_type + owner_id)
    # to enforce db integrity
    owner_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    owner_organization_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    # Note: creator is not necessarily the owner
    # should be a user and should be the same as owner_user_id if owner is of type user
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # if public, the project can only access public apps and functions
    # if private, the project can access all apps and functions, useful for A/B testing and internal testing before releasing
    # newly added apps and functions to public
    visibility_access: Mapped[Visibility] = mapped_column(
        Enum(Visibility), default=Visibility.PUBLIC, nullable=False
    )

    """ quota related fields: TODO: TBD how to implement quota system """
    daily_quota_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, init=False)
    daily_quota_reset_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    total_quota_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False, init=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    # deleting project will delete all agents under the project
    agents: Mapped[list[Agent]] = relationship(
        "Agent", lazy="select", cascade="all, delete-orphan", init=False
    )

    # check constraint to ensure project owner is either a user or an organization
    __table_args__ = (
        CheckConstraint(
            "(owner_user_id IS NOT NULL AND owner_organization_id IS NULL) OR "
            "(owner_user_id IS NULL AND owner_organization_id IS NOT NULL)",
            name="cc_project_owner",
        ),
    )


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    # agent level control of what apps and functions are not accessible by the agent, apart from the project level control
    # TODO: reconsider if this should be in a separate table to enforce data integrity, or use periodic task to clean up
    excluded_apps: Mapped[list[UUID]] = mapped_column(ARRAY(PGUUID(as_uuid=True)), nullable=False)
    excluded_functions: Mapped[list[UUID]] = mapped_column(
        ARRAY(PGUUID(as_uuid=True)), nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    # Note: for now each agent has one API key, but we can add more flexibility in the future if needed
    # deleting agent will delete all API keys under the agent
    api_keys: Mapped[list[APIKey]] = relationship(
        "APIKey", lazy="select", cascade="all, delete-orphan", init=False
    )


class APIKey(Base):
    __tablename__ = "api_keys"

    class Status(enum.Enum):
        ACTIVE = "active"
        # can only be disabled by aipolabs
        DISABLED = "disabled"
        # TODO: this is soft delete (requested by user), in the future might consider hard delete and keep audit logs somewhere else
        DELETED = "deleted"

    # id is not the actual API key, it's just a unique identifier to easily reference each API key entry without depending
    # on the API key string itself.
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    # "key" is the actual API key string that the user will use to authenticate
    key: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False, unique=True)
    agent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("agents.id"), unique=True, nullable=False
    )
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )


# Note: filtering categories should be manageable because the App table will be very small
# in the unlikely event that it grows too large, we can consider using a separate table for categories
# TODO: create index on embedding and other fields that are frequently used for filtering
class App(Base):
    __tablename__ = "apps"

    class AuthType(str, enum.Enum):
        CUSTOM = "custom"  # placeholder, not really used yet
        NO_AUTH = "no_auth"  # for apps that does not require authentication, or only to access functions that does not require auth
        API_KEY = "api_key"
        HTTP_BASIC = "http_basic"
        HTTP_BEARER = "http_bearer"
        OAUTH2 = "oauth2"
        OPEN_ID = "open_id"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    # e.g., "github", "google". Note there can be another app also named "github" but from a different company,
    # in this case we need to make sure the name is unique by adding some kind of provider field or version or random string.
    # Need it to be unique to support both sdk (where user can specify apps by name) and globally unique function name.
    name: Mapped[str] = mapped_column(String(SHORT_STRING_LENGTH), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(SHORT_STRING_LENGTH), nullable=False)
    # provider (or company) of the app, e.g., google, github, or aipolabs or user (if allow user to create custom apps)
    provider: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    server_url: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    logo: Mapped[str | None] = mapped_column(Text, nullable=True)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    supported_auth_types: Mapped[list[AuthType]] = mapped_column(
        ARRAY(Enum(AuthType)), nullable=False
    )
    # key is the auth type, value is the corresponding auth config
    auth_configs: Mapped[dict] = mapped_column(JSON, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENTION), nullable=False)
    version: Mapped[str] = mapped_column(String(SHORT_STRING_LENGTH), nullable=False)
    # if private, the app is only visible to App creator (e.g., aipolabs team only, useful for internal testing)
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), nullable=False)
    # if false, the app is not visible and reachable to all and will not be shown in the app store
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    # deleting app will delete all functions under the app
    functions: Mapped[list["Function"]] = relationship(
        "Function", lazy="select", cascade="all, delete-orphan", init=False
    )


# TODO: how to do versioning for app and funcitons to allow backward compatibility, or we don't actually need to
# because function schema is loaded dynamically from the database to user
# TODO: do we need auth_required on function level?
class Function(Base):
    __tablename__ = "functions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    # Note: the function name is unique across the platform and should have app information, e.g., "github_clone_repo"
    # ideally this should just be <app name>_<function name>
    name: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False, unique=True)
    app_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("apps.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # TODO: should response schema be generic (data + execution success of not + optional error) or specific to the function
    response: Mapped[dict] = mapped_column(JSON, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    # TODO: currently created with name, description, parameters, response
    # TODO: should we provide EMBEDDING_DIMENTION here? which makes it less flexible if we want to change the embedding dimention in the future
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENTION), nullable=False)
    # empty dict for function that takes no args
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    # if private, the app is only visible to App creator (e.g., aipolabs team only, useful for internal testing)
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), nullable=False)
    # if false, the function is not visible and will not be searchable and executable
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )


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

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    app_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("apps.id"), nullable=False
    )
    # controlled by users to enable or disable the app integration
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # exclude certain functions from the app.
    # TODO: Reconsider if this should be in a separate table to enforce data integrity, or use periodic task to clean up
    excluded_functions: Mapped[list[UUID]] = mapped_column(
        ARRAY(PGUUID(as_uuid=True)), nullable=False, default_factory=list
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    # unique constraint
    __table_args__ = (UniqueConstraint("project_id", "app_id", name="uc_project_app"),)


# a connected account is specific to an app in a project.
class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default_factory=uuid4, init=False
    )
    project_app_integration_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("project_app_integrations.id"), nullable=False
    )
    # account_owner should be unique per app per project (or just per ProjectAppIntegration), it identifies the end user, not the project owner.
    # ideally this should be some user id in client's system that uniquely identify this account owner.
    account_owner_id: Mapped[str] = mapped_column(String(NORMAL_STRING_LENGTH), nullable=False)
    # here we assume it's possible to have connected account but no auth is required, in which case auth_data will be null
    auth_type: Mapped[App.AuthType] = mapped_column(Enum(App.AuthType), nullable=False)
    # auth_data is different for each auth type, e.g., API key, OAuth2 (access token, refresh token, scope, etc) etc
    auth_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "project_app_integration_id", "account_owner_id", name="uc_project_app_account_owner"
        ),
    )
