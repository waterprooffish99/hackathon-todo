from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
import os
from typing import Generator

# Get database URL from environment or use in-memory for testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create engine based on the database URL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(bind=engine)

def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    with Session(engine) as session:
        yield session