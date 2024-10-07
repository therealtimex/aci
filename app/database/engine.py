import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_FULL_URL = os.getenv("DB_FULL_URL")
if not DB_FULL_URL:
    raise ValueError("DB_FULL_URL environment variable is not set")

SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(DB_FULL_URL))
