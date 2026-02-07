"""
Event consumer for the notification service.
Consumes reminder events to send user notifications.
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime
from sqlmodel import Session


class ReminderEventConsumer:
    """
    Consumer that processes reminder events to send notifications to users.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def process_reminder_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a reminder event to send appropriate notification to the user.

        Args:
            event_data: The event data containing reminder information

        Returns:
            True if successfully processed, False otherwise
        """
        try:
            # Extract reminder information from the event
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id")

            # Get the reminder details from the payload
            payload_str = event_data.get("payload", "{}")
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                print(f"Failed to parse payload for reminder event for task {task_id}")
                return False

            # Send notification to the user
            success = await self.send_notification(user_id, task_id, payload)

            if success:
                print(f"Successfully sent notification for task {task_id} to user {user_id}")
            else:
                print(f"Failed to send notification for task {task_id} to user {user_id}")

            return success
        except Exception as e:
            print(f"Error processing reminder event: {e}")
            return False

    async def send_notification(self, user_id: str, task_id: str, payload: Dict[str, Any]) -> bool:
        """
        Send a notification to the user based on their preferences.

        Args:
            user_id: The ID of the user to notify
            task_id: The ID of the task that triggered the reminder
            payload: The reminder event payload

        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            # In a real implementation, this would:
            # 1. Look up user's notification preferences
            # 2. Determine the appropriate notification method (email, SMS, push)
            # 3. Send the notification via the chosen method

            # For now, we'll just simulate sending a notification
            notification_message = self.format_notification_message(task_id, payload)

            # Determine notification method based on user preferences (simulated)
            notification_method = self.get_user_notification_preference(user_id)

            print(f"Sending {notification_method} notification to user {user_id}: {notification_message}")

            # Simulate notification delivery
            await asyncio.sleep(0.1)  # Simulate network delay

            # Log the notification
            self.log_notification(user_id, task_id, notification_method, notification_message)

            return True
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False

    def format_notification_message(self, task_id: str, payload: Dict[str, Any]) -> str:
        """
        Format the notification message based on the task information.

        Args:
            task_id: The ID of the task
            payload: The task payload

        Returns:
            Formatted notification message
        """
        # Extract task information from payload
        task_title = payload.get("title", "Unknown Task")

        # Create a meaningful notification message
        return f"Reminder: '{task_title}' is due soon!"

    def get_user_notification_preference(self, user_id: str) -> str:
        """
        Get the user's preferred notification method.

        Args:
            user_id: The ID of the user

        Returns:
            Preferred notification method
        """
        # In a real implementation, this would query a user preferences table
        # For now, we'll default to push notifications
        return "push"

    def log_notification(self, user_id: str, task_id: str, method: str, message: str):
        """
        Log the notification for tracking and debugging purposes.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task
            method: The notification method used
            message: The notification message sent
        """
        # In a real implementation, this would log to a notifications table
        print(f"NOTIFICATION_LOG: user={user_id}, task={task_id}, method={method}, message={message}")


# Global instance (would be initialized with actual session when used)
# reminder_event_consumer = ReminderEventConsumer(db_session)