"""
Task CRUD skill module for handling task operations.

This module centralizes all task-related CRUD operations without authentication logic,
focusing solely on the domain operations for tasks.
"""

from sqlmodel import Session, select
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from src.models.task import Task
from src.models.user import User

class TaskCrudSkill:
    """
    Task CRUD skill class for handling task operations.
    """

    @staticmethod
    def create_task(user_id: UUID, title: str, description: Optional[str], session: Session) -> Task:
        """
        Create a new task for a user.

        Args:
            user_id: ID of the user who owns the task
            title: Title of the task
            description: Optional description of the task
            session: Database session

        Returns:
            Task: The created task object
        """
        task = Task(user_id=user_id, title=title, description=description, completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_tasks_for_user(user_id: UUID, session: Session, completed: Optional[bool] = None,
                          limit: Optional[int] = 100, offset: int = 0) -> List[Task]:
        """
        Get all tasks for a specific user.

        Args:
            user_id: ID of the user whose tasks to retrieve
            session: Database session
            completed: Optional filter for completed status
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            List[Task]: List of tasks for the user
        """
        query = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        query = query.offset(offset).limit(limit) if limit else query.offset(offset)

        return session.exec(query).all()

    @staticmethod
    def get_task_by_id(task_id: UUID, user_id: UUID, session: Session) -> Optional[Task]:
        """
        Get a specific task by ID for a user.

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user who owns the task
            session: Database session

        Returns:
            Task: The task object if found and owned by the user, None otherwise
        """
        task = session.exec(select(Task).where(Task.id == task_id).where(Task.user_id == user_id)).first()
        return task

    @staticmethod
    def update_task(task_id: UUID, user_id: UUID, session: Session, title: Optional[str] = None,
                    description: Optional[str] = None) -> Optional[Task]:
        """
        Update a task for a user.

        Args:
            task_id: ID of the task to update
            user_id: ID of the user who owns the task
            title: New title (optional)
            description: New description (optional)
            session: Database session

        Returns:
            Task: The updated task object if successful, None if not found
        """
        task = TaskCrudSkill.get_task_by_id(task_id, user_id, session)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    @staticmethod
    def delete_task(task_id: UUID, user_id: UUID, session: Session) -> bool:
        """
        Delete a task for a user.

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user who owns the task
            session: Database session

        Returns:
            bool: True if deletion was successful, False if task not found
        """
        task = TaskCrudSkill.get_task_by_id(task_id, user_id, session)
        if task:
            session.delete(task)
            session.commit()
            return True
        return False

    @staticmethod
    def toggle_task_completion(task_id: UUID, user_id: UUID, completed: bool, session: Session) -> Optional[Task]:
        """
        Toggle the completion status of a task.

        Args:
            task_id: ID of the task to update
            user_id: ID of the user who owns the task
            completed: New completion status
            session: Database session

        Returns:
            Task: The updated task object if successful, None if not found
        """
        task = TaskCrudSkill.get_task_by_id(task_id, user_id, session)
        if task:
            task.completed = completed
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    @staticmethod
    def get_task_count_for_user(user_id: UUID, session: Session, completed: Optional[bool] = None) -> int:
        """
        Get the count of tasks for a user.

        Args:
            user_id: ID of the user whose tasks to count
            session: Database session
            completed: Optional filter for completed status

        Returns:
            int: Number of tasks matching the criteria
        """
        count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)

        if completed is not None:
            count_query = count_query.where(Task.completed == completed)

        return session.exec(count_query).one()