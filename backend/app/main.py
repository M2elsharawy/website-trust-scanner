import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.rate_limiter import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

_MAX_REQUEST_BODY_BYTES = 512 * 1024  # 512 KB

app = FastAPI(
    title="Website Trust & Security Advisor API",
    description="مساعد تقييم أمان وموثوقية المواقع",
    version="1.0.0",
    docs_url="/api/docs" if settings.app_env == "development" else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if settings.app_env == "development" else None,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept-Language"],
)

# Only enforce trusted hosts in production to avoid breaking local dev
if settings.app_env == "production":
    _allowed_hosts = [
        o.replace("https://", "").replace("http://", "")
        for o in settings.allowed_origins
    ]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=_allowed_hosts)


@app.middleware("http")
async def limit_request_body(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > _MAX_REQUEST_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"error": "REQUEST_TOO_LARGE", "message": "Request body too large"},
        )
    return await call_next(request)


@app.middleware("http")
async def csrf_origin_check(request: Request, call_next):
    """
    CSRF protection for cookie-authenticated state-changing requests.

    SameSite=Lax on cookies provides the primary defence. This server-side
    Origin check adds defence-in-depth in production. Bearer requests are
    CSRF-immune by design and are excluded from this check.
    """
    if settings.app_env != "development":
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            has_bearer = "authorization" in request.headers
            if not has_bearer:
                origin = request.headers.get("origin") or request.headers.get("referer", "")
                if not any(origin.startswith(allowed) for allowed in settings.allowed_origins):
                    return JSONResponse(
                        status_code=403,
                        content={"error": "CSRF_REJECTED", "message": "Origin not allowed"},
                    )
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert all AppError subclasses to a consistent JSON error envelope."""
    body: dict = {"error": exc.error_code, "message": exc.message}
    if exc.detail:
        body["detail"] = exc.detail
    return JSONResponse(status_code=exc.status_code, content=body)


app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Website Trust Scanner API", "docs": "/api/docs"}
