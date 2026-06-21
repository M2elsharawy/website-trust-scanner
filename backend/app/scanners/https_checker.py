"""
HTTPS and HSTS checker.

Checks:
1. Whether the site is accessible over HTTPS.
2. Whether HTTP redirects to HTTPS (first hop only, no redirect following).
3. Whether HSTS header is present on the HTTPS response.

Header VALUES are never stored or logged — only presence is recorded.
"""

import httpx

from app.core.url_validator import validate_redirect_url
from app.scanners.result import HTTPSCheckResult

_TIMEOUT = httpx.Timeout(8.0, connect=5.0)
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TrustScanner/1.0; +https://trustscanner.app)"}


def _on_redirect(request: httpx.Request) -> None:
    """Validate each redirect destination before following."""
    validate_redirect_url(str(request.url))


async def check_https(domain: str) -> HTTPSCheckResult:
    result = HTTPSCheckResult()

    # 1. Check HTTPS availability and HSTS
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
            result.available = True
            result.hsts_present = "strict-transport-security" in response.headers
    except httpx.SSLError:
        result.available = False
    except Exception:
        result.available = False

    # 2. Check if HTTP redirects to HTTPS (single hop, no following)
    try:
        async with httpx.AsyncClient(
            verify=False,
            timeout=_TIMEOUT,
            follow_redirects=False,
            headers=_HEADERS,
        ) as client:
            response = await client.get(f"http://{domain}/")
            if response.is_redirect:
                location = response.headers.get("location", "")
                result.redirects_from_http = location.lower().startswith("https://")
    except Exception:
        pass  # HTTP not available is fine

    return result
