from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user,
    set_auth_cookie,
    clear_auth_cookie,
)
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
):
    """Register a new user."""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create token and set cookie
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    set_auth_cookie(response, token)
    
    return user


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    """Login and get access token."""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    set_auth_cookie(response, token)
    
    return Token(access_token=token)


@router.post("/logout")
def logout(response: Response):
    """Logout and clear auth cookie."""
    clear_auth_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user

