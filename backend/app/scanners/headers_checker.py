"""
Security headers checker.

Checks PRESENCE only — header values are never stored or returned.
Checked headers:
  - Content-Security-Policy
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
  - Permissions-Policy
"""

import httpx

from app.core.url_validator import validate_redirect_url
from app.scanners.result import HeadersCheckResult

_TIMEOUT = httpx.Timeout(8.0, connect=5.0)
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TrustScanner/1.0; +https://trustscanner.app)"}

_CHECKED_HEADERS = {
    "content-security-policy": "csp_present",
    "x-frame-options": "x_frame_options_present",
    "x-content-type-options": "x_content_type_options_present",
    "referrer-policy": "referrer_policy_present",
    "permissions-policy": "permissions_policy_present",
}


def _on_redirect(request: httpx.Request) -> None:
    validate_redirect_url(str(request.url))


async def check_headers(domain: str) -> HeadersCheckResult:
    result = HeadersCheckResult()
    try:
        async with httpx.AsyncClient(
            verify=True,
            timeout=_TIMEOUT,
            follow_redirects=True,
            max_redirects=5,
            event_hooks={"request": [lambda r: _on_redirect(r)]},
            headers=_HEADERS,
        ) as client:
            response = await client.get(f"https://{domain}/")
            for header_name, attr in _CHECKED_HEADERS.items():
                if header_name in response.headers:
                    setattr(result, attr, True)
    except Exception:
        result.error = "headers_fetch_failed"

    return result
