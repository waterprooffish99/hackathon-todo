"""
Module for scheduling reminders using Dapr capabilities.
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from .dapr_client import dapr_client


class ReminderScheduler:
    """
    Scheduler for task reminders using Dapr capabilities.
    """

    def __init__(self, dapr_http_port: int = 3500):
        self.dapr_http_port = dapr_http_port
        self.base_url = f"http://localhost:{dapr_http_port}"

    async def schedule_reminder(
        self,
        task_id: str,
        reminder_time: datetime,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Schedule a reminder for a specific task at a given time.
        """
        try:
            # Calculate delay in seconds from now until reminder time
            now = datetime.utcnow()
            delay_seconds = max(0, (reminder_time - now).total_seconds())

            # Prepare reminder data
            reminder_data = {
                "task_id": task_id,
                "user_id": user_id,
                "scheduled_at": now.isoformat(),
                "reminder_time": reminder_time.isoformat(),
                "triggered": False
            }

            # Use Dapr's pub/sub to schedule the reminder
            # In a real implementation, we might use Dapr's Actor reminders or a job scheduler
            # For now, we'll publish to the reminders topic
            success = await dapr_client.publish_event(
                pubsub_name="task-pubsub",
                topic_name="reminders",
                data=reminder_data,
                user_context=user_context
            )

            return success
        except Exception as e:
            print(f"Failed to schedule reminder: {e}")
            return False

    async def cancel_reminder(
        self,
        task_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cancel a scheduled reminder for a task.
        """
        try:
            # In a real implementation, we would need a mechanism to cancel scheduled reminders
            # For now, we'll just log that cancellation was requested
            print(f"Reminder cancellation requested for task {task_id}")
            return True
        except Exception as e:
            print(f"Failed to cancel reminder: {e}")
            return False

    async def process_reminder_request(self, reminder_data: Dict[str, Any]) -> bool:
        """
        Process a reminder request and send notification.
        This would typically be called by the notification service.
        """
        try:
            # Extract reminder information
            task_id = reminder_data.get("task_id")
            user_id = reminder_data.get("user_id")

            # In a real implementation, this would trigger sending the actual notification
            # For now, we'll just log the reminder event
            print(f"Processing reminder for task {task_id} and user {user_id}")

            # Update reminder as triggered
            reminder_data["triggered"] = True
            reminder_data["triggered_at"] = datetime.utcnow().isoformat()

            return True
        except Exception as e:
            print(f"Failed to process reminder: {e}")
            return False


# Global instance
reminder_scheduler = ReminderScheduler()