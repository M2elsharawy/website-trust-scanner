"""
HTTPS and HSTS checker.

Checks:
1. Whether the site is accessible over HTTPS.
2. Whether HTTP redirects to HTTPS (first hop only, no redirect following).
3. Whether HSTS header is present on the HTTPS response.

Header VALUES are never stored or logged — only presence is recorded.
"""

from app.core.http_client import make_safe_client
from app.scanners.result import HTTPSCheckResult


async def check_https(domain: str) -> HTTPSCheckResult:
    result = HTTPSCheckResult()

    # 1. Check HTTPS availability and HSTS; validate every redirect hop.
    try:
        async with make_safe_client(follow_redirects=True, verify=True) as client:
            response = await client.get(f"https://{domain}/")
            result.available = True
            result.hsts_present = "strict-transport-security" in response.headers
    except Exception:
        result.available = False

    # 2. Check if HTTP redirects to HTTPS (single hop, no following).
    try:
        async with make_safe_client(follow_redirects=False, verify=False) as client:
            response = await client.get(f"http://{domain}/")
            if response.is_redirect:
                location = response.headers.get("location", "")
                result.redirects_from_http = location.lower().startswith("https://")
    except Exception:
        pass  # HTTP not available is fine

    return result
