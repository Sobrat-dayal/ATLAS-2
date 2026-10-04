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

CANONICAL_PERMISSIONS = [
    (PermissionCode.ATLAS_ACCESS, "Atlas Access", "Base access to the ATLAS application.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_HOME_VIEW, "View Home", "View the Home module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_MARKETS_VIEW, "View Markets", "View the Markets module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_CHARTS_VIEW, "View Charts", "View the Charts module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_WATCHLISTS_VIEW, "View Watchlists", "View the Watchlists module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_SCREENERS_VIEW, "View Screeners", "View the Screeners module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_COMPANIES_VIEW, "View Companies", "View the Companies module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_ECONOMICS_VIEW, "View Economics", "View the Economics module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_NEWS_VIEW, "View News", "View the News module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_RESEARCH_VIEW, "View Research", "View the Research module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_MAPS_VIEW, "View Maps", "View the Maps module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_INTELLIGENCE_VIEW, "View Intelligence", "View the Intelligence module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_OPTIONS_VIEW, "View Options", "View the Options module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_TRADING_VIEW, "View Trading", "View the Trading module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_PORTFOLIOS_VIEW, "View Portfolios", "View the Portfolios module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_RISK_VIEW, "View Risk", "View the Risk module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_AI_VIEW, "View AI", "View the AI module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_DATA_VIEW, "View Data", "View the Data module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_SAVED_VIEW, "View Saved", "View the Saved module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_WORKSPACES_VIEW, "View Workspaces", "View the Workspaces module.", PermissionRiskClass.READ),
    (PermissionCode.MODULE_AGENTS_VIEW, "View Agents", "View the Agents module.", PermissionRiskClass.READ),
    (PermissionCode.SETTINGS_READ, "Read Settings", "View application settings.", PermissionRiskClass.READ),
    (PermissionCode.SETTINGS_WRITE_SELF, "Write Settings (Self)", "Modify own settings.", PermissionRiskClass.WRITE),
    (PermissionCode.AUTHZ_READ, "Read Authorization", "View roles and permissions.", PermissionRiskClass.READ),
    (PermissionCode.AUTHZ_MANAGE, "Manage Authorization", "Manage user roles and authorization settings.", PermissionRiskClass.CRITICAL),
]
