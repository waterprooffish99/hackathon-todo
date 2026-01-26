from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    """
    User model representing a registered user account with authentication credentials and metadata.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, nullable=False, max_length=255)
    name: str = Field(nullable=False, min_length=1, max_length=255)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # For Pydantic serialization compatibility
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}