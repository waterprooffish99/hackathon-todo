"""
Database skill module for handling database operations.

This module centralizes all database connection and session management logic
to ensure consistency and reusability across the application.
"""

from sqlmodel import Session, select
from typing import Optional, List, TypeVar, Generic
from uuid import UUID
from src.db.database import get_session, engine
from contextlib import contextmanager

T = TypeVar('T')

class DatabaseSkill(Generic[T]):
    """
    Generic database skill class for common CRUD operations.
    """

    def __init__(self, model_class: T):
        self.model_class = model_class

    @contextmanager
    def get_db_session(self):
        """Get a database session with proper cleanup."""
        with get_session() as session:
            try:
                yield session
            finally:
                session.close()

    def create(self, obj: T, session: Session) -> T:
        """Create a new object in the database."""
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def get_by_id(self, id: UUID, session: Session) -> Optional[T]:
        """Retrieve an object by its ID."""
        statement = select(self.model_class).where(self.model_class.id == id)
        return session.exec(statement).first()

    def get_all(self, session: Session, offset: int = 0, limit: int = 100) -> List[T]:
        """Retrieve all objects with optional pagination."""
        statement = select(self.model_class).offset(offset).limit(limit)
        return session.exec(statement).all()

    def update(self, id: UUID, updates: dict, session: Session) -> Optional[T]:
        """Update an object by ID with provided updates."""
        obj = self.get_by_id(id, session)
        if obj:
            for key, value in updates.items():
                setattr(obj, key, value)
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj

    def delete(self, id: UUID, session: Session) -> bool:
        """Delete an object by ID."""
        obj = self.get_by_id(id, session)
        if obj:
            session.delete(obj)
            session.commit()
            return True
        return False

def get_db_session_context():
    """Get database session using context manager."""
    return get_session()

def get_engine():
    """Get the database engine instance."""
    return engine