from enum import StrEnum


class PermissionRiskClass(StrEnum):
    READ = "read"
    WRITE = "write"
    ACTION = "action"
    CRITICAL = "critical"

class PermissionCode(StrEnum):
    ATLAS_ACCESS = "atlas.access"

    MODULE_HOME_VIEW = "module.home.view"
    MODULE_MARKETS_VIEW = "module.markets.view"
    MODULE_CHARTS_VIEW = "module.charts.view"
    MODULE_WATCHLISTS_VIEW = "module.watchlists.view"
    MODULE_SCREENERS_VIEW = "module.screeners.view"
    MODULE_COMPANIES_VIEW = "module.companies.view"
    MODULE_ECONOMICS_VIEW = "module.economics.view"
    MODULE_NEWS_VIEW = "module.news.view"
    MODULE_RESEARCH_VIEW = "module.research.view"
    MODULE_MAPS_VIEW = "module.maps.view"
    MODULE_INTELLIGENCE_VIEW = "module.intelligence.view"
    MODULE_OPTIONS_VIEW = "module.options.view"
    MODULE_TRADING_VIEW = "module.trading.view"
    MODULE_PORTFOLIOS_VIEW = "module.portfolios.view"
    MODULE_RISK_VIEW = "module.risk.view"
    MODULE_AI_VIEW = "module.ai.view"
    MODULE_DATA_VIEW = "module.data.view"
    MODULE_SAVED_VIEW = "module.saved.view"
    MODULE_WORKSPACES_VIEW = "module.workspaces.view"
    MODULE_AGENTS_VIEW = "module.agents.view"

    SETTINGS_READ = "settings.read"
    SETTINGS_WRITE_SELF = "settings.write_self"

    AUTHZ_READ = "authz.read"
    AUTHZ_MANAGE = "authz.manage"
