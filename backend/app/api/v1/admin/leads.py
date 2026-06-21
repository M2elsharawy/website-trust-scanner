"""
Admin Lead management endpoints.

All routes require X-Admin-Key header (verified by require_admin dependency).

Audit Policy for Lead Audit:
  - Only PUBLIC_TRUST-equivalent scan is performed (same 5 checkers as Phase 4)
  - Forbidden: port scan, file enumeration, crawling, deep security scan
  - Status rejected / do_not_contact → audit blocked
  - Outreach report contains NO vulnerability details
"""

import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin.auth import require_admin
from app.core.exceptions import DomainBlockedError
from app.core.url_validator import validate_url
from app.db.session import get_db
from app.models.do_not_scan import DoNotScan
from app.models.lead import (
    Lead,
    LeadStatus,
    LEAD_AUDIT_BLOCKED_STATUSES,
    LEAD_STATUS_TRANSITIONS,
)
from app.scanners.lead_score import compute_lead_score, score_to_opportunity_level
from app.scanners.outreach import generate_outreach
from app.scanners.runner import run_public_scan
from app.schemas.lead import (
    LeadCreate,
    LeadDetail,
    LeadStatusUpdate,
    LeadSummary,
    OutreachReport,
)
from app.services.audit_logger import log_event

router = APIRouter(
    prefix="/admin/leads",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


# ── Create lead ───────────────────────────────────────────────────────────────

@router.post("", response_model=LeadDetail, status_code=status.HTTP_201_CREATED)
async def create_lead(
    request: Request,
    body: LeadCreate,
    db: AsyncSession = Depends(get_db),
) -> LeadDetail:
    actor_ip = request.client.host if request.client else None

    # Validate domain via URL validator
    validate_url(f"https://{body.domain}", allow_http=False)

    # Check Do Not Scan list
    dns_row = await db.execute(
        select(DoNotScan).where(func.lower(DoNotScan.domain) == body.domain.lower())
    )
    if dns_row.scalar_one_or_none() is not None:
        raise DomainBlockedError()

    # Reject duplicate
    existing = await db.execute(
        select(Lead).where(func.lower(Lead.domain) == body.domain.lower())
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lead for this domain already exists",
        )

    lead = Lead(domain=body.domain, status=LeadStatus.new)
    db.add(lead)
    await db.flush()

    await log_event(
        db,
        action="admin.lead.created",
        actor_ip=actor_ip,
        resource_type="lead",
        resource_id=str(lead.id),
        details={"domain": body.domain},
    )

    return LeadDetail.model_validate(lead)


# ── List leads ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[LeadSummary])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    status_filter: LeadStatus | None = None,
) -> list[LeadSummary]:
    query = select(Lead).order_by(Lead.created_at.desc())
    if status_filter is not None:
        query = query.where(Lead.status == status_filter)
    result = await db.execute(query)
    return [LeadSummary.model_validate(row) for row in result.scalars().all()]


# ── Get lead detail ───────────────────────────────────────────────────────────

@router.get("/{lead_id}", response_model=LeadDetail)
async def get_lead(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> LeadDetail:
    lead = await _get_lead_or_404(lead_id, db)
    return LeadDetail.model_validate(lead)


# ── Update lead status ────────────────────────────────────────────────────────

@router.patch("/{lead_id}/status", response_model=LeadDetail)
async def update_lead_status(
    lead_id: uuid.UUID,
    request: Request,
    body: LeadStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> LeadDetail:
    actor_ip = request.client.host if request.client else None
    lead = await _get_lead_or_404(lead_id, db)

    allowed = LEAD_STATUS_TRANSITIONS[lead.status]
    if body.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Cannot transition from '{lead.status.value}' to '{body.status.value}'. "
                f"Allowed next statuses: {[s.value for s in allowed] or 'none (terminal state)'}"
            ),
        )

    old_status = lead.status
    lead.status = body.status
    if body.notes:
        lead.notes = body.notes

    await log_event(
        db,
        action="admin.lead.status_changed",
        actor_ip=actor_ip,
        resource_type="lead",
        resource_id=str(lead.id),
        details={
            "domain": lead.domain,
            "from_status": old_status.value,
            "to_status": body.status.value,
        },
    )

    return LeadDetail.model_validate(lead)


# ── Run lead audit ────────────────────────────────────────────────────────────

@router.post("/{lead_id}/audit", response_model=OutreachReport)
async def run_lead_audit(
    lead_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> OutreachReport:
    """
    Run a surface-level marketing audit (same 5 checkers as public trust scan).

    FORBIDDEN: port scan, file enumeration, crawling, deep security scan.
    This is a MARKETING audit only — output contains no vulnerability details.
    """
    actor_ip = request.client.host if request.client else None
    lead = await _get_lead_or_404(lead_id, db)

    # Block audit for rejected / do_not_contact leads
    if lead.status in LEAD_AUDIT_BLOCKED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Audit blocked for lead with status '{lead.status.value}'",
        )

    # Check Do Not Scan list (re-verify in case it was added after lead creation)
    dns_row = await db.execute(
        select(DoNotScan).where(func.lower(DoNotScan.domain) == lead.domain.lower())
    )
    if dns_row.scalar_one_or_none() is not None:
        # Auto-update lead status and block
        lead.status = LeadStatus.do_not_contact
        await log_event(
            db,
            action="admin.lead.auto_blocked_do_not_scan",
            actor_ip=actor_ip,
            resource_type="lead",
            resource_id=str(lead.id),
            details={"domain": lead.domain},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Domain is on the Do Not Scan list. Lead status updated to do_not_contact.",
        )

    # Run the same surface-level checkers as public trust scan
    scan_data = await run_public_scan(lead.domain)

    # Compute Lead Score (business opportunity, not security grade)
    lead_score = compute_lead_score(scan_data)
    opportunity = score_to_opportunity_level(lead_score)

    # Generate safe bilingual outreach content (no vuln details)
    outreach = generate_outreach(lead.domain, scan_data)

    # Safe checks summary (same rules as public report — no IPs, no header values)
    checks_summary = {
        "https": scan_data.https.available,
        "ssl_valid": scan_data.ssl.valid,
        "hsts": scan_data.https.hsts_present,
        "headers_score": scan_data.headers.score,
        "headers_max": scan_data.headers.MAX_SCORE,
        "reputation": (
            "flagged"
            if scan_data.reputation.status == "suspicious"
            else scan_data.reputation.status
        ),
    }

    # Update lead with latest audit snapshot
    lead.last_audit_at = datetime.now(timezone.utc)
    lead.last_lead_score = lead_score

    await log_event(
        db,
        action="admin.lead.audit_completed",
        actor_ip=actor_ip,
        resource_type="lead",
        resource_id=str(lead.id),
        details={
            "domain": lead.domain,
            "lead_score": lead_score,
            "opportunity_level": opportunity,
        },
    )

    return OutreachReport(
        lead_id=lead.id,
        domain=lead.domain,
        lead_score=lead_score,
        opportunity_level=opportunity,
        improvement_areas_en=outreach["improvement_areas_en"],
        improvement_areas_ar=outreach["improvement_areas_ar"],
        outreach_message_en=outreach["outreach_message_en"],
        outreach_message_ar=outreach["outreach_message_ar"],
        checks_summary=checks_summary,
        generated_at=datetime.now(timezone.utc),
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_lead_or_404(lead_id: uuid.UUID, db: AsyncSession) -> Lead:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead
