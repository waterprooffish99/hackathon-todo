"""
Module for implementing event tracing and correlation for debugging purposes.
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class TraceLogLevel(Enum):
    """
    Log level for trace entries.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class EventTracer:
    """
    System for tracking and correlating events for debugging purposes.
    """

    def __init__(self):
        # In-memory store for trace data (in production, this would be a database)
        self.trace_store = {}
        self.correlation_store = {}

    def start_trace(self, event_type: str, initial_data: Dict[str, Any] = None) -> str:
        """
        Start a new trace for an event.

        Args:
            event_type: Type of the event being traced
            initial_data: Initial data to associate with the trace

        Returns:
            Trace ID for the new trace
        """
        trace_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        trace_entry = {
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            "event_type": event_type,
            "start_time": datetime.utcnow().isoformat(),
            "entries": [],
            "status": "active",
            "initial_data": initial_data or {}
        }

        self.trace_store[trace_id] = trace_entry

        # Store by correlation ID as well
        if correlation_id not in self.correlation_store:
            self.correlation_store[correlation_id] = []
        self.correlation_store[correlation_id].append(trace_id)

        return trace_id

    def add_trace_entry(
        self,
        trace_id: str,
        log_level: TraceLogLevel,
        message: str,
        data: Dict[str, Any] = None,
        component: str = None
    ):
        """
        Add an entry to an existing trace.

        Args:
            trace_id: ID of the trace to add the entry to
            log_level: Level of the log entry
            message: Message for the log entry
            data: Additional data to include in the log entry
            component: Component that generated the trace entry
        """
        if trace_id not in self.trace_store:
            print(f"Warning: Trace {trace_id} not found")
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": log_level.value,
            "message": message,
            "component": component or "unknown",
            "data": data or {}
        }

        self.trace_store[trace_id]["entries"].append(entry)

    def end_trace(self, trace_id: str, status: str = "completed", final_data: Dict[str, Any] = None):
        """
        End a trace with a final status.

        Args:
            trace_id: ID of the trace to end
            status: Final status of the trace (completed, failed, etc.)
            final_data: Final data to associate with the trace
        """
        if trace_id not in self.trace_store:
            print(f"Warning: Trace {trace_id} not found")
            return

        trace = self.trace_store[trace_id]
        trace["end_time"] = datetime.utcnow().isoformat()
        trace["status"] = status
        if final_data:
            trace["final_data"] = final_data

    def correlate_events(self, correlation_id: str) -> List[Dict[str, Any]]:
        """
        Get all traces associated with a correlation ID.

        Args:
            correlation_id: ID to correlate events by

        Returns:
            List of trace data associated with the correlation ID
        """
        if correlation_id not in self.correlation_store:
            return []

        traces = []
        for trace_id in self.correlation_store[correlation_id]:
            if trace_id in self.trace_store:
                traces.append(self.trace_store[trace_id])

        return traces

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific trace by its ID.

        Args:
            trace_id: ID of the trace to retrieve

        Returns:
            Trace data or None if not found
        """
        return self.trace_store.get(trace_id)

    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a specific trace.

        Args:
            trace_id: ID of the trace to summarize

        Returns:
            Trace summary or None if not found
        """
        trace = self.trace_store.get(trace_id)
        if not trace:
            return None

        duration = None
        if "end_time" in trace:
            start = datetime.fromisoformat(trace["start_time"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(trace["end_time"].replace("Z", "+00:00"))
            duration = (end - start).total_seconds()

        return {
            "trace_id": trace["trace_id"],
            "correlation_id": trace["correlation_id"],
            "event_type": trace["event_type"],
            "start_time": trace["start_time"],
            "end_time": trace.get("end_time"),
            "duration_seconds": duration,
            "status": trace["status"],
            "entry_count": len(trace["entries"]),
            "error_count": len([e for e in trace["entries"] if e["level"] == "ERROR"]),
            "warning_count": len([e for e in trace["entries"] if e["level"] == "WARNING"])
        }

    def search_traces(
        self,
        event_type: str = None,
        status: str = None,
        start_time_after: str = None,
        end_time_before: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for traces matching certain criteria.

        Args:
            event_type: Filter by event type
            status: Filter by status
            start_time_after: Filter for traces started after this time
            end_time_before: Filter for traces ended before this time
            limit: Maximum number of results to return

        Returns:
            List of trace summaries matching the criteria
        """
        matching_traces = []

        for trace_id, trace in self.trace_store.items():
            # Apply filters
            if event_type and trace["event_type"] != event_type:
                continue
            if status and trace["status"] != status:
                continue
            if start_time_after:
                if datetime.fromisoformat(trace["start_time"].replace("Z", "+00:00")) < \
                   datetime.fromisoformat(start_time_after.replace("Z", "+00:00")):
                    continue
            if end_time_before and "end_time" in trace:
                if datetime.fromisoformat(trace["end_time"].replace("Z", "+00:00")) > \
                   datetime.fromisoformat(end_time_before.replace("Z", "+00:00")):
                    continue

            summary = self.get_trace_summary(trace_id)
            if summary:
                matching_traces.append(summary)

                # Apply limit
                if len(matching_traces) >= limit:
                    break

        return matching_traces

    def export_trace(self, trace_id: str) -> str:
        """
        Export a trace as a JSON string.

        Args:
            trace_id: ID of the trace to export

        Returns:
            JSON string representation of the trace
        """
        trace = self.get_trace(trace_id)
        if trace:
            return json.dumps(trace, indent=2)
        return "{}"

    def get_component_stats(self, trace_id: str) -> Dict[str, Any]:
        """
        Get statistics about components involved in a trace.

        Args:
            trace_id: ID of the trace to analyze

        Returns:
            Statistics about components in the trace
        """
        trace = self.trace_store.get(trace_id)
        if not trace:
            return {}

        component_stats = {}
        for entry in trace["entries"]:
            component = entry["component"]
            if component not in component_stats:
                component_stats[component] = {
                    "count": 0,
                    "levels": {},
                    "messages": []
                }

            component_stats[component]["count"] += 1

            level = entry["level"]
            if level not in component_stats[component]["levels"]:
                component_stats[component]["levels"][level] = 0
            component_stats[component]["levels"][level] += 1

            component_stats[component]["messages"].append({
                "timestamp": entry["timestamp"],
                "message": entry["message"],
                "level": entry["level"]
            })

        return component_stats


class EventTraceMiddleware:
    """
    Middleware for automatically tracing events through the system.
    """

    def __init__(self):
        self.tracer = EventTracer()

    async def trace_event_processing(
        self,
        event_data: Dict[str, Any],
        processor_func,
        component_name: str,
        *args,
        **kwargs
    ):
        """
        Process an event with automatic tracing.

        Args:
            event_data: The event data to process
            processor_func: Function to process the event
            component_name: Name of the component processing the event
            *args: Additional arguments to pass to the processor
            **kwargs: Additional keyword arguments to pass to the processor

        Returns:
            Result of the event processing
        """
        # Extract trace and correlation IDs from event, or create new ones
        correlation_id = event_data.get("correlation_id", str(uuid.uuid4()))
        trace_id = self.tracer.start_trace(
            event_data.get("event_type", "unknown"),
            {"event_data_keys": list(event_data.keys())}
        )

        # Add initial trace entry
        self.tracer.add_trace_entry(
            trace_id,
            TraceLogLevel.INFO,
            f"Event processing started in {component_name}",
            {"event_type": event_data.get("event_type")},
            component_name
        )

        try:
            # Process the event
            result = await processor_func(event_data, *args, **kwargs)

            # Add success trace entry
            self.tracer.add_trace_entry(
                trace_id,
                TraceLogLevel.INFO,
                f"Event processing completed successfully in {component_name}",
                {"result_type": type(result).__name__},
                component_name
            )

            # End the trace
            self.tracer.end_trace(trace_id, "completed", {"result": str(result)[:200]})  # Limit result length

            return result
        except Exception as e:
            # Add error trace entry
            self.tracer.add_trace_entry(
                trace_id,
                TraceLogLevel.ERROR,
                f"Event processing failed in {component_name}: {str(e)}",
                {"error_type": type(e).__name__},
                component_name
            )

            # End the trace with error status
            self.tracer.end_trace(trace_id, "failed", {"error": str(e)})

            # Re-raise the exception
            raise

    def get_correlation_trace(self, correlation_id: str) -> List[Dict[str, Any]]:
        """
        Get all traces for a correlation ID.

        Args:
            correlation_id: ID to get traces for

        Returns:
            List of traces associated with the correlation ID
        """
        return self.tracer.correlate_events(correlation_id)


# Global instance
event_tracer = EventTraceMiddleware()