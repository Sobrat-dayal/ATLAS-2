"""Chart action adapter for ATLAS AI Financial Action Engine (Stage 128, Parts XXIII - XXVIII)."""

from __future__ import annotations

import copy
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from atlas.ai.actions.adapters.base import ActionAdapter
from atlas.ai.actions.domain import (
    AiActionClassification,
    AiActionDiff,
    AiActionType,
    AiFinancialAction,
    AiFinancialActionPreview,
    ApprovalPolicy,
    ReversibilityPolicy,
)
from atlas.ai.actions.errors import (
    AiActionParameterUnsupportedError,
    AiActionResourceConflictError,
    AiActionTargetNotFoundError,
    AiActionValidationFailedError,
)

VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M"}
VALID_CHART_TYPES = {"candlestick", "line", "area", "bar", "heikin_ashi"}
SUPPORTED_INDICATORS = {
    "SMA": {"required": ["period"], "min_period": 1, "max_period": 500},
    "EMA": {"required": ["period"], "min_period": 1, "max_period": 500},
    "RSI": {"required": ["period"], "min_period": 2, "max_period": 100},
    "MACD": {"required": ["fast_period", "slow_period", "signal_period"], "min_period": 1},
    "BOLL": {"required": ["period", "std_dev"], "min_period": 2},
    "VOL": {"required": []},
    "ATR": {"required": ["period"], "min_period": 1},
    "VWAP": {"required": []},
}


class MockChartStore:
    """In-memory stateful chart storage for testing and session management."""

    def __init__(self) -> None:
        self._charts: Dict[str, Dict[str, Any]] = {}
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        # Pre-seed Fixture A chart
        self.seed_chart(
            chart_id="chart_fixture_a",
            instrument_id="TEST_A",
            chart_type="candlestick",
            interval="1D",
            indicators=[],
            comparisons=[],
            user_id="test_user_stage128",
            tenant_id="default_tenant",
        )

    def seed_chart(
        self,
        chart_id: str,
        instrument_id: str,
        chart_type: str = "candlestick",
        interval: str = "1D",
        indicators: Optional[List[Dict[str, Any]]] = None,
        comparisons: Optional[List[str]] = None,
        user_id: str = "test_user_stage128",
        tenant_id: str = "default_tenant",
    ) -> None:
        state = {
            "chart_id": chart_id,
            "instrument_id": instrument_id,
            "chart_type": chart_type,
            "interval": interval,
            "indicators": indicators or [],
            "comparisons": comparisons or [],
            "user_id": user_id,
            "tenant_id": tenant_id,
            "revision": f"rev_{chart_id}_1",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._charts[chart_id] = state
        self._history[chart_id] = [copy.deepcopy(state)]

    def get_chart(self, chart_id: str) -> Optional[Dict[str, Any]]:
        return self._charts.get(chart_id)

    def update_chart(self, chart_id: str, new_state: Dict[str, Any]) -> str:
        current = self._charts.get(chart_id)
        if not current:
            raise AiActionTargetNotFoundError("chart_config", chart_id)

        # Generate new revision
        rev_count = len(self._history.get(chart_id, [])) + 1
        new_rev = f"rev_{chart_id}_{rev_count}"
        updated = copy.deepcopy(new_state)
        updated["revision"] = new_rev
        updated["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._charts[chart_id] = updated
        self._history.setdefault(chart_id, []).append(copy.deepcopy(updated))
        return new_rev

    def restore_revision(self, chart_id: str, target_revision: str) -> str:
        history = self._history.get(chart_id, [])
        matched = next((item for item in history if item["revision"] == target_revision), None)
        if not matched:
            raise AiActionValidationFailedError(
                f"Cannot restore chart '{chart_id}' to revision '{target_revision}': snapshot not found."
            )
        return self.update_chart(chart_id, matched)


_CHART_STORE = MockChartStore()


def get_chart_store() -> MockChartStore:
    return _CHART_STORE


class ChartActionAdapter(ActionAdapter):
    """Handles all chart configuration actions."""

    def __init__(self, action_type_val: AiActionType = AiActionType.CHART_ADD_INDICATOR) -> None:
        self._action_type = action_type_val

    @property
    def action_type(self) -> AiActionType:
        return self._action_type

    @property
    def target_module(self) -> str:
        return "charts"

    @property
    def classification(self) -> AiActionClassification:
        if self._action_type in (
            AiActionType.CHART_SAVE_CONFIGURATION,
            AiActionType.CHART_RESTORE_CONFIGURATION,
        ):
            return AiActionClassification.PERSISTENT_CONFIGURATION_CHANGE
        return AiActionClassification.SESSION_UI_CHANGE

    @property
    def default_approval_policy(self) -> ApprovalPolicy:
        if self._action_type in (
            AiActionType.CHART_SAVE_CONFIGURATION,
            AiActionType.CHART_RESTORE_CONFIGURATION,
        ):
            return ApprovalPolicy.USER_PREVIEW_CONFIRM
        return ApprovalPolicy.USER_PREVIEW_CONFIRM

    @property
    def reversibility_policy(self) -> ReversibilityPolicy:
        return ReversibilityPolicy.REVERSIBLE

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "chart_id": {"type": "string"},
                "instrument_id": {"type": "string"},
                "interval": {"type": "string", "enum": list(VALID_INTERVALS)},
                "chart_type": {"type": "string", "enum": list(VALID_CHART_TYPES)},
                "indicator": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "period": {"type": "integer"},
                        "fast_period": {"type": "integer"},
                        "slow_period": {"type": "integer"},
                        "signal_period": {"type": "integer"},
                        "std_dev": {"type": "number"},
                    },
                },
                "indicators": {"type": "array"},
                "comparison_instrument_id": {"type": "string"},
            },
            "required": ["chart_id"],
        }

    def validate_parameters(self, proposed_args: Dict[str, Any]) -> Dict[str, Any]:
        if not proposed_args.get("chart_id"):
            raise AiActionValidationFailedError("Missing required parameter 'chart_id'")

        # Interval check
        if "interval" in proposed_args:
            inv = proposed_args["interval"]
            if inv not in VALID_INTERVALS:
                raise AiActionParameterUnsupportedError("interval", inv, list(VALID_INTERVALS))

        # Chart type check
        if "chart_type" in proposed_args:
            ct = proposed_args["chart_type"]
            if ct not in VALID_CHART_TYPES:
                raise AiActionParameterUnsupportedError("chart_type", ct, list(VALID_CHART_TYPES))

        # Indicator validation
        indicators_to_check = []
        if "indicator" in proposed_args and proposed_args["indicator"]:
            indicators_to_check.append(proposed_args["indicator"])
        if "indicators" in proposed_args and isinstance(proposed_args["indicators"], list):
            indicators_to_check.extend(proposed_args["indicators"])

        for ind in indicators_to_check:
            ind_type = ind.get("type", "").upper()
            if ind_type not in SUPPORTED_INDICATORS:
                raise AiActionParameterUnsupportedError(
                    "indicator.type",
                    ind_type,
                    list(SUPPORTED_INDICATORS.keys()),
                )
            spec = SUPPORTED_INDICATORS[ind_type]
            for req in spec.get("required", []):
                if req not in ind:
                    raise AiActionValidationFailedError(
                        f"Indicator '{ind_type}' missing required parameter '{req}'"
                    )
            if "period" in ind and ind["period"] < spec.get("min_period", 1):
                raise AiActionValidationFailedError(
                    f"Indicator '{ind_type}' period {ind['period']} is below minimum {spec.get('min_period', 1)}"
                )
            if ind_type == "MACD":
                if ind.get("fast_period", 12) >= ind.get("slow_period", 26):
                    raise AiActionValidationFailedError(
                        "MACD fast_period must be strictly less than slow_period"
                    )

        return proposed_args

    async def get_current_state(
        self,
        resource_id: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[Dict[str, Any], str]:
        chart = get_chart_store().get_chart(resource_id)
        if not chart:
            # Create a default session chart if not exists
            get_chart_store().seed_chart(
                chart_id=resource_id,
                instrument_id="TEST_A",
                user_id=actor_user_id,
                tenant_id=tenant_id,
            )
            chart = get_chart_store().get_chart(resource_id)
        return copy.deepcopy(chart), chart["revision"]

    async def generate_preview(
        self,
        action_id: str,
        resource_id: str,
        current_state: Dict[str, Any],
        current_revision: str,
        proposed_args: Dict[str, Any],
        actor_user_id: str,
        tenant_id: str,
    ) -> AiFinancialActionPreview:
        proposed_state = copy.deepcopy(current_state)
        diffs: List[AiActionDiff] = []
        assumptions: List[str] = [
            f"Target Chart ID: {resource_id}",
            f"Active Instrument: {current_state.get('instrument_id', 'UNKNOWN')}",
        ]

        if "instrument_id" in proposed_args and proposed_args["instrument_id"] != current_state.get(
            "instrument_id"
        ):
            diffs.append(
                AiActionDiff(
                    field_path="instrument_id",
                    before_value=current_state.get("instrument_id"),
                    after_value=proposed_args["instrument_id"],
                    change_type="MODIFY",
                )
            )
            proposed_state["instrument_id"] = proposed_args["instrument_id"]

        if "interval" in proposed_args and proposed_args["interval"] != current_state.get(
            "interval"
        ):
            diffs.append(
                AiActionDiff(
                    field_path="interval",
                    before_value=current_state.get("interval"),
                    after_value=proposed_args["interval"],
                    change_type="MODIFY",
                )
            )
            proposed_state["interval"] = proposed_args["interval"]

        if "chart_type" in proposed_args and proposed_args["chart_type"] != current_state.get(
            "chart_type"
        ):
            diffs.append(
                AiActionDiff(
                    field_path="chart_type",
                    before_value=current_state.get("chart_type"),
                    after_value=proposed_args["chart_type"],
                    change_type="MODIFY",
                )
            )
            proposed_state["chart_type"] = proposed_args["chart_type"]

        # Adding indicators
        new_indicators = list(proposed_state.get("indicators", []))
        if "indicator" in proposed_args and proposed_args["indicator"]:
            ind = proposed_args["indicator"]
            new_indicators.append(ind)
            diffs.append(
                AiActionDiff(
                    field_path="indicators",
                    before_value=current_state.get("indicators", []),
                    after_value=new_indicators,
                    change_type="ADD",
                    financial_impact_if_computable=f"Added indicator {ind.get('type')}({ind.get('period', '')})",
                )
            )
            assumptions.append(
                f"Technical calculation: {ind.get('type')} over {ind.get('period', '')} bars."
            )

        if "indicators" in proposed_args and isinstance(proposed_args["indicators"], list):
            for ind in proposed_args["indicators"]:
                new_indicators.append(ind)
            diffs.append(
                AiActionDiff(
                    field_path="indicators",
                    before_value=current_state.get("indicators", []),
                    after_value=new_indicators,
                    change_type="ADD",
                    financial_impact_if_computable=f"Added {len(proposed_args['indicators'])} indicators",
                )
            )
        proposed_state["indicators"] = new_indicators

        # Comparisons
        if "comparison_instrument_id" in proposed_args:
            comp = proposed_args["comparison_instrument_id"]
            current_comps = list(proposed_state.get("comparisons", []))
            if comp not in current_comps:
                current_comps.append(comp)
                diffs.append(
                    AiActionDiff(
                        field_path="comparisons",
                        before_value=current_state.get("comparisons", []),
                        after_value=current_comps,
                        change_type="ADD",
                        financial_impact_if_computable=f"Normalized % comparison with {comp}",
                    )
                )
                proposed_state["comparisons"] = current_comps
                assumptions.append("Normalized starting value to 100% at earliest common bar.")

        # Compute preview hash
        hash_input = json.dumps(
            {
                "resource_id": resource_id,
                "revision": current_revision,
                "proposed": proposed_args,
                "diffs": [d.to_dict() for d in diffs],
            },
            sort_keys=True,
            default=str,
        )
        preview_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        return AiFinancialActionPreview(
            preview_id=f"prev_{uuid.uuid4().hex[:12]}",
            action_id=action_id,
            target_resource_type="chart_config",
            target_resource_id=resource_id,
            current_state=current_state,
            proposed_state=proposed_state,
            diffs=diffs,
            financial_assumptions=assumptions,
            estimated_cost="NONE",
            approval_policy=self.default_approval_policy,
            reversibility_policy=self.reversibility_policy,
            preview_hash=preview_hash,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )

    async def execute(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[Dict[str, Any], str, List[AiActionDiff]]:
        store = get_chart_store()
        current = store.get_chart(action.target_resource_id)
        if not current:
            raise AiActionTargetNotFoundError("chart_config", action.target_resource_id)

        # Optimistic concurrency check
        if (
            action.expected_resource_revision
            and current["revision"] != action.expected_resource_revision
        ):
            raise AiActionResourceConflictError(
                action.target_resource_id,
                action.expected_resource_revision,
                current["revision"],
            )

        new_state = copy.deepcopy(current)
        args = action.proposed_arguments

        diffs: List[AiActionDiff] = []
        if "instrument_id" in args:
            new_state["instrument_id"] = args["instrument_id"]
        if "interval" in args:
            new_state["interval"] = args["interval"]
        if "chart_type" in args:
            new_state["chart_type"] = args["chart_type"]

        if "indicator" in args and args["indicator"]:
            ind = args["indicator"]
            new_state.setdefault("indicators", []).append(ind)
            diffs.append(
                AiActionDiff(
                    field_path="indicators",
                    before_value=current.get("indicators", []),
                    after_value=new_state["indicators"],
                    change_type="ADD",
                )
            )

        if "indicators" in args and isinstance(args["indicators"], list):
            for ind in args["indicators"]:
                new_state.setdefault("indicators", []).append(ind)
            diffs.append(
                AiActionDiff(
                    field_path="indicators",
                    before_value=current.get("indicators", []),
                    after_value=new_state["indicators"],
                    change_type="ADD",
                )
            )

        if "comparison_instrument_id" in args:
            comp = args["comparison_instrument_id"]
            if comp not in new_state.setdefault("comparisons", []):
                new_state["comparisons"].append(comp)

        new_rev = store.update_chart(action.target_resource_id, new_state)
        return new_state, new_rev, diffs

    async def undo(
        self,
        action: AiFinancialAction,
        receipt: Any,
        actor_user_id: str,
        tenant_id: str,
    ) -> str:
        store = get_chart_store()
        before_rev = getattr(receipt, "target_revision_before", None)
        if not before_rev:
            raise AiActionValidationFailedError(
                "Cannot undo: missing target_revision_before in receipt"
            )
        return store.restore_revision(action.target_resource_id, before_rev)
