"""Static, version-controlled command specifications for ATLAS Command Language v1."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AtlasCommandModuleSpec:
    """Specification for a canonical ATLAS module command."""

    module_id: str
    canonical_slash_name: str
    command_id: str
    entity_command_id: Optional[str]
    route: str
    required_permission: str
    aliases: List[str]
    supports_entity_context: bool = False
    allowed_target_entity_types: Optional[List[str]] = None
    default_action: Optional[str] = None


@dataclass(frozen=True)
class AtlasUtilityCommandSpec:
    """Specification for a shell utility command (e.g. /settings, /search)."""

    utility_id: str
    canonical_slash_name: str
    command_id: str
    aliases: List[str]
    description: str


@dataclass(frozen=True)
class AtlasShorthandSpec:
    """Specification for Bloomberg-style deterministic shorthand."""

    pattern_name: str
    syntax_kind: str  # "suffix" or "prefix" or "exact"
    keyword: str
    command_id: str
    module_id: str
    action: str
    target_required: bool
    allowed_target_entity_types: Optional[List[str]] = None
    available: bool = True
    unavailable_reason: Optional[str] = None


# Exact 20 canonical modules
CANONICAL_MODULE_SPECS: List[AtlasCommandModuleSpec] = [
    AtlasCommandModuleSpec(
        module_id="home",
        canonical_slash_name="home",
        command_id="navigation.home",
        entity_command_id=None,
        route="/home",
        required_permission="module.home.view",
        aliases=[],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="markets",
        canonical_slash_name="markets",
        command_id="navigation.markets",
        entity_command_id="navigation.markets.entity",
        route="/markets",
        required_permission="module.markets.view",
        aliases=["market", "mkt", "mkts"],
        supports_entity_context=True,
        allowed_target_entity_types=None,  # any entity
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="charts",
        canonical_slash_name="charts",
        command_id="navigation.charts",
        entity_command_id="navigation.charts.entity",
        route="/charts",
        required_permission="module.charts.view",
        aliases=["chart", "ch"],
        supports_entity_context=True,
        allowed_target_entity_types=[
            "financial_instrument",
            "security",
            "index",
            "currency_pair",
            "cryptocurrency",
        ],
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="watchlists",
        canonical_slash_name="watchlists",
        command_id="navigation.watchlists",
        entity_command_id=None,
        route="/watchlists",
        required_permission="module.watchlists.view",
        aliases=["watchlist", "watch", "wl"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="screeners",
        canonical_slash_name="screeners",
        command_id="navigation.screeners",
        entity_command_id=None,
        route="/screeners",
        required_permission="module.screeners.view",
        aliases=["screener", "screen", "scr"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="companies",
        canonical_slash_name="companies",
        command_id="navigation.companies",
        entity_command_id="navigation.companies.entity",
        route="/companies",
        required_permission="module.companies.view",
        aliases=["company", "co", "comp"],
        supports_entity_context=True,
        allowed_target_entity_types=["company"],
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="economics",
        canonical_slash_name="economics",
        command_id="navigation.economics",
        entity_command_id=None,
        route="/economics",
        required_permission="module.economics.view",
        aliases=["econ", "macro"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="news",
        canonical_slash_name="news",
        command_id="navigation.news",
        entity_command_id="navigation.news.entity",
        route="/news",
        required_permission="module.news.view",
        aliases=["nw"],
        supports_entity_context=True,
        allowed_target_entity_types=None,  # any entity
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="research",
        canonical_slash_name="research",
        command_id="navigation.research",
        entity_command_id="navigation.research.entity",
        route="/research",
        required_permission="module.research.view",
        aliases=["rsch", "res"],
        supports_entity_context=True,
        allowed_target_entity_types=None,  # any entity
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="maps",
        canonical_slash_name="maps",
        command_id="navigation.maps",
        entity_command_id="navigation.maps.entity",
        route="/maps",
        required_permission="module.maps.view",
        aliases=["map"],
        supports_entity_context=True,
        allowed_target_entity_types=None,  # any entity
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="intelligence",
        canonical_slash_name="intelligence",
        command_id="navigation.intelligence",
        entity_command_id="navigation.intelligence.entity",
        route="/intelligence",
        required_permission="module.intelligence.view",
        aliases=["intel", "ai_intel"],
        supports_entity_context=True,
        allowed_target_entity_types=None,  # any entity
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="options",
        canonical_slash_name="options",
        command_id="navigation.options",
        entity_command_id="navigation.options.entity",
        route="/options",
        required_permission="module.options.view",
        aliases=["option", "opt", "opts"],
        supports_entity_context=True,
        allowed_target_entity_types=["financial_instrument", "security"],
        default_action="open",
    ),
    AtlasCommandModuleSpec(
        module_id="trading",
        canonical_slash_name="trading",
        command_id="navigation.trading",
        entity_command_id=None,
        route="/trading",
        required_permission="module.trading.view",
        aliases=["trade"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="portfolios",
        canonical_slash_name="portfolios",
        command_id="navigation.portfolios",
        entity_command_id=None,
        route="/portfolios",
        required_permission="module.portfolios.view",
        aliases=["portfolio", "port", "ports"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="risk",
        canonical_slash_name="risk",
        command_id="navigation.risk",
        entity_command_id=None,
        route="/risk",
        required_permission="module.risk.view",
        aliases=["rk"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="ai",
        canonical_slash_name="ai",
        command_id="navigation.ai",
        entity_command_id=None,
        route="/ai",
        required_permission="module.ai.view",
        aliases=["assistant"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="data",
        canonical_slash_name="data",
        command_id="navigation.data",
        entity_command_id=None,
        route="/data",
        required_permission="module.data.view",
        aliases=["dt"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="saved",
        canonical_slash_name="saved",
        command_id="navigation.saved",
        entity_command_id=None,
        route="/saved",
        required_permission="module.saved.view",
        aliases=["save", "bookmarks"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="workspaces",
        canonical_slash_name="workspaces",
        command_id="navigation.workspaces",
        entity_command_id=None,
        route="/workspaces",
        required_permission="module.workspaces.view",
        aliases=["workspace", "ws"],
        supports_entity_context=False,
    ),
    AtlasCommandModuleSpec(
        module_id="agents",
        canonical_slash_name="agents",
        command_id="navigation.agents",
        entity_command_id=None,
        route="/agents",
        required_permission="module.agents.view",
        aliases=["agent", "bot", "bots"],
        supports_entity_context=False,
    ),
]

# Utility commands
CANONICAL_UTILITY_SPECS: List[AtlasUtilityCommandSpec] = [
    AtlasUtilityCommandSpec(
        utility_id="settings",
        canonical_slash_name="settings",
        command_id="settings.global.open",
        aliases=["preferences", "config"],
        description="Open global settings dialog",
    ),
    AtlasUtilityCommandSpec(
        utility_id="search",
        canonical_slash_name="search",
        command_id="search.focus",
        aliases=["find"],
        description="Focus global search bar",
    ),
    AtlasUtilityCommandSpec(
        utility_id="clear_entity",
        canonical_slash_name="clear",
        command_id="entity.selection.clear",
        aliases=["clear_entity"],
        description="Clear currently selected entity context",
    ),
]

# Shorthand specifications
CANONICAL_SHORTHAND_SPECS: List[AtlasShorthandSpec] = [
    AtlasShorthandSpec(
        pattern_name="target_chart",
        syntax_kind="suffix",
        keyword="CHART",
        command_id="navigation.charts.entity",
        module_id="charts",
        action="open",
        target_required=True,
        allowed_target_entity_types=[
            "financial_instrument",
            "security",
            "index",
            "currency_pair",
            "cryptocurrency",
        ],
        available=True,
    ),
    AtlasShorthandSpec(
        pattern_name="target_news",
        syntax_kind="suffix",
        keyword="NEWS",
        command_id="navigation.news.entity",
        module_id="news",
        action="open",
        target_required=True,
        allowed_target_entity_types=None,
        available=True,
    ),
    AtlasShorthandSpec(
        pattern_name="target_research",
        syntax_kind="suffix",
        keyword="RESEARCH",
        command_id="navigation.research.entity",
        module_id="research",
        action="open",
        target_required=True,
        allowed_target_entity_types=None,
        available=True,
    ),
    AtlasShorthandSpec(
        pattern_name="map_target",
        syntax_kind="prefix",
        keyword="MAP",
        command_id="navigation.maps.entity",
        module_id="maps",
        action="open",
        target_required=True,
        allowed_target_entity_types=None,
        available=True,
    ),
    AtlasShorthandSpec(
        pattern_name="options_target",
        syntax_kind="prefix",
        keyword="OPTIONS",
        command_id="navigation.options.entity",
        module_id="options",
        action="open",
        target_required=True,
        allowed_target_entity_types=["financial_instrument", "security"],
        available=True,
    ),
    # Reserved unavailable shorthands
    AtlasShorthandSpec(
        pattern_name="target_fa",
        syntax_kind="suffix",
        keyword="FA",
        command_id="company.fundamentals.view",
        module_id="companies",
        action="fundamentals",
        target_required=True,
        available=False,
        unavailable_reason="Fundamental analysis is not available in ATLAS v1.",
    ),
    AtlasShorthandSpec(
        pattern_name="port_risk",
        syntax_kind="exact",
        keyword="PORT RISK",
        command_id="portfolio.risk.view",
        module_id="risk",
        action="analyze",
        target_required=False,
        available=False,
        unavailable_reason="Portfolio risk analysis is not available in ATLAS v1.",
    ),
    AtlasShorthandSpec(
        pattern_name="buy_target",
        syntax_kind="prefix",
        keyword="BUY",
        command_id="trading.order.buy",
        module_id="trading",
        action="buy",
        target_required=True,
        available=False,
        unavailable_reason="Trading execution and order placement are not supported via commands.",
    ),
    AtlasShorthandSpec(
        pattern_name="sell_target",
        syntax_kind="prefix",
        keyword="SELL",
        command_id="trading.order.sell",
        module_id="trading",
        action="sell",
        target_required=True,
        available=False,
        unavailable_reason="Trading execution and order placement are not supported via commands.",
    ),
]


class AtlasCommandSpecRegistry:
    """Registry providing lookup and collision validation for command specs."""

    def __init__(
        self,
        module_specs: Optional[List[AtlasCommandModuleSpec]] = None,
        utility_specs: Optional[List[AtlasUtilityCommandSpec]] = None,
        shorthand_specs: Optional[List[AtlasShorthandSpec]] = None,
    ) -> None:
        self.module_specs = (
            module_specs if module_specs is not None else list(CANONICAL_MODULE_SPECS)
        )
        self.utility_specs = (
            utility_specs if utility_specs is not None else list(CANONICAL_UTILITY_SPECS)
        )
        self.shorthand_specs = (
            shorthand_specs if shorthand_specs is not None else list(CANONICAL_SHORTHAND_SPECS)
        )

        self.modules_by_id: Dict[str, AtlasCommandModuleSpec] = {}
        self.module_alias_map: Dict[str, AtlasCommandModuleSpec] = {}
        self.utilities_by_id: Dict[str, AtlasUtilityCommandSpec] = {}
        self.utility_alias_map: Dict[str, AtlasUtilityCommandSpec] = {}

        self._initialize()

    def _initialize(self) -> None:
        seen_slash_keys: Dict[str, str] = {}

        # Register modules
        for mod in self.module_specs:
            self.modules_by_id[mod.module_id] = mod

            canonical_key = mod.canonical_slash_name.lower()
            if canonical_key in seen_slash_keys:
                raise ValueError(
                    f"Collision detected: '{canonical_key}' already registered "
                    f"by {seen_slash_keys[canonical_key]}"
                )
            seen_slash_keys[canonical_key] = f"module:{mod.module_id}"
            self.module_alias_map[canonical_key] = mod

            for alias in mod.aliases:
                alias_key = alias.lower()
                if alias_key in seen_slash_keys:
                    raise ValueError(
                        f"Collision detected for alias '{alias_key}': registered "
                        f"by {seen_slash_keys[alias_key]} and module:{mod.module_id}"
                    )
                seen_slash_keys[alias_key] = f"module:{mod.module_id}"
                self.module_alias_map[alias_key] = mod

        # Register utilities
        for util in self.utility_specs:
            self.utilities_by_id[util.utility_id] = util

            canonical_key = util.canonical_slash_name.lower()
            if canonical_key in seen_slash_keys:
                raise ValueError(
                    f"Collision detected: '{canonical_key}' already registered "
                    f"by {seen_slash_keys[canonical_key]}"
                )
            seen_slash_keys[canonical_key] = f"utility:{util.utility_id}"
            self.utility_alias_map[canonical_key] = util

            for alias in util.aliases:
                alias_key = alias.lower()
                if alias_key in seen_slash_keys:
                    raise ValueError(
                        f"Collision detected for alias '{alias_key}': registered "
                        f"by {seen_slash_keys[alias_key]} and utility:{util.utility_id}"
                    )
                seen_slash_keys[alias_key] = f"utility:{util.utility_id}"
                self.utility_alias_map[alias_key] = util

    def resolve_module_by_name_or_alias(self, name: str) -> Optional[AtlasCommandModuleSpec]:
        """Resolves a module spec by its canonical name or exact registered alias."""
        return self.module_alias_map.get(name.strip().lower())

    def resolve_utility_by_name_or_alias(self, name: str) -> Optional[AtlasUtilityCommandSpec]:
        """Resolves a utility spec by its canonical name or exact registered alias."""
        return self.utility_alias_map.get(name.strip().lower())

    def find_shorthand_by_suffix(self, keyword: str) -> Optional[AtlasShorthandSpec]:
        """Looks up a suffix shorthand spec by keyword (e.g. 'CHART', 'NEWS')."""
        upper_kw = keyword.strip().upper()
        for spec in self.shorthand_specs:
            if spec.syntax_kind == "suffix" and spec.keyword.upper() == upper_kw:
                return spec
        return None

    def find_shorthand_by_prefix(self, keyword: str) -> Optional[AtlasShorthandSpec]:
        """Looks up a prefix shorthand spec by keyword (e.g. 'MAP', 'OPTIONS')."""
        upper_kw = keyword.strip().upper()
        for spec in self.shorthand_specs:
            if spec.syntax_kind == "prefix" and spec.keyword.upper() == upper_kw:
                return spec
        return None

    def find_shorthand_exact(self, text: str) -> Optional[AtlasShorthandSpec]:
        """Looks up an exact shorthand spec (e.g. 'PORT RISK')."""
        upper_text = " ".join(text.strip().upper().split())
        for spec in self.shorthand_specs:
            if spec.syntax_kind == "exact" and spec.keyword.upper() == upper_text:
                return spec
        return None


# Global immutable instance verified at import time
COMMAND_SPEC_REGISTRY = AtlasCommandSpecRegistry()
