"""
Module for implementing idempotent event processing to handle at-least-once delivery.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from .models import Event


class IdempotencyService:
    """
    Service for handling idempotent event processing to prevent duplicate processing.
    """

    def __init__(self, session: Session):
        self.session = session

    def is_processed(self, event_id: str) -> bool:
        """
        Check if an event has already been processed.

        Args:
            event_id: The unique identifier for the event

        Returns:
            True if the event has already been processed, False otherwise
        """
        # In a real implementation, we'd have a separate table to track processed events
        # For now, we'll use the processed field in the Event model
        event = self.session.get(Event, event_id)
        if event:
            return event.processed
        return False

    def mark_as_processed(self, event_id: str) -> bool:
        """
        Mark an event as processed.

        Args:
            event_id: The unique identifier for the event

        Returns:
            True if successfully marked as processed, False otherwise
        """
        event = self.session.get(Event, event_id)
        if event:
            event.processed = True
            self.session.add(event)
            self.session.commit()
            return True
        return False

    def process_event_once(self, event: Event, processor_func, *args, **kwargs) -> Any:
        """
        Process an event only if it hasn't been processed before.

        Args:
            event: The event to process
            processor_func: The function to call to process the event
            *args: Arguments to pass to the processor function
            **kwargs: Keyword arguments to pass to the processor function

        Returns:
            Result of the processor function if event was processed, None otherwise
        """
        # Check if the event has already been processed using the correlation ID
        if self.is_processed(str(event.event_id)):
            print(f"Event {event.event_id} has already been processed. Skipping.")
            return None

        # Process the event
        result = processor_func(event, *args, **kwargs)

        # Mark the event as processed
        self.mark_as_processed(str(event.event_id))

        return result

    def generate_event_fingerprint(self, event_data: Dict[str, Any]) -> str:
        """
        Generate a unique fingerprint for an event to identify duplicates.

        Args:
            event_data: The event data dictionary

        Returns:
            A hash string representing the event fingerprint
        """
        # Create a string representation of the event data
        # Sort keys to ensure consistent hashing
        sorted_data = json.dumps(event_data, sort_keys=True, default=str)

        # Generate SHA256 hash
        hash_object = hashlib.sha256(sorted_data.encode())
        return hash_object.hexdigest()

    def check_duplicate_by_content(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if an event with the same content has already been processed.

        Args:
            event_data: The event data dictionary

        Returns:
            True if a duplicate event exists, False otherwise
        """
        fingerprint = self.generate_event_fingerprint(event_data)

        # In a real implementation, we'd have a table to store fingerprints
        # For now, we'll just return False to indicate no duplicates found
        return False


# Example usage function
def example_event_processor(event: Event, *args, **kwargs):
    """
    Example processor function that would be called to handle an event.
    """
    print(f"Processing event: {event.event_type} for task {event.task_id}")
    # Actual event processing logic would go here
    return {"status": "processed", "event_id": str(event.event_id)}