"""
Module for implementing event schema validation and versioning system.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re


class EventSchemaValidator:
    """
    Validator for event schemas with versioning support.
    """

    def __init__(self):
        # Define known event schemas by type and version
        self.schemas = {
            "task.created": {
                "1.0.0": {
                    "required": ["event_type", "event_version", "task_id", "user_id", "payload", "timestamp", "correlation_id"],
                    "properties": {
                        "event_type": {"type": "string", "pattern": "^task\\.created$"},
                        "event_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                        "task_id": {"type": "string", "format": "uuid"},
                        "user_id": {"type": "string", "format": "uuid"},
                        "payload": {"type": "string"},  # JSON string
                        "timestamp": {"type": "string", "format": "date-time"},
                        "correlation_id": {"type": "string", "format": "uuid"}
                    }
                }
            },
            "task.updated": {
                "1.0.0": {
                    "required": ["event_type", "event_version", "task_id", "user_id", "payload", "timestamp", "correlation_id"],
                    "properties": {
                        "event_type": {"type": "string", "pattern": "^task\\.updated$"},
                        "event_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                        "task_id": {"type": "string", "format": "uuid"},
                        "user_id": {"type": "string", "format": "uuid"},
                        "payload": {"type": "string"},  # JSON string
                        "timestamp": {"type": "string", "format": "date-time"},
                        "correlation_id": {"type": "string", "format": "uuid"}
                    }
                }
            },
            "task.completed": {
                "1.0.0": {
                    "required": ["event_type", "event_version", "task_id", "user_id", "payload", "timestamp", "correlation_id"],
                    "properties": {
                        "event_type": {"type": "string", "pattern": "^task\\.completed$"},
                        "event_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                        "task_id": {"type": "string", "format": "uuid"},
                        "user_id": {"type": "string", "format": "uuid"},
                        "payload": {"type": "string"},  # JSON string
                        "timestamp": {"type": "string", "format": "date-time"},
                        "correlation_id": {"type": "string", "format": "uuid"}
                    }
                }
            },
            "task.deleted": {
                "1.0.0": {
                    "required": ["event_type", "event_version", "task_id", "user_id", "payload", "timestamp", "correlation_id"],
                    "properties": {
                        "event_type": {"type": "string", "pattern": "^task\\.deleted$"},
                        "event_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                        "task_id": {"type": "string", "format": "uuid"},
                        "user_id": {"type": "string", "format": "uuid"},
                        "payload": {"type": "string"},  # JSON string
                        "timestamp": {"type": "string", "format": "date-time"},
                        "correlation_id": {"type": "string", "format": "uuid"}
                    }
                }
            },
            "reminder.triggered": {
                "1.0.0": {
                    "required": ["event_type", "event_version", "task_id", "user_id", "payload", "timestamp", "correlation_id"],
                    "properties": {
                        "event_type": {"type": "string", "pattern": "^reminder\\.triggered$"},
                        "event_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                        "task_id": {"type": "string", "format": "uuid"},
                        "user_id": {"type": "string", "format": "uuid"},
                        "payload": {"type": "string"},  # JSON string
                        "timestamp": {"type": "string", "format": "date-time"},
                        "correlation_id": {"type": "string", "format": "uuid"}
                    }
                }
            }
        }

    def validate_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an event against its schema.

        Args:
            event_data: The event data to validate

        Returns:
            Dictionary with validation result and any errors
        """
        try:
            # Extract event type and version
            event_type = event_data.get("event_type")
            event_version = event_data.get("event_version", "1.0.0")

            # Check if schema exists for this event type and version
            if event_type not in self.schemas:
                return {
                    "valid": False,
                    "errors": [f"Unknown event type: {event_type}"]
                }

            # Find the closest matching version (prefer exact match, fall back to major version)
            schema = self._get_schema_for_version(event_type, event_version)
            if not schema:
                return {
                    "valid": False,
                    "errors": [f"No schema found for event type {event_type} and version {event_version}"]
                }

            # Validate against schema
            errors = self._validate_against_schema(event_data, schema)

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "schema_used": f"{event_type}:{event_version}"
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }

    def _get_schema_for_version(self, event_type: str, requested_version: str) -> Optional[Dict[str, Any]]:
        """
        Get the appropriate schema for the requested version.

        Args:
            event_type: The type of event
            requested_version: The requested version

        Returns:
            Schema dictionary or None if not found
        """
        # Exact version match
        if requested_version in self.schemas[event_type]:
            return self.schemas[event_type][requested_version]

        # Try to find a compatible version (same major version)
        req_major = requested_version.split('.')[0]
        for version, schema in self.schemas[event_type].items():
            if version.startswith(req_major + '.'):
                return schema

        return None

    def _validate_against_schema(self, event_data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """
        Validate event data against a specific schema.

        Args:
            event_data: The event data to validate
            schema: The schema to validate against

        Returns:
            List of validation errors
        """
        errors = []

        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in event_data:
                errors.append(f"Missing required field: {field}")

        # Validate each property
        properties = schema.get("properties", {})
        for field, constraints in properties.items():
            if field in event_data:
                field_value = event_data[field]
                field_errors = self._validate_field(field, field_value, constraints)
                errors.extend(field_errors)
            # Don't report missing required fields here since we checked above

        return errors

    def _validate_field(self, field_name: str, value: Any, constraints: Dict[str, Any]) -> List[str]:
        """
        Validate a single field against its constraints.

        Args:
            field_name: Name of the field
            value: Value of the field
            constraints: Validation constraints

        Returns:
            List of validation errors
        """
        errors = []

        field_type = constraints.get("type")
        if field_type:
            if field_type == "string":
                if not isinstance(value, str):
                    errors.append(f"Field '{field_name}' must be a string, got {type(value).__name__}")
            elif field_type == "number":
                if not isinstance(value, (int, float)):
                    errors.append(f"Field '{field_name}' must be a number, got {type(value).__name__}")
            elif field_type == "integer":
                if not isinstance(value, int):
                    errors.append(f"Field '{field_name}' must be an integer, got {type(value).__name__}")
            elif field_type == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"Field '{field_name}' must be a boolean, got {type(value).__name__}")

        # Check pattern if specified
        pattern = constraints.get("pattern")
        if pattern and isinstance(value, str):
            if not re.match(pattern, value):
                errors.append(f"Field '{field_name}' does not match pattern: {pattern}")

        # Check format if specified
        format_constraint = constraints.get("format")
        if format_constraint and isinstance(value, str):
            if format_constraint == "uuid":
                # Simple UUID validation (checking format)
                uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                if not re.match(uuid_pattern, value, re.IGNORECASE):
                    errors.append(f"Field '{field_name}' is not a valid UUID: {value}")
            elif format_constraint == "date-time":
                try:
                    # Try to parse ISO format date-time
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"Field '{field_name}' is not a valid ISO date-time: {value}")

        # Check if JSON string is valid when format requires it
        if field_name == "payload" and field_type == "string":
            try:
                # Attempt to parse as JSON to ensure it's valid
                json.loads(value)
            except json.JSONDecodeError:
                errors.append(f"Field '{field_name}' is not valid JSON: {value[:50]}...")

        return errors

    def register_schema(self, event_type: str, version: str, schema: Dict[str, Any]):
        """
        Register a new event schema.

        Args:
            event_type: Type of the event
            version: Version of the schema
            schema: Schema definition
        """
        if event_type not in self.schemas:
            self.schemas[event_type] = {}

        self.schemas[event_type][version] = schema

    def get_supported_versions(self, event_type: str) -> List[str]:
        """
        Get all supported versions for an event type.

        Args:
            event_type: Type of the event

        Returns:
            List of supported versions
        """
        if event_type in self.schemas:
            return list(self.schemas[event_type].keys())
        return []


class EventVersioningSystem:
    """
    System for managing event versioning and compatibility.
    """

    def __init__(self):
        self.validator = EventSchemaValidator()

    def validate_and_transform(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an event and transform it to the latest compatible version if needed.

        Args:
            event_data: The event data to validate and transform

        Returns:
            Dictionary with validation result, transformed data, and any errors
        """
        # First, validate the event
        validation_result = self.validator.validate_event(event_data)

        if not validation_result["valid"]:
            return validation_result

        # If valid, return the original data with validation success
        return {
            "valid": True,
            "transformed_data": event_data,
            "errors": [],
            "schema_used": validation_result["schema_used"]
        }

    def is_compatible_version(self, event_type: str, version1: str, version2: str) -> bool:
        """
        Check if two versions are compatible (same major version).

        Args:
            event_type: Type of the event
            version1: First version
            version2: Second version

        Returns:
            True if versions are compatible, False otherwise
        """
        # Two versions are compatible if they have the same major version
        major1 = version1.split('.')[0]
        major2 = version2.split('.')[0]
        return major1 == major2


# Global instance
event_validator = EventVersioningSystem()