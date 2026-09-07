import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import time
from typing import Any


SESSION_COOKIE_NAME = "fleettrack_session"
DEFAULT_SESSION_TTL_SECONDS = 8 * 60 * 60
_LEGACY_MD5_PATTERN = re.compile(r"^(?:[0-9A-Fa-f]{2}-){15}[0-9A-Fa-f]{2}$")


class InvalidSessionToken(ValueError):
    pass


def _encode_base64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode_base64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(value + padding, altchars=b"-_", validate=True)


def _session_secret() -> bytes:
    secret = os.getenv("AUTH_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError("AUTH_SECRET must be configured with at least 32 characters")
    return secret.encode("utf-8")


def session_ttl_seconds() -> int:
    value = int(os.getenv("AUTH_SESSION_TTL_SECONDS", str(DEFAULT_SESSION_TTL_SECONDS)))
    if value < 60:
        raise RuntimeError("AUTH_SESSION_TTL_SECONDS must be at least 60")
    return value


def cookie_secure() -> bool:
    return os.getenv("AUTH_COOKIE_SECURE", "false").strip().lower() in {"1", "true", "yes", "on"}


def verify_legacy_password(password: str, stored_password: str) -> bool:
    """Verify the portal's legacy uppercase, hyphenated 16-byte MD5 digest."""
    if not _LEGACY_MD5_PATTERN.fullmatch(stored_password or ""):
        return False
    digest = hashlib.md5(password.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
    candidate = "-".join(digest[index:index + 2] for index in range(0, len(digest), 2))
    return hmac.compare_digest(candidate, stored_password.upper())


def create_session_token(user: dict[str, Any], now: int | None = None) -> str:
    issued_at = int(time.time() if now is None else now)
    payload = {
        "v": 1,
        "sub": int(user["userId"]),
        "username": user["userName"],
        "displayName": user["displayName"],
        "iat": issued_at,
        "exp": issued_at + session_ttl_seconds(),
    }
    encoded_payload = _encode_base64(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = _encode_base64(
        hmac.new(_session_secret(), encoded_payload.encode("ascii"), hashlib.sha256).digest()
    )
    return f"{encoded_payload}.{signature}"


def decode_session_token(token: str, now: int | None = None) -> dict[str, Any]:
    try:
        encoded_payload, supplied_signature = token.split(".", 1)
        expected_signature = _encode_base64(
            hmac.new(_session_secret(), encoded_payload.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise InvalidSessionToken("Invalid session signature")
        payload = json.loads(_decode_base64(encoded_payload))
        current_time = int(time.time() if now is None else now)
        if payload.get("v") != 1 or int(payload["exp"]) <= current_time:
            raise InvalidSessionToken("Session expired")
        if int(payload["sub"]) <= 0:
            raise InvalidSessionToken("Invalid session subject")
        return payload
    except (binascii.Error, KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        if isinstance(exc, InvalidSessionToken):
            raise
        raise InvalidSessionToken("Invalid session token") from exc
