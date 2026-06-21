"""
Admin API key authentication dependency.

Phase 5 uses a simple static API key (X-Admin-Key header).
Phase 6 will replace this with JWT + role-based auth.

The key is compared in constant time to prevent timing attacks.
"""

import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_admin(x_admin_key: str = Header(...)) -> None:
    """
    FastAPI dependency: validates X-Admin-Key header.

    Uses secrets.compare_digest to prevent timing-based key enumeration.
    Raises 401 on failure — never reveals why (invalid vs missing).
    """
    if not secrets.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
