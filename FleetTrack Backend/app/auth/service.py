import hashlib

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import repository
from .schemas import AuthenticatedUser
from .security import verify_legacy_password


ACTIVE_USER_STATUS = 1


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )


def authenticate_user(db: Session, username: str, password: str) -> AuthenticatedUser:
    normalized_username = username.strip()
    row = repository.get_user_by_username(db, normalized_username)

    # Always perform digest work so a missing username is not an immediate fast path.
    if row is None:
        hashlib.md5(password.encode("utf-8"), usedforsecurity=False).digest()
        raise _invalid_credentials()

    if int(row["Status"]) != ACTIVE_USER_STATUS:
        raise _invalid_credentials()
    if not verify_legacy_password(password, row["Password"]):
        raise _invalid_credentials()

    return AuthenticatedUser(
        userId=int(row["UserID"]),
        userName=row["UserName"],
        displayName=row["DisplayName"],
    )
