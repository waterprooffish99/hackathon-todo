"""
Module for handling user context propagation through Dapr metadata.
"""

from typing import Optional, Dict, Any
import json
from fastapi import Request, HTTPException
from .auth import get_current_user


def get_user_context_from_request(request: Request) -> Dict[str, Any]:
    """
    Extract user context from the incoming request.
    This would typically extract user info from JWT token in headers.
    """
    user_context = {}

    # In a real implementation, we would extract user info from auth headers
    # For now, we'll simulate getting user context
    try:
        # This is a placeholder - in real implementation, we'd use the auth system
        user_id = request.headers.get("user-id")  # Could come from JWT token
        if user_id:
            user_context["user_id"] = user_id

        # Add other user context as needed
        user_context["tenant_id"] = request.headers.get("tenant-id", "default")

        return user_context
    except Exception as e:
        # In case of error extracting user context, return minimal context
        return {"user_id": "anonymous", "tenant_id": "default"}


def inject_user_context_in_dapr_call(metadata: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject user context into Dapr call metadata for service-to-service communication.
    """
    # Add user context to metadata for propagation
    updated_metadata = metadata.copy()

    # Serialize user context to string for transport
    user_context_str = json.dumps(user_context)
    updated_metadata["user-context"] = user_context_str

    # Add correlation ID if not present
    if "correlation-id" not in updated_metadata:
        import uuid
        updated_metadata["correlation-id"] = str(uuid.uuid4())

    return updated_metadata


def extract_user_context_from_dapr_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user context from Dapr metadata in incoming service calls.
    """
    user_context = {}

    # Extract user context from metadata
    if "user-context" in metadata:
        try:
            user_context = json.loads(metadata["user-context"])
        except json.JSONDecodeError:
            # If parsing fails, return empty context
            user_context = {"user_id": "anonymous", "tenant_id": "default"}

    # Extract correlation ID
    correlation_id = metadata.get("correlation-id", "")
    if correlation_id:
        user_context["correlation_id"] = correlation_id

    return user_context


def create_dapr_client_with_user_context(user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a Dapr client configuration with user context.
    This is a simplified representation - in reality, you'd use the Dapr SDK.
    """
    dapr_config = {
        "headers": {}
    }

    if user_context:
        # Inject user context into headers for Dapr service invocation
        import json
        dapr_config["headers"]["user-context"] = json.dumps(user_context)

        # Add correlation ID
        import uuid
        dapr_config["headers"]["correlation-id"] = user_context.get("correlation_id", str(uuid.uuid4()))

    return dapr_config