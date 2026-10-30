"""Tool Discovery Service for Stage 126: ATLAS AI Tool Gateway.

Discovers, ranks, and filters authorized tool declarations for injection into
the AI model's function-calling interface.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from atlas.ai.tools.domain import AtlasAiToolDefinition, ToolLifecycleStatus
from atlas.ai.tools.registry import AtlasAiToolRegistry

logger = logging.getLogger(__name__)

# Route-to-tool affinity weights for relevance ranking
ROUTE_TOOL_AFFINITIES: Dict[str, List[str]] = {
    "/instruments": [
        "atlas.instrument.search",
        "atlas.instrument.get",
        "atlas.market.quote",
        "atlas.company.get",
    ],
    "/company": [
        "atlas.company.get",
        "atlas.company.financials",
        "atlas.instrument.get",
        "atlas.market.quote",
    ],
    "/charts": [
        "atlas.market.quote",
        "atlas.market.history_summary",
        "atlas.instrument.get",
        "atlas.watchlist.list",
    ],
    "/screener": ["atlas.screener.get_definition", "atlas.instrument.search", "atlas.company.get"],
    "/watchlists": ["atlas.watchlist.list", "atlas.market.quote", "atlas.instrument.search"],
    "/economics": ["atlas.economics.search_series", "atlas.economics.get_observations"],
    "/news": ["atlas.news.search_headlines", "atlas.instrument.search"],
    "/research": ["atlas.research.list_metadata", "atlas.company.get"],
    "/portfolios": [
        "atlas.portfolio.list",
        "atlas.portfolio.get_summary",
        "atlas.portfolio.get_performance",
        "atlas.risk.list_runs",
    ],
    "/risk": ["atlas.risk.list_runs", "atlas.risk.get_run_summary", "atlas.portfolio.get_summary"],
    "/data": ["atlas.data.list_sources", "atlas.saved.list"],
    "/saved": ["atlas.saved.list", "atlas.workspace.list"],
    "/workspaces": ["atlas.workspace.list", "atlas.saved.list"],
}


class ToolDiscoveryService:
    """Discovers and filters relevant tool definitions for a user request."""

    _instance: Optional["ToolDiscoveryService"] = None

    def __init__(self, registry: Optional[AtlasAiToolRegistry] = None) -> None:
        self.registry = registry or AtlasAiToolRegistry.get_instance()

    @classmethod
    def get_instance(cls) -> "ToolDiscoveryService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def discover_tools(
        self,
        user_id: str,
        user_permissions: Optional[List[str]] = None,
        disabled_tool_ids: Optional[List[str]] = None,
        active_route: Optional[str] = None,
        model_id: Optional[str] = None,
        max_tools: int = 12,
    ) -> List[AtlasAiToolDefinition]:
        """Discovers authorized, enabled tools ordered by contextual relevance."""
        disabled_set = set(disabled_tool_ids or [])
        user_perms_set = set(user_permissions or ["*"])  # Default allow read scopes

        all_tools = self.registry.list_tools(include_disabled=False)
        eligible_tools: List[AtlasAiToolDefinition] = []

        for tool in all_tools:
            # 1. Check lifecycle status
            if tool.lifecycle_status != ToolLifecycleStatus.ENABLED:
                continue

            # 2. Check user-level disabled tools
            if tool.tool_id in disabled_set:
                continue

            # 3. Check permission scopes
            if "*" not in user_perms_set:
                required = tool.capability_scope.value
                if required not in user_perms_set and "tools:read" not in user_perms_set:
                    continue

            # 4. Check model compatibility
            if model_id and "*" not in tool.supported_models:
                if model_id not in tool.supported_models:
                    continue

            eligible_tools.append(tool)

        # Rank tools contextually by route affinity
        if active_route:
            primary_route = "/" + active_route.strip("/").split("/")[0] if active_route else ""
            affinity_list = ROUTE_TOOL_AFFINITIES.get(primary_route, [])

            def rank_key(t: AtlasAiToolDefinition) -> tuple:
                is_affinity = t.tool_id in affinity_list
                affinity_index = affinity_list.index(t.tool_id) if is_affinity else 999
                return (not is_affinity, affinity_index, t.tool_id)

            eligible_tools.sort(key=rank_key)

        return eligible_tools[:max_tools]

    def format_tools_for_model(
        self,
        tools: List[AtlasAiToolDefinition],
    ) -> List[Dict[str, Any]]:
        """Formats definitions into OpenAI function calling format."""
        return [tool.to_openai_function_declaration() for tool in tools]
