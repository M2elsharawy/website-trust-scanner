from fastapi import APIRouter
from app.api.v1 import health
from app.api.v1 import scans
from app.api.v1.admin import leads as admin_leads

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(scans.router)
api_router.include_router(admin_leads.router)
