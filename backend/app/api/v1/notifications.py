from fastapi import APIRouter, Depends
from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    limit = min(limit, 200)
    q = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        q = q.where(Notification.is_read.is_(False))
    q = q.order_by(desc(Notification.created_at)).limit(limit)
    result = await db.execute(q)
    notifications = result.scalars().all()

    lang = current_user.preferred_lang
    return [
        {
            "id": str(n.id),
            "type": n.notification_type.value,
            "title": n.title_ar if lang == "ar" else n.title_en,
            "body": n.body_ar if lang == "ar" else n.body_en,
            "is_read": n.is_read,
            "previous_score": n.previous_score,
            "current_score": n.current_score,
            "site_id": str(n.site_id) if n.site_id else None,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.post("/{notification_id}/read", status_code=204)
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import uuid as _uuid
    from fastapi import HTTPException

    try:
        nid = _uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Notification not found")

    await db.execute(
        update(Notification)
        .where(Notification.id == nid, Notification.user_id == current_user.id)
        .values(is_read=True)
    )


@router.post("/read-all", status_code=204)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
