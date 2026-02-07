"""
Module for implementing event ordering and sequencing where required.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from collections import defaultdict, deque
import threading
import time


class EventSequencer:
    """
    Sequencer for managing event ordering and ensuring sequential processing of related events.
    """

    def __init__(self):
        # Dictionary to hold queues for each stream/entity
        self.stream_queues = defaultdict(deque)

        # Dictionary to hold processing locks for each stream
        self.stream_locks = defaultdict(asyncio.Lock)

        # Dictionary to track the sequence numbers
        self.sequence_trackers = defaultdict(lambda: {"last_processed": -1, "pending": {}})

        # Thread safety for sync operations
        self.sync_locks = defaultdict(threading.Lock)

    async def submit_event(
        self,
        event_stream_id: str,
        event_data: Dict[str, Any],
        processor_func: Callable,
        sequence_number: Optional[int] = None
    ) -> Any:
        """
        Submit an event for processing, ensuring ordering if sequence number is provided.

        Args:
            event_stream_id: Identifier for the event stream (e.g., user_id, task_id)
            event_data: The event data to process
            processor_func: Function to process the event
            sequence_number: Optional sequence number for ordering

        Returns:
            Result of the event processing
        """
        if sequence_number is not None:
            # Process with sequence ordering
            return await self._submit_ordered_event(
                event_stream_id, event_data, processor_func, sequence_number
            )
        else:
            # Process without ordering constraints
            return await self._submit_unordered_event(event_data, processor_func)

    async def _submit_ordered_event(
        self,
        event_stream_id: str,
        event_data: Dict[str, Any],
        processor_func: Callable,
        sequence_number: int
    ) -> Any:
        """
        Submit an event for processing with sequence ordering.

        Args:
            event_stream_id: Identifier for the event stream
            event_data: The event data to process
            processor_func: Function to process the event
            sequence_number: Sequence number for ordering

        Returns:
            Result of the event processing
        """
        # Acquire the lock for this stream to safely check and update sequence
        async with self.stream_locks[event_stream_id]:
            tracker = self.sequence_trackers[event_stream_id]

            # If this is the next expected sequence, process immediately
            if sequence_number == tracker["last_processed"] + 1:
                result = await processor_func(event_data)
                tracker["last_processed"] = sequence_number

                # Process any pending events that are now in sequence
                await self._process_pending_events(event_stream_id)

                return result
            else:
                # Add to pending events if it's a future sequence
                if sequence_number > tracker["last_processed"]:
                    tracker["pending"][sequence_number] = {
                        "event_data": event_data,
                        "processor_func": processor_func,
                        "submitted_at": datetime.utcnow()
                    }
                    print(f"Event {sequence_number} queued for stream {event_stream_id}, "
                          f"waiting for sequence {tracker['last_processed'] + 1}")

                    # Wait for the event to be processed when its turn comes
                    return await self._wait_for_sequence_processing(event_stream_id, sequence_number)
                else:
                    # This is a past sequence number - could be a duplicate or out-of-order
                    print(f"Out-of-sequence event {sequence_number} for stream {event_stream_id}, "
                          f"last processed: {tracker['last_processed']}")
                    return None

    async def _submit_unordered_event(
        self,
        event_data: Dict[str, Any],
        processor_func: Callable
    ) -> Any:
        """
        Submit an event for processing without sequence ordering.

        Args:
            event_data: The event data to process
            processor_func: Function to process the event

        Returns:
            Result of the event processing
        """
        return await processor_func(event_data)

    async def _process_pending_events(self, event_stream_id: str):
        """
        Process pending events that are now in sequence.

        Args:
            event_stream_id: Identifier for the event stream
        """
        tracker = self.sequence_trackers[event_stream_id]
        processed_any = True

        # Keep processing while there are pending events in sequence
        while processed_any:
            processed_any = False
            next_seq = tracker["last_processed"] + 1

            if next_seq in tracker["pending"]:
                # Process the next in-sequence event
                pending_event = tracker["pending"].pop(next_seq)

                try:
                    result = await pending_event["processor_func"](pending_event["event_data"])
                    tracker["last_processed"] = next_seq
                    processed_any = True

                    print(f"Processed pending event {next_seq} for stream {event_stream_id}")
                except Exception as e:
                    print(f"Error processing pending event {next_seq} for stream {event_stream_id}: {e}")
                    # We don't want to get stuck, so we remove the problematic event
                    # In a real system, you might want to implement dead letter queue logic
                    continue

    async def _wait_for_sequence_processing(self, event_stream_id: str, sequence_number: int):
        """
        Wait for an event to be processed when its turn comes in sequence.

        Args:
            event_stream_id: Identifier for the event stream
            sequence_number: The sequence number of the event to wait for

        Returns:
            Result of the event processing
        """
        # This is a simplified implementation - in a real system you might use
        # a more sophisticated notification mechanism
        max_wait_time = 30  # seconds
        wait_interval = 0.1  # seconds

        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            async with self.stream_locks[event_stream_id]:
                tracker = self.sequence_trackers[event_stream_id]

                if sequence_number <= tracker["last_processed"]:
                    # Event has been processed (or skipped)
                    # In a real system, we'd need to store the result somewhere
                    return {"status": "processed", "sequence": sequence_number}
                elif sequence_number not in tracker["pending"]:
                    # Event was removed (possibly due to error or timeout)
                    return {"status": "cancelled", "sequence": sequence_number}

            await asyncio.sleep(wait_interval)

        # Timeout reached
        async with self.stream_locks[event_stream_id]:
            tracker = self.sequence_trackers[event_stream_id]
            if sequence_number in tracker["pending"]:
                del tracker["pending"][sequence_number]

        return {"status": "timeout", "sequence": sequence_number}

    def cleanup_old_pending_events(self, event_stream_id: str, max_age_seconds: int = 300):
        """
        Clean up old pending events that have been waiting too long.

        Args:
            event_stream_id: Identifier for the event stream
            max_age_seconds: Maximum age in seconds for pending events
        """
        current_time = datetime.utcnow()
        tracker = self.sequence_trackers[event_stream_id]

        old_sequences = []
        for seq_num, event_info in tracker["pending"].items():
            age = (current_time - event_info["submitted_at"]).total_seconds()
            if age > max_age_seconds:
                old_sequences.append(seq_num)

        for seq_num in old_sequences:
            print(f"Removing old pending event {seq_num} for stream {event_stream_id} "
                  f"(age: {(current_time - tracker['pending'][seq_num]['submitted_at']).total_seconds()}s)")
            del tracker["pending"][seq_num]

    def get_stream_status(self, event_stream_id: str) -> Dict[str, Any]:
        """
        Get status information for an event stream.

        Args:
            event_stream_id: Identifier for the event stream

        Returns:
            Status information for the stream
        """
        tracker = self.sequence_trackers[event_stream_id]
        return {
            "last_processed": tracker["last_processed"],
            "pending_count": len(tracker["pending"]),
            "pending_sequences": sorted(tracker["pending"].keys()),
            "stream_id": event_stream_id
        }


class EventOrderingMiddleware:
    """
    Middleware for ensuring event ordering at the service level.
    """

    def __init__(self):
        self.sequencer = EventSequencer()

    async def process_ordered_event(
        self,
        event_stream_id: str,
        sequence_number: int,
        event_data: Dict[str, Any],
        processor_func: Callable
    ) -> Any:
        """
        Process an event with guaranteed ordering.

        Args:
            event_stream_id: Identifier for the event stream
            sequence_number: Sequence number for ordering
            event_data: The event data to process
            processor_func: Function to process the event

        Returns:
            Result of the event processing
        """
        return await self.sequencer.submit_event(
            event_stream_id, event_data, processor_func, sequence_number
        )

    def get_stream_status(self, event_stream_id: str) -> Dict[str, Any]:
        """
        Get status information for an event stream.

        Args:
            event_stream_id: Identifier for the event stream

        Returns:
            Status information for the stream
        """
        return self.sequencer.get_stream_status(event_stream_id)


# Global instance
event_sequencer = EventOrderingMiddleware()