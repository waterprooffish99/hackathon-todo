"""
Event consumer for the recurring task service.
Consumes task completion events to create next occurrences for recurring tasks.
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select
from ...shared.src.models import Task, Event, RecurrenceRuleEnum
from ...shared.src.services import TaskService


class TaskEventConsumer:
    """
    Consumer that processes task events, particularly completion events for recurring tasks.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.task_service = TaskService(db_session)

    async def process_task_completed_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a task completion event to create next occurrence if the task is recurring.

        Args:
            event_data: The event data containing task completion information

        Returns:
            True if successfully processed, False otherwise
        """
        try:
            # Extract task information from the event
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id")

            # Get the completed task from the payload
            payload_str = event_data.get("payload", "{}")
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                print(f"Failed to parse payload for task {task_id}")
                return False

            # Check if the task is recurring
            recurrence_rule_str = payload.get("recurrence_rule")
            if not recurrence_rule_str or recurrence_rule_str == "":
                print(f"Task {task_id} is not recurring, skipping next occurrence creation")
                return True

            # Create the next occurrence based on the recurrence rule
            success = await self.create_next_occurrence(payload)
            if success:
                print(f"Successfully created next occurrence for recurring task {task_id}")
            else:
                print(f"Failed to create next occurrence for recurring task {task_id}")

            return success
        except Exception as e:
            print(f"Error processing task completed event: {e}")
            return False

    async def create_next_occurrence(self, completed_task_data: Dict[str, Any]) -> bool:
        """
        Create the next occurrence of a recurring task based on the recurrence rule.

        Args:
            completed_task_data: The data of the completed task

        Returns:
            True if successfully created, False otherwise
        """
        try:
            # Create a new task with the same properties as the completed one
            new_task_data = completed_task_data.copy()

            # Reset the ID to create a new record
            new_task_data["task_id"] = None

            # Reset completion status
            new_task_data["completed"] = False
            new_task_data["completion_date"] = None

            # Update creation and update times
            new_task_data["created_at"] = datetime.utcnow()
            new_task_data["updated_at"] = datetime.utcnow()

            # Calculate next due date based on recurrence rule
            recurrence_rule = new_task_data.get("recurrence_rule")
            current_due_at = new_task_data.get("due_at")

            if current_due_at and recurrence_rule:
                new_due_at = self.calculate_next_due_date(current_due_at, recurrence_rule)
                new_task_data["due_at"] = new_due_at

            # Calculate next reminder time if applicable
            current_remind_at = new_task_data.get("remind_at")
            if current_remind_at and current_due_at:
                time_diff = self.parse_datetime(current_due_at) - self.parse_datetime(current_remind_at)
                new_remind_at = self.parse_datetime(new_task_data["due_at"]) - time_diff
                new_task_data["remind_at"] = new_remind_at.isoformat() if new_task_data["due_at"] else None

            # Create the new task
            from ...shared.src.models import Task
            new_task = Task(**{k: v for k, v in new_task_data.items() if k in Task.__fields__})

            created_task = self.task_service.create(new_task)
            return created_task is not None
        except Exception as e:
            print(f"Error creating next occurrence: {e}")
            return False

    def calculate_next_due_date(self, current_due_at: str, recurrence_rule: str) -> str:
        """
        Calculate the next due date based on the recurrence rule.

        Args:
            current_due_at: The current due date as ISO string
            recurrence_rule: The recurrence rule (daily, weekly, monthly)

        Returns:
            The next due date as ISO string
        """
        current_date = self.parse_datetime(current_due_at)

        if recurrence_rule == "daily":
            next_date = current_date + timedelta(days=1)
        elif recurrence_rule == "weekly":
            next_date = current_date + timedelta(weeks=1)
        elif recurrence_rule == "monthly":
            # Simple implementation - add approximately one month
            next_date = current_date + timedelta(days=30)
        else:
            # Default to daily if unknown rule
            next_date = current_date + timedelta(days=1)

        return next_date.isoformat()

    def parse_datetime(self, date_str: str) -> datetime:
        """
        Parse an ISO datetime string to a datetime object.

        Args:
            date_str: The date string in ISO format

        Returns:
            A datetime object
        """
        try:
            # Handle the case where microseconds are included
            if "." in date_str:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            # If the above formats don't work, try without timezone
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))


# Global instance (would be initialized with actual session when used)
# task_event_consumer = TaskEventConsumer(db_session)