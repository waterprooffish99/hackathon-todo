"""
Module for publishing events for task lifecycle operations.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from .models import Task
from .dapr_client import dapr_client


class EventPublisher:
    """
    Publisher for task lifecycle events (created, updated, completed, deleted).
    """

    def __init__(self):
        self.pubsub_name = "task-pubsub"

    async def publish_task_created(
        self,
        task: Task,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish an event when a task is created.
        """
        event_data = {
            "event_type": "task.created",
            "event_version": "1.0.0",
            "task_id": str(task.task_id),
            "user_id": str(task.user_id),
            "payload": self._serialize_task(task),
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self._generate_correlation_id()
        }

        return await dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event_data,
            user_context=user_context
        )

    async def publish_task_updated(
        self,
        task: Task,
        previous_state: Optional[Task] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish an event when a task is updated.
        """
        event_data = {
            "event_type": "task.updated",
            "event_version": "1.0.0",
            "task_id": str(task.task_id),
            "user_id": str(task.user_id),
            "payload": self._serialize_task(task),
            "previous_payload": self._serialize_task(previous_state) if previous_state else None,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self._generate_correlation_id()
        }

        return await dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event_data,
            user_context=user_context
        )

    async def publish_task_completed(
        self,
        task: Task,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish an event when a task is completed.
        """
        event_data = {
            "event_type": "task.completed",
            "event_version": "1.0.0",
            "task_id": str(task.task_id),
            "user_id": str(task.user_id),
            "payload": self._serialize_task(task),
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self._generate_correlation_id()
        }

        return await dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event_data,
            user_context=user_context
        )

    async def publish_task_deleted(
        self,
        task_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish an event when a task is deleted.
        """
        event_data = {
            "event_type": "task.deleted",
            "event_version": "1.0.0",
            "task_id": task_id,
            "user_id": user_id,
            "payload": {
                "task_id": task_id,
                "deleted_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self._generate_correlation_id()
        }

        return await dapr_client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name="task-events",
            data=event_data,
            user_context=user_context
        )

    def _serialize_task(self, task: Task) -> str:
        """
        Serialize a task object to a JSON string for event payload.
        """
        if not task:
            return "{}"

        # Convert task to dictionary with proper serialization
        task_dict = {
            "task_id": str(task.task_id) if hasattr(task, 'task_id') else None,
            "title": getattr(task, 'title', ''),
            "description": getattr(task, 'description', ''),
            "priority": getattr(task, 'priority', '').value if hasattr(task, 'priority') and hasattr(task.priority, 'value') else getattr(task, 'priority', ''),
            "tags": getattr(task, 'tags', []),
            "due_at": task.due_at.isoformat() if hasattr(task, 'due_at') and task.due_at else None,
            "remind_at": task.remind_at.isoformat() if hasattr(task, 'remind_at') and task.remind_at else None,
            "completed": getattr(task, 'completed', False),
            "completion_date": task.completion_date.isoformat() if hasattr(task, 'completion_date') and task.completion_date else None,
            "recurrence_rule": getattr(task, 'recurrence_rule', '').value if hasattr(task, 'recurrence_rule') and hasattr(task.recurrence_rule, 'value') else getattr(task, 'recurrence_rule', ''),
            "user_id": str(task.user_id) if hasattr(task, 'user_id') else None,
            "created_at": task.created_at.isoformat() if hasattr(task, 'created_at') and task.created_at else None,
            "updated_at": task.updated_at.isoformat() if hasattr(task, 'updated_at') and task.updated_at else None,
            "version": getattr(task, 'version', 1)
        }

        return json.dumps(task_dict)

    def _generate_correlation_id(self) -> str:
        """
        Generate a correlation ID for tracking related events.
        """
        import uuid
        return str(uuid.uuid4())


# Global instance
event_publisher = EventPublisher()