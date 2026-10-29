"""ATLAS Portfolios V1 — Business Logic & Domain Service.

Coordinates portfolio and account lifecycles, transaction posting and previews,
reversals and corrections, FIFO tax-lot calculations, market-price/FX resolution,
valuation generation, and accounting reconciliation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from atlas.portfolios.accounting import PortfolioAccountingEngine
from atlas.portfolios.enums import (
    AccountStatus,
    AccountType,
    CostBasisMethod,
    PortfolioStatus,
    PortfolioType,
    QuoteFreshness,
    TransactionStatus,
    TransactionType,
    ValuationCompletenessStatus,
)
from atlas.portfolios.errors import (
    PortfolioAccountArchivedError,
    PortfolioAccountCurrencyUnsupportedError,
    PortfolioAccountNotFoundError,
    PortfolioBaseCurrencyUnsupportedError,
    PortfolioNameInvalidError,
    PortfolioTransactionAlreadyReversedError,
    PortfolioTransactionNotFoundError,
    PortfolioTransactionReversalInvalidError,
)
from atlas.portfolios.models import (
    InvestmentAccount,
    Portfolio,
    PortfolioCashBalance,
    PortfolioCashLedgerEntry,
    PortfolioPosition,
    PortfolioReconciliationResult,
    PortfolioSecurityLot,
    PortfolioTransaction,
    PortfolioValuation,
)
from atlas.portfolios.repository import PortfolioRepository
from atlas.portfolios.schemas import (
    AccountCreateRequest,
    AccountUpdateRequest,
    PortfolioCreateRequest,
    PortfolioUpdateRequest,
    TransactionCorrectRequest,
    TransactionCreateRequest,
    TransactionPreviewResponse,
    TransactionReverseRequest,
)
from atlas.portfolios.valuation import PortfolioValuationEngine

logger = logging.getLogger("atlas.portfolios.service")

SUPPORTED_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "INR",
    "JPY",
    "CAD",
    "AUD",
    "CHF",
    "SGD",
    "HKD",
}


class PortfolioService:
    """Institutional portfolio management service."""

    def __init__(self, repository: Optional[PortfolioRepository] = None) -> None:
        self.repository = repository or PortfolioRepository()
        self._price_feed: dict[str, dict[str, Any]] = {}
        self._fx_feed: dict[tuple[str, str], dict[str, Any]] = {}
        self._init_default_market_data()

    def _init_default_market_data(self) -> None:
        """Seed default canonical quotes and FX rates."""
        now = datetime.utcnow()
        # Canonical baseline FX pairs
        self._fx_feed[("INR", "USD")] = {
            "rate": Decimal("0.012"),
            "as_of": now,
            "source": "CANONICAL_ECB_FX",
        }
        self._fx_feed[("USD", "INR")] = {
            "rate": Decimal("83.3333"),
            "as_of": now,
            "source": "CANONICAL_ECB_FX",
        }
        self._fx_feed[("EUR", "USD")] = {
            "rate": Decimal("1.0850"),
            "as_of": now,
            "source": "CANONICAL_ECB_FX",
        }
        self._fx_feed[("USD", "EUR")] = {
            "rate": Decimal("0.9216"),
            "as_of": now,
            "source": "CANONICAL_ECB_FX",
        }
        self._fx_feed[("GBP", "USD")] = {
            "rate": Decimal("1.2700"),
            "as_of": now,
            "source": "CANONICAL_ECB_FX",
        }
        self._fx_feed[("USD", "GBP")] = {
            "rate": Decimal("0.7874"),
            "as_of": now,
            "source": "CANONICAL_ECB_FX",
        }

    def set_mock_quote(
        self,
        instrument_id: str,
        price: Decimal,
        currency: str = "USD",
        freshness: QuoteFreshness = QuoteFreshness.REALTIME,
        source: str = "CANONICAL_EXCHANGE_FEED",
    ) -> None:
        """Register or update an eligible mark quote for an instrument."""
        self._price_feed[instrument_id] = {
            "price": price,
            "currency": currency,
            "freshness": freshness,
            "source": source,
            "as_of": datetime.utcnow(),
        }

    def set_mock_fx(
        self,
        base_pair: str,
        quote_pair: str,
        rate: Decimal,
        source: str = "CANONICAL_FX_FEED",
    ) -> None:
        """Register or update an eligible FX rate."""
        self._fx_feed[(base_pair, quote_pair)] = {
            "rate": rate,
            "source": source,
            "as_of": datetime.utcnow(),
        }

    # -----------------------------------------------------------------------
    # Portfolio CRUD
    # -----------------------------------------------------------------------

    def create_portfolio(self, user_id: str, request: PortfolioCreateRequest) -> Portfolio:
        if not request.name.strip():
            raise PortfolioNameInvalidError("Portfolio name cannot be empty.")
        cur = request.base_currency.upper().strip()
        if cur not in SUPPORTED_CURRENCIES:
            raise PortfolioBaseCurrencyUnsupportedError(cur)

        portfolio_id = f"port_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        portfolio = Portfolio(
            id=portfolio_id,
            user_id=user_id,
            name=request.name.strip(),
            portfolio_type=request.portfolio_type,
            base_currency=cur,
            status=PortfolioStatus.ACTIVE,
            cost_basis_method=CostBasisMethod.FIFO,
            description=request.description.strip() if request.description else None,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        saved = self.repository.create_portfolio(portfolio)

        # Create a default investment account
        account_id = f"acc_{uuid.uuid4().hex[:12]}"
        default_account = InvestmentAccount(
            id=account_id,
            portfolio_id=saved.id,
            user_id=user_id,
            account_name="Primary Investment Account",
            account_type=AccountType.INVESTMENT_ACCOUNT,
            primary_currency=cur,
            created_at=now,
            updated_at=now,
        )
        self.repository.create_account(default_account)
        return saved

    def get_portfolio(self, portfolio_id: str, user_id: str) -> Portfolio:
        return self.repository.get_portfolio(portfolio_id, user_id)

    def list_portfolios(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Portfolio], int]:
        return self.repository.list_portfolios(user_id, limit, offset)

    def update_portfolio(
        self, portfolio_id: str, user_id: str, request: PortfolioUpdateRequest
    ) -> Portfolio:
        existing = self.repository.get_portfolio(portfolio_id, user_id)
        if request.name is not None:
            if not request.name.strip():
                raise PortfolioNameInvalidError("Portfolio name cannot be empty.")
            existing.name = request.name.strip()
        if request.description is not None:
            existing.description = request.description.strip() if request.description else None
        if request.status is not None:
            existing.status = request.status

        existing.updated_at = datetime.utcnow()
        return self.repository.update_portfolio(existing, request.revision)

    def delete_portfolio(self, portfolio_id: str, user_id: str) -> bool:
        return self.repository.delete_portfolio(portfolio_id, user_id)

    # -----------------------------------------------------------------------
    # Account CRUD
    # -----------------------------------------------------------------------

    def create_account(
        self, portfolio_id: str, user_id: str, request: AccountCreateRequest
    ) -> InvestmentAccount:
        self.repository.get_portfolio(portfolio_id, user_id)
        cur = request.primary_currency.upper().strip()
        if cur not in SUPPORTED_CURRENCIES:
            raise PortfolioAccountCurrencyUnsupportedError(cur)

        now = datetime.utcnow()
        account = InvestmentAccount(
            id=f"acc_{uuid.uuid4().hex[:12]}",
            portfolio_id=portfolio_id,
            user_id=user_id,
            account_name=request.account_name.strip(),
            account_type=request.account_type,
            primary_currency=cur,
            custodian_name=request.custodian_name.strip() if request.custodian_name else None,
            account_number_mask=request.account_number_mask.strip() if request.account_number_mask else None,
            status=AccountStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        return self.repository.create_account(account)

    def get_account(self, account_id: str, user_id: str) -> InvestmentAccount:
        return self.repository.get_account(account_id, user_id)

    def list_accounts(self, portfolio_id: str, user_id: str) -> list[InvestmentAccount]:
        return self.repository.list_accounts(portfolio_id, user_id)

    def update_account(
        self, account_id: str, user_id: str, request: AccountUpdateRequest
    ) -> InvestmentAccount:
        acc = self.repository.get_account(account_id, user_id)
        if request.account_name is not None:
            acc.account_name = request.account_name.strip()
        if request.custodian_name is not None:
            acc.custodian_name = request.custodian_name.strip() if request.custodian_name else None
        if request.account_number_mask is not None:
            acc.account_number_mask = request.account_number_mask.strip() if request.account_number_mask else None
        if request.status is not None:
            acc.status = request.status
        acc.updated_at = datetime.utcnow()
        return self.repository.update_account(acc)

    def delete_account(self, account_id: str, user_id: str) -> bool:
        return self.repository.delete_account(account_id, user_id)

    # -----------------------------------------------------------------------
    # Transactions
    # -----------------------------------------------------------------------

    def preview_transaction(
        self, portfolio_id: str, user_id: str, request: TransactionCreateRequest
    ) -> TransactionPreviewResponse:
        self.repository.get_portfolio(portfolio_id, user_id)
        acc = self.repository.get_account(request.account_id, user_id)
        if acc.status != AccountStatus.ACTIVE:
            raise PortfolioAccountArchivedError(request.account_id)

        # Get current state from replay
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        positions, cash_balances, lots, _, _ = PortfolioAccountingEngine.replay_ledger(
            portfolio_id, txs
        )

        dummy_tx = PortfolioTransaction(
            id="preview_tx",
            portfolio_id=portfolio_id,
            account_id=request.account_id,
            user_id=user_id,
            transaction_type=request.transaction_type,
            cash_currency=request.cash_currency.upper().strip(),
            trade_date=request.trade_date or datetime.utcnow(),
            settlement_date=request.settlement_date or request.trade_date or datetime.utcnow(),
            instrument_id=request.instrument_id,
            symbol=request.symbol,
            exchange=request.exchange,
            company_name=request.company_name,
            quantity=request.quantity,
            unit_price=request.unit_price,
            gross_amount=request.gross_amount,
            fee=request.fee,
            tax=request.tax,
        )

        preview = PortfolioAccountingEngine.calculate_preview(
            dummy_tx, positions, cash_balances, lots
        )
        return TransactionPreviewResponse(**preview)

    def post_transaction(
        self, portfolio_id: str, user_id: str, request: TransactionCreateRequest
    ) -> PortfolioTransaction:
        portfolio = self.repository.get_portfolio(portfolio_id, user_id)
        acc = self.repository.get_account(request.account_id, user_id)
        if acc.status != AccountStatus.ACTIVE:
            raise PortfolioAccountArchivedError(request.account_id)

        now = datetime.utcnow()
        trade_dt = request.trade_date or now
        settle_dt = request.settlement_date or trade_dt
        cur = request.cash_currency.upper().strip()
        if cur not in SUPPORTED_CURRENCIES:
            raise PortfolioAccountCurrencyUnsupportedError(cur)

        tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        tx = PortfolioTransaction(
            id=tx_id,
            portfolio_id=portfolio_id,
            account_id=request.account_id,
            user_id=user_id,
            transaction_type=request.transaction_type,
            cash_currency=cur,
            trade_date=trade_dt,
            settlement_date=settle_dt,
            status=TransactionStatus.POSTED,
            instrument_id=request.instrument_id or (f"inst_{request.symbol.lower()}" if request.symbol else None),
            symbol=request.symbol.upper().strip() if request.symbol else None,
            exchange=request.exchange.upper().strip() if request.exchange else "NASDAQ",
            company_name=request.company_name.strip() if request.company_name else None,
            quantity=request.quantity,
            unit_price=request.unit_price,
            gross_amount=request.gross_amount,
            fee=request.fee,
            tax=request.tax,
            idempotency_key=request.idempotency_key,
            notes=request.notes.strip() if request.notes else None,
            created_at=now,
        )

        # Validate parameters and test-replay with existing stream
        PortfolioAccountingEngine.validate_transaction_parameters(tx)

        existing_txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        candidate_stream = existing_txs + [tx]
        # Replay to verify valid lot holdings and cost basis
        PortfolioAccountingEngine.replay_ledger(portfolio_id, candidate_stream)

        # Persist transaction
        saved_tx = self.repository.create_transaction(tx)

        # Invalidate/refresh valuation automatically
        try:
            self.calculate_portfolio_valuation(portfolio_id, user_id)
        except Exception as e:
            logger.warning(f"Background valuation recalculation notice: {e}")

        return saved_tx

    def get_transaction(
        self, portfolio_id: str, transaction_id: str, user_id: str
    ) -> PortfolioTransaction:
        self.repository.get_portfolio(portfolio_id, user_id)
        return self.repository.get_transaction(transaction_id, user_id)

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
        return self.repository.list_transactions(
            portfolio_id, user_id, account_id, instrument_id, tx_type, limit, offset
        )

    def reverse_transaction(
        self,
        portfolio_id: str,
        transaction_id: str,
        user_id: str,
        request: TransactionReverseRequest,
    ) -> PortfolioTransaction:
        portfolio = self.repository.get_portfolio(portfolio_id, user_id)
        orig_tx = self.repository.get_transaction(transaction_id, user_id)

        if orig_tx.status != TransactionStatus.POSTED:
            raise PortfolioTransactionAlreadyReversedError(transaction_id)
        if orig_tx.transaction_type == TransactionType.CORRECTION_REVERSAL:
            raise PortfolioTransactionReversalInvalidError("Cannot reverse a reversal transaction.")

        now = datetime.utcnow()
        reversal_id = f"tx_rev_{uuid.uuid4().hex[:10]}"

        # Create reversal transaction record
        reversal_tx = PortfolioTransaction(
            id=reversal_id,
            portfolio_id=portfolio_id,
            account_id=orig_tx.account_id,
            user_id=user_id,
            transaction_type=TransactionType.CORRECTION_REVERSAL,
            cash_currency=orig_tx.cash_currency,
            trade_date=now,
            settlement_date=now,
            status=TransactionStatus.POSTED,
            instrument_id=orig_tx.instrument_id,
            symbol=orig_tx.symbol,
            exchange=orig_tx.exchange,
            company_name=orig_tx.company_name,
            quantity=orig_tx.quantity,
            unit_price=orig_tx.unit_price,
            gross_amount=orig_tx.gross_amount,
            fee=orig_tx.fee,
            tax=orig_tx.tax,
            reverses_transaction_id=orig_tx.id,
            notes=f"Reversal of {orig_tx.id}: {request.reason}",
            created_at=now,
        )

        # Mark original as reversed
        orig_tx.status = TransactionStatus.REVERSED
        orig_tx.reversed_by_transaction_id = reversal_id
        self.repository.update_transaction(orig_tx)
        saved_reversal = self.repository.create_transaction(reversal_tx)

        # Trigger valuation refresh
        try:
            self.calculate_portfolio_valuation(portfolio_id, user_id)
        except Exception:
            pass

        return saved_reversal

    def correct_transaction(
        self,
        portfolio_id: str,
        transaction_id: str,
        user_id: str,
        request: TransactionCorrectRequest,
    ) -> PortfolioTransaction:
        # 1. Reverse the original
        self.reverse_transaction(
            portfolio_id,
            transaction_id,
            user_id,
            TransactionReverseRequest(reason=f"Correction: {request.reason}"),
        )
        # 2. Post the replacement
        replacement_tx = self.post_transaction(portfolio_id, user_id, request.replacement)
        return replacement_tx

    # -----------------------------------------------------------------------
    # Holdings & Cash Queries
    # -----------------------------------------------------------------------

    def get_positions(
        self,
        portfolio_id: str,
        user_id: str,
        account_id: Optional[str] = None,
        as_of: Optional[datetime] = None,
    ) -> list[PortfolioPosition]:
        self.repository.get_portfolio(portfolio_id, user_id)
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        positions, _, _, _, _ = PortfolioAccountingEngine.replay_ledger(
            portfolio_id, txs, as_of=as_of
        )
        if account_id:
            positions = [p for p in positions if p.account_id == account_id]
        return positions

    def get_lots(
        self,
        portfolio_id: str,
        user_id: str,
        instrument_id: str,
        account_id: Optional[str] = None,
    ) -> list[PortfolioSecurityLot]:
        self.repository.get_portfolio(portfolio_id, user_id)
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        _, _, lots, _, _ = PortfolioAccountingEngine.replay_ledger(portfolio_id, txs)
        matching_lots = [
            l for l in lots
            if l.instrument_id == instrument_id
            and (account_id is None or l.account_id == account_id)
        ]
        matching_lots.sort(key=lambda l: (l.acquisition_date, l.created_at))
        return matching_lots

    def get_cash_balances(
        self,
        portfolio_id: str,
        user_id: str,
        account_id: Optional[str] = None,
    ) -> list[PortfolioCashBalance]:
        self.repository.get_portfolio(portfolio_id, user_id)
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        _, cash_balances, _, _, _ = PortfolioAccountingEngine.replay_ledger(portfolio_id, txs)
        if account_id:
            cash_balances = [c for c in cash_balances if c.account_id == account_id]
        return cash_balances

    def get_cash_ledger(
        self,
        portfolio_id: str,
        user_id: str,
        account_id: str,
    ) -> list[PortfolioCashLedgerEntry]:
        self.repository.get_portfolio(portfolio_id, user_id)
        self.repository.get_account(account_id, user_id)
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        _, _, _, cash_entries, _ = PortfolioAccountingEngine.replay_ledger(portfolio_id, txs)
        acc_entries = [e for e in cash_entries if e.account_id == account_id]
        acc_entries.sort(key=lambda e: e.effective_date, reverse=True)
        return acc_entries

    # -----------------------------------------------------------------------
    # Valuation & Reconciliation
    # -----------------------------------------------------------------------

    def calculate_portfolio_valuation(
        self,
        portfolio_id: str,
        user_id: str,
        as_of: Optional[datetime] = None,
    ) -> PortfolioValuation:
        portfolio = self.repository.get_portfolio(portfolio_id, user_id)
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        positions, cash_balances, _, _, _ = PortfolioAccountingEngine.replay_ledger(
            portfolio_id, txs, as_of=as_of
        )

        valuation = PortfolioValuationEngine.calculate_valuation(
            portfolio=portfolio,
            positions=positions,
            cash_balances=cash_balances,
            market_quotes=self._price_feed,
            fx_rates=self._fx_feed,
            as_of=as_of,
        )
        self.repository.save_valuation(valuation)
        return valuation

    def get_latest_valuation(
        self, portfolio_id: str, user_id: str
    ) -> Optional[PortfolioValuation]:
        val = self.repository.get_latest_valuation(portfolio_id, user_id)
        if not val:
            # Generate initial valuation on first read
            val = self.calculate_portfolio_valuation(portfolio_id, user_id)
        return val

    def reconcile_portfolio(
        self, portfolio_id: str, user_id: str
    ) -> PortfolioReconciliationResult:
        self.repository.get_portfolio(portfolio_id, user_id)
        txs, _ = self.repository.list_transactions(portfolio_id, user_id, limit=5000)
        positions, cash_balances, lots, cash_entries, _ = PortfolioAccountingEngine.replay_ledger(
            portfolio_id, txs
        )

        return PortfolioAccountingEngine.reconcile(
            portfolio_id=portfolio_id,
            transactions=txs,
            positions=positions,
            cash_balances=cash_balances,
            lots=lots,
            cash_entries=cash_entries,
        )

