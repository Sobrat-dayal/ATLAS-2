"""Action capability registry and discovery for ATLAS AI Financial Actions (Stage 128, Part XIII)."""

from __future__ import annotations

from typing import Dict, List

from atlas.ai.actions.adapters.base import ActionAdapter
from atlas.ai.actions.adapters.charts import ChartActionAdapter
from atlas.ai.actions.adapters.portfolios import PortfolioActionAdapter
from atlas.ai.actions.adapters.risk import RiskActionAdapter
from atlas.ai.actions.adapters.screeners import ScreenerActionAdapter
from atlas.ai.actions.domain import (
    AiActionType,
)
from atlas.ai.actions.errors import AiActionUnsupportedError
from atlas.ai.actions.schemas import ActionCapabilityDTO


class AtlasActionRegistry:
    """Singleton registry indexing all supported financial action types and their adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[AiActionType, ActionAdapter] = {}
        self._descriptions: Dict[AiActionType, str] = {}
        self._initialize_default_adapters()

    def _initialize_default_adapters(self) -> None:
        # Chart adapters
        chart_actions = [
            (AiActionType.CHART_SELECT_INSTRUMENT, "Select active instrument on chart panel"),
            (
                AiActionType.CHART_SET_TIMEFRAME,
                "Set chart interval timeframe (e.g. 1m, 1h, 1D, 1W)",
            ),
            (AiActionType.CHART_SET_DATE_RANGE, "Set custom start and end date range"),
            (
                AiActionType.CHART_SET_TYPE,
                "Change chart visualization type (candlestick, line, etc.)",
            ),
            (
                AiActionType.CHART_ADD_INDICATOR,
                "Add technical indicator (SMA, EMA, RSI, MACD, etc.)",
            ),
            (AiActionType.CHART_REMOVE_INDICATOR, "Remove active technical indicator"),
            (AiActionType.CHART_UPDATE_INDICATOR, "Modify indicator parameters"),
            (AiActionType.CHART_ADD_COMPARISON, "Add normalized percentage performance comparison"),
            (AiActionType.CHART_REMOVE_COMPARISON, "Remove comparison instrument"),
            (AiActionType.CHART_SAVE_CONFIGURATION, "Persist current chart layout and settings"),
            (
                AiActionType.CHART_RESTORE_CONFIGURATION,
                "Restore prior chart configuration revision",
            ),
        ]
        for atype, desc in chart_actions:
            self.register(atype, ChartActionAdapter(atype), desc)

        # Screener adapters
        screener_actions = [
            (AiActionType.SCREENER_CREATE_DRAFT, "Create a new financial screener query draft"),
            (AiActionType.SCREENER_ADD_FILTER, "Add typed financial metric filter condition"),
            (AiActionType.SCREENER_UPDATE_FILTER, "Update existing filter threshold or operator"),
            (AiActionType.SCREENER_REMOVE_FILTER, "Remove filter constraint"),
            (AiActionType.SCREENER_SET_UNIVERSE, "Set security universe (e.g. NIFTY500, SP500)"),
            (AiActionType.SCREENER_SET_SORT, "Set sorting metric and order"),
            (AiActionType.SCREENER_SET_COLUMNS, "Select output result columns"),
            (AiActionType.SCREENER_PREVIEW, "Preview screener rules and estimated matches"),
            (AiActionType.SCREENER_EXECUTE, "Execute authorized screener query across universe"),
            (AiActionType.SCREENER_SAVE, "Save screener configuration as named saved item"),
            (AiActionType.SCREENER_UPDATE_SAVED, "Update saved screener configuration"),
            (AiActionType.SCREENER_RESTORE_REVISION, "Restore earlier saved screener revision"),
        ]
        for atype, desc in screener_actions:
            self.register(atype, ScreenerActionAdapter(atype), desc)

        # Portfolio adapters (Hypothetical & Analytical Only!)
        portfolio_actions = [
            (
                AiActionType.PORTFOLIO_ANALYZE_ALLOCATION,
                "Analyze current portfolio asset/sector allocation",
            ),
            (
                AiActionType.PORTFOLIO_PROPOSE_TARGETS,
                "Propose hypothetical target allocation weights",
            ),
            (
                AiActionType.PORTFOLIO_CALCULATE_DELTA,
                "Calculate allocation and notional target deltas",
            ),
            (
                AiActionType.PORTFOLIO_CREATE_SCENARIO_DRAFT,
                "Create non-executing portfolio scenario draft",
            ),
            (
                AiActionType.PORTFOLIO_COMPARE_ALLOCATIONS,
                "Compare current allocation with benchmark or scenario",
            ),
            (
                AiActionType.PORTFOLIO_SAVE_SCENARIO_DRAFT,
                "Save hypothetical scenario draft for review",
            ),
        ]
        for atype, desc in portfolio_actions:
            self.register(atype, PortfolioActionAdapter(atype), desc)

        # Risk adapters
        risk_actions = [
            (
                AiActionType.RISK_GET_MODELS,
                "Discover supported institutional risk calculation models",
            ),
            (AiActionType.RISK_VALIDATE_PARAMETERS, "Validate parameters for requested risk model"),
            (
                AiActionType.RISK_PREVIEW_RUN,
                "Preview risk calculation inputs, horizon, and confidence",
            ),
            (AiActionType.RISK_START_RUN, "Launch real risk calculation job on worker compute"),
            (AiActionType.RISK_GET_RUN_STATUS, "Poll status of running risk computation job"),
            (AiActionType.RISK_CANCEL_RUN, "Cancel running risk calculation job"),
            (
                AiActionType.RISK_GET_RUN_RESULTS,
                "Retrieve verified metrics from completed risk run",
            ),
            (AiActionType.RISK_COMPARE_RUNS, "Compare results between two immutable risk runs"),
            (
                AiActionType.RISK_RUN_STRESS_SCENARIO,
                "Run hypothetical equity shock and rate shift stress test",
            ),
        ]
        for atype, desc in risk_actions:
            self.register(atype, RiskActionAdapter(atype), desc)

    def register(self, action_type: AiActionType, adapter: ActionAdapter, description: str) -> None:
        self._adapters[action_type] = adapter
        self._descriptions[action_type] = description

    def get_adapter(self, action_type: AiActionType | str) -> ActionAdapter:
        if isinstance(action_type, str):
            try:
                action_type = AiActionType(action_type)
            except ValueError:
                raise AiActionUnsupportedError(action_type)
        adapter = self._adapters.get(action_type)
        if not adapter:
            raise AiActionUnsupportedError(action_type.value)
        return adapter

    def get_capabilities(self) -> List[ActionCapabilityDTO]:
        caps: List[ActionCapabilityDTO] = []
        for atype, adapter in self._adapters.items():
            caps.append(
                ActionCapabilityDTO(
                    action_type=atype.value,
                    action_version="1.0.0",
                    target_module=adapter.target_module,
                    classification=adapter.classification.value,
                    approval_policy=adapter.default_approval_policy.value,
                    reversibility_policy=adapter.reversibility_policy.value,
                    description=self._descriptions.get(atype, ""),
                    parameters_schema=adapter.get_parameters_schema(),
                )
            )
        return caps


_ACTION_REGISTRY = AtlasActionRegistry()


def get_action_registry() -> AtlasActionRegistry:
    return _ACTION_REGISTRY
