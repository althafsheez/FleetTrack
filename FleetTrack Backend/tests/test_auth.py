"""Authentication tests using isolated SQLite and synthetic credentials."""
import hashlib
import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException, Response
from sqlalchemy import BigInteger, Column, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth import service
from app.auth.dependencies import get_current_user
from app.auth.router import login, logout
from app.auth.schemas import LoginRequest
from app.auth.security import (
    InvalidSessionToken,
    create_session_token,
    decode_session_token,
    verify_legacy_password,
)
from app.generated_models.models import t_VT_ApplicationUsers


def _legacy_digest(password: str) -> str:
    digest = hashlib.md5(password.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
    return "-".join(digest[index:index + 2] for index in range(0, len(digest), 2))


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool)
        metadata = MetaData()
        source = t_VT_ApplicationUsers
        self.users = Table(
            source.name,
            metadata,
            Column("UserID", BigInteger, primary_key=True),
            Column("UserName", String(256), nullable=False),
            Column("Password", String(100), nullable=False),
            Column("DisplayName", String(250), nullable=False),
            Column("Status", Integer, nullable=False),
        )
        metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.execute(self.users.insert(), [
            {
                "UserID": 12,
                "UserName": "portal.user",
                "Password": _legacy_digest("correct-password"),
                "DisplayName": "Portal User",
                "Status": 1,
            },
            {
                "UserID": 13,
                "UserName": "inactive.user",
                "Password": _legacy_digest("correct-password"),
                "DisplayName": "Inactive User",
                "Status": 2,
            },
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_authenticates_active_portal_user(self):
        user = service.authenticate_user(self.db, " portal.user ", "correct-password")
        self.assertEqual(user.userId, 12)
        self.assertEqual(user.displayName, "Portal User")

    def test_rejects_wrong_password_unknown_and_inactive_user(self):
        for username, password in [
            ("portal.user", "wrong"),
            ("missing.user", "wrong"),
            ("inactive.user", "correct-password"),
        ]:
            with self.subTest(username=username), self.assertRaises(HTTPException) as error:
                service.authenticate_user(self.db, username, password)
            self.assertEqual(error.exception.status_code, 401)
            self.assertEqual(error.exception.detail, "Invalid username or password")

    def test_legacy_password_format_is_strict(self):
        stored = _legacy_digest("correct-password")
        self.assertTrue(verify_legacy_password("correct-password", stored))
        self.assertFalse(verify_legacy_password("wrong", stored))
        self.assertFalse(verify_legacy_password("correct-password", "plaintext"))

    def test_signed_session_round_trip_expiry_and_tampering(self):
        user = {"userId": 12, "userName": "portal.user", "displayName": "Portal User"}
        environment = {
            "AUTH_SECRET": "test-secret-that-is-longer-than-thirty-two-characters",
            "AUTH_SESSION_TTL_SECONDS": "3600",
        }
        with patch.dict(os.environ, environment, clear=False):
            token = create_session_token(user, now=1_000)
            payload = decode_session_token(token, now=1_001)
            self.assertEqual(payload["sub"], 12)
            with self.assertRaises(InvalidSessionToken):
                decode_session_token(token, now=4_600)
            with self.assertRaises(InvalidSessionToken):
                decode_session_token(token + "changed", now=1_001)
            with self.assertRaises(InvalidSessionToken):
                decode_session_token("not-valid-base64.signature", now=1_001)

    def test_login_cookie_current_user_and_logout(self):
        environment = {
            "AUTH_SECRET": "test-secret-that-is-longer-than-thirty-two-characters",
            "AUTH_SESSION_TTL_SECONDS": "3600",
            "AUTH_COOKIE_SECURE": "false",
        }
        with patch.dict(os.environ, environment, clear=False):
            response = Response()
            body = login(
                LoginRequest(username="portal.user", password="correct-password"),
                response,
                self.db,
            )
            self.assertEqual(body.user.userId, 12)
            cookie_header = response.headers["set-cookie"]
            self.assertIn("fleettrack_session=", cookie_header)
            self.assertIn("HttpOnly", cookie_header)
            self.assertIn("SameSite=lax", cookie_header)
            token = cookie_header.split("fleettrack_session=", 1)[1].split(";", 1)[0]
            self.assertEqual(get_current_user(token).userName, "portal.user")

            logout_response = logout()
            self.assertEqual(logout_response.status_code, 204)
            self.assertIn("fleettrack_session=", logout_response.headers["set-cookie"])


if __name__ == "__main__":
    unittest.main()
