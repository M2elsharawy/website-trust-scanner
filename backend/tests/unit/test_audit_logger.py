"""
Unit tests for the audit logger service.
Tests focus on sanitization logic (no DB required for sanitization tests).
"""

from unittest.mock import AsyncMock, MagicMock

from app.services.audit_logger import _sanitize_details, log_event


# ── Sanitization ─────────────────────────────────────────────────────────────

class TestSanitizeDetails:
    def test_none_returns_none(self):
        assert _sanitize_details(None) is None

    def test_clean_dict_passes_through(self):
        data = {"domain": "example.com", "status": "queued"}
        assert _sanitize_details(data) == data

    def test_sensitive_key_is_redacted(self):
        data = {"password": "secret123", "email": "user@example.com"}
        result = _sanitize_details(data)
        assert result["password"] == "[REDACTED]"
        assert result["email"] == "user@example.com"

    def test_all_sensitive_keys_redacted(self):
        sensitive = {
            "password": "x",
            "hashed_password": "x",
            "secret": "x",
            "secret_key": "x",
            "api_key": "x",
            "access_token": "x",
            "refresh_token": "x",
            "token": "x",
            "authorization": "x",
            "cookie": "x",
            "private_key": "x",
            "credit_card": "x",
            "card_number": "x",
            "cvv": "x",
            "ssn": "x",
            "raw_html": "x",
            "file_content": "x",
            "file_contents": "x",
        }
        result = _sanitize_details(sensitive)
        for key in sensitive:
            assert result[key] == "[REDACTED]", f"Key '{key}' was not redacted"

    def test_nested_sensitive_key_redacted(self):
        data = {"request": {"token": "abc123", "url": "https://example.com"}}
        result = _sanitize_details(data)
        assert result["request"]["token"] == "[REDACTED]"
        assert result["request"]["url"] == "https://example.com"

    def test_list_of_dicts_sanitized(self):
        data = {"items": [{"token": "secret"}, {"name": "ok"}]}
        result = _sanitize_details(data)
        assert result["items"][0]["token"] == "[REDACTED]"
        assert result["items"][1]["name"] == "ok"

    def test_case_insensitive_key_matching(self):
        # Keys are lowercased before comparison
        data = {"PASSWORD": "secret", "Token": "abc"}
        result = _sanitize_details(data)
        assert result["PASSWORD"] == "[REDACTED]"
        assert result["Token"] == "[REDACTED]"

    def test_non_sensitive_list_values_preserved(self):
        data = {"tags": ["safe", "public", "ok"]}
        result = _sanitize_details(data)
        assert result["tags"] == ["safe", "public", "ok"]


# ── log_event (DB integration) ───────────────────────────────────────────────

class TestLogEvent:
    async def test_log_event_writes_to_db(self):
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        await log_event(
            mock_db,
            action="scan.requested",
            outcome="success",
            actor_id="user-uuid-123",
            actor_role="guest",
            actor_ip="1.2.3.4",
            resource_type="scan",
            resource_id="scan-uuid-456",
            details={"url": "https://example.com"},
        )

        mock_db.add.assert_called_once()
        entry = mock_db.add.call_args[0][0]
        assert entry.action == "scan.requested"
        assert entry.actor_ip == "1.2.3.4"
        assert entry.outcome == "success"

    async def test_log_event_never_raises_on_db_error(self):
        """Audit logging must not crash the caller's business logic."""
        mock_db = AsyncMock()
        mock_db.add = MagicMock(side_effect=Exception("DB down"))

        # Must not propagate the exception
        await log_event(mock_db, action="scan.requested")

    async def test_log_event_sanitizes_details(self):
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        await log_event(
            mock_db,
            action="auth.login",
            details={"email": "user@example.com", "password": "secret"},
        )

        entry = mock_db.add.call_args[0][0]
        assert entry.details["password"] == "[REDACTED]"
        assert entry.details["email"] == "user@example.com"

    async def test_actor_ip_stored_but_this_is_db_only(self):
        """Confirm actor_ip is passed to the model (API layer must not expose it)."""
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        await log_event(
            mock_db,
            action="scan.requested",
            actor_ip="203.0.113.5",
        )

        entry = mock_db.add.call_args[0][0]
        assert entry.actor_ip == "203.0.113.5"
