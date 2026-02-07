"""
Module for Dapr service-to-service communication with mTLS.
"""

import httpx
from typing import Dict, Any, Optional
import json
from .dapr_context import inject_user_context_in_dapr_call


class DaprClient:
    """
    Client for Dapr service-to-service communication with mTLS.
    """

    def __init__(self, dapr_http_port: int = 3500, dapr_grpc_port: int = 50001):
        self.dapr_http_port = dapr_http_port
        self.dapr_grpc_port = dapr_grpc_port
        self.base_url = f"http://localhost:{dapr_http_port}"

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a method on another service via Dapr service invocation.
        """
        if headers is None:
            headers = {}

        # Inject user context into headers
        if user_context:
            headers = inject_user_context_in_dapr_call(headers, user_context)

        # Add Dapr-specific headers
        headers["dapr-app-id"] = app_id

        # Prepare the request
        url = f"{self.base_url}/v1.0/invoke/{app_id}/method/{method}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if data:
                    response = await client.post(url, json=data, headers=headers)
                else:
                    response = await client.get(url, headers=headers)

                # Raise exception for bad status codes
                response.raise_for_status()

                # Return the response JSON
                return response.json()
            except httpx.HTTPStatusError as e:
                # Handle HTTP errors
                raise Exception(f"Dapr service invocation failed: {e}")
            except httpx.RequestError as e:
                # Handle connection errors
                raise Exception(f"Failed to connect to Dapr: {e}")

    async def publish_event(
        self,
        pubsub_name: str,
        topic_name: str,
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish an event to a Dapr pub/sub topic.
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic_name}"

        # Prepare the payload with user context if provided
        payload = {
            "data": data
        }

        if user_context:
            # Add user context to the payload
            payload["data"]["user_context"] = user_context

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)

                # Raise exception for bad status codes
                response.raise_for_status()

                return True
            except httpx.HTTPStatusError as e:
                print(f"Failed to publish event: {e}")
                return False
            except httpx.RequestError as e:
                print(f"Failed to connect to Dapr for publishing: {e}")
                return False

    async def get_secret(
        self,
        store_name: str,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Retrieve a secret from Dapr secret store.
        """
        if metadata is None:
            metadata = {}

        url = f"{self.base_url}/v1.0/secrets/{store_name}/{key}"

        # Add metadata as query parameters
        params = {f"metadata.{k}": v for k, v in metadata.items()}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)

                # Raise exception for bad status codes
                response.raise_for_status()

                result = response.json()
                # Secrets are returned in a dictionary with the key as the secret name
                return result.get(key)
            except httpx.HTTPStatusError as e:
                print(f"Failed to retrieve secret: {e}")
                return None
            except httpx.RequestError as e:
                print(f"Failed to connect to Dapr for secrets: {e}")
                return None


# Global Dapr client instance
dapr_client = DaprClient()