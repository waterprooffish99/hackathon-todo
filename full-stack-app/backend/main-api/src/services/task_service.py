from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import json
from ..models import Task, User


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, task: Task) -> Task:
        """Create a new task."""
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        import uuid
        try:
            uuid_obj = uuid.UUID(task_id)
        except ValueError:
            return None  # Invalid UUID format

        statement = select(Task).where(Task.id == uuid_obj)
        return self.session.exec(statement).first()

    def list_by_user(self, user_id: str) -> List[Task]:
        """List all tasks for a user."""
        # The user_id here might already be a UUID object from get_current_user
        # Check if it's already a UUID, otherwise convert from string
        import uuid
        if isinstance(user_id, uuid.UUID):
            uuid_obj = user_id
        else:
            try:
                uuid_obj = uuid.UUID(user_id)
            except ValueError:
                return []  # Invalid UUID format

        statement = select(Task).where(Task.user_id == uuid_obj)
        return self.session.exec(statement).all()

    def update(self, task_id: str, task_data: Task) -> Task:
        """Update a task."""
        task = self.get(task_id)
        if not task:
            raise ValueError("Task not found")

        # Update fields
        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task_id: str) -> bool:
        """Delete a task."""
        task = self.get(task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    def mark_complete(self, task_id: str) -> Optional[Task]:
        """Mark a task as complete."""
        task = self.get(task_id)
        if not task:
            return None

        task.completed = True
        task.completed_at = datetime.now()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def sort_tasks(self, tasks: List[Task], sort_by: str, order: str) -> List[Task]:
        """Sort tasks by a given field."""
        reverse = order.lower() == "desc"

        if sort_by == "title":
            tasks.sort(key=lambda x: x.title or "", reverse=reverse)
        elif sort_by == "created_date":
            tasks.sort(key=lambda x: x.created_at or datetime.min, reverse=reverse)
        elif sort_by == "due_date":
            tasks.sort(key=lambda x: x.due_at or datetime.max, reverse=reverse)
        elif sort_by == "completed":
            tasks.sort(key=lambda x: x.completed, reverse=reverse)
        elif sort_by == "priority":
            tasks.sort(key=lambda x: x.priority or "", reverse=reverse)

        return tasks

    def search_tasks(self, user_id: str, query: str) -> List[Task]:
        """Search tasks by content."""
        statement = select(Task).where(
            (Task.user_id == user_id) &
            (
                (Task.title.contains(query)) |
                (Task.description.contains(query)) |
                (Task.tags.contains(query))
            )
        )
        return self.session.exec(statement).all()