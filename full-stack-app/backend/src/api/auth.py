from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from src.db.database import get_session
from src.skills.auth_skill import AuthSkill
from src.models.user import User
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = AuthSkill.verify_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

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

    Args:
        user_create: User creation data (name, email, password)
        session: Database session

    Returns:
        UserResponse: User details and JWT access token

    Raises:
        HTTPException: If email already exists or password is too long
    """
    try:
        # Attempt to create user
        user = AuthSkill.create_user(
            name=user_create.name,
            email=user_create.email,
            password=user_create.password,
            session=session
        )
    except ValueError as e:
        # Handle password validation errors (e.g., too long for bcrypt)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Create JWT access token
    token_data = {"sub": str(user.id)}
    access_token = AuthSkill.create_access_token(data=token_data)

    return UserResponse(
        user_id=str(user.id),
        email=user.email,
        name=user.name,
        access_token=access_token
    )


@router.post("/login", response_model=UserResponse)
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticate user and return JWT token.

    Args:
        user_login: User login data (email, password)
        session: Database session

    Returns:
        UserResponse: User details and JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user = AuthSkill.authenticate_user(
        email=user_login.email,
        password=user_login.password,
        session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create JWT access token
    token_data = {"sub": str(user.id)}
    access_token = AuthSkill.create_access_token(data=token_data)

    return UserResponse(
        user_id=str(user.id),
        email=user.email,
        name=user.name,
        access_token=access_token
    )