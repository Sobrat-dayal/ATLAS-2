from atlas.activity.router import router as activity_router
from atlas.approvals.router import router as approvals_router
from atlas.home.market_summary.router import router as home_router
from atlas.identifiers.router import router as identifiers_router
from atlas.markets.bonds.router import router as bonds_router
from atlas.markets.crypto.router import router as crypto_router
from atlas.markets.equities.router import router as equities_router
from atlas.markets.funds.router import router as funds_router
from atlas.markets.futures.router import router as futures_router
from atlas.markets.fx.router import router as fx_router
from atlas.markets.heatmaps.router import router as heatmaps_router
from atlas.markets.movers.router import router as movers_router
from atlas.markets.overview.router import router as markets_router
from atlas.tasks.router import router as tasks_router
from fastapi import APIRouter

from ..auth.router import router as auth_router
from ..authorization.router import router as authz_router
from ..entities.router import router as entity_router
from ..preferences.router import router as pref_router
from .aliases import router as aliases_router
from .commands import router as commands_router
from .companies import router as companies_router
from .economics import router as economics_router
from .geography import router as geography_router
from .health import router as health_router
from .news import router as news_router
from .notifications import router as notifications_router
from .provenance import router as provenance_router
from .providers import router as providers_router
from .realtime import router as realtime_router
from .relationships import router as relationships_router
from .research import router as research_router
from .resolution import router as resolution_router
from .search import router as search_router

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
api_router.include_router(home_router, prefix="")
api_router.include_router(markets_router, prefix="")
api_router.include_router(equities_router, prefix="")
api_router.include_router(funds_router, prefix="")
api_router.include_router(fx_router, prefix="")
api_router.include_router(crypto_router, prefix="")
api_router.include_router(bonds_router, prefix="")
api_router.include_router(futures_router, prefix="")
api_router.include_router(movers_router, prefix="")
api_router.include_router(heatmaps_router, prefix="")
api_router.include_router(activity_router, prefix="")
api_router.include_router(tasks_router, prefix="")
api_router.include_router(approvals_router, prefix="")
