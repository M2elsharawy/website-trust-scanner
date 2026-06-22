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

from app.core.http_client import make_safe_client
from app.scanners.result import HeadersCheckResult

_CHECKED_HEADERS = {
    "content-security-policy": "csp_present",
    "x-frame-options": "x_frame_options_present",
    "x-content-type-options": "x_content_type_options_present",
    "referrer-policy": "referrer_policy_present",
    "permissions-policy": "permissions_policy_present",
}


async def check_headers(domain: str) -> HeadersCheckResult:
    result = HeadersCheckResult()
    try:
        async with make_safe_client(follow_redirects=True, verify=True) as client:
            response = await client.get(f"https://{domain}/")
            for header_name, attr in _CHECKED_HEADERS.items():
                if header_name in response.headers:
                    setattr(result, attr, True)
    except Exception:
        result.error = "headers_fetch_failed"

    return result
