from fastapi import APIRouter
from app.api.v1 import auth, health, owner_scans, scans, sites
from app.api.v1.admin import leads as admin_leads

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(scans.router)
api_router.include_router(admin_leads.router)
api_router.include_router(auth.router)
api_router.include_router(sites.router)
api_router.include_router(owner_scans.router)
