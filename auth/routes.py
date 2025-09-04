from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from schemas.auth_schemas import Token, User
from auth.jwt_handler import authenticate_user, create_access_token, get_current_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token, summary="Login and get JWT (valid 20 minutes)")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form.username, form.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=form.username, expires_delta=access_token_expires)
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
    )


@router.get("/me", response_model=User, summary="Validate token and get current user")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
