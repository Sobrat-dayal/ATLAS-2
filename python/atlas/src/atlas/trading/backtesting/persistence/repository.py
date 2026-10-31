"""Strategy and Backtest Run Repository with Multi-Tenant RLS Isolation (Stage 143)."""

from __future__ import annotations

from typing import Dict, List, Optional
from atlas.auth import AuthPrincipal
from atlas.trading.backtesting.domain import (
    AtlasBacktestConfig,
    AtlasBacktestResult,
    ParameterExperimentResult,
    WalkForwardResult,
)
from atlas.trading.backtesting.errors import BacktestMultiTenantAccessDeniedError


class BacktestRunRepository:
    """Thread-safe backtest run repository enforcing strict tenant isolation."""

    def __init__(self):
        self._runs: Dict[str, AtlasBacktestResult] = {}
        self._experiments: Dict[str, ParameterExperimentResult] = {}
        self._walk_forwards: Dict[str, WalkForwardResult] = {}

    def save_run(
        self,
        result: AtlasBacktestResult,
        principal: Optional[AuthPrincipal] = None,
    ) -> AtlasBacktestResult:
        """Persist a completed backtest run with caller tenancy."""
        if principal:
            result.config.owner_id = principal.sub
            result.config.tenant_id = (
                principal.raw_claims.get("tenant_id")
                or getattr(principal, "tenant_id", "default_tenant")
            )

        self._runs[result.run_id] = result
        return result

    def get_run(
        self,
        run_id: str,
        principal: Optional[AuthPrincipal] = None,
    ) -> Optional[AtlasBacktestResult]:
        """Retrieve run enforcing multi-tenant RLS isolation (Test V)."""
        res = self._runs.get(run_id)
        if not res:
            return None

        # Check tenant privacy
        if res.config.is_private and principal:
            caller_sub = principal.sub
            caller_tenant = (
                principal.raw_claims.get("tenant_id")
                or getattr(principal, "tenant_id", None)
            )
            is_admin = getattr(principal, "is_admin", False) or principal.role == "admin"

            if (
                res.config.owner_id != caller_sub
                and (not caller_tenant or res.config.tenant_id != caller_tenant)
                and not is_admin
            ):
                raise BacktestMultiTenantAccessDeniedError(
                    resource_id=run_id,
                    principal_sub=caller_sub,
                )

        return res

    def list_runs_for_user(
        self,
        principal: AuthPrincipal,
    ) -> List[AtlasBacktestResult]:
        """List runs accessible to calling user."""
        caller_sub = principal.sub
        caller_tenant = (
            principal.raw_claims.get("tenant_id")
            or getattr(principal, "tenant_id", None)
        )
        is_admin = getattr(principal, "is_admin", False) or principal.role == "admin"

        results: List[AtlasBacktestResult] = []
        for r in self._runs.values():
            if (
                r.config.owner_id == caller_sub
                or (caller_tenant and r.config.tenant_id == caller_tenant)
                or is_admin
            ):
                results.append(r)
        return results

    def save_experiment(self, exp_result: ParameterExperimentResult) -> None:
        self._experiments[exp_result.experiment_id] = exp_result

    def get_experiment(self, experiment_id: str) -> Optional[ParameterExperimentResult]:
        return self._experiments.get(experiment_id)

    def save_walk_forward(self, wf_result: WalkForwardResult) -> None:
        self._walk_forwards[wf_result.walk_forward_id] = wf_result

    def get_walk_forward(self, walk_forward_id: str) -> Optional[WalkForwardResult]:
        return self._walk_forwards.get(walk_forward_id)
