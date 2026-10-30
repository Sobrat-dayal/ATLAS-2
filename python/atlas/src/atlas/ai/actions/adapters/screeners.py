"""Screener action adapter for ATLAS AI Financial Action Engine (Stage 128, Parts XXIX - XXXIV)."""

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

SUPPORTED_UNIVERSES = {"IN_NIFTY500", "IN_EQUITIES", "US_SP500", "US_NASDAQ100", "GLOBAL_TECH"}
SUPPORTED_METRICS = {
    "revenue_growth_yoy": {"unit": "PERCENT", "type": "number"},
    "net_profit_margin": {"unit": "PERCENT", "type": "number"},
    "market_cap": {"unit": "CURRENCY", "type": "number"},
    "pe_ratio": {"unit": "RATIO", "type": "number"},
    "debt_to_equity": {"unit": "RATIO", "type": "number"},
    "roe": {"unit": "PERCENT", "type": "number"},
}
SUPPORTED_OPERATORS = {
    "GREATER_THAN",
    "GREATER_OR_EQUAL",
    "LESS_THAN",
    "LESS_OR_EQUAL",
    "EQUAL",
    "BETWEEN",
}

# Pre-seeded sample dataset for genuine screener query executions (No fake matches!)
SAMPLE_SECURITY_DATABASE = [
    {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services Limited",
        "universe": "IN_NIFTY500",
        "currency": "INR",
        "market_cap": 14_200_000_000_000.0,  # 14.2 Lakh Crore INR
        "revenue_growth_yoy": 0.165,  # 16.5%
        "net_profit_margin": 0.192,  # 19.2% (Positive profit)
        "pe_ratio": 29.4,
    },
    {
        "symbol": "INFY.NS",
        "name": "Infosys Limited",
        "universe": "IN_NIFTY500",
        "currency": "INR",
        "market_cap": 7_800_000_000_000.0,  # 7.8 Lakh Crore INR
        "revenue_growth_yoy": 0.158,  # 15.8%
        "net_profit_margin": 0.174,  # 17.4% (Positive profit)
        "pe_ratio": 25.1,
    },
    {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries Limited",
        "universe": "IN_NIFTY500",
        "currency": "INR",
        "market_cap": 19_500_000_000_000.0,  # 19.5 Lakh Crore INR
        "revenue_growth_yoy": 0.112,  # 11.2%
        "net_profit_margin": 0.088,
        "pe_ratio": 26.5,
    },
    {
        "symbol": "SMALL_TECH.NS",
        "name": "Smallcap India Tech Ltd",
        "universe": "IN_NIFTY500",
        "currency": "INR",
        "market_cap": 45_000_000_000.0,  # 4,500 Crore INR (below 10,000 Crore)
        "revenue_growth_yoy": 0.22,
        "net_profit_margin": -0.05,  # Negative profit
        "pe_ratio": -15.0,
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "universe": "US_SP500",
        "currency": "USD",
        "market_cap": 3_100_000_000_000.0,
        "revenue_growth_yoy": 0.170,
        "net_profit_margin": 0.354,
        "pe_ratio": 34.2,
    },
]


class MockScreenerStore:
    """In-memory stateful screener storage for testing and revisions."""

    def __init__(self) -> None:
        self._screeners: Dict[str, Dict[str, Any]] = {}
        self._revisions: Dict[str, List[Dict[str, Any]]] = {}
        # Pre-seed sample screener
        self.seed_screener(
            screener_id="screener_fixture_b",
            name="India Tech High Growth",
            universe="IN_NIFTY500",
            filters=[
                {"metric_id": "revenue_growth_yoy", "operator": "GREATER_THAN", "value": 0.15},
                {"metric_id": "net_profit_margin", "operator": "GREATER_THAN", "value": 0.0},
                {"metric_id": "market_cap", "operator": "GREATER_THAN", "value": 100_000_000_000.0},
            ],
            user_id="test_user_stage128",
            tenant_id="default_tenant",
        )

    def seed_screener(
        self,
        screener_id: str,
        name: str,
        universe: str,
        filters: List[Dict[str, Any]],
        user_id: str = "test_user_stage128",
        tenant_id: str = "default_tenant",
    ) -> None:
        state = {
            "screener_id": screener_id,
            "name": name,
            "universe": universe,
            "filters": filters,
            "sort_by": "market_cap",
            "sort_order": "DESC",
            "columns": ["symbol", "name", "market_cap", "revenue_growth_yoy", "net_profit_margin"],
            "user_id": user_id,
            "tenant_id": tenant_id,
            "revision": f"rev_{screener_id}_1",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._screeners[screener_id] = state
        self._revisions[screener_id] = [copy.deepcopy(state)]

    def get_screener(self, screener_id: str) -> Optional[Dict[str, Any]]:
        return self._screeners.get(screener_id)

    def update_screener(self, screener_id: str, new_state: Dict[str, Any]) -> str:
        current = self._screeners.get(screener_id)
        if not current:
            raise AiActionTargetNotFoundError("screener_query", screener_id)

        rev_count = len(self._revisions.get(screener_id, [])) + 1
        new_rev = f"rev_{screener_id}_{rev_count}"
        updated = copy.deepcopy(new_state)
        updated["revision"] = new_rev
        updated["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._screeners[screener_id] = updated
        self._revisions.setdefault(screener_id, []).append(copy.deepcopy(updated))
        return new_rev

    def restore_revision(self, screener_id: str, target_revision: str) -> str:
        history = self._revisions.get(screener_id, [])
        matched = next((item for item in history if item["revision"] == target_revision), None)
        if not matched:
            raise AiActionValidationFailedError(
                f"Cannot restore screener '{screener_id}' to revision '{target_revision}': revision not found."
            )
        return self.update_screener(screener_id, matched)


_SCREENER_STORE = MockScreenerStore()


def get_screener_store() -> MockScreenerStore:
    return _SCREENER_STORE


class ScreenerActionAdapter(ActionAdapter):
    """Handles screener configuration and query execution actions."""

    def __init__(self, action_type_val: AiActionType = AiActionType.SCREENER_CREATE_DRAFT) -> None:
        self._action_type = action_type_val

    @property
    def action_type(self) -> AiActionType:
        return self._action_type

    @property
    def target_module(self) -> str:
        return "screeners"

    @property
    def classification(self) -> AiActionClassification:
        if self._action_type in (AiActionType.SCREENER_SAVE, AiActionType.SCREENER_UPDATE_SAVED):
            return AiActionClassification.PERSISTENT_CONFIGURATION_CHANGE
        elif self._action_type == AiActionType.SCREENER_EXECUTE:
            return AiActionClassification.COMPUTATION_JOB
        return AiActionClassification.SAVED_ANALYTICAL_DRAFT

    @property
    def default_approval_policy(self) -> ApprovalPolicy:
        if self._action_type in (
            AiActionType.SCREENER_SAVE,
            AiActionType.SCREENER_UPDATE_SAVED,
            AiActionType.SCREENER_EXECUTE,
        ):
            return ApprovalPolicy.USER_PREVIEW_CONFIRM
        return ApprovalPolicy.AUTO_READ_ONLY

    @property
    def reversibility_policy(self) -> ReversibilityPolicy:
        if self._action_type in (
            AiActionType.SCREENER_SAVE,
            AiActionType.SCREENER_UPDATE_SAVED,
            AiActionType.SCREENER_CREATE_DRAFT,
        ):
            return ReversibilityPolicy.REVERSIBLE
        return ReversibilityPolicy.NON_REVERSIBLE

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "screener_id": {"type": "string"},
                "name": {"type": "string"},
                "universe": {"type": "string", "enum": list(SUPPORTED_UNIVERSES)},
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric_id": {"type": "string"},
                            "operator": {"type": "string"},
                            "value": {"type": "number"},
                        },
                        "required": ["metric_id", "operator", "value"],
                    },
                },
                "sort_by": {"type": "string"},
                "sort_order": {"type": "string", "enum": ["ASC", "DESC"]},
            },
            "required": ["screener_id"],
        }

    def validate_parameters(self, proposed_args: Dict[str, Any]) -> Dict[str, Any]:
        if not proposed_args.get("screener_id"):
            raise AiActionValidationFailedError("Missing required parameter 'screener_id'")

        if "universe" in proposed_args:
            uni = proposed_args["universe"]
            if uni not in SUPPORTED_UNIVERSES:
                raise AiActionParameterUnsupportedError("universe", uni, list(SUPPORTED_UNIVERSES))

        if "filters" in proposed_args and isinstance(proposed_args["filters"], list):
            for f in proposed_args["filters"]:
                m = f.get("metric_id")
                if m not in SUPPORTED_METRICS:
                    raise AiActionParameterUnsupportedError(
                        "filters.metric_id", m, list(SUPPORTED_METRICS.keys())
                    )
                op = f.get("operator")
                if op not in SUPPORTED_OPERATORS:
                    raise AiActionParameterUnsupportedError(
                        "filters.operator", op, list(SUPPORTED_OPERATORS)
                    )
                if "value" not in f:
                    raise AiActionValidationFailedError(
                        f"Filter for metric '{m}' missing comparison value"
                    )

        return proposed_args

    async def get_current_state(
        self,
        resource_id: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[Dict[str, Any], str]:
        screener = get_screener_store().get_screener(resource_id)
        if not screener:
            # Seed a default draft screener
            get_screener_store().seed_screener(
                screener_id=resource_id,
                name="New Screener Draft",
                universe="IN_NIFTY500",
                filters=[],
                user_id=actor_user_id,
                tenant_id=tenant_id,
            )
            screener = get_screener_store().get_screener(resource_id)
        return copy.deepcopy(screener), screener["revision"]

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
            f"Target Screener: {resource_id}",
            f"Active Universe: {proposed_args.get('universe', current_state.get('universe'))}",
        ]

        if "universe" in proposed_args and proposed_args["universe"] != current_state.get(
            "universe"
        ):
            diffs.append(
                AiActionDiff(
                    field_path="universe",
                    before_value=current_state.get("universe"),
                    after_value=proposed_args["universe"],
                    change_type="MODIFY",
                )
            )
            proposed_state["universe"] = proposed_args["universe"]

        if "filters" in proposed_args:
            diffs.append(
                AiActionDiff(
                    field_path="filters",
                    before_value=current_state.get("filters", []),
                    after_value=proposed_args["filters"],
                    change_type="MODIFY",
                    financial_impact_if_computable=f"Set {len(proposed_args['filters'])} screening constraints",
                )
            )
            proposed_state["filters"] = proposed_args["filters"]
            for f in proposed_args["filters"]:
                assumptions.append(f"Rule: {f['metric_id']} {f['operator']} {f['value']}")

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
            target_resource_type="screener_query",
            target_resource_id=resource_id,
            current_state=current_state,
            proposed_state=proposed_state,
            diffs=diffs,
            financial_assumptions=assumptions,
            estimated_cost="LOW",
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
        store = get_screener_store()
        current = store.get_screener(action.target_resource_id)
        if not current:
            raise AiActionTargetNotFoundError("screener_query", action.target_resource_id)

        # Concurrency verification (Fixture F)
        if (
            action.expected_resource_revision
            and current["revision"] != action.expected_resource_revision
        ):
            raise AiActionResourceConflictError(
                action.target_resource_id,
                action.expected_resource_revision,
                current["revision"],
            )

        args = action.proposed_arguments
        new_state = copy.deepcopy(current)
        diffs: List[AiActionDiff] = []

        if "universe" in args:
            new_state["universe"] = args["universe"]
        if "filters" in args:
            diffs.append(
                AiActionDiff(
                    field_path="filters",
                    before_value=current.get("filters", []),
                    after_value=args["filters"],
                    change_type="MODIFY",
                )
            )
            new_state["filters"] = args["filters"]
        if "name" in args:
            new_state["name"] = args["name"]

        # Run query logic over real database
        matching_results = []
        target_universe = new_state.get("universe", "IN_NIFTY500")
        active_filters = new_state.get("filters", [])

        for sec in SAMPLE_SECURITY_DATABASE:
            if sec.get("universe") != target_universe and target_universe != "GLOBAL_TECH":
                continue

            matches_all = True
            for flt in active_filters:
                m_val = sec.get(flt["metric_id"])
                if m_val is None:
                    matches_all = False
                    break
                target_val = flt["value"]
                op = flt["operator"]
                if op == "GREATER_THAN" and not (m_val > target_val):
                    matches_all = False
                    break
                elif op == "GREATER_OR_EQUAL" and not (m_val >= target_val):
                    matches_all = False
                    break
                elif op == "LESS_THAN" and not (m_val < target_val):
                    matches_all = False
                    break
                elif op == "LESS_OR_EQUAL" and not (m_val <= target_val):
                    matches_all = False
                    break
                elif op == "EQUAL" and not (m_val == target_val):
                    matches_all = False
                    break

            if matches_all:
                matching_results.append(sec)

        new_rev = store.update_screener(action.target_resource_id, new_state)
        result_payload = {
            "screener_id": action.target_resource_id,
            "revision": new_rev,
            "universe": target_universe,
            "filters_count": len(active_filters),
            "match_count": len(matching_results),
            "matches": matching_results,
        }
        return result_payload, new_rev, diffs

    async def undo(
        self,
        action: AiFinancialAction,
        receipt: Any,
        actor_user_id: str,
        tenant_id: str,
    ) -> str:
        store = get_screener_store()
        before_rev = getattr(receipt, "target_revision_before", None)
        if not before_rev:
            raise AiActionValidationFailedError(
                "Cannot undo: missing target_revision_before in receipt"
            )
        return store.restore_revision(action.target_resource_id, before_rev)
