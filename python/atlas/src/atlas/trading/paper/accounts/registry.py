"""Paper Trading Account Registry (Stage 144)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from atlas.trading.paper.domain import PaperAccount
from atlas.trading.paper.errors import (
    AccountInactiveError,
    AccountNotFoundError,
    CrossTenantAccessError,
)


class PaperAccountRegistry:
    """In-memory registry of all paper trading accounts."""

    def __init__(self) -> None:
        self._accounts: Dict[str, PaperAccount] = {}
        self._tenant_accounts: Dict[str, List[str]] = {}

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_account(
        self,
        tenant_id: str,
        label: str,
        currency: str,
        initial_cash: float,
        description: str = "",
    ) -> PaperAccount:
        """Create a new paper account for *tenant_id*."""
        if initial_cash < 0:
            raise ValueError("initial_cash must be >= 0")

        account_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        account = PaperAccount(
            account_id=account_id,
            tenant_id=tenant_id,
            label=label,
            currency=currency,
            initial_cash=initial_cash,
            cash=initial_cash,
            equity=initial_cash,
            margin_used=0.0,
            buying_power=initial_cash,
            daily_realized_pnl=0.0,
            created_at=now,
            updated_at=now,
            is_active=True,
            kill_switch_active=False,
            description=description,
        )
        self._accounts[account_id] = account
        self._tenant_accounts.setdefault(tenant_id, []).append(account_id)
        return account

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_account(self, account_id: str, tenant_id: str) -> PaperAccount:
        """Return account; raise appropriate errors if inaccessible."""
        account = self._accounts.get(account_id)
        if account is None:
            raise AccountNotFoundError(f"Account '{account_id}' not found.")
        if account.tenant_id != tenant_id:
            raise CrossTenantAccessError(
                f"Account '{account_id}' does not belong to tenant '{tenant_id}'."
            )
        if not account.is_active:
            raise AccountInactiveError(f"Account '{account_id}' is inactive.")
        return account

    def list_accounts(self, tenant_id: str) -> List[PaperAccount]:
        """Return all accounts belonging to *tenant_id*."""
        ids = self._tenant_accounts.get(tenant_id, [])
        return [self._accounts[aid] for aid in ids if aid in self._accounts]

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def update_account(self, account: PaperAccount) -> None:
        """Persist an updated account object."""
        self._accounts[account.account_id] = account

    def deactivate_account(self, account_id: str, tenant_id: str) -> None:
        """Deactivate an account (soft-delete)."""
        account = self.get_account(account_id, tenant_id)
        account.is_active = False
        account.updated_at = datetime.now(timezone.utc)
        self._accounts[account_id] = account

    def reset_account(self, account_id: str, tenant_id: str) -> None:
        """Reset a paper account back to initial_cash; clear daily PnL."""
        account = self.get_account(account_id, tenant_id)
        account.cash = account.initial_cash
        account.equity = account.initial_cash
        account.buying_power = account.initial_cash
        account.margin_used = 0.0
        account.daily_realized_pnl = 0.0
        account.kill_switch_active = False
        account.updated_at = datetime.now(timezone.utc)
        self._accounts[account_id] = account
