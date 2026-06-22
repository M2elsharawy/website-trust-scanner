from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    TokenInvalidError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token_str,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.audit_logger import log_event

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_ACCESS_COOKIE = "access_token"


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = settings.app_env != "development"
    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1/auth/refresh",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE)
    response.delete_cookie(_REFRESH_COOKIE, path="/api/v1/auth/refresh")


def _actor_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    hashed = hash_password(body.password)
    user = User(
        email=body.email,
        hashed_password=hashed,
        preferred_lang=body.preferred_lang,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise EmailAlreadyRegisteredError()

    raw_refresh = create_refresh_token_str()
    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
        created_ip=_actor_ip(request),
    )
    db.add(refresh_record)

    access_token = create_access_token(str(user.id), user.role.value)

    await log_event(
        db,
        action="user.register",
        actor_id=str(user.id),
        actor_role=user.role.value,
        actor_ip=_actor_ip(request),
        resource_type="user",
        resource_id=str(user.id),
    )

    _set_auth_cookies(response, access_token, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    ip = _actor_ip(request)
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None:
        await log_event(
            db,
            action="user.login.failed",
            outcome="failure",
            actor_ip=ip,
            details={"reason": "user_not_found"},
        )
        raise InvalidCredentialsError()

    # Check lockout before verifying password
    now = datetime.now(timezone.utc)
    if user.locked_until and user.locked_until > now:
        await log_event(
            db,
            action="user.login.failed",
            outcome="failure",
            actor_id=str(user.id),
            actor_role=user.role.value,
            actor_ip=ip,
            resource_type="user",
            resource_id=str(user.id),
            details={"reason": "account_locked"},
        )
        raise AccountLockedError()

    if not verify_password(body.password, user.hashed_password):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.max_failed_logins:
            user.locked_until = now + timedelta(minutes=settings.login_lockout_minutes)
            await log_event(
                db,
                action="user.login.locked",
                outcome="failure",
                actor_id=str(user.id),
                actor_role=user.role.value,
                actor_ip=ip,
                resource_type="user",
                resource_id=str(user.id),
                details={"failed_count": user.failed_login_count},
            )
        else:
            await log_event(
                db,
                action="user.login.failed",
                outcome="failure",
                actor_id=str(user.id),
                actor_role=user.role.value,
                actor_ip=ip,
                resource_type="user",
                resource_id=str(user.id),
                details={
                    "reason": "wrong_password",
                    "failed_count": user.failed_login_count,
                },
            )
        raise InvalidCredentialsError()

    if not user.is_active:
        raise AccountInactiveError()

    # Successful login — reset failure counters
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now

    raw_refresh = create_refresh_token_str()
    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        created_ip=ip,
    )
    db.add(refresh_record)

    access_token = create_access_token(str(user.id), user.role.value)

    await log_event(
        db,
        action="user.login",
        actor_id=str(user.id),
        actor_role=user.role.value,
        actor_ip=ip,
        resource_type="user",
        resource_id=str(user.id),
    )

    _set_auth_cookies(response, access_token, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    raw_refresh = request.cookies.get(_REFRESH_COOKIE)
    if not raw_refresh:
        raise TokenInvalidError()

    token_hash = hash_refresh_token(raw_refresh)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if (
        record is None
        or record.revoked
        or record.expires_at.replace(tzinfo=timezone.utc) < now
    ):
        raise TokenInvalidError()

    # Rotate: revoke old, issue new
    record.revoked = True

    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise TokenInvalidError()

    new_raw_refresh = create_refresh_token_str()
    new_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_raw_refresh),
        expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        created_ip=_actor_ip(request),
    )
    db.add(new_record)

    access_token = create_access_token(str(user.id), user.role.value)

    _set_auth_cookies(response, access_token, new_raw_refresh)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> None:
    raw_refresh = request.cookies.get(_REFRESH_COOKIE)
    if raw_refresh:
        token_hash = hash_refresh_token(raw_refresh)
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record = result.scalar_one_or_none()
        if record and not record.revoked:
            record.revoked = True
    _clear_auth_cookies(response)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
