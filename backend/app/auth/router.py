from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.schemas.auth import Token, UserLogin, UserCreate, User
from backend.app.crud.user import create_user, authenticate_user
from backend.app.services.user_service import get_user_by_email
from backend.app.utils.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.app.database import get_db

auth_router = APIRouter(tags=["AUTHENTICATION"], prefix="/auth")

@auth_router.post("/signup", response_model=User)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"} 