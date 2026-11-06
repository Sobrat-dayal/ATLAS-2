"""
Ecosystem Governance and Financial Safety Firewall for Stage 149.
Enforces permission attenuation, resource quotas, and financial trading restrictions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from atlas.ecosystem.domain import ToolSideEffectClass
from atlas.ecosystem.errors import (
    FinancialSafetyViolationError,
    PermissionDeniedEcosystemError,
    ResourceQuotaExceededError,
)

FORBIDDEN_FINANCIAL_PATTERNS = [
    re.compile(r".*broker.*order.*", re.IGNORECASE),
    re.compile(r".*order.*submit.*", re.IGNORECASE),
    re.compile(r".*trade.*execute.*", re.IGNORECASE),
    re.compile(r".*live.*money.*", re.IGNORECASE),
    re.compile(r".*wire.*funds.*", re.IGNORECASE),
]


class EcosystemGovernance:
    """
    Enforces institutional governance, permission attenuation, and financial safety rules.
    """

    @staticmethod
    def enforce_financial_safety(action_name: str, payload: Dict[str, Any]) -> None:
        """
        Guarantees that no ecosystem plugin, package, custom tool, or MCP server
        can execute live-money financial market orders.
        """
        for pattern in FORBIDDEN_FINANCIAL_PATTERNS:
            if pattern.match(action_name):
                raise FinancialSafetyViolationError(
                    f"Financial Safety Firewall: Action '{action_name}' attempted live financial execution. "
                    "All ecosystem extensions are restricted to read-only or paper trading simulations."
                )

        # Inspect payload for live order indicators
        if payload.get("execution_mode") == "LIVE_MONEY" or payload.get("is_live_trading") is True:
            raise FinancialSafetyViolationError(
                "Financial Safety Firewall: Explicit LIVE_MONEY execution mode is barred in ecosystem extensions."
            )

    @staticmethod
    def verify_permission_attenuation(
        requested_scopes: Tuple[str, ...],
        installer_scopes: Tuple[str, ...],
    ) -> None:
        """
        Ensures an installed extension cannot obtain broader scopes than the installer possesses.
        """
        unauthorized = [s for s in requested_scopes if s not in installer_scopes]
        if unauthorized:
            raise PermissionDeniedEcosystemError(
                f"Permission attenuation violation: Installer lacks scopes: {unauthorized}."
            )

    @staticmethod
    def check_resource_quota(
        current_usage: int,
        quota_limit: int,
        metric_name: str = "tokens",
    ) -> None:
        if current_usage >= quota_limit:
            raise ResourceQuotaExceededError(
                f"Resource quota exceeded for {metric_name}: current {current_usage} >= limit {quota_limit}."
            )

