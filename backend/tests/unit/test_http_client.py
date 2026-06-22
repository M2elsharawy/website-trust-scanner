"""
Tests for the Safe HTTP client factory (app/core/http_client.py).

Coverage:
- _redirect_hook calls validate_redirect_url on every hop
- _redirect_hook propagates exceptions from validate_redirect_url
- make_safe_client wires the hook when follow_redirects=True
- make_safe_client omits the hook when follow_redirects=False
- make_safe_client sets expected timeout, User-Agent, and max_redirects
- https_checker and headers_checker call make_safe_client (not httpx directly)
- no scanner file instantiates httpx.AsyncClient directly
"""

import re
from pathlib import Path

import httpx
import pytest

from app.core.exceptions import SSRFBlockedError
from app.core.http_client import _redirect_hook, make_safe_client


# ── _redirect_hook ────────────────────────────────────────────────────────────

class TestRedirectHook:
    def test_calls_validate_redirect_url(self, monkeypatch):
        validated: list[str] = []
        monkeypatch.setattr("app.core.http_client.validate_redirect_url", lambda url: validated.append(url))

        _redirect_hook(httpx.Request("GET", "https://safe.example.com/page"))

        assert validated == ["https://safe.example.com/page"]

    def test_propagates_ssrf_error(self, monkeypatch):
        def raise_ssrf(url: str) -> None:
            raise SSRFBlockedError()

        monkeypatch.setattr("app.core.http_client.validate_redirect_url", raise_ssrf)

        with pytest.raises(SSRFBlockedError):
            _redirect_hook(httpx.Request("GET", "http://169.254.169.254/"))


# ── make_safe_client ──────────────────────────────────────────────────────────

class TestMakeSafeClient:
    def test_follow_redirects_true_includes_hook(self):
        client = make_safe_client(follow_redirects=True)
        assert _redirect_hook in client.event_hooks.get("request", [])

    def test_follow_redirects_false_omits_hook(self):
        client = make_safe_client(follow_redirects=False)
        assert _redirect_hook not in client.event_hooks.get("request", [])

    def test_timeout_values(self):
        client = make_safe_client()
        assert client.timeout.read == 8.0
        assert client.timeout.connect == 5.0

    def test_user_agent_set(self):
        client = make_safe_client()
        assert "TrustScanner" in client.headers.get("user-agent", "")

    def test_max_redirects(self):
        client = make_safe_client(follow_redirects=True)
        assert client.max_redirects == 5


# ── Checker integration: factory is called ───────────────────────────────────

class _MockResponse:
    headers: dict = {}
    is_redirect: bool = False


class _MockClient:
    """Minimal async context manager that returns a blank MockResponse."""

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, url: str) -> _MockResponse:
        return _MockResponse()


async def test_https_checker_calls_make_safe_client(monkeypatch):
    from app.scanners import https_checker

    calls: list[dict] = []

    def mock_factory(**kwargs: object) -> _MockClient:
        calls.append(kwargs)
        return _MockClient()

    monkeypatch.setattr(https_checker, "make_safe_client", mock_factory)
    await https_checker.check_https("example.com")

    assert len(calls) >= 1, "make_safe_client was never called by check_https"


async def test_headers_checker_calls_make_safe_client(monkeypatch):
    from app.scanners import headers_checker

    calls: list[dict] = []

    def mock_factory(**kwargs: object) -> _MockClient:
        calls.append(kwargs)
        return _MockClient()

    monkeypatch.setattr(headers_checker, "make_safe_client", mock_factory)
    await headers_checker.check_headers("example.com")

    assert len(calls) >= 1, "make_safe_client was never called by check_headers"


# ── Static analysis: no direct httpx.AsyncClient in scanner files ─────────────

def test_no_direct_httpx_asyncclient_in_scanners():
    """
    Scanner modules must use make_safe_client(), not httpx.AsyncClient() directly.
    Only app/core/http_client.py is allowed to instantiate AsyncClient.

    Catches both forms:
      httpx.AsyncClient(...)
      from httpx import AsyncClient  (alias that could then be called directly)
    """
    scanner_dir = Path(__file__).resolve().parent.parent.parent / "app" / "scanners"
    # Direct instantiation via module attribute
    direct = re.compile(r"httpx\.AsyncClient\s*\(")
    # Import alias — importing AsyncClient by name enables bypassing the factory
    alias = re.compile(r"from\s+httpx\s+import\b[^\n]*\bAsyncClient\b")

    violations = [
        f.name
        for f in scanner_dir.rglob("*.py")
        if direct.search(f.read_text()) or alias.search(f.read_text())
    ]

    assert not violations, (
        f"httpx.AsyncClient used directly in scanner files "
        f"(use make_safe_client instead): {violations}"
    )
