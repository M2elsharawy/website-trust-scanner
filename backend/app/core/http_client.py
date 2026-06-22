"""
Safe HTTP client factory — single source of truth for outbound HTTP in the scanner.

Every httpx.AsyncClient created here:
- enforces a consistent timeout and connection cap
- sends a fixed User-Agent
- validates every redirect destination through validate_redirect_url()
  so a redirect chain cannot escape to a private/SSRF-unsafe address

Only this module may instantiate httpx.AsyncClient directly.
All scanner code must call make_safe_client() so redirect validation
can never be skipped by an individual checker.
"""

import httpx

from app.core.url_validator import validate_redirect_url

_TIMEOUT = httpx.Timeout(8.0, connect=5.0)
_LIMITS = httpx.Limits(
    max_connections=10,
    max_keepalive_connections=5,
    keepalive_expiry=30.0,
)
_USER_AGENT = "Mozilla/5.0 (compatible; TrustScanner/1.0; +https://trustscanner.app)"
_MAX_REDIRECTS = 5


def _redirect_hook(request: httpx.Request) -> None:
    validate_redirect_url(str(request.url))


def make_safe_client(
    *,
    follow_redirects: bool = True,
    verify: bool = True,
) -> httpx.AsyncClient:
    """
    Return a configured httpx.AsyncClient for use as an async context manager.

    When follow_redirects=True every hop is validated by validate_redirect_url()
    before it is followed — same SSRF rules as validate_url().
    Response bodies and header values are never logged by this layer.
    """
    event_hooks: dict[str, list] = {}
    if follow_redirects:
        event_hooks = {"request": [_redirect_hook]}

    return httpx.AsyncClient(
        verify=verify,
        timeout=_TIMEOUT,
        limits=_LIMITS,
        follow_redirects=follow_redirects,
        max_redirects=_MAX_REDIRECTS,
        event_hooks=event_hooks,
        headers={"User-Agent": _USER_AGENT},
    )
