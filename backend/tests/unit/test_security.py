"""
Unit tests for core security utilities (password hashing, JWT, refresh tokens).
"""


import pytest
from jose import JWTError

from app.core.security import (
    ALGORITHM,
    create_access_token,
    create_refresh_token_str,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


# ── Password hashing ──────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_is_not_plain_text(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"

    def test_verify_correct_password(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_same_password_produces_different_hashes(self):
        # bcrypt uses a random salt
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_hash_starts_with_bcrypt_prefix(self):
        hashed = hash_password("test")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


# ── Access token ──────────────────────────────────────────────────────────────

class TestAccessToken:
    def test_create_and_decode(self):
        token = create_access_token("user-123", "free_user")
        payload = decode_access_token(token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "free_user"

    def test_token_type_is_access(self):
        token = create_access_token("u", "admin")
        payload = decode_access_token(token)
        assert payload["type"] == "access"

    def test_tampered_token_raises(self):
        token = create_access_token("u", "free_user")
        # Replace the signature part entirely with garbage
        header, payload, _ = token.split(".")
        tampered = f"{header}.{payload}.invalidsignatureXXXXXXXXXXXXXXXX"
        with pytest.raises(JWTError):
            decode_access_token(tampered)

    def test_wrong_secret_raises(self, monkeypatch):
        from app.core import security as sec_mod
        token = create_access_token("u", "free_user")
        monkeypatch.setattr(
            "app.core.security.settings",
            type("S", (), {"secret_key": "different-secret"})(),
        )
        with pytest.raises(JWTError):
            sec_mod.decode_access_token(token)

    def test_wrong_token_type_raises(self):
        from jose import jwt
        from app.core.config import settings

        payload = {"sub": "u", "role": "free_user", "type": "refresh"}
        token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
        with pytest.raises(JWTError):
            decode_access_token(token)


# ── Refresh token ─────────────────────────────────────────────────────────────

class TestRefreshToken:
    def test_raw_token_is_url_safe_string(self):
        raw = create_refresh_token_str()
        assert isinstance(raw, str)
        assert len(raw) > 32

    def test_two_tokens_are_unique(self):
        assert create_refresh_token_str() != create_refresh_token_str()

    def test_hash_is_64_hex_chars(self):
        raw = create_refresh_token_str()
        digest = hash_refresh_token(raw)
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_same_raw_produces_same_hash(self):
        raw = create_refresh_token_str()
        assert hash_refresh_token(raw) == hash_refresh_token(raw)

    def test_different_raws_produce_different_hashes(self):
        r1 = create_refresh_token_str()
        r2 = create_refresh_token_str()
        assert hash_refresh_token(r1) != hash_refresh_token(r2)

    def test_raw_token_never_equals_hash(self):
        raw = create_refresh_token_str()
        assert raw != hash_refresh_token(raw)
