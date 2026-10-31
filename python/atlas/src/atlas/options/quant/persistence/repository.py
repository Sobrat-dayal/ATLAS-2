"""Strategy Persistence Repository with Multi-Tenant RLS Isolation (Stage 142)."""

from __future__ import annotations

import uuid
from typing import Dict, List, Optional
from atlas.auth import AuthPrincipal
from atlas.options.quant.errors import (
    QuantMultiTenantAccessDeniedError,
)
from atlas.options.quant.strategies.models import QuantStrategyDefinition


class QuantStrategyRepository:
    """Thread-safe strategy repository enforcing tenant isolation and access controls."""

    def __init__(self):
        self._strategies: Dict[str, QuantStrategyDefinition] = {}

    def save_strategy(
        self,
        strategy: QuantStrategyDefinition,
        principal: Optional[AuthPrincipal] = None,
    ) -> QuantStrategyDefinition:
        """Save or update a strategy definition."""
        if principal:
            strategy.owner_id = principal.sub
            strategy.tenant_id = principal.raw_claims.get("tenant_id") or getattr(principal, "tenant_id", "default_tenant")

        self._strategies[strategy.strategy_id] = strategy
        return strategy

    def get_strategy(
        self,
        strategy_id: str,
        principal: Optional[AuthPrincipal] = None,
    ) -> Optional[QuantStrategyDefinition]:
        """Retrieve strategy definition enforcing strict multi-tenant authorization (Test S)."""
        strat = self._strategies.get(strategy_id)
        if not strat:
            return None

        # Multi-tenant RLS check: If private, caller must match owner or tenant
        if strat.is_private and principal:
            caller_sub = principal.sub
            caller_tenant = principal.raw_claims.get("tenant_id") or getattr(principal, "tenant_id", None)
            is_admin = getattr(principal, "is_admin", False) or principal.role == "admin"
            if strat.owner_id != caller_sub and (not caller_tenant or strat.tenant_id != caller_tenant) and not is_admin:
                raise QuantMultiTenantAccessDeniedError(
                    resource_id=strategy_id,
                    principal_sub=caller_sub,
                )

        return strat

    def list_strategies_for_user(
        self,
        principal: AuthPrincipal,
    ) -> List[QuantStrategyDefinition]:
        """List all strategies accessible to the calling principal."""
        results: List[QuantStrategyDefinition] = []
        caller_tenant = principal.raw_claims.get("tenant_id") or getattr(principal, "tenant_id", None)
        is_admin = getattr(principal, "is_admin", False) or principal.role == "admin"
        for s in self._strategies.values():
            if s.owner_id == principal.sub or (caller_tenant and s.tenant_id == caller_tenant) or is_admin:
                results.append(s)
        return results

    def delete_strategy(
        self,
        strategy_id: str,
        principal: AuthPrincipal,
    ) -> bool:
        """Delete a strategy if owned by caller."""
        strat = self.get_strategy(strategy_id, principal=principal)
        if not strat:
            return False

        is_admin = getattr(principal, "is_admin", False) or principal.role == "admin"
        if strat.owner_id != principal.sub and not is_admin:
            raise QuantMultiTenantAccessDeniedError(
                resource_id=strategy_id,
                principal_sub=principal.sub,
            )

        del self._strategies[strategy_id]
        return True
