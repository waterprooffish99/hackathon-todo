"""
User isolation skill module for enforcing user access controls.

This module centralizes all user isolation logic to ensure that users
can only access their own resources and not others' data.
"""

from typing import Optional
from fastapi import HTTPException, status
from uuid import UUID

class UserIsolationSkill:
    """
    User isolation skill class for enforcing user access controls.
    """

    @staticmethod
    def verify_user_owns_resource(token_user_id: str, resource_user_id: str) -> bool:
        """
        Verify that the user ID in the JWT token matches the resource's owner ID.

        Args:
            token_user_id: User ID extracted from JWT token
            resource_user_id: User ID associated with the resource

        Returns:
            bool: True if user IDs match, False otherwise
        """
        return token_user_id == resource_user_id

    @staticmethod
    def enforce_user_ownership(token_user_id: str, path_user_id: str):
        """
        Enforce that the token user ID matches the path user ID.

        Args:
            token_user_id: User ID from the JWT token
            path_user_id: User ID from the request path

        Raises:
            HTTPException: If user IDs don't match
        """
        if token_user_id != path_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources"
            )

    @staticmethod
    def validate_user_access(current_user_id: str, target_user_id: str) -> bool:
        """
        Validate that the current user can access the target resource.

        Args:
            current_user_id: ID of the currently authenticated user
            target_user_id: ID of the resource owner

        Returns:
            bool: True if access is allowed, False otherwise
        """
        return current_user_id == target_user_id

    @staticmethod
    def check_cross_user_access_attempt(requesting_user_id: str, target_user_id: str) -> bool:
        """
        Check if a cross-user access attempt is happening.

        Args:
            requesting_user_id: ID of the user making the request
            target_user_id: ID of the resource owner

        Returns:
            bool: True if attempting cross-user access, False if accessing own resources
        """
        return requesting_user_id != target_user_id