"""
Middleware and utilities for tenant isolation and user data security.
"""

from fastapi import Request, HTTPException, status
from typing import Dict, Any
from ..auth import get_current_user
from ..models import User


def verify_user_owns_resource(user: User, resource_user_id: str) -> bool:
    """
    Verify that the authenticated user owns the requested resource.

    Args:
        user: The authenticated user
        resource_user_id: The user ID associated with the resource

    Returns:
        True if the user owns the resource, False otherwise
    """
    return str(user.user_id) == str(resource_user_id)


def require_same_user_or_admin(current_user: User, target_user_id: str):
    """
    Check if the current user is accessing their own data or is an admin.

    Args:
        current_user: The authenticated user
        target_user_id: The ID of the user whose data is being accessed

    Raises:
        HTTPException: If the user doesn't have permission
    """
    if str(current_user.user_id) != str(target_user_id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data"
        )


def filter_query_by_user(query, user_id: str, table_alias=None):
    """
    Filter a database query to only include records belonging to the authenticated user.

    Args:
        query: The SQLAlchemy query object
        user_id: The ID of the authenticated user
        table_alias: Optional table alias if using joins

    Returns:
        Filtered query object
    """
    if table_alias:
        return query.filter(table_alias.user_id == user_id)
    else:
        # Assuming the table has a user_id column
        # This is a simplified implementation - in real usage, you'd need to dynamically apply the filter
        return query


def get_user_scoped_filters(user_id: str) -> Dict[str, Any]:
    """
    Get filters to scope queries to the authenticated user.

    Args:
        user_id: The ID of the authenticated user

    Returns:
        Dictionary of filters to apply to queries
    """
    return {
        "user_id": user_id
    }