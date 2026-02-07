"""
Event consumer for the audit service.
Consumes all task events for immutable logging and compliance.
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from ...shared.src.models import Event, AuditLog, ActionTypeEnum
from ...shared.src.services import AuditLogService


class AuditEventConsumer:
    """
    Consumer that processes all task events for immutable logging and compliance.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.audit_log_service = AuditLogService(db_session)

    async def process_task_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process any task event to create an audit log entry.

        Args:
            event_data: The event data containing task operation information

        Returns:
            True if successfully processed, False otherwise
        """
        try:
            # Extract event information
            event_type = event_data.get("event_type")
            task_id = event_data.get("task_id")
            user_id = event_data.get("user_id")

            # Convert event type to audit action type
            action_type = self.convert_event_type_to_action(event_type)

            # Get the task state from the payload
            payload_str = event_data.get("payload", "{}")
            try:
                new_state = json.loads(payload_str)
            except json.JSONDecodeError:
                print(f"Failed to parse payload for audit event for task {task_id}")
                return False

            # Get previous state if available
            previous_payload_str = event_data.get("previous_payload", "{}")
            try:
                previous_state = json.loads(previous_payload_str) if previous_payload_str != "{}" else None
            except json.JSONDecodeError:
                previous_state = None

            # Create audit log entry
            success = await self.create_audit_log(
                event_data.get("event_id"),
                task_id,
                user_id,
                action_type,
                previous_state,
                new_state
            )

            if success:
                print(f"Successfully created audit log for {event_type} event for task {task_id}")
            else:
                print(f"Failed to create audit log for {event_type} event for task {task_id}")

            return success
        except Exception as e:
            print(f"Error processing audit event: {e}")
            return False

    def convert_event_type_to_action(self, event_type: str) -> ActionTypeEnum:
        """
        Convert the event type string to an ActionTypeEnum value.

        Args:
            event_type: The event type string

        Returns:
            Corresponding ActionTypeEnum value
        """
        if event_type.endswith("created"):
            return ActionTypeEnum.task_created
        elif event_type.endswith("updated"):
            return ActionTypeEnum.task_updated
        elif event_type.endswith("completed"):
            return ActionTypeEnum.task_completed
        elif event_type.endswith("deleted"):
            return ActionTypeEnum.task_deleted
        else:
            # Default to updated for any other task-related events
            return ActionTypeEnum.task_updated

    async def create_audit_log(
        self,
        event_id: str,
        task_id: str,
        user_id: str,
        action: ActionTypeEnum,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any]
    ) -> bool:
        """
        Create an audit log entry for the event.

        Args:
            event_id: The ID of the event
            task_id: The ID of the task
            user_id: The ID of the user
            action: The action type
            previous_state: The previous state of the task
            new_state: The new state of the task

        Returns:
            True if audit log was created successfully, False otherwise
        """
        try:
            from ...shared.src.models import AuditLog

            # Convert states to JSON strings
            previous_state_str = json.dumps(previous_state) if previous_state else None
            new_state_str = json.dumps(new_state)

            # Create audit log object
            audit_log = AuditLog(
                event_id=event_id,
                task_id=task_id,
                user_id=user_id,
                action=action,
                previous_state=previous_state_str,
                new_state=new_state_str,
                metadata=json.dumps({
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "task-event-consumer"
                })
            )

            # Save to database
            created_log = self.audit_log_service.create(audit_log)

            return created_log is not None
        except Exception as e:
            print(f"Error creating audit log: {e}")
            return False

    async def process_multiple_events(self, events_data: list) -> Dict[str, int]:
        """
        Process multiple events in batch.

        Args:
            events_data: List of event data dictionaries

        Returns:
            Dictionary with counts of successful and failed operations
        """
        results = {"success": 0, "failed": 0}

        for event_data in events_data:
            success = await self.process_task_event(event_data)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1

        return results


# Global instance (would be initialized with actual session when used)
# audit_event_consumer = AuditEventConsumer(db_session)