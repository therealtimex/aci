from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aipolabs.server import config

SessionMaker = sessionmaker(
    autocommit=False, autoflush=False, bind=create_engine(config.DB_FULL_URL)
)
