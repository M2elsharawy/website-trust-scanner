from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    # Check Redis
    try:
        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        await r.aclose()
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall,
        "version": "1.0.0",
        "environment": settings.app_env,
        "services": {
            "database": db_status,
            "redis": redis_status,
        },
    }
