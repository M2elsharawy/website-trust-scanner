import socket

from app.scanners.result import DNSCheckResult


async def check_dns(domain: str) -> DNSCheckResult:
    """Verify the domain resolves. No DNS records are stored or returned."""
    try:
        socket.getaddrinfo(domain, None)
        return DNSCheckResult(resolves=True)
    except socket.gaierror:
        return DNSCheckResult(resolves=False, error="dns_resolution_failed")
    except Exception:
        return DNSCheckResult(resolves=False, error="dns_error")
