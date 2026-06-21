from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Website Trust & Security Advisor API",
    description="مساعد تقييم أمان وموثوقية المواقع",
    version="1.0.0",
    docs_url="/api/docs" if settings.app_env == "development" else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if settings.app_env == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept-Language"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Website Trust Scanner API", "docs": "/api/docs"}
