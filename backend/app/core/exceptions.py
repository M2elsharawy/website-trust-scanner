from fastapi import status


class AppError(Exception):
    """Base application exception."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None, detail: str | None = None):
        self.message = message or self.__class__.message
        self.detail = detail
        super().__init__(self.message)


# ── URL / SSRF ──────────────────────────────────────────────────────────────

class URLValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "INVALID_URL"
    message = "The provided URL is invalid"


class URLNotSafeError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "URL_NOT_SAFE"
    message = "The URL resolves to a disallowed address"


class SSRFBlockedError(URLNotSafeError):
    error_code = "SSRF_BLOCKED"
    message = "The URL targets a private or reserved address"


# ── Scan policy ──────────────────────────────────────────────────────────────

class DomainBlockedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "DOMAIN_BLOCKED"
    message = "This domain is on the Do Not Scan list"


class ScanNotAllowedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "SCAN_NOT_ALLOWED"
    message = "This scan type is not allowed for this site"


class AuthorizationRequiredError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_REQUIRED"
    message = "An Authorization Record is required for this scan"


# ── Rate limiting ────────────────────────────────────────────────────────────

class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests — please slow down"


# ── Auth ─────────────────────────────────────────────────────────────────────

class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "INVALID_CREDENTIALS"
    message = "Incorrect email or password"


class AccountLockedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "ACCOUNT_LOCKED"
    message = "Account is temporarily locked due to too many failed login attempts"


class AccountInactiveError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "ACCOUNT_INACTIVE"
    message = "Account is inactive"


class TokenInvalidError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "TOKEN_INVALID"
    message = "Invalid or expired token"


class InsufficientRoleError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "INSUFFICIENT_ROLE"
    message = "You do not have permission to perform this action"


class EmailAlreadyRegisteredError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "EMAIL_ALREADY_REGISTERED"
    message = "An account with this email already exists"


# ── Ownership ─────────────────────────────────────────────────────────────────

class OwnershipVerificationError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "OWNERSHIP_VERIFICATION_FAILED"
    message = "DNS TXT record verification failed"


class SiteNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "SITE_NOT_FOUND"
    message = "Site not found"
