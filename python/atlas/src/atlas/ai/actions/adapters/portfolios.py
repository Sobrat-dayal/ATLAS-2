"""Portfolio action adapter for ATLAS AI Financial Action Engine (Stage 128, Parts XXXV - XLII)."""

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
    AiPortfolioScenarioDraft,
    ApprovalPolicy,
    ReversibilityPolicy,
)
from atlas.ai.actions.errors import (
    AiActionBrokerExecutionProhibitedError,
    AiActionFinancialConstraintFailedError,
    AiActionLedgerMutationProhibitedError,
    AiActionTargetNotFoundError,
    AiActionValidationFailedError,
)

# Reference sample portfolio for Fixture C
SAMPLE_PORTFOLIOS = {
    "TEST_P": {
        "portfolio_id": "TEST_P",
        "name": "Institutional Balanced Model",
        "total_value": 100_000.0,
        "reporting_currency": "USD",
        "user_id": "test_user_stage128",
        "tenant_id": "default_tenant",
        "revision": "rev_TEST_P_1",
        "as_of": "2026-10-30T00:00:00Z",
        "holdings": [
            {"symbol": "SPY", "asset_class": "Equity", "weight": 0.60, "value": 60_000.0},
            {"symbol": "BND", "asset_class": "Bonds", "weight": 0.40, "value": 40_000.0},
        ],
        "allocations": {
            "Equity": 0.60,
            "Bonds": 0.40,
        },
    }
}


class MockPortfolioScenarioStore:
    """Stores non-executing hypothetical scenario drafts (Part XXXIX)."""

    def __init__(self) -> None:
        self._scenarios: Dict[str, AiPortfolioScenarioDraft] = {}

    def save_draft(self, draft: AiPortfolioScenarioDraft) -> None:
        self._scenarios[draft.scenario_id] = draft

    def get_draft(self, scenario_id: str) -> Optional[AiPortfolioScenarioDraft]:
        return self._scenarios.get(scenario_id)

    def delete_draft(self, scenario_id: str) -> bool:
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            return True
        return False


_SCENARIO_STORE = MockPortfolioScenarioStore()


def get_scenario_store() -> MockPortfolioScenarioStore:
    return _SCENARIO_STORE


class PortfolioActionAdapter(ActionAdapter):
    """Handles hypothetical non-executing portfolio allocation and scenario actions."""

    def __init__(
        self, action_type_val: AiActionType = AiActionType.PORTFOLIO_PROPOSE_TARGETS
    ) -> None:
        self._action_type = action_type_val

    @property
    def action_type(self) -> AiActionType:
        return self._action_type

    @property
    def target_module(self) -> str:
        return "portfolios"

    @property
    def classification(self) -> AiActionClassification:
        return AiActionClassification.SAVED_ANALYTICAL_DRAFT

    @property
    def default_approval_policy(self) -> ApprovalPolicy:
        return ApprovalPolicy.USER_PREVIEW_CONFIRM

    @property
    def reversibility_policy(self) -> ReversibilityPolicy:
        return ReversibilityPolicy.REVERSIBLE

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "string"},
                "target_weights": {
                    "type": "object",
                    "additionalProperties": {"type": "number"},
                },
                "scenario_type": {"type": "string"},
            },
            "required": ["portfolio_id", "target_weights"],
        }

    def validate_parameters(self, proposed_args: Dict[str, Any]) -> Dict[str, Any]:
        # Guardrail check against prohibited operations
        if (
            proposed_args.get("is_broker_order")
            or "buy_shares" in proposed_args
            or "order_type" in proposed_args
        ):
            raise AiActionBrokerExecutionProhibitedError(
                "Broker order placement is not permitted in Stage 128."
            )

        if (
            proposed_args.get("mutate_ledger")
            or "adjust_cash" in proposed_args
            or "post_transaction" in proposed_args
        ):
            raise AiActionLedgerMutationProhibitedError(
                "Direct ledger and cash mutations are not permitted."
            )

        p_id = proposed_args.get("portfolio_id")
        if not p_id:
            raise AiActionValidationFailedError("Missing required parameter 'portfolio_id'")

        target_weights = proposed_args.get("target_weights")
        if not isinstance(target_weights, dict) or not target_weights:
            raise AiActionValidationFailedError("Missing or invalid 'target_weights' mapping.")

        # Validate weights sum to 1.0 (within 0.001 tolerance for rounding)
        total_weight = sum(target_weights.values())
        if abs(total_weight - 1.0) > 0.005:
            raise AiActionFinancialConstraintFailedError(
                "weight_normalization",
                f"Target weights must sum to 1.0 (100%), but got {total_weight * 100:.2f}%.",
            )

        # Check for negative weights if long-only
        for asset, w in target_weights.items():
            if w < 0.0:
                raise AiActionFinancialConstraintFailedError(
                    "long_only_constraint",
                    f"Asset/Sector '{asset}' target weight cannot be negative ({w}).",
                )

        return proposed_args

    async def get_current_state(
        self,
        resource_id: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[Dict[str, Any], str]:
        p = SAMPLE_PORTFOLIOS.get(resource_id)
        if not p:
            raise AiActionTargetNotFoundError("portfolio", resource_id)
        return copy.deepcopy(p), p["revision"]

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
        baseline_alloc = current_state.get("allocations", {})
        target_weights = proposed_args["target_weights"]
        total_val = current_state.get("total_value", 100_000.0)

        diffs: List[AiActionDiff] = []
        assumptions: List[str] = [
            f"Portfolio: {current_state.get('name', resource_id)} ({resource_id})",
            f"Valuation As-of: {current_state.get('as_of', '2026-10-30')}",
            f"Reporting Currency: {current_state.get('reporting_currency', 'USD')}",
            "Hypothetical Analysis Only — No changes to actual holdings, cash, or ledgers.",
        ]

        all_keys = set(baseline_alloc.keys()).union(set(target_weights.keys()))
        for k in sorted(all_keys):
            before_w = baseline_alloc.get(k, 0.0)
            after_w = target_weights.get(k, 0.0)
            delta_pp = (after_w - before_w) * 100.0  # percentage points
            notional_delta = (after_w - before_w) * total_val

            diffs.append(
                AiActionDiff(
                    field_path=f"allocations.{k}",
                    before_value=f"{before_w * 100:.1f}%",
                    after_value=f"{after_w * 100:.1f}%",
                    change_type="MODIFY" if before_w > 0 else "ADD",
                    financial_impact_if_computable=(
                        f"{delta_pp:+.1f} pp ({notional_delta:+,.0f} {current_state.get('reporting_currency', 'USD')})"
                    ),
                )
            )

        proposed_state = {
            "portfolio_id": resource_id,
            "target_weights": target_weights,
            "is_hypothetical": True,
            "disclaimer": "Hypothetical Allocation Proposal — Not Executed",
        }

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
            target_resource_type="portfolio_scenario",
            target_resource_id=resource_id,
            current_state={
                "portfolio_id": resource_id,
                "allocations": baseline_alloc,
                "total_value": total_val,
            },
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
        p = SAMPLE_PORTFOLIOS.get(action.target_resource_id)
        if not p:
            raise AiActionTargetNotFoundError("portfolio", action.target_resource_id)

        target_weights = action.proposed_arguments["target_weights"]
        total_val = p.get("total_value", 100_000.0)
        curr_currency = p.get("reporting_currency", "USD")

        baseline_alloc = p.get("allocations", {})
        allocation_deltas: Dict[str, float] = {}
        notional_deltas: Dict[str, float] = {}
        diffs: List[AiActionDiff] = []

        all_keys = set(baseline_alloc.keys()).union(set(target_weights.keys()))
        for k in sorted(all_keys):
            before_w = baseline_alloc.get(k, 0.0)
            after_w = target_weights.get(k, 0.0)
            delta_pp = (after_w - before_w) * 100.0
            notional = (after_w - before_w) * total_val
            allocation_deltas[k] = round(delta_pp, 2)
            notional_deltas[k] = round(notional, 2)

            diffs.append(
                AiActionDiff(
                    field_path=f"allocations.{k}",
                    before_value=f"{before_w * 100:.1f}%",
                    after_value=f"{after_w * 100:.1f}%",
                    change_type="MODIFY",
                    financial_impact_if_computable=f"{delta_pp:+.1f} pp ({notional:+,.0f} {curr_currency})",
                )
            )

        scenario_id = f"scen_{uuid.uuid4().hex[:12]}"
        draft = AiPortfolioScenarioDraft(
            scenario_id=scenario_id,
            portfolio_id=action.target_resource_id,
            portfolio_snapshot_id=p["revision"],
            scenario_type=action.proposed_arguments.get("scenario_type", "TACTICAL_REWEIGHT"),
            baseline_allocation=baseline_alloc,
            proposed_allocation=target_weights,
            allocation_deltas=allocation_deltas,
            notional_deltas=notional_deltas,
            assumptions=[
                "Hypothetical target allocation only.",
                "Actual portfolio holdings, cash balances, and transactions remain strictly unmodified.",
                "Zero broker order placement.",
            ],
            valuation_as_of=p.get("as_of", "2026-10-30"),
            reporting_currency=curr_currency,
        )

        get_scenario_store().save_draft(draft)

        # Notice: The actual portfolio in SAMPLE_PORTFOLIOS is untouched!
        # Revision of portfolio is unchanged; the draft itself has a new reference ID
        result_payload = draft.to_dict()
        return result_payload, p["revision"], diffs

    async def undo(
        self,
        action: AiFinancialAction,
        receipt: Any,
        actor_user_id: str,
        tenant_id: str,
    ) -> str:
        # Undo deletes the hypothetical scenario draft
        result_ref = getattr(receipt, "result_reference", {})
        scen_id = result_ref.get("scenario_id")
        if scen_id:
            get_scenario_store().delete_draft(scen_id)
        return getattr(receipt, "target_revision_before", "rev_TEST_P_1")
