from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.skills.auth_skill import AuthSkill
from src.models.user import User
from sqlmodel import Session, select
from src.db.database import get_session
from uuid import UUID

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current authenticated user based on JWT token.

    Args:
        credentials: The authorization credentials from the request
        session: Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    # Verify the token
    payload = AuthSkill.verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert user_id string to UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def verify_user_owns_resource(user_id_from_token: str, user_id_from_path: str) -> bool:
    """
    Verify that the user ID in the JWT token matches the user ID in the path.

    Args:
        user_id_from_token: User ID extracted from JWT token
        user_id_from_path: User ID from the request path

    Returns:
        bool: True if user IDs match, False otherwise
    """
    try:
        token_uuid = UUID(user_id_from_token)
        path_uuid = UUID(user_id_from_path)
        return token_uuid == path_uuid
    except ValueError:
        return False

def require_user_match(token_user_id: str, path_user_id: str):
    """
    Decorator-like function to require that token user ID matches path user ID.

    Args:
        token_user_id: User ID from the JWT token
        path_user_id: User ID from the request path

    Raises:
        HTTPException: If user IDs don't match
    """
    # Convert both user IDs to UUID for proper comparison
    try:
        token_uuid = UUID(token_user_id)
        path_uuid = UUID(path_user_id)
        if token_uuid != path_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )