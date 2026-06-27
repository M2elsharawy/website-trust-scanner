"""
Celery periodic task: re-scan all verified sites once every 24 hours.

Compares new score to the most recent stored score and fires notifications
if the drop is >= 10 points or if there's a recovery.

All security enforcement (Do Not Scan, SSRF, URL validation, scan policy)
is delegated to run_owner_trust_scan — the scheduler has no override capability.
"""

import asyncio
import logging

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import desc, select

from app.core.config import settings
from app.core.safe_scan_runner import run_owner_trust_scan
from app.db.session import AsyncSessionFactory
from app.models.scan_result import ScanResult
from app.models.site import Site, SiteStatus
from app.services.notification_service import (
    notify_scan_complete,
    notify_score_drop,
    notify_score_recovered,
)

logger = logging.getLogger(__name__)

_SCORE_DROP_THRESHOLD = 10
_SCORE_RECOVERY_THRESHOLD = 10

celery_app = Celery("trust_scanner", broker=settings.redis_url, backend=settings.redis_url)

celery_app.conf.beat_schedule = {
    "rescan-verified-sites-daily": {
        "task": "app.tasks.scheduled_scans.rescan_all_verified_sites",
        "schedule": crontab(hour=3, minute=0),  # 03:00 UTC daily
    },
}
celery_app.conf.timezone = "UTC"


@celery_app.task(name="app.tasks.scheduled_scans.rescan_all_verified_sites")
def rescan_all_verified_sites() -> dict:
    """Synchronous Celery entry-point; delegates to async runner."""
    return asyncio.run(_async_rescan_all())


async def _async_rescan_all() -> dict:
    scanned = 0
    errors = 0

    async with AsyncSessionFactory() as db:
        result = await db.execute(
            select(Site).where(Site.status == SiteStatus.active)
        )
        sites = result.scalars().all()

        for site in sites:
            try:
                await _rescan_site(db, site)
                scanned += 1
            except Exception:
                logger.exception("scheduled rescan failed for site_id=%s", site.id)
                errors += 1

        await db.commit()

    return {"scanned": scanned, "errors": errors}


async def _rescan_site(db, site: Site) -> None:
    # Get previous score before running the new scan
    prev_result = await db.execute(
        select(ScanResult)
        .where(ScanResult.site_id == site.id)
        .order_by(desc(ScanResult.scanned_at))
        .limit(1)
    )
    prev = prev_result.scalar_one_or_none()
    prev_score = prev.trust_score if prev else None

    # All security checks (Do Not Scan, SSRF, URL validation, scan policy)
    # are enforced inside run_owner_trust_scan — no scheduler override possible.
    report = await run_owner_trust_scan(
        domain=site.domain,
        actor_id="scheduler",
        actor_role="system",
        site_id=str(site.id),
        db=db,
    )
    new_score = report["trust_score"]

    new_result = ScanResult(
        site_id=site.id,
        domain=site.domain,
        trust_score=new_score,
        result_json=report,
    )
    db.add(new_result)
    await db.flush()

    await notify_scan_complete(
        db, user_id=site.owner_id, site_id=site.id,
        domain=site.domain, score=new_score,
    )

    if prev_score is not None:
        drop = prev_score - new_score
        gain = new_score - prev_score
        if drop >= _SCORE_DROP_THRESHOLD:
            await notify_score_drop(
                db, user_id=site.owner_id, site_id=site.id,
                domain=site.domain,
                previous_score=prev_score, current_score=new_score,
            )
        elif gain >= _SCORE_RECOVERY_THRESHOLD:
            await notify_score_recovered(
                db, user_id=site.owner_id, site_id=site.id,
                domain=site.domain,
                previous_score=prev_score, current_score=new_score,
            )
