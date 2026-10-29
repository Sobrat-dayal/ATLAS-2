"""ATLAS Portfolios V1 — In-Memory Thread-Safe Repository.

Provides persistent storage, optimistic concurrency control, tenant isolation,
and transaction idempotency enforcement for portfolios, accounts, transactions,
and valuation snapshots.
"""

from __future__ import annotations

import threading
from copy import deepcopy
from typing import Optional

from atlas.portfolios.enums import (
    AccountStatus,
    PortfolioStatus,
    TransactionStatus,
    TransactionType,
)
from atlas.portfolios.errors import (
    PortfolioAccessDeniedError,
    PortfolioAccountAccessDeniedError,
    PortfolioAccountHasPostedTransactionsError,
    PortfolioAccountNotFoundError,
    PortfolioArchivedError,
    PortfolioDeleteConflictError,
    PortfolioNotFoundError,
    PortfolioRevisionConflictError,
    PortfolioTransactionDuplicateError,
    PortfolioTransactionNotFoundError,
)
from atlas.portfolios.models import (
    InvestmentAccount,
    Portfolio,
    PortfolioTransaction,
    PortfolioValuation,
)


class PortfolioRepository:
    """Thread-safe in-memory repository for Portfolios V1."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._portfolios: dict[str, Portfolio] = {}
        self._accounts: dict[str, InvestmentAccount] = {}
        self._transactions: dict[str, PortfolioTransaction] = {}
        self._idempotency_map: dict[tuple[str, str], str] = {}  # (account_id, idempotency_key) -> tx_id
        self._valuations: dict[str, PortfolioValuation] = {}
        self._portfolio_latest_valuation: dict[str, str] = {}  # portfolio_id -> valuation_id

    # -----------------------------------------------------------------------
    # Portfolio Operations
    # -----------------------------------------------------------------------

    def create_portfolio(self, portfolio: Portfolio) -> Portfolio:
        with self._lock:
            self._portfolios[portfolio.id] = deepcopy(portfolio)
            return deepcopy(portfolio)

    def get_portfolio(self, portfolio_id: str, user_id: Optional[str] = None) -> Portfolio:
        with self._lock:
            p = self._portfolios.get(portfolio_id)
            if not p:
                raise PortfolioNotFoundError(portfolio_id)
            if user_id is not None and p.user_id != user_id:
                raise PortfolioAccessDeniedError(portfolio_id)
            return deepcopy(p)

    def list_portfolios(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Portfolio], int]:
        with self._lock:
            user_ports = [
                p for p in self._portfolios.values()
                if p.user_id == user_id and p.status != PortfolioStatus.ARCHIVED
            ]
            user_ports.sort(key=lambda x: x.created_at, reverse=True)
            total = len(user_ports)
            sliced = user_ports[offset : offset + limit]
            return [deepcopy(p) for p in sliced], total

    def update_portfolio(self, portfolio: Portfolio, expected_revision: int) -> Portfolio:
        with self._lock:
            existing = self._portfolios.get(portfolio.id)
            if not existing:
                raise PortfolioNotFoundError(portfolio.id)
            if existing.user_id != portfolio.user_id:
                raise PortfolioAccessDeniedError(portfolio.id)
            if existing.status == PortfolioStatus.ARCHIVED:
                raise PortfolioArchivedError(portfolio.id)
            if existing.revision != expected_revision:
                raise PortfolioRevisionConflictError(expected_revision, existing.revision)

            portfolio.revision = existing.revision + 1
            self._portfolios[portfolio.id] = deepcopy(portfolio)
            return deepcopy(portfolio)

    def delete_portfolio(self, portfolio_id: str, user_id: str) -> bool:
        with self._lock:
            p = self.get_portfolio(portfolio_id, user_id)
            # Check if there are active accounts with transactions
            p_accounts = [a for a in self._accounts.values() if a.portfolio_id == portfolio_id]
            for acc in p_accounts:
                txs = [t for t in self._transactions.values() if t.account_id == acc.id and t.status == TransactionStatus.POSTED]
                if txs:
                    raise PortfolioDeleteConflictError(
                        f"Portfolio has account '{acc.account_name}' with {len(txs)} active posted transactions. Archive instead."
                    )

            # Soft-delete by archiving
            p.status = PortfolioStatus.ARCHIVED
            self._portfolios[portfolio_id] = p
            return True

    # -----------------------------------------------------------------------
    # Account Operations
    # -----------------------------------------------------------------------

    def create_account(self, account: InvestmentAccount) -> InvestmentAccount:
        with self._lock:
            # Verify parent portfolio ownership
            self.get_portfolio(account.portfolio_id, account.user_id)
            self._accounts[account.id] = deepcopy(account)
            return deepcopy(account)

    def get_account(self, account_id: str, user_id: Optional[str] = None) -> InvestmentAccount:
        with self._lock:
            acc = self._accounts.get(account_id)
            if not acc:
                raise PortfolioAccountNotFoundError(account_id)
            if user_id is not None and acc.user_id != user_id:
                raise PortfolioAccountAccessDeniedError(account_id)
            return deepcopy(acc)

    def list_accounts(self, portfolio_id: str, user_id: str) -> list[InvestmentAccount]:
        with self._lock:
            # Verify portfolio ownership
            self.get_portfolio(portfolio_id, user_id)
            accs = [
                a for a in self._accounts.values()
                if a.portfolio_id == portfolio_id and a.user_id == user_id and a.status != AccountStatus.ARCHIVED
            ]
            accs.sort(key=lambda x: x.created_at)
            return [deepcopy(a) for a in accs]

    def update_account(self, account: InvestmentAccount) -> InvestmentAccount:
        with self._lock:
            existing = self.get_account(account.id, account.user_id)
            self._accounts[account.id] = deepcopy(account)
            return deepcopy(account)

    def delete_account(self, account_id: str, user_id: str) -> bool:
        with self._lock:
            acc = self.get_account(account_id, user_id)
            txs = [t for t in self._transactions.values() if t.account_id == account_id and t.status == TransactionStatus.POSTED]
            if txs:
                raise PortfolioAccountHasPostedTransactionsError(account_id, len(txs))

            acc.status = AccountStatus.ARCHIVED
            self._accounts[account_id] = acc
            return True

    # -----------------------------------------------------------------------
    # Transaction Operations
    # -----------------------------------------------------------------------

    def create_transaction(self, tx: PortfolioTransaction) -> PortfolioTransaction:
        with self._lock:
            # Check idempotency
            if tx.idempotency_key:
                key = (tx.account_id, tx.idempotency_key)
                if key in self._idempotency_map:
                    raise PortfolioTransactionDuplicateError(tx.idempotency_key)
                self._idempotency_map[key] = tx.id

            self._transactions[tx.id] = deepcopy(tx)
            return deepcopy(tx)

    def get_transaction(self, tx_id: str, user_id: Optional[str] = None) -> PortfolioTransaction:
        with self._lock:
            tx = self._transactions.get(tx_id)
            if not tx:
                raise PortfolioTransactionNotFoundError(tx_id)
            if user_id is not None and tx.user_id != user_id:
                raise PortfolioAccessDeniedError(tx.portfolio_id)
            return deepcopy(tx)

    def list_transactions(
        self,
        portfolio_id: str,
        user_id: str,
        account_id: Optional[str] = None,
        instrument_id: Optional[str] = None,
        tx_type: Optional[TransactionType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[PortfolioTransaction], int]:
        with self._lock:
            self.get_portfolio(portfolio_id, user_id)
            txs = [
                t for t in self._transactions.values()
                if t.portfolio_id == portfolio_id and t.user_id == user_id
            ]
            if account_id:
                txs = [t for t in txs if t.account_id == account_id]
            if instrument_id:
                txs = [t for t in txs if t.instrument_id == instrument_id]
            if tx_type:
                txs = [t for t in txs if t.transaction_type == tx_type]

            txs.sort(key=lambda t: (t.trade_date, t.created_at), reverse=True)
            total = len(txs)
            sliced = txs[offset : offset + limit]
            return [deepcopy(t) for t in sliced], total

    def update_transaction(self, tx: PortfolioTransaction) -> PortfolioTransaction:
        with self._lock:
            existing = self.get_transaction(tx.id, tx.user_id)
            self._transactions[tx.id] = deepcopy(tx)
            return deepcopy(tx)

    # -----------------------------------------------------------------------
    # Valuation Operations
    # -----------------------------------------------------------------------

    def save_valuation(self, valuation: PortfolioValuation) -> PortfolioValuation:
        with self._lock:
            self._valuations[valuation.id] = deepcopy(valuation)
            self._portfolio_latest_valuation[valuation.portfolio_id] = valuation.id
            return deepcopy(valuation)

    def get_latest_valuation(self, portfolio_id: str, user_id: str) -> Optional[PortfolioValuation]:
        with self._lock:
            self.get_portfolio(portfolio_id, user_id)
            val_id = self._portfolio_latest_valuation.get(portfolio_id)
            if not val_id:
                return None
            return deepcopy(self._valuations.get(val_id))

    def get_valuation(self, valuation_id: str, user_id: str) -> Optional[PortfolioValuation]:
        with self._lock:
            val = self._valuations.get(valuation_id)
            if not val:
                return None
            self.get_portfolio(val.portfolio_id, user_id)
            return deepcopy(val)

