"""
Authentication skill module for handling user authentication operations.

This module centralizes all authentication-related logic including
password hashing, user creation, and user verification.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlmodel import Session, select
from src.models.user import User
from src.db.database import get_session
from pydantic import BaseModel
import os

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str

class AuthSkill:
    """
    Authentication skill class for handling authentication operations.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate a hash for the given password."""
        # Validate password length to prevent bcrypt errors (bcrypt max 72 bytes)
        # Note: bcrypt allows exactly 72 bytes, so we check for greater than 72
        if len(password.encode('utf-8')) > 72:
            raise ValueError("Password cannot be longer than 72 bytes")

        return pwd_context.hash(password)

    @staticmethod
    def create_user(name: str, email: str, password: str, session: Session) -> Optional[User]:
        """Create a new user with hashed password."""
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == email)).first()
        if existing_user:
            return None  # User already exists

        # Hash the password - this will raise ValueError if password is too long
        hashed_password = AuthSkill.get_password_hash(password)

        # Create the user
        user = User(name=name, email=email, password_hash=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def authenticate_user(email: str, password: str, session: Session) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = session.exec(select(User).where(User.email == email)).first()
        if not user or not AuthSkill.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str) -> Optional[dict]:
        """Verify a JWT access token and return the payload."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def get_current_user_id(token: str) -> Optional[str]:
        """Extract user ID from JWT token."""
        payload = AuthSkill.verify_access_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                return user_id
        return None

    @staticmethod
    def decode_token_payload(token: str) -> Optional[dict]:
        """Decode the token payload without validation (use carefully)."""
        try:
            # This method decodes without validating signature - use only for inspection
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
            return payload
        except JWTError:
            return None