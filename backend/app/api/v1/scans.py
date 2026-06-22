from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limiter import GUEST_SCAN_LIMIT, limiter
from app.core.safe_scan_runner import run_public_trust_scan
from app.db.session import get_db
from app.schemas.scan import PublicScanRequest, TrustReport

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
    return await run_public_trust_scan(
        raw_url=body.url,
        actor_ip=actor_ip,
        db=db,
    )
