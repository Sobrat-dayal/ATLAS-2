"""Paper Strategy Deployment Registry (Stage 144)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from atlas.trading.paper.errors import StrategyDeploymentError


class PaperStrategyRegistry:
    """Manages strategy deployments against paper trading accounts."""

    def __init__(self) -> None:
        self._deployments: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def deploy(
        self,
        strategy_id: str,
        account_id: str,
        tenant_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new strategy deployment record."""
        deployment_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        record: Dict[str, Any] = {
            "deployment_id": deployment_id,
            "strategy_id": strategy_id,
            "account_id": account_id,
            "tenant_id": tenant_id,
            "config": config,
            "status": "ACTIVE",
            "deployed_at": now,
            "stopped_at": None,
        }
        self._deployments[strategy_id] = record
        return record

    def get(self, strategy_id: str) -> Dict[str, Any]:
        """Return the deployment record for *strategy_id*."""
        record = self._deployments.get(strategy_id)
        if record is None:
            raise StrategyDeploymentError(f"Strategy '{strategy_id}' has no deployment record.")
        return record

    def stop(self, strategy_id: str, account_id: str, tenant_id: str) -> None:
        """Stop (deactivate) a strategy deployment."""
        record = self.get(strategy_id)
        if record["account_id"] != account_id or record["tenant_id"] != tenant_id:
            raise StrategyDeploymentError(
                f"Strategy '{strategy_id}' does not belong to this account/tenant."
            )
        record["status"] = "STOPPED"
        record["stopped_at"] = datetime.now(timezone.utc).isoformat()

    def list_active(self, account_id: str) -> List[Dict[str, Any]]:
        """Return all ACTIVE deployments for *account_id*."""
        return [
            r
            for r in self._deployments.values()
            if r["account_id"] == account_id and r["status"] == "ACTIVE"
        ]
