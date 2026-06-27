"""
Safe Scan Runner — single enforcement point for all scan types.

Mandatory security order (must not be reordered):
  1.  Normalize input without DNS
  2.  Do Not Scan check          — before any network call
  3.  URL validation / SSRF      — DNS resolution + IP-range check
  4.  Extract validated hostname  — guard if empty
  4b. Second Do Not Scan check   — only if hostname changed after DNS
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
from app.scanners.result import ScanData
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


async def run_owner_trust_scan(
    *,
    domain: str,
    actor_id: str,
    actor_role: str,
    site_id: str,
    db: AsyncSession,
) -> dict:
    """
    Execute an Owner Trust scan with the same mandatory security order as
    run_public_trust_scan.

    `domain` is the verified site domain from the DB — no raw URL parsing.
    Returns the raw report dict. The caller persists ScanResult and writes
    the completed audit after the DB flush.

    Raises AppError subclasses on security violations.
    """
    clean_domain = domain.strip().lower()

    # ── Step 2: Do Not Scan — before any DNS resolution ──────────────────────
    dns_row = await db.execute(
        select(DoNotScan).where(func.lower(DoNotScan.domain) == clean_domain)
    )
    if dns_row.scalar_one_or_none() is not None:
        await log_event(
            db,
            action="scan.owner.blocked_do_not_scan",
            outcome="blocked",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="site",
            resource_id=site_id,
            details={"reason": "do_not_scan"},
        )
        raise DomainBlockedError()

    # ── Step 3: URL validation / SSRF (DNS resolution happens here) ───────────
    clean_url = validate_url(f"https://{clean_domain}")

    # ── Step 4: Extract validated hostname — guard if empty ───────────────────
    validated_hostname = urlparse(clean_url).hostname or ""
    if not validated_hostname:
        raise URLValidationError(
            message="validate_url returned URL with no extractable hostname"
        )

    # ── Step 4b: Second Do Not Scan — only if hostname changed after DNS ───────
    if validated_hostname != clean_domain:
        dns_row2 = await db.execute(
            select(DoNotScan).where(
                func.lower(DoNotScan.domain) == validated_hostname.lower()
            )
        )
        if dns_row2.scalar_one_or_none() is not None:
            await log_event(
                db,
                action="scan.owner.blocked_do_not_scan",
                outcome="blocked",
                actor_id=actor_id,
                actor_role=actor_role,
                resource_type="domain",
                resource_id=validated_hostname,
                details={"reason": "do_not_scan"},
            )
            raise DomainBlockedError()

    # ── Step 5: Scan policy check ─────────────────────────────────────────────
    check_scan_allowed(
        domain=clean_domain,
        scan_type=ScanType.PUBLIC_TRUST,
        is_on_do_not_scan_list=False,
    )

    # ── Steps 6–8: Run passive scanners, return report for caller to persist ──
    try:
        scan_data = await run_public_scan(validated_hostname)
        # compute_trust_report receives site.domain (not validated_hostname)
        # so the displayed domain matches what the owner registered.
        report = compute_trust_report(domain, scan_data)
    except Exception:
        await log_event(
            db,
            action="scan.owner.failed",
            outcome="error",
            actor_id=actor_id,
            actor_role=actor_role,
            resource_type="site",
            resource_id=site_id,
        )
        raise

    return report


async def run_lead_audit_scan(
    *,
    domain: str,
    lead_id: str,
    actor_ip: str | None,
    db: AsyncSession,
) -> ScanData:
    """
    Execute a surface-level Lead Audit scan with the same mandatory security
    order as run_owner_trust_scan.

    `domain` is the pre-validated domain from the leads DB record.
    Returns raw ScanData. The caller computes lead_score, generates outreach,
    and writes the completed audit log.

    Raises AppError subclasses on security violations.
    """
    clean_domain = domain.strip().lower()

    # ── Step 2: Do Not Scan — before any DNS resolution ──────────────────────
    dns_row = await db.execute(
        select(DoNotScan).where(func.lower(DoNotScan.domain) == clean_domain)
    )
    if dns_row.scalar_one_or_none() is not None:
        await log_event(
            db,
            action="scan.lead_audit.blocked_do_not_scan",
            outcome="blocked",
            actor_ip=actor_ip,
            resource_type="lead",
            resource_id=lead_id,
            details={"reason": "do_not_scan"},
        )
        raise DomainBlockedError()

    # ── Step 3: URL validation / SSRF (DNS resolution happens here) ───────────
    clean_url = validate_url(f"https://{clean_domain}")

    # ── Step 4: Extract validated hostname — guard if empty ───────────────────
    validated_hostname = urlparse(clean_url).hostname or ""
    if not validated_hostname:
        raise URLValidationError(
            message="validate_url returned URL with no extractable hostname"
        )

    # ── Step 4b: Second Do Not Scan — only if hostname changed after DNS ───────
    if validated_hostname != clean_domain:
        dns_row2 = await db.execute(
            select(DoNotScan).where(
                func.lower(DoNotScan.domain) == validated_hostname.lower()
            )
        )
        if dns_row2.scalar_one_or_none() is not None:
            await log_event(
                db,
                action="scan.lead_audit.blocked_do_not_scan",
                outcome="blocked",
                actor_ip=actor_ip,
                resource_type="lead",
                resource_id=lead_id,
                details={"reason": "do_not_scan"},
            )
            raise DomainBlockedError()

    # ── Step 5: Scan policy check ─────────────────────────────────────────────
    check_scan_allowed(
        domain=clean_domain,
        scan_type=ScanType.PUBLIC_TRUST,
        is_on_do_not_scan_list=False,
    )

    # ── Steps 6–8: Run passive scanners, return ScanData for caller to process ─
    try:
        scan_data = await run_public_scan(validated_hostname)
    except Exception:
        await log_event(
            db,
            action="scan.lead_audit.failed",
            outcome="error",
            actor_ip=actor_ip,
            resource_type="lead",
            resource_id=lead_id,
        )
        raise

    return scan_data
