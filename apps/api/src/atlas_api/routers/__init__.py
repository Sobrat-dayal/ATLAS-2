from fastapi import APIRouter

from ..auth.router import router as auth_router
from ..authorization.router import router as authz_router
from ..entities.router import router as entity_router
from ..preferences.router import router as pref_router
from .companies import router as companies_router
from .economics import router as economics_router
from .geography import router as geography_router
from .health import router as health_router
from .news import router as news_router
from .research import router as research_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="")
api_router.include_router(auth_router, prefix="")
api_router.include_router(authz_router, prefix="")
api_router.include_router(pref_router, prefix="")
api_router.include_router(entity_router, prefix="")
api_router.include_router(companies_router, prefix="")
api_router.include_router(geography_router, prefix="")
api_router.include_router(economics_router, prefix="")
api_router.include_router(research_router, prefix="")
api_router.include_router(news_router, prefix="")
