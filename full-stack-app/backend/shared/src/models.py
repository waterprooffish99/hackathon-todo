from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum
from sqlalchemy import JSON, ARRAY, String


# Enums
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class RecurrenceRuleEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class ActionTypeEnum(str, Enum):
    task_created = "task_created"
    task_updated = "task_updated"
    task_completed = "task_completed"
    task_deleted = "task_deleted"


# Base model with common fields
class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User model
class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = None


class User(UserBase, TimestampMixin, table=True):
    __tablename__ = "users"

    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")


# Task model
class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(max_length=10000)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)
    tags: Optional[str] = Field(default=None)  # Store as JSON string representation of array
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    completed: bool = Field(default=False)
    completion_date: Optional[datetime] = None
    recurrence_rule: Optional[RecurrenceRuleEnum] = None
    user_id: uuid.UUID = Field(foreign_key="users.user_id")


class Task(TaskBase, TimestampMixin, table=True):
    __tablename__ = "tasks"

    task_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    version: int = Field(default=1)  # For optimistic locking

    # Relationship
    user: User = Relationship(back_populates="tasks")


# Event model
class EventBase(SQLModel):
    event_type: str
    event_version: str = Field(default="1.0.0")
    task_id: uuid.UUID = Field(foreign_key="tasks.task_id")
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    payload: str = Field(default="{}")  # Store as JSON string
    correlation_id: str
    processed: bool = Field(default=False)


class Event(EventBase, table=True):
    __tablename__ = "events"

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# AuditLog model
class AuditLogBase(SQLModel):
    event_id: uuid.UUID = Field(foreign_key="events.event_id")
    task_id: uuid.UUID = Field(foreign_key="tasks.task_id")
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    action: ActionTypeEnum
    previous_state: Optional[dict] = Field(default=None)  # JSON field for previous task state
    new_state: dict = Field(default={})  # JSON field for new task state
    metadata: Optional[dict] = Field(default={})  # Additional context


class AuditLog(AuditLogBase, table=True):
    __tablename__ = "audit_logs"

    log_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)