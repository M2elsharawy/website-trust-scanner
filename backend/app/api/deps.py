from typing import Annotated

from fastapi import Cookie, Depends
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InsufficientRoleError, TokenInvalidError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole


async def _get_user_from_token(
    access_token: str | None,
    db: AsyncSession,
) -> User | None:
    if not access_token:
        return None
    try:
        payload = decode_access_token(access_token)
    except JWTError:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def optional_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    return await _get_user_from_token(access_token, db)


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(access_token, db)
    if user is None:
        raise TokenInvalidError()
    if not user.is_active:
        raise TokenInvalidError()
    return user


def require_role(*roles: UserRole):
    """Return a dependency that enforces one of the given roles."""

    async def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise InsufficientRoleError()
        return current_user

    return _dep
