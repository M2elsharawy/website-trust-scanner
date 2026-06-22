from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.url_validator import validate_url
from app.core.exceptions import URLValidationError
from app.db.session import get_db
from app.models.site import Site
from app.models.user import User
from app.schemas.site import SiteCreate, SiteDetail
from app.services.audit_logger import log_event

router = APIRouter(prefix="/sites", tags=["sites"])


@router.post("", response_model=SiteDetail, status_code=201)
async def add_site(
    body: SiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SiteDetail:
    # Normalise to bare domain — validate_url requires a scheme, so we add one
    raw = body.domain.strip()
    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"
    try:
        validate_url(raw)
    except Exception as exc:
        raise URLValidationError(str(exc)) from exc

    from urllib.parse import urlparse
    domain = urlparse(raw).hostname or body.domain.strip()

    site = Site(owner_id=current_user.id, domain=domain)
    db.add(site)
    await db.flush()

    await log_event(
        db,
        action="site.add",
        actor_id=str(current_user.id),
        actor_role=current_user.role.value,
        resource_type="site",
        resource_id=str(site.id),
        details={"domain": domain},
    )

    return SiteDetail.model_validate(site)


@router.get("", response_model=list[SiteDetail])
async def list_sites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SiteDetail]:
    result = await db.execute(
        select(Site).where(Site.owner_id == current_user.id).order_by(Site.created_at)
    )
    sites = result.scalars().all()
    return [SiteDetail.model_validate(s) for s in sites]


@router.get("/{site_id}", response_model=SiteDetail)
async def get_site(
    site_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SiteDetail:
    import uuid as _uuid
    from fastapi import HTTPException

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
    return SiteDetail.model_validate(site)
