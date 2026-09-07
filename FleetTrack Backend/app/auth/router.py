from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.session import get_db

from .dependencies import get_current_user
from .schemas import AuthenticatedUser, LoginRequest, LoginResponse
from .security import (
    SESSION_COOKIE_NAME,
    cookie_secure,
    create_session_token,
    session_ttl_seconds,
)
from .service import authenticate_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(user.model_dump()),
        max_age=session_ttl_seconds(),
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
        path="/",
    )
    return LoginResponse(user=user)


@router.get("/me", response_model=AuthenticatedUser)
def me(current_user: AuthenticatedUser = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=204)
def logout():
    response = Response(status_code=204)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
        path="/",
    )
    return response
