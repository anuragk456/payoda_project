from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Iterator

from config import SQLALCHEMY_DATABASE_URL
from models.record_model import Base

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create DB tables (call at startup)."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
