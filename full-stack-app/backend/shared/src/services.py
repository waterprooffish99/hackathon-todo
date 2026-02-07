from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from sqlmodel import Session, select
from .models import User, Task, Event, AuditLog

T = TypeVar('T')

class BaseService(ABC, Generic[T]):
    """Base service class with common operations."""

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def create(self, obj: T) -> T:
        """Create a new object."""
        pass

    @abstractmethod
    def get(self, id: int) -> Optional[T]:
        """Get an object by ID."""
        pass

    @abstractmethod
    def update(self, id: int, obj: T) -> Optional[T]:
        """Update an object."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an object."""
        pass

    @abstractmethod
    def list(self) -> List[T]:
        """List all objects."""
        pass


class UserService(BaseService[User]):
    """Service for user operations."""

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def update(self, user_id: int, user: User) -> Optional[User]:
        db_user = self.session.get(User, user_id)
        if db_user:
            for key, value in user.dict(exclude_unset=True).items():
                setattr(db_user, key, value)
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        return None

    def delete(self, user_id: int) -> bool:
        user = self.session.get(User, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def list(self) -> List[User]:
        return self.session.exec(select(User)).all()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()


class TaskService(BaseService[Task]):
    """Service for task operations."""

    def create(self, task: Task) -> Task:
        # Validate task constraints before creating
        if task.due_at and task.remind_at and task.remind_at >= task.due_at:
            raise ValueError("Reminder time must be before due time")

        if task.due_at and task.due_at < datetime.utcnow():
            raise ValueError("Due date must be in the future")

        if task.remind_at and task.remind_at < datetime.utcnow():
            raise ValueError("Reminder time must be in the future")

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def update(self, task_id: int, task: Task) -> Optional[Task]:
        db_task = self.session.get(Task, task_id)
        if db_task:
            # Validate task constraints before updating
            if task.due_at and task.remind_at and task.remind_at >= task.due_at:
                raise ValueError("Reminder time must be before due time")

            if task.due_at and task.due_at < datetime.utcnow():
                raise ValueError("Due date must be in the future")

            if task.remind_at and task.remind_at < datetime.utcnow():
                raise ValueError("Reminder time must be in the future")

            for key, value in task.dict(exclude_unset=True).items():
                setattr(db_task, key, value)
            self.session.add(db_task)
            self.session.commit()
            self.session.refresh(db_task)
            return db_task
        return None

    def delete(self, task_id: int) -> bool:
        task = self.session.get(Task, task_id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False

    def list(self) -> List[Task]:
        return self.session.exec(select(Task)).all()

    def list_by_user(self, user_id: int) -> List[Task]:
        """Get all tasks for a specific user."""
        statement = select(Task).where(Task.user_id == user_id)
        return self.session.exec(statement).all()

    def list_by_status(self, user_id: int, completed: bool) -> List[Task]:
        """Get tasks for a user by completion status."""
        statement = select(Task).where(Task.user_id == user_id, Task.completed == completed)
        return self.session.exec(statement).all()

    def list_by_priority(self, user_id: int, priority: str) -> List[Task]:
        """Get tasks for a user by priority."""
        statement = select(Task).where(Task.user_id == user_id, Task.priority == priority)
        return self.session.exec(statement).all()

    def list_by_tags(self, user_id: int, tags: List[str]) -> List[Task]:
        """Get tasks for a user by tags."""
        # This is a simplified implementation - in a real system, you'd need to parse the JSON tags string
        statement = select(Task).where(Task.user_id == user_id)
        all_tasks = self.session.exec(statement).all()
        # Filter tasks that have any of the specified tags (simplified logic)
        filtered_tasks = []
        for task in all_tasks:
            if task.tags:  # If task has tags
                import json
                try:
                    task_tags = json.loads(task.tags) if isinstance(task.tags, str) else task.tags
                    if task_tags and any(tag in task_tags for tag in tags):
                        filtered_tasks.append(task)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat tags as a comma-separated string
                    task_tags = task.tags.split(',') if isinstance(task.tags, str) else []
                    if any(tag.strip() in [t.strip() for t in task_tags] for tag in tags):
                        filtered_tasks.append(task)
        return filtered_tasks

    def list_by_due_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Task]:
        """Get tasks for a user by due date range."""
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.due_at >= start_date,
            Task.due_at <= end_date
        )
        return self.session.exec(statement).all()

    def search_tasks(self, user_id: int, query: str) -> List[Task]:
        """Full-text search on task titles and descriptions."""
        statement = select(Task).where(
            Task.user_id == user_id
        ).where(
            (Task.title.contains(query)) | (Task.description.contains(query))
        )
        return self.session.exec(statement).all()

    def sort_tasks(self, tasks: List[Task], sort_by: str, order: str = "asc") -> List[Task]:
        """Sort tasks by a given field."""
        reverse = order.lower() == "desc"
        if sort_by.lower() == "due_date":
            return sorted(tasks, key=lambda t: t.due_at or datetime.min, reverse=reverse)
        elif sort_by.lower() == "priority":
            priority_order = {"high": 3, "medium": 2, "low": 1}
            return sorted(tasks, key=lambda t: priority_order.get(t.priority.value, 0), reverse=reverse)
        elif sort_by.lower() == "created_date":
            return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)
        elif sort_by.lower() == "title":
            return sorted(tasks, key=lambda t: t.title.lower(), reverse=reverse)
        else:
            # Default to sorting by creation date
            return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)

    def mark_complete(self, task_id: int) -> Optional[Task]:
        """Mark a task as complete."""
        db_task = self.session.get(Task, task_id)
        if db_task:
            db_task.completed = True
            db_task.completion_date = datetime.utcnow()
            self.session.add(db_task)
            self.session.commit()
            self.session.refresh(db_task)

            # If this was a recurring task, create the next occurrence
            if db_task.recurrence_rule:
                self._create_next_recurring_task(db_task)

            return db_task
        return None

    def _create_next_recurring_task(self, completed_task: Task) -> Optional[Task]:
        """Create the next occurrence of a recurring task."""
        if not completed_task.recurrence_rule:
            return None

        from copy import deepcopy
        new_task = deepcopy(completed_task)
        new_task.task_id = None  # Reset ID to create a new record
        new_task.created_at = datetime.utcnow()
        new_task.updated_at = datetime.utcnow()
        new_task.completed = False
        new_task.completion_date = None

        # Calculate next due date based on recurrence rule
        if completed_task.due_at:
            if completed_task.recurrence_rule == RecurrenceRuleEnum.daily:
                new_task.due_at = completed_task.due_at.replace(day=completed_task.due_at.day + 1)
            elif completed_task.recurrence_rule == RecurrenceRuleEnum.weekly:
                new_task.due_at = completed_task.due_at.replace(day=completed_task.due_at.day + 7)
            elif completed_task.recurrence_rule == RecurrenceRuleEnum.monthly:
                # Simple implementation - add 30 days
                new_task.due_at = completed_task.due_at.replace(day=min(completed_task.due_at.day + 30, 28))

        # Calculate next reminder time if applicable
        if completed_task.remind_at and completed_task.due_at:
            time_diff = completed_task.due_at - completed_task.remind_at
            if new_task.due_at:
                new_task.remind_at = new_task.due_at - time_diff

        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task


class EventService(BaseService[Event]):
    """Service for event operations."""

    def create(self, event: Event) -> Event:
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def get(self, event_id: int) -> Optional[Event]:
        return self.session.get(Event, event_id)

    def update(self, event_id: int, event: Event) -> Optional[Event]:
        db_event = self.session.get(Event, event_id)
        if db_event:
            for key, value in event.dict(exclude_unset=True).items():
                setattr(db_event, key, value)
            self.session.add(db_event)
            self.session.commit()
            self.session.refresh(db_event)
            return db_event
        return None

    def delete(self, event_id: int) -> bool:
        event = self.session.get(Event, event_id)
        if event:
            self.session.delete(event)
            self.session.commit()
            return True
        return False

    def list(self) -> List[Event]:
        return self.session.exec(select(Event)).all()

    def list_by_task(self, task_id: int) -> List[Event]:
        """Get all events for a specific task."""
        statement = select(Event).where(Event.task_id == task_id)
        return self.session.exec(statement).all()

    def list_by_user(self, user_id: int) -> List[Event]:
        """Get all events for a specific user."""
        statement = select(Event).where(Event.user_id == user_id)
        return self.session.exec(statement).all()

    def publish_to_topic(self, event: Event, topic_name: str):
        """
        Publish an event to a specific Kafka topic using Dapr.
        This method would integrate with the event_publisher module.
        """
        # This would typically call the event_publisher to publish to the specific topic
        # For now, we'll just mark the event as published in the DB
        event.processed = True
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event


class AuditLogService(BaseService[AuditLog]):
    """Service for audit log operations."""

    def create(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        self.session.commit()
        self.session.refresh(audit_log)
        return audit_log

    def get(self, log_id: int) -> Optional[AuditLog]:
        return self.session.get(AuditLog, log_id)

    def update(self, log_id: int, audit_log: AuditLog) -> Optional[AuditLog]:
        db_log = self.session.get(AuditLog, log_id)
        if db_log:
            for key, value in audit_log.dict(exclude_unset=True).items():
                setattr(db_log, key, value)
            self.session.add(db_log)
            self.session.commit()
            self.session.refresh(db_log)
            return db_log
        return None

    def delete(self, log_id: int) -> bool:
        audit_log = self.session.get(AuditLog, log_id)
        if audit_log:
            self.session.delete(audit_log)
            self.session.commit()
            return True
        return False

    def list(self) -> List[AuditLog]:
        return self.session.exec(select(AuditLog)).all()

    def list_by_task(self, task_id: int) -> List[AuditLog]:
        """Get all audit logs for a specific task."""
        statement = select(AuditLog).where(AuditLog.task_id == task_id)
        return self.session.exec(statement).all()

    def list_by_user(self, user_id: int) -> List[AuditLog]:
        """Get all audit logs for a specific user."""
        statement = select(AuditLog).where(AuditLog.user_id == user_id)
        return self.session.exec(statement).all()