"""Domain models, enums, and dataclasses for ATLAS AI Financial Action Engine (Stage 128)."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AiActionType(str, enum.Enum):
    """Supported canonical action types across Charts, Screeners, Portfolios, and Risk."""

    # Chart Actions (Parts XXIII - XXVIII)
    CHART_SELECT_INSTRUMENT = "atlas.chart.select_instrument"
    CHART_SET_TIMEFRAME = "atlas.chart.set_timeframe"
    CHART_SET_DATE_RANGE = "atlas.chart.set_date_range"
    CHART_SET_TYPE = "atlas.chart.set_type"
    CHART_ADD_INDICATOR = "atlas.chart.add_indicator"
    CHART_REMOVE_INDICATOR = "atlas.chart.remove_indicator"
    CHART_UPDATE_INDICATOR = "atlas.chart.update_indicator"
    CHART_ADD_COMPARISON = "atlas.chart.add_comparison"
    CHART_REMOVE_COMPARISON = "atlas.chart.remove_comparison"
    CHART_SAVE_CONFIGURATION = "atlas.chart.save_configuration"
    CHART_RESTORE_CONFIGURATION = "atlas.chart.restore_configuration"

    # Screener Actions (Parts XXIX - XXXIV)
    SCREENER_CREATE_DRAFT = "atlas.screener.create_draft"
    SCREENER_ADD_FILTER = "atlas.screener.add_filter"
    SCREENER_UPDATE_FILTER = "atlas.screener.update_filter"
    SCREENER_REMOVE_FILTER = "atlas.screener.remove_filter"
    SCREENER_SET_UNIVERSE = "atlas.screener.set_universe"
    SCREENER_SET_SORT = "atlas.screener.set_sort"
    SCREENER_SET_COLUMNS = "atlas.screener.set_columns"
    SCREENER_PREVIEW = "atlas.screener.preview"
    SCREENER_EXECUTE = "atlas.screener.execute"
    SCREENER_SAVE = "atlas.screener.save"
    SCREENER_UPDATE_SAVED = "atlas.screener.update_saved"
    SCREENER_RESTORE_REVISION = "atlas.screener.restore_revision"

    # Portfolio Actions (Parts XXXV - XLII - Analytical / Draft Only)
    PORTFOLIO_ANALYZE_ALLOCATION = "atlas.portfolio.analyze_allocation"
    PORTFOLIO_PROPOSE_TARGETS = "atlas.portfolio.propose_targets"
    PORTFOLIO_CALCULATE_DELTA = "atlas.portfolio.calculate_allocation_delta"
    PORTFOLIO_CREATE_SCENARIO_DRAFT = "atlas.portfolio.create_scenario_draft"
    PORTFOLIO_COMPARE_ALLOCATIONS = "atlas.portfolio.compare_allocations"
    PORTFOLIO_SAVE_SCENARIO_DRAFT = "atlas.portfolio.save_scenario_draft"

    # Risk Actions (Parts XLIII - L - Genuine Worker Runs & Immutability)
    RISK_GET_MODELS = "atlas.risk.get_models"
    RISK_VALIDATE_PARAMETERS = "atlas.risk.validate_parameters"
    RISK_PREVIEW_RUN = "atlas.risk.preview_run"
    RISK_START_RUN = "atlas.risk.start_run"
    RISK_GET_RUN_STATUS = "atlas.risk.get_run_status"
    RISK_CANCEL_RUN = "atlas.risk.cancel_run"
    RISK_GET_RUN_RESULTS = "atlas.risk.get_run_results"
    RISK_COMPARE_RUNS = "atlas.risk.compare_runs"
    RISK_RUN_STRESS_SCENARIO = "atlas.risk.run_stress_scenario"

    # Prohibited Types (Explicitly blocked)
    PROHIBITED_LEDGER_MUTATION = "atlas.prohibited.ledger_mutation"
    PROHIBITED_BROKER_ORDER = "atlas.prohibited.broker_order"
    PROHIBITED_ARBITRARY_CODE = "atlas.prohibited.arbitrary_code"


class AiActionClassification(str, enum.Enum):
    """Classification of action side effects and security requirements (Part IX)."""

    READ_ONLY = "READ_ONLY"
    SESSION_UI_CHANGE = "SESSION_UI_CHANGE"
    USER_PREFERENCE_CHANGE = "USER_PREFERENCE_CHANGE"
    PERSISTENT_CONFIGURATION_CHANGE = "PERSISTENT_CONFIGURATION_CHANGE"
    SAVED_ANALYTICAL_DRAFT = "SAVED_ANALYTICAL_DRAFT"
    COMPUTATION_JOB = "COMPUTATION_JOB"
    FINANCIAL_LEDGER_MUTATION = "FINANCIAL_LEDGER_MUTATION"  # Prohibited in Stage 128
    BROKER_SIDE_EFFECT = "BROKER_SIDE_EFFECT"  # Prohibited in Stage 128
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"  # Prohibited in Stage 128
    PRIVILEGED_OPERATION = "PRIVILEGED_OPERATION"  # Prohibited in Stage 128


class ApprovalPolicy(str, enum.Enum):
    """Approval policies governing execution requirements (Part XVII)."""

    AUTO_READ_ONLY = "AUTO_READ_ONLY"
    USER_PREVIEW_CONFIRM = "USER_PREVIEW_CONFIRM"
    EXPLICIT_SENSITIVE_APPROVAL = "EXPLICIT_SENSITIVE_APPROVAL"
    COMPUTATION_COST_APPROVAL = "COMPUTATION_COST_APPROVAL"
    PROHIBITED = "PROHIBITED"


class ReversibilityPolicy(str, enum.Enum):
    """Reversibility and compensation capabilities (Part XXII)."""

    REVERSIBLE = "REVERSIBLE"
    COMPENSATABLE = "COMPENSATABLE"
    NON_REVERSIBLE = "NON_REVERSIBLE"
    CANCELLABLE_ONLY = "CANCELLABLE_ONLY"


class ActionLifecycleState(str, enum.Enum):
    """Lifecycle states of an AI financial action (Part X)."""

    REQUESTED = "REQUESTED"
    INTERPRETING = "INTERPRETING"
    RESOLVING_CONTEXT = "RESOLVING_CONTEXT"
    VALIDATING = "VALIDATING"
    PREVIEW_READY = "PREVIEW_READY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    CONFLICTED = "CONFLICTED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass
class AiActionDiff:
    """Typed representation of a field change between current and proposed state (Part XV)."""

    field_path: str
    before_value: Any
    after_value: Any
    change_type: str = "MODIFY"  # ADD, MODIFY, REMOVE
    validation_status: str = "VALID"
    financial_impact_if_computable: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_path": self.field_path,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "change_type": self.change_type,
            "validation_status": self.validation_status,
            "financial_impact_if_computable": self.financial_impact_if_computable,
        }


@dataclass
class AiFinancialActionPreview:
    """Accurate preview computed from live resource state and validated proposed arguments (Part XIV)."""

    preview_id: str
    action_id: str
    target_resource_type: str
    target_resource_id: str
    current_state: Dict[str, Any]
    proposed_state: Dict[str, Any]
    diffs: List[AiActionDiff] = field(default_factory=list)
    financial_assumptions: List[str] = field(default_factory=list)
    estimated_cost: str = "LOW"  # NONE, LOW, MEDIUM, HIGH
    approval_policy: ApprovalPolicy = ApprovalPolicy.USER_PREVIEW_CONFIRM
    reversibility_policy: ReversibilityPolicy = ReversibilityPolicy.REVERSIBLE
    preview_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preview_id": self.preview_id,
            "action_id": self.action_id,
            "target_resource_type": self.target_resource_type,
            "target_resource_id": self.target_resource_id,
            "current_state": self.current_state,
            "proposed_state": self.proposed_state,
            "diffs": [d.to_dict() for d in self.diffs],
            "financial_assumptions": self.financial_assumptions,
            "estimated_cost": self.estimated_cost,
            "approval_policy": self.approval_policy.value,
            "reversibility_policy": self.reversibility_policy.value,
            "preview_hash": self.preview_hash,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


@dataclass
class AiFinancialAction:
    """Canonical individual AI financial action unit (Part VII)."""

    action_id: str
    action_type: AiActionType
    action_version: str
    target_module: str  # charts, screeners, portfolios, risk
    target_resource_type: str  # chart_config, screener_query, portfolio_scenario, risk_run
    target_resource_id: str
    actor_user_id: str
    tenant_scope: str
    proposed_arguments: Dict[str, Any]
    normalized_arguments_hash: str
    expected_resource_revision: str
    classification: AiActionClassification
    approval_policy: ApprovalPolicy
    reversibility_policy: ReversibilityPolicy
    action_status: ActionLifecycleState = ActionLifecycleState.REQUESTED
    conversation_id: Optional[str] = None
    generation_id: Optional[str] = None
    tool_call_id: Optional[str] = None
    preview: Optional[AiFinancialActionPreview] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "action_version": self.action_version,
            "target_module": self.target_module,
            "target_resource_type": self.target_resource_type,
            "target_resource_id": self.target_resource_id,
            "actor_user_id": self.actor_user_id,
            "tenant_scope": self.tenant_scope,
            "proposed_arguments": self.proposed_arguments,
            "normalized_arguments_hash": self.normalized_arguments_hash,
            "expected_resource_revision": self.expected_resource_revision,
            "classification": self.classification.value,
            "approval_policy": self.approval_policy.value,
            "reversibility_policy": self.reversibility_policy.value,
            "action_status": self.action_status.value,
            "conversation_id": self.conversation_id,
            "generation_id": self.generation_id,
            "tool_call_id": self.tool_call_id,
            "preview": self.preview.to_dict() if self.preview else None,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


@dataclass
class AiFinancialActionPlan:
    """Coordinated multi-step action plan with dependency graph (Part VIII & LI)."""

    plan_id: str
    owner_user_id: str
    tenant_id: str
    user_intent: str
    actions: List[AiFinancialAction] = field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    conversation_id: Optional[str] = None
    status: ActionLifecycleState = ActionLifecycleState.REQUESTED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "owner_user_id": self.owner_user_id,
            "tenant_id": self.tenant_id,
            "user_intent": self.user_intent,
            "actions": [a.to_dict() for a in self.actions],
            "dependency_graph": self.dependency_graph,
            "conversation_id": self.conversation_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


@dataclass
class AiActionExecutionReceipt:
    """Cryptographically verifiable, immutable receipt of completed or attempted action (Part XXI)."""

    receipt_id: str
    action_id: str
    plan_id: str
    tool_call_id: Optional[str]
    actor_user_id: str
    target_resource_id: str
    target_revision_before: str
    target_revision_after: str
    operation_status: ActionLifecycleState
    started_at: datetime
    completed_at: datetime
    result_reference: Dict[str, Any] = field(default_factory=dict)
    diffs: List[AiActionDiff] = field(default_factory=list)
    source_manifest_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    undo_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "action_id": self.action_id,
            "plan_id": self.plan_id,
            "tool_call_id": self.tool_call_id,
            "actor_user_id": self.actor_user_id,
            "target_resource_id": self.target_resource_id,
            "target_revision_before": self.target_revision_before,
            "target_revision_after": self.target_revision_after,
            "operation_status": self.operation_status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "result_reference": self.result_reference,
            "diffs": [d.to_dict() for d in self.diffs],
            "source_manifest_id": self.source_manifest_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "undo_reference": self.undo_reference,
        }


@dataclass
class AiPortfolioScenarioDraft:
    """Hypothetical non-executing portfolio allocation scenario draft (Part XXXIX)."""

    scenario_id: str
    portfolio_id: str
    portfolio_snapshot_id: str
    scenario_type: str  # TACTICAL_REWEIGHT, SECTOR_TILT, FACTOR_HEDGE
    baseline_allocation: Dict[str, float]  # asset_class/sector -> weight (0.0 - 1.0)
    proposed_allocation: Dict[str, float]
    allocation_deltas: Dict[str, float]  # percentage points change
    notional_deltas: Dict[str, float]  # currency amounts if base value supplied
    assumptions: List[str]
    valuation_as_of: str
    reporting_currency: str = "USD"
    validation_status: str = "VALID"
    is_hypothetical: bool = True
    disclaimer: str = (
        "Hypothetical Allocation Proposal — Not Executed. No broker orders or ledger mutations."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "portfolio_id": self.portfolio_id,
            "portfolio_snapshot_id": self.portfolio_snapshot_id,
            "scenario_type": self.scenario_type,
            "baseline_allocation": self.baseline_allocation,
            "proposed_allocation": self.proposed_allocation,
            "allocation_deltas": self.allocation_deltas,
            "notional_deltas": self.notional_deltas,
            "assumptions": self.assumptions,
            "valuation_as_of": self.valuation_as_of,
            "reporting_currency": self.reporting_currency,
            "validation_status": self.validation_status,
            "is_hypothetical": self.is_hypothetical,
            "disclaimer": self.disclaimer,
        }


@dataclass
class AiRiskRunRecord:
    """Immutable record of an executed risk calculation job (Part L)."""

    run_id: str
    portfolio_id: str
    snapshot_id: str
    model_id: str
    model_version: str
    confidence_level: float
    horizon_days: int
    historical_window_days: int
    valuation_as_of: str
    reporting_currency: str
    status: str  # COMPLETED, FAILED, RUNNING, CANCELLED
    metrics: Dict[str, Any] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    source_manifest_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "portfolio_id": self.portfolio_id,
            "snapshot_id": self.snapshot_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "confidence_level": self.confidence_level,
            "horizon_days": self.horizon_days,
            "historical_window_days": self.historical_window_days,
            "valuation_as_of": self.valuation_as_of,
            "reporting_currency": self.reporting_currency,
            "status": self.status,
            "metrics": self.metrics,
            "assumptions": self.assumptions,
            "source_manifest_id": self.source_manifest_id,
            "created_at": self.created_at.isoformat(),
        }
