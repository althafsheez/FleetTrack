from fastapi import Cookie, HTTPException, status

from .schemas import AuthenticatedUser
from .security import InvalidSessionToken, SESSION_COOKIE_NAME, decode_session_token


def get_current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> AuthenticatedUser:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_session_token(session_token)
    except (InvalidSessionToken, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        ) from None
    return AuthenticatedUser(
        userId=int(payload["sub"]),
        userName=payload["username"],
        displayName=payload["displayName"],
    )
