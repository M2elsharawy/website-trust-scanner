"""
Admin authentication dependency.

Accepts EITHER:
  1. JWT access token (httpOnly cookie) with admin or super_admin role, OR
  2. Static X-Admin-Key header (backward-compatible fallback from Phase 5).

The API-key path uses constant-time comparison to prevent timing attacks.
"""

import secrets

from fastapi import Cookie, Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InsufficientRoleError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import ADMIN_ROLES, User


async def require_admin(
    access_token: str | None = Cookie(default=None),
    x_admin_key: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    FastAPI dependency: grants access to admin routes.

    JWT path (preferred): validates access token cookie and confirms role is
    admin or super_admin.

    API-key path (fallback): validates X-Admin-Key using constant-time
    comparison.  Returns None for actor since we have no User record.
    """
    # --- JWT path ---
    if access_token:
        try:
            payload = decode_access_token(access_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        if user.role not in ADMIN_ROLES:
            raise InsufficientRoleError()
        return user

    # --- API-key fallback path ---
    if x_admin_key and secrets.compare_digest(x_admin_key, settings.admin_api_key):
        return None  # No User object for key-based auth

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
    )
