"""
SSL certificate checker.

Only extracts the certificate expiry date. All other cert fields
(subject, issuer, serial, SANs) are intentionally ignored and never stored.
"""

import asyncio
import socket
import ssl
from datetime import datetime, timezone
from functools import partial

from app.scanners.result import SSLCheckResult

_EXPIRY_WARNING_DAYS = 30
_CONNECT_TIMEOUT = 5.0


def _sync_check_ssl(hostname: str) -> SSLCheckResult:
    """
    Synchronous SSL check run in a thread executor.

    Returns (valid, expiry_warning). No cert details are stored.
    """
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=_CONNECT_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after_str = cert.get("notAfter", "")
                if not_after_str:
                    not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                    not_after = not_after.replace(tzinfo=timezone.utc)
                    days_left = (not_after - datetime.now(timezone.utc)).days
                    return SSLCheckResult(valid=True, expiry_warning=days_left < _EXPIRY_WARNING_DAYS)
                return SSLCheckResult(valid=True)
    except ssl.SSLCertVerificationError:
        return SSLCheckResult(valid=False, error="ssl_cert_invalid")
    except ssl.SSLError:
        return SSLCheckResult(valid=False, error="ssl_error")
    except (socket.timeout, ConnectionRefusedError, OSError):
        return SSLCheckResult(valid=False, error="ssl_connect_failed")
    except Exception:
        return SSLCheckResult(valid=False, error="ssl_error")


async def check_ssl(hostname: str) -> SSLCheckResult:
    """Async wrapper — runs the blocking SSL handshake in a thread executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_sync_check_ssl, hostname))
