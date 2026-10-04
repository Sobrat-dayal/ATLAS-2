from fastapi import APIRouter

from .health import router as health_router
from ..auth.router import router as auth_router
from ..authorization.router import router as authz_router
from ..preferences.router import router as pref_router
from ..entities.router import router as entity_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="")
api_router.include_router(auth_router, prefix="")
api_router.include_router(authz_router, prefix="")
api_router.include_router(pref_router, prefix="")
api_router.include_router(entity_router, prefix="")

