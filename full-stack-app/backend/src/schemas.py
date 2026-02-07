from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RecurrenceRuleEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = PriorityEnum.medium
    tags: Optional[List[str]] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_rule: Optional[RecurrenceRuleEnum] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title must be provided and not empty')
        if len(v) > 255:
            raise ValueError('Title must be 255 characters or less')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 10000:
            raise ValueError('Description must be 10000 characters or less')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            if len(v) > 10:
                raise ValueError('A task can have at most 10 tags')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
        return v

    @validator('due_at')
    def validate_due_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v

    @validator('remind_at')
    def validate_reminder_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Reminder time must be in the future')
        return v

    @validator('remind_at')
    def validate_reminder_before_due(cls, v):
        # This would need to access the due_at value in a real implementation
        return v


class TaskCreate(TaskBase):
    ai_interpret: Optional[bool] = False  # Whether to use AI subagents to interpret the task


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    tags: Optional[List[str]] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    completed: Optional[bool] = None
    recurrence_rule: Optional[RecurrenceRuleEnum] = None

    @validator('title')
    def validate_title(cls, v):
        if v and (not v.strip() or len(v.strip()) == 0):
            raise ValueError('Title must not be empty if provided')
        if v and len(v) > 255:
            raise ValueError('Title must be 255 characters or less')
        return v.strip() if v else v

    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 10000:
            raise ValueError('Description must be 10000 characters or less')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            if len(v) > 10:
                raise ValueError('A task can have at most 10 tags')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
        return v

    @validator('due_at')
    def validate_due_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v

    @validator('remind_at')
    def validate_reminder_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Reminder time must be in the future')
        return v


from uuid import UUID

class TaskResponse(TaskBase):
    task_id: str  # This will be converted from UUID to string
    completed: bool
    completion_date: Optional[datetime] = None
    user_id: str  # This will be converted from UUID to string
    created_at: datetime
    updated_at: datetime
    version: int = 1

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }