from fastapi import APIRouter

from ..auth.router import router as auth_router
from ..authorization.router import router as authz_router
from ..entities.router import router as entity_router
from ..preferences.router import router as pref_router
from atlas.identifiers.router import router as identifiers_router
from .companies import router as companies_router
from .economics import router as economics_router
from .geography import router as geography_router
from .health import router as health_router
from .news import router as news_router
from .research import router as research_router
from .aliases import router as aliases_router
from .resolution import router as resolution_router
from .relationships import router as relationships_router
from .provenance import router as provenance_router
from .providers import router as providers_router
from .realtime import router as realtime_router
from .search import router as search_router
from .commands import router as commands_router
from .notifications import router as notifications_router

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
api_router.include_router(identifiers_router, prefix="")
api_router.include_router(aliases_router, prefix="")
api_router.include_router(resolution_router, prefix="")
api_router.include_router(relationships_router, prefix="")
api_router.include_router(provenance_router, prefix="")
api_router.include_router(providers_router, prefix="")
api_router.include_router(realtime_router, prefix="")
api_router.include_router(search_router, prefix="")
api_router.include_router(commands_router, prefix="")
api_router.include_router(notifications_router, prefix="")
