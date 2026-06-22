"""
Safe Scan Runner — single enforcement point for Public Trust scans.

Mandatory security order (must not be reordered):
  1.  Normalize input without DNS
  2.  Do Not Scan check          — before any network call
  3.  URL validation / SSRF      — DNS resolution + IP-range check
  4.  Extract validated hostname  — guard if empty
  5.  Scan policy check
  6.  Rate limit / quota          — TODO: per-domain cap (IP-level handled by @limiter at API layer)
  7.  Audit log: scan requested
  8.  Run passive scanners
  9.  Audit log: completed or failed
  10. Return sanitized result only

Only passive checks run here. No port scan, no crawling, no exposed-file
enumeration. Header values and response bodies are never stored or returned.
"""

from urllib.parse import urlparse

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainBlockedError, URLValidationError
from app.core.scan_policy import ScanType, check_scan_allowed
from app.core.url_validator import validate_url
from app.models.do_not_scan import DoNotScan
from app.scanners.runner import run_public_scan
from app.scanners.trust_score import compute_trust_report
from app.schemas.scan import TrustReport
from app.services.audit_logger import log_event


async def run_public_trust_scan(
    *,
    raw_url: str,
    actor_ip: str | None,
    db: AsyncSession,
) -> TrustReport:
    """
    Execute a Public Trust scan with full security enforcement.

    Raises AppError subclasses on any security violation — callers should
    let these propagate to the FastAPI exception handlers unchanged.
    Never returns raw IPs, header values, or response bodies.
    """
    # ── Step 1: Normalize input without DNS ───────────────────────────────────
    url_str = raw_url.strip()
    # Add scheme for parsing only — no DNS lookup here
    parse_target = url_str if "://" in url_str else f"https://{url_str}"
    raw_domain = (urlparse(parse_target).hostname or "").lower()
    if not raw_domain:
        raise URLValidationError(message="Cannot extract domain from input")

    # ── Step 2: Do Not Scan check — before any DNS resolution ─────────────────
    dns_row = await db.execute(
        select(DoNotScan).where(func.lower(DoNotScan.domain) == raw_domain)
    )
    if dns_row.scalar_one_or_none() is not None:
        await log_event(
            db,
            action="scan.blocked_do_not_scan",
            outcome="blocked",
            actor_ip=actor_ip,
            resource_type="domain",
            resource_id=raw_domain,
        )
        raise DomainBlockedError()

    # ── Step 3: URL validation / SSRF (DNS resolution happens here) ───────────
    clean_url = validate_url(parse_target, allow_http=True)

    # ── Step 4: Extract validated hostname — guard if empty ───────────────────
    validated_hostname = urlparse(clean_url).hostname or ""
    if not validated_hostname:
        raise URLValidationError(
            message="validate_url returned URL with no extractable hostname"
        )

    # ── Step 4b: Second Do Not Scan check — only if hostname changed after DNS ─
    # validate_url does not rewrite hostnames, but defensive re-check catches
    # any future normalization (IDN, CNAME flattening) that produces a different
    # hostname than the one checked pre-DNS in Step 2.
    if validated_hostname != raw_domain:
        dns_row2 = await db.execute(
            select(DoNotScan).where(func.lower(DoNotScan.domain) == validated_hostname.lower())
        )
        if dns_row2.scalar_one_or_none() is not None:
            await log_event(
                db,
                action="scan.blocked_do_not_scan",
                outcome="blocked",
                actor_ip=actor_ip,
                resource_type="domain",
                resource_id=validated_hostname,
            )
            raise DomainBlockedError()

    # ── Step 5: Scan policy check ─────────────────────────────────────────────
    check_scan_allowed(
        domain=validated_hostname,
        scan_type=ScanType.PUBLIC_TRUST,
        is_on_do_not_scan_list=False,
    )

    # ── Step 6: Rate limit / quota ────────────────────────────────────────────
    # Per-IP rate limiting is handled by @limiter.limit at the API layer.
    # TODO: add per-domain cap (DOMAIN_SCAN_LIMIT) here in a dedicated PR.

    # ── Step 7: Audit log — scan requested ───────────────────────────────────
    await log_event(
        db,
        action="scan.public_trust.requested",
        outcome="pending",
        actor_ip=actor_ip,
        resource_type="domain",
        resource_id=validated_hostname,
    )

    # ── Steps 8–10: Run scanners, audit result, return sanitized report ────────
    try:
        scan_data = await run_public_scan(validated_hostname)
        report = compute_trust_report(validated_hostname, scan_data)

        # ── Step 9: Audit log — completed ────────────────────────────────────
        await log_event(
            db,
            action="scan.public_trust.completed",
            outcome="success",
            actor_ip=actor_ip,
            resource_type="domain",
            resource_id=validated_hostname,
            details={
                "trust_score": report["trust_score"],
                "trust_level": report["trust_level"],
            },
        )
    except Exception:
        # ── Step 9: Audit log — failed ────────────────────────────────────────
        await log_event(
            db,
            action="scan.public_trust.failed",
            outcome="error",
            actor_ip=actor_ip,
            resource_type="domain",
            resource_id=validated_hostname,
        )
        raise

    # ── Step 10: Return sanitized result only ─────────────────────────────────
    return TrustReport(**report)
