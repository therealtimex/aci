from . import db
from sqlalchemy.orm import Session
from typing import Generator


def get_db_session() -> Generator[Session, None, None]:
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
