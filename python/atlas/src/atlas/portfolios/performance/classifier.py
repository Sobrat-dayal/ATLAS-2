"""Cash-Flow Classifier for ATLAS Portfolio Performance (Stage 111).

Distinguishes external capital flows (investor contributions/withdrawals)
from internal events (security purchases, sales, dividends, fees, splits, internal transfers).
Enforces correct sign conventions between portfolio and investor perspectives.
"""

from decimal import Decimal
from typing import Callable, Optional
from uuid import uuid4

from atlas.portfolios.enums import TransactionType
from atlas.portfolios.models import PortfolioTransaction
from atlas.portfolios.performance.enums import CashFlowClassification, MeasurementScope
from atlas.portfolios.performance.models import PerformanceCashFlow


class CashFlowClassifier:
    """Classifies portfolio transactions into external or internal cash movements."""

    def __init__(
        self,
        base_currency: str,
        fx_resolver: Optional[Callable[[str, str, object], Decimal]] = None,
    ):
        self.base_currency = base_currency
        self.fx_resolver = fx_resolver or self._default_fx

    def _default_fx(self, base: str, quote: str, as_of: object) -> Decimal:
        if base == quote:
            return Decimal("1.0")
        return Decimal("1.0")

    def classify_transaction(
        self,
        tx: PortfolioTransaction,
        scope: MeasurementScope = MeasurementScope.PORTFOLIO,
        target_account_id: Optional[object] = None,
    ) -> PerformanceCashFlow:
        """Classifies a single transaction relative to the measurement boundary."""
        amount_val = getattr(tx, "net_cash_amount", None)
        if amount_val is None:
            amount_val = getattr(tx, "net_amount", None)
        native_amount = abs(amount_val) if amount_val is not None else Decimal("0.00")

        currency = getattr(tx, "cash_currency", None) or getattr(tx, "currency", "USD")

        # Resolve FX rate on transaction date
        fx_rate = self.fx_resolver(currency, self.base_currency, tx.trade_date)
        base_amount = native_amount * fx_rate

        classification = CashFlowClassification.UNCLASSIFIED
        investor_flow = Decimal("0.00")
        portfolio_flow = Decimal("0.00")
        description = f"{tx.transaction_type.value} {tx.symbol or ''}".strip()

        t_type = tx.transaction_type

        if t_type in (TransactionType.BUY, TransactionType.SELL):
            # Internal security trades: exchange cash for shares within portfolio
            classification = CashFlowClassification.INTERNAL_SECURITY_TRADE
            investor_flow = Decimal("0.00")
            portfolio_flow = Decimal("0.00")
            description = f"Internal trade: {t_type.value} {tx.quantity} {tx.symbol}"

        elif t_type == TransactionType.CASH_DEPOSIT:
            # External capital contribution
            classification = CashFlowClassification.EXTERNAL_CONTRIBUTION
            investor_flow = -base_amount  # Cash leaving investor's external pocket
            portfolio_flow = +base_amount  # Cash entering portfolio capital base
            description = f"External contribution: {native_amount} {currency}"

        elif t_type == TransactionType.CASH_WITHDRAWAL:
            # External capital withdrawal
            classification = CashFlowClassification.EXTERNAL_WITHDRAWAL
            investor_flow = +base_amount  # Cash returned to investor
            portfolio_flow = -base_amount  # Cash removed from portfolio capital base
            description = f"External withdrawal: {native_amount} {currency}"

        elif t_type in (TransactionType.CASH_DIVIDEND, TransactionType.CASH_INTEREST):
            # Internal investment income
            classification = CashFlowClassification.INTERNAL_INCOME
            investor_flow = Decimal("0.00")
            portfolio_flow = Decimal("0.00")
            description = f"Investment income: {t_type.value} {native_amount} {currency}"

        elif t_type in (TransactionType.ACCOUNT_FEE, TransactionType.WITHHOLDING_TAX):
            # Internal costs reducing net performance
            classification = CashFlowClassification.INTERNAL_FEE
            investor_flow = Decimal("0.00")
            portfolio_flow = Decimal("0.00")
            description = f"Portfolio fee/tax: {t_type.value} {native_amount} {currency}"

        elif t_type in (TransactionType.CASH_TRANSFER_IN, TransactionType.CASH_TRANSFER_OUT):
            if scope == MeasurementScope.PORTFOLIO:
                # Internal to the combined portfolio
                classification = CashFlowClassification.INTERNAL_TRANSFER
                investor_flow = Decimal("0.00")
                portfolio_flow = Decimal("0.00")
                description = f"Internal transfer across accounts ({t_type.value})"
            else:
                # External relative to this specific individual account boundary
                if t_type == TransactionType.CASH_TRANSFER_IN:
                    classification = CashFlowClassification.EXTERNAL_CONTRIBUTION
                    investor_flow = -base_amount
                    portfolio_flow = +base_amount
                    description = f"Transfer in to account: {native_amount} {currency}"
                else:
                    classification = CashFlowClassification.EXTERNAL_WITHDRAWAL
                    investor_flow = +base_amount
                    portfolio_flow = -base_amount
                    description = f"Transfer out of account: {native_amount} {currency}"

        elif t_type == TransactionType.STOCK_SPLIT_ADJUSTMENT:
            classification = CashFlowClassification.CORPORATE_ACTION_NONCASH
            investor_flow = Decimal("0.00")
            portfolio_flow = Decimal("0.00")
            description = f"Corporate action non-cash split: {tx.symbol}"

        elif t_type == TransactionType.CORRECTION_REVERSAL:
            # Reversal entry
            classification = CashFlowClassification.INTERNAL_TRANSFER
            investor_flow = Decimal("0.00")
            portfolio_flow = Decimal("0.00")
            description = f"Correction reversal: {tx.notes or ''}"

        return PerformanceCashFlow(
            id=str(uuid4()),
            portfolio_id=str(tx.portfolio_id),
            account_id=str(tx.account_id) if tx.account_id else None,
            source_transaction_id=str(tx.id) if tx.id else None,
            classification=classification,
            flow_date=tx.trade_date,
            native_amount=native_amount,
            native_currency=currency,
            base_amount=base_amount,
            base_currency=self.base_currency,
            fx_rate=fx_rate,
            investor_flow_amount=investor_flow,
            portfolio_flow_amount=portfolio_flow,
            description=description,
        )

