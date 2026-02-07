from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from ..database import get_session
from ..auth import SECRET_KEY, ALGORITHM, create_access_token, get_current_user
from ..models import User
from typing import Optional
import bcrypt
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    access_token: str
    token_type: str = "bearer"

@router.post("/signup", response_model=UserResponse)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user account.
    """
    # Check if user already exists
    from sqlmodel import select
    existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = bcrypt.hashpw(user_create.password.encode('utf-8'), bcrypt.gensalt())

    # Create user
    user = User(
        email=user_create.email,
        name=user_create.name,
        password_hash=hashed_password.decode('utf-8')
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "user_id": str(user.user_id)},
        expires_delta=access_token_expires
    )

    return UserResponse(
        user_id=str(user.user_id),
        email=user.email,
        name=user.name,
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/login", response_model=UserResponse)
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticate user and return access token.
    """
    # Find user by email
    from sqlmodel import select
    user = session.exec(select(User).where(User.email == user_login.email)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify password
    if not bcrypt.checkpw(user_login.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "user_id": str(user.user_id)},
        expires_delta=access_token_expires
    )

    return UserResponse(
        user_id=str(user.user_id),
        email=user.email,
        name=user.name,
        access_token=access_token,
        token_type="bearer"
    )