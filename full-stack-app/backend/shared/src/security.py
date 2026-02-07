"""
Security utilities for user context verification and access control.
"""

from typing import Optional
from sqlmodel import Session, select
from .models import User, Task, Event, AuditLog


class SecurityContext:
    """
    Class to handle security context and access verification.
    """

    def __init__(self, session: Session):
        self.session = session

    def verify_user_access_to_task(self, user_id: str, task_id: str) -> bool:
        """
        Verify that the user has access to a specific task.

        Args:
            user_id: The ID of the requesting user
            task_id: The ID of the task to check access for

        Returns:
            True if the user has access, False otherwise
        """
        task = self.session.get(Task, task_id)
        if not task:
            return False

        return str(task.user_id) == str(user_id)

    def verify_user_access_to_event(self, user_id: str, event_id: str) -> bool:
        """
        Verify that the user has access to a specific event.

        Args:
            user_id: The ID of the requesting user
            event_id: The ID of the event to check access for

        Returns:
            True if the user has access, False otherwise
        """
        event = self.session.get(Event, event_id)
        if not event:
            return False

        return str(event.user_id) == str(user_id)

    def verify_user_access_to_audit_log(self, user_id: str, log_id: str) -> bool:
        """
        Verify that the user has access to a specific audit log.

        Args:
            user_id: The ID of the requesting user
            log_id: The ID of the audit log to check access for

        Returns:
            True if the user has access, False otherwise
        """
        audit_log = self.session.get(AuditLog, log_id)
        if not audit_log:
            return False

        return str(audit_log.user_id) == str(user_id)

    def get_user_tasks(self, user_id: str) -> list:
        """
        Get all tasks that belong to a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of tasks belonging to the user
        """
        statement = select(Task).where(Task.user_id == user_id)
        return self.session.exec(statement).all()

    def get_user_events(self, user_id: str) -> list:
        """
        Get all events that belong to a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of events belonging to the user
        """
        statement = select(Event).where(Event.user_id == user_id)
        return self.session.exec(statement).all()

    def get_user_audit_logs(self, user_id: str) -> list:
        """
        Get all audit logs that belong to a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of audit logs belonging to the user
        """
        statement = select(AuditLog).where(AuditLog.user_id == user_id)
        return self.session.exec(statement).all()

    def filter_query_by_user(self, model_class, user_id: str):
        """
        Create a query filtered by user ID for a given model.

        Args:
            model_class: The SQLModel class to query
            user_id: The ID of the user

        Returns:
            Filtered query statement
        """
        if hasattr(model_class, 'user_id'):
            return select(model_class).where(model_class.user_id == user_id)
        else:
            # For models that don't have user_id, return all (e.g., for User model itself)
            return select(model_class)