from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainBlockedError
from app.core.rate_limiter import GUEST_SCAN_LIMIT, limiter
from app.core.scan_policy import ScanType, check_scan_allowed
from app.core.url_validator import validate_url
from app.db.session import get_db
from app.models.do_not_scan import DoNotScan
from app.scanners.runner import run_public_scan
from app.scanners.trust_score import compute_trust_report
from app.schemas.scan import PublicScanRequest, TrustReport
from app.services.audit_logger import log_event

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/public", response_model=TrustReport, status_code=200)
@limiter.limit(GUEST_SCAN_LIMIT)
async def public_scan(
    request: Request,
    body: PublicScanRequest,
    db: AsyncSession = Depends(get_db),
) -> TrustReport:
    """
    Run a public trust check on any URL.

    Returns a trust score, level, check summary, and safe recommendations.
    No sensitive technical details (IPs, cert info, raw headers) are included.
    """
    actor_ip = request.client.host if request.client else None

    # 1. SSRF-safe URL validation (raises URLValidationError / SSRFBlockedError)
    clean_url = validate_url(body.url, allow_http=True)
    parsed = urlparse(clean_url)
    domain = parsed.hostname or ""

    # 2. Do Not Scan check
    dns_row = await db.execute(
        select(DoNotScan).where(func.lower(DoNotScan.domain) == domain.lower())
    )
    if dns_row.scalar_one_or_none() is not None:
        await log_event(
            db,
            action="scan.blocked_do_not_scan",
            outcome="blocked",
            actor_ip=actor_ip,
            resource_type="domain",
            resource_id=domain,
        )
        raise DomainBlockedError()

    # 3. Scan policy check
    check_scan_allowed(
        domain=domain,
        scan_type=ScanType.PUBLIC_TRUST,
        is_on_do_not_scan_list=False,
    )

    # 4. Run all checkers concurrently
    scan_data = await run_public_scan(domain)

    # 5. Compute safe trust report
    report_dict = compute_trust_report(domain, scan_data)

    # 6. Audit log (actor_ip stored in DB, never returned in response)
    await log_event(
        db,
        action="scan.public_trust.completed",
        outcome="success",
        actor_ip=actor_ip,
        resource_type="domain",
        resource_id=domain,
        details={
            "trust_score": report_dict["trust_score"],
            "trust_level": report_dict["trust_level"],
        },
    )

    return TrustReport(**report_dict)
