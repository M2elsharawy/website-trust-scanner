"""Create in-app notifications for site owners."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType

_SCORE_DROP_THRESHOLD = 10  # alert if score drops by this much


async def notify_score_drop(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    site_id: uuid.UUID,
    domain: str,
    previous_score: int,
    current_score: int,
) -> None:
    drop = previous_score - current_score
    notif = Notification(
        user_id=user_id,
        site_id=site_id,
        notification_type=NotificationType.score_drop,
        title_ar=f"تحذير: انخفضت درجة الثقة لموقع {domain}",
        title_en=f"Warning: Trust score dropped for {domain}",
        body_ar=(
            f"انخفضت درجة الثقة لموقعك من {previous_score} إلى {current_score} "
            f"(انخفاض بمقدار {drop} نقطة). يُنصح بمراجعة نتائج الفحص."
        ),
        body_en=(
            f"Your site's trust score dropped from {previous_score} to {current_score} "
            f"(a drop of {drop} points). Please review the latest scan results."
        ),
        previous_score=previous_score,
        current_score=current_score,
    )
    db.add(notif)
    await db.flush()


async def notify_score_recovered(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    site_id: uuid.UUID,
    domain: str,
    previous_score: int,
    current_score: int,
) -> None:
    gain = current_score - previous_score
    notif = Notification(
        user_id=user_id,
        site_id=site_id,
        notification_type=NotificationType.score_recovered,
        title_ar=f"تحسّنت درجة الثقة لموقع {domain}",
        title_en=f"Trust score improved for {domain}",
        body_ar=(
            f"ارتفعت درجة الثقة لموقعك من {previous_score} إلى {current_score} "
            f"(ارتفاع بمقدار {gain} نقطة)."
        ),
        body_en=(
            f"Your site's trust score improved from {previous_score} to {current_score} "
            f"(+{gain} points)."
        ),
        previous_score=previous_score,
        current_score=current_score,
    )
    db.add(notif)
    await db.flush()


async def notify_scan_complete(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    site_id: uuid.UUID,
    domain: str,
    score: int,
) -> None:
    notif = Notification(
        user_id=user_id,
        site_id=site_id,
        notification_type=NotificationType.scan_complete,
        title_ar=f"اكتمل الفحص الدوري لموقع {domain}",
        title_en=f"Scheduled scan complete for {domain}",
        body_ar=f"درجة الثقة الحالية: {score}/100",
        body_en=f"Current trust score: {score}/100",
        current_score=score,
    )
    db.add(notif)
    await db.flush()
