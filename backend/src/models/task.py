from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    """
    Task model representing a todo item owned by a specific user with status and metadata.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(nullable=False, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # For Pydantic serialization compatibility
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}