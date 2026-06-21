"""
Scan runner — orchestrates all checkers concurrently.
"""

import asyncio

from app.scanners.dns_checker import check_dns
from app.scanners.headers_checker import check_headers
from app.scanners.https_checker import check_https
from app.scanners.reputation_checker import check_reputation
from app.scanners.result import ScanData
from app.scanners.ssl_checker import check_ssl


async def run_public_scan(domain: str) -> ScanData:
    """
    Run all public-trust checkers concurrently.

    Each checker is independent and catches its own exceptions internally,
    so a failure in one does not block the others.
    """
    dns_result, https_result, ssl_result, headers_result, reputation_result = (
        await asyncio.gather(
            check_dns(domain),
            check_https(domain),
            check_ssl(domain),
            check_headers(domain),
            check_reputation(domain),
        )
    )

    return ScanData(
        domain=domain,
        dns=dns_result,
        https=https_result,
        ssl=ssl_result,
        headers=headers_result,
        reputation=reputation_result,
    )
