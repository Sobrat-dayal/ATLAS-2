"""Authoritative Stage 4 canonical module registry contract for activity tracking."""

from typing import NamedTuple


class CanonicalModuleInfo(NamedTuple):
    id: str
    label: str
    route: str
    required_permission: str


CANONICAL_MODULES: dict[str, CanonicalModuleInfo] = {
    "home": CanonicalModuleInfo("home", "Home", "/home", "module.home.view"),
    "markets": CanonicalModuleInfo("markets", "Markets", "/markets", "module.markets.view"),
    "charts": CanonicalModuleInfo("charts", "Charts", "/charts", "module.charts.view"),
    "watchlists": CanonicalModuleInfo(
        "watchlists", "Watchlists", "/watchlists", "module.watchlists.view"
    ),
    "screeners": CanonicalModuleInfo(
        "screeners", "Screeners", "/screeners", "module.screeners.view"
    ),
    "companies": CanonicalModuleInfo(
        "companies", "Companies", "/companies", "module.companies.view"
    ),
    "economics": CanonicalModuleInfo(
        "economics", "Economics", "/economics", "module.economics.view"
    ),
    "news": CanonicalModuleInfo("news", "News", "/news", "module.news.view"),
    "research": CanonicalModuleInfo("research", "Research", "/research", "module.research.view"),
    "maps": CanonicalModuleInfo("maps", "Maps", "/maps", "module.maps.view"),
    "intelligence": CanonicalModuleInfo(
        "intelligence", "Intelligence", "/intelligence", "module.intelligence.view"
    ),
    "options": CanonicalModuleInfo("options", "Options", "/options", "module.options.view"),
    "trading": CanonicalModuleInfo("trading", "Trading", "/trading", "module.trading.view"),
    "portfolios": CanonicalModuleInfo(
        "portfolios", "Portfolios", "/portfolios", "module.portfolios.view"
    ),
    "risk": CanonicalModuleInfo("risk", "Risk", "/risk", "module.risk.view"),
    "ai": CanonicalModuleInfo("ai", "AI", "/ai", "module.ai.view"),
    "data": CanonicalModuleInfo("data", "Data", "/data", "module.data.view"),
    "saved": CanonicalModuleInfo("saved", "Saved", "/saved", "module.saved.view"),
    "workspaces": CanonicalModuleInfo(
        "workspaces", "Workspaces", "/workspaces", "module.workspaces.view"
    ),
    "agents": CanonicalModuleInfo("agents", "Agents", "/agents", "module.agents.view"),
}


def is_valid_module_id(module_id: str) -> bool:
    """Checks whether the given string is one of the 20 canonical ATLAS modules."""
    return module_id in CANONICAL_MODULES


def get_module_info(module_id: str) -> CanonicalModuleInfo | None:
    """Retrieves canonical metadata for a module ID if valid."""
    return CANONICAL_MODULES.get(module_id)
