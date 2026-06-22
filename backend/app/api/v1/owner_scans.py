"""
Verified-owner scan endpoints.

Only sites with status=active (DNS-verified) can be scanned here.
Results are persisted in scan_results and linked to the site.
"""

import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.scan_result import ScanResult
from app.models.site import Site, SiteStatus
from app.models.user import User
from app.scanners.runner import run_public_scan
from app.scanners.trust_score import compute_trust_report
from app.schemas.scan_result import ScanResultDetail, ScanResultSummary
from app.services.audit_logger import log_event

router = APIRouter(prefix="/sites/{site_id}/scans", tags=["owner-scans"])

_MAX_HISTORY = 50


@router.post("", response_model=ScanResultDetail, status_code=201)
async def run_owner_scan(
    site_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanResultDetail:
    """Run a new scan for a verified site and persist the result."""
    site = await _get_active_site(db, site_id, current_user)

    scan_data = await run_public_scan(site.domain)
    report = compute_trust_report(site.domain, scan_data)

    result = ScanResult(
        site_id=site.id,
        domain=site.domain,
        trust_score=report["trust_score"],
        result_json=report,
    )
    db.add(result)
    await db.flush()

    await log_event(
        db,
        action="scan.owner.completed",
        actor_id=str(current_user.id),
        actor_role=current_user.role.value,
        resource_type="site",
        resource_id=str(site.id),
        details={"trust_score": report["trust_score"], "domain": site.domain},
    )

    return ScanResultDetail.model_validate(result)


@router.get("", response_model=list[ScanResultSummary])
async def list_scan_history(
    site_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScanResultSummary]:
    """Return up to 50 most recent scan summaries for the site."""
    site = await _get_active_site(db, site_id, current_user)

    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.site_id == site.id)
        .order_by(desc(ScanResult.scanned_at))
        .limit(_MAX_HISTORY)
    )
    return [ScanResultSummary.model_validate(r) for r in result.scalars().all()]


@router.get("/{scan_id}", response_model=ScanResultDetail)
async def get_scan_result(
    site_id: str,
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanResultDetail:
    site = await _get_active_site(db, site_id, current_user)

    try:
        sid = _uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Scan not found")

    result = await db.execute(
        select(ScanResult).where(
            ScanResult.id == sid, ScanResult.site_id == site.id
        )
    )
    scan = result.scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanResultDetail.model_validate(scan)


# ── helpers ────────────────────────────────────────────────────────────────────

async def _get_active_site(
    db: AsyncSession, site_id: str, current_user: User
) -> Site:
    try:
        uid = _uuid.UUID(site_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Site not found")

    result = await db.execute(
        select(Site).where(Site.id == uid, Site.owner_id == current_user.id)
    )
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    if site.status != SiteStatus.active:
        raise HTTPException(
            status_code=403,
            detail="Site must be verified before scanning. "
            "Use POST /sites/{id}/verify first.",
        )
    return site
