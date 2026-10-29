"""ATLAS Portfolios V1 — Deterministic Accounting and Lot Matching Engine.

Implements FIFO tax-lot matching, cash ledger balance computation, corporate action
split adjustments, and full transaction replay projections.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional

from atlas.portfolios.enums import (
    CashBalanceType,
    CostBasisMethod,
    ReconciliationStatus,
    TransactionStatus,
    TransactionType,
)
from atlas.portfolios.errors import (
    PortfolioCostBasisLotInsufficientError,
    PortfolioCostBasisMethodUnsupportedError,
    PortfolioTransactionAccountingFailedError,
    PortfolioTransactionInsufficientCashError,
    PortfolioTransactionInsufficientHoldingsError,
    PortfolioTransactionInvalidPriceError,
    PortfolioTransactionInvalidQuantityError,
)
from atlas.portfolios.models import (
    PortfolioCashBalance,
    PortfolioCashLedgerEntry,
    PortfolioLotConsumption,
    PortfolioPosition,
    PortfolioReconciliationResult,
    PortfolioSecurityLot,
    PortfolioTransaction,
)

FOUR_DECIMALS = Decimal("0.0001")
TWO_DECIMALS = Decimal("0.01")


def round_currency(val: Decimal) -> Decimal:
    """Round a currency amount to 2 decimal places."""
    return val.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP)


def fmt_curr(val: Optional[Decimal]) -> str:
    """Format currency decimal to standard 2-decimal string."""
    if val is None:
        return "0.00"
    return f"{round_currency(val):.2f}"


def round_basis(val: Decimal) -> Decimal:
    """Round a unit basis to 4 decimal places."""
    return val.quantize(FOUR_DECIMALS, rounding=ROUND_HALF_UP)


class PortfolioAccountingEngine:
    """Pure deterministic portfolio ledger and projection engine."""

    @staticmethod
    def validate_transaction_parameters(tx: PortfolioTransaction) -> None:
        """Validate numeric bounds and required parameters for a transaction."""
        if tx.transaction_type in (
            TransactionType.BUY,
            TransactionType.SELL,
            TransactionType.STOCK_SPLIT_ADJUSTMENT,
        ):
            if tx.quantity is None or tx.quantity <= Decimal("0"):
                raise PortfolioTransactionInvalidQuantityError(
                    str(tx.quantity), "Security transaction quantity must be strictly positive."
                )

        if tx.transaction_type in (TransactionType.BUY, TransactionType.SELL):
            if tx.unit_price is None or tx.unit_price < Decimal("0"):
                raise PortfolioTransactionInvalidPriceError(
                    str(tx.unit_price), "Unit price must be non-negative."
                )

        if tx.fee < Decimal("0") or tx.tax < Decimal("0"):
            raise PortfolioTransactionAccountingFailedError("Fees and taxes cannot be negative.")

    @classmethod
    def calculate_preview(
        cls,
        tx: PortfolioTransaction,
        current_positions: list[PortfolioPosition],
        current_cash: list[PortfolioCashBalance],
        open_lots: list[PortfolioSecurityLot],
    ) -> dict[str, Any]:
        """Compute the simulated accounting effects of a candidate transaction before posting."""
        cls.validate_transaction_parameters(tx)

        gross_amount = Decimal("0")
        net_cash_amount = Decimal("0")
        realized_pnl = Decimal("0")
        consumed_basis = Decimal("0")
        warnings: list[str] = []

        # Find available cash for account & currency
        matching_cash = next(
            (c for c in current_cash if c.account_id == tx.account_id and c.currency == tx.cash_currency),
            None,
        )
        available_cash = matching_cash.available_cash if matching_cash else Decimal("0")

        # Find available quantity for instrument
        matching_position = next(
            (p for p in current_positions if p.account_id == tx.account_id and p.instrument_id == tx.instrument_id),
            None,
        )
        available_quantity = matching_position.quantity if matching_position else Decimal("0")

        if tx.transaction_type == TransactionType.BUY:
            qty = tx.quantity or Decimal("0")
            price = tx.unit_price or Decimal("0")
            gross_amount = qty * price
            total_acquisition_cost = gross_amount + tx.fee + tx.tax
            net_cash_amount = -total_acquisition_cost
            resulting_cash = available_cash - total_acquisition_cost
            if resulting_cash < Decimal("0"):
                warnings.append(
                    f"Warning: Transaction requires {total_acquisition_cost} {tx.cash_currency}, "
                    f"exceeding available cash of {available_cash} {tx.cash_currency}."
                )
            unit_cost = (total_acquisition_cost / qty) if qty > Decimal("0") else Decimal("0")

            return {
                "transaction_type": tx.transaction_type.value,
                "gross_amount": fmt_curr(gross_amount),
                "fee": fmt_curr(tx.fee),
                "tax": fmt_curr(tx.tax),
                "net_cash_amount": fmt_curr(net_cash_amount),
                "estimated_resulting_cash": fmt_curr(resulting_cash),
                "resulting_quantity": str(available_quantity + qty),
                "unit_cost_basis": str(round_basis(unit_cost)),
                "warnings": warnings,
            }

        elif tx.transaction_type == TransactionType.SELL:
            qty = tx.quantity or Decimal("0")
            price = tx.unit_price or Decimal("0")
            gross_amount = qty * price
            net_proceeds = gross_amount - tx.fee - tx.tax
            net_cash_amount = net_proceeds
            resulting_cash = available_cash + net_proceeds

            if qty > available_quantity:
                raise PortfolioTransactionInsufficientHoldingsError(
                    tx.instrument_id or "unknown",
                    str(available_quantity),
                    str(qty),
                )

            # Simulate FIFO consumption
            eligible_lots = sorted(
                [lot for lot in open_lots if lot.instrument_id == tx.instrument_id and not lot.is_fully_disposed],
                key=lambda l: (l.acquisition_date, l.created_at),
            )
            needed = qty
            for lot in eligible_lots:
                if needed <= Decimal("0"):
                    break
                take = min(needed, lot.remaining_quantity)
                lot_basis = take * lot.unit_cost_basis
                consumed_basis += lot_basis
                needed -= take

            realized_pnl = net_proceeds - consumed_basis

            return {
                "transaction_type": tx.transaction_type.value,
                "gross_amount": fmt_curr(gross_amount),
                "fee": fmt_curr(tx.fee),
                "tax": fmt_curr(tx.tax),
                "net_cash_amount": fmt_curr(net_cash_amount),
                "estimated_resulting_cash": fmt_curr(resulting_cash),
                "resulting_quantity": str(available_quantity - qty),
                "consumed_basis": fmt_curr(consumed_basis),
                "estimated_realized_pnl": fmt_curr(realized_pnl),
                "warnings": warnings,
            }

        elif tx.transaction_type in (TransactionType.CASH_DEPOSIT, TransactionType.CASH_DIVIDEND, TransactionType.CASH_INTEREST):
            amount = tx.gross_amount or Decimal("0")
            net_cash_amount = amount - tx.fee - tx.tax
            resulting_cash = available_cash + net_cash_amount
            return {
                "transaction_type": tx.transaction_type.value,
                "gross_amount": fmt_curr(amount),
                "fee": fmt_curr(tx.fee),
                "tax": fmt_curr(tx.tax),
                "net_cash_amount": fmt_curr(net_cash_amount),
                "estimated_resulting_cash": fmt_curr(resulting_cash),
                "warnings": warnings,
            }

        elif tx.transaction_type in (TransactionType.CASH_WITHDRAWAL, TransactionType.ACCOUNT_FEE, TransactionType.WITHHOLDING_TAX):
            amount = tx.gross_amount or Decimal("0")
            net_cash_amount = -(amount + tx.fee + tx.tax)
            resulting_cash = available_cash + net_cash_amount
            if resulting_cash < Decimal("0"):
                warnings.append(
                    f"Warning: Cash balance will be negative ({resulting_cash} {tx.cash_currency})."
                )
            return {
                "transaction_type": tx.transaction_type.value,
                "gross_amount": fmt_curr(amount),
                "fee": fmt_curr(tx.fee),
                "tax": fmt_curr(tx.tax),
                "net_cash_amount": fmt_curr(net_cash_amount),
                "estimated_resulting_cash": fmt_curr(resulting_cash),
                "warnings": warnings,
            }

        elif tx.transaction_type == TransactionType.STOCK_SPLIT_ADJUSTMENT:
            split_ratio = tx.unit_price or Decimal("1")
            new_qty = available_quantity * split_ratio
            return {
                "transaction_type": tx.transaction_type.value,
                "split_ratio": str(split_ratio),
                "current_quantity": str(available_quantity),
                "resulting_quantity": str(new_qty),
                "net_cash_amount": "0.00",
                "warnings": warnings,
            }

        return {
            "transaction_type": tx.transaction_type.value,
            "net_cash_amount": "0.00",
            "warnings": warnings,
        }

    @classmethod
    def replay_ledger(
        cls,
        portfolio_id: str,
        transactions: list[PortfolioTransaction],
        as_of: Optional[datetime] = None,
        cost_basis_method: CostBasisMethod = CostBasisMethod.FIFO,
    ) -> tuple[
        list[PortfolioPosition],
        list[PortfolioCashBalance],
        list[PortfolioSecurityLot],
        list[PortfolioCashLedgerEntry],
        list[PortfolioLotConsumption],
    ]:
        """Deterministically replay a transaction stream to derive holdings, lots, and cash balances."""
        if cost_basis_method != CostBasisMethod.FIFO:
            raise PortfolioCostBasisMethodUnsupportedError(cost_basis_method.value)

        # 1. Filter out reversed transactions and apply as_of cutoff
        active_txs = [
            tx for tx in transactions
            if tx.status == TransactionStatus.POSTED
            and (as_of is None or tx.trade_date <= as_of)
        ]

        # 2. Sort chronologically by trade_date, then created_at
        active_txs.sort(key=lambda t: (t.trade_date, t.created_at))

        lots: list[PortfolioSecurityLot] = []
        consumptions: list[PortfolioLotConsumption] = []
        cash_entries: list[PortfolioCashLedgerEntry] = []

        # Cash balance accumulators: (account_id, currency) -> dict of balances
        cash_acc: dict[tuple[str, str], dict[str, Decimal]] = defaultdict(
            lambda: {
                "posted": Decimal("0"),
                "settled": Decimal("0"),
                "unsettled_rec": Decimal("0"),
                "unsettled_pay": Decimal("0"),
            }
        )

        now = as_of or datetime.utcnow()

        for tx in active_txs:
            cls.validate_transaction_parameters(tx)
            acc_cur = (tx.account_id, tx.cash_currency)

            if tx.transaction_type == TransactionType.BUY:
                qty = tx.quantity or Decimal("0")
                unit_price = tx.unit_price or Decimal("0")
                gross = qty * unit_price
                total_acquisition_cost = gross + tx.fee + tx.tax
                unit_basis = total_acquisition_cost / qty

                # Update tx fields
                tx.gross_amount = gross
                tx.net_cash_amount = -total_acquisition_cost

                # Record lot
                lot_id = f"lot_{tx.id}"
                new_lot = PortfolioSecurityLot(
                    id=lot_id,
                    portfolio_id=portfolio_id,
                    account_id=tx.account_id,
                    instrument_id=tx.instrument_id or "",
                    acquisition_transaction_id=tx.id,
                    acquisition_date=tx.trade_date,
                    original_quantity=qty,
                    remaining_quantity=qty,
                    unit_cost_basis=unit_basis,
                    total_cost_basis=total_acquisition_cost,
                    currency=tx.cash_currency,
                    created_at=tx.created_at,
                    updated_at=tx.created_at,
                )
                lots.append(new_lot)

                # Cash ledger
                cash_entry = PortfolioCashLedgerEntry(
                    id=f"cle_{tx.id}",
                    portfolio_id=portfolio_id,
                    account_id=tx.account_id,
                    transaction_id=tx.id,
                    currency=tx.cash_currency,
                    amount=-total_acquisition_cost,
                    balance_type=CashBalanceType.POSTED_CASH,
                    effective_date=tx.trade_date,
                    description=f"Buy {qty} {tx.symbol or ''} @ {unit_price}",
                    created_at=tx.created_at,
                )
                cash_entries.append(cash_entry)

                # Update cash accumulator
                cash_acc[acc_cur]["posted"] -= total_acquisition_cost
                if tx.settlement_date <= now:
                    cash_acc[acc_cur]["settled"] -= total_acquisition_cost
                else:
                    cash_acc[acc_cur]["unsettled_pay"] += total_acquisition_cost

            elif tx.transaction_type == TransactionType.SELL:
                qty = tx.quantity or Decimal("0")
                unit_price = tx.unit_price or Decimal("0")
                gross = qty * unit_price
                net_proceeds = gross - tx.fee - tx.tax

                tx.gross_amount = gross
                tx.net_cash_amount = net_proceeds

                # FIFO lot allocation within the same account and instrument
                open_lots = [
                    l for l in lots
                    if l.account_id == tx.account_id
                    and l.instrument_id == tx.instrument_id
                    and not l.is_fully_disposed
                    and l.remaining_quantity > Decimal("0")
                ]
                open_lots.sort(key=lambda l: (l.acquisition_date, l.created_at))

                total_available = sum(l.remaining_quantity for l in open_lots)
                if qty > total_available:
                    raise PortfolioTransactionInsufficientHoldingsError(
                        tx.instrument_id or "unknown",
                        str(total_available),
                        str(qty),
                    )

                needed = qty
                total_sale_fee = tx.fee + tx.tax

                for lot in open_lots:
                    if needed <= Decimal("0"):
                        break

                    consume_qty = min(needed, lot.remaining_quantity)
                    lot_portion_ratio = consume_qty / qty
                    portion_gross = consume_qty * unit_price
                    portion_fee = total_sale_fee * lot_portion_ratio
                    portion_net_proceeds = portion_gross - portion_fee

                    basis_consumed = consume_qty * lot.unit_cost_basis
                    realized_pnl = portion_net_proceeds - basis_consumed

                    consumption = PortfolioLotConsumption(
                        id=f"lc_{tx.id}_{lot.id}",
                        sell_transaction_id=tx.id,
                        lot_id=lot.id,
                        quantity_consumed=consume_qty,
                        unit_cost_basis=lot.unit_cost_basis,
                        total_cost_basis_consumed=basis_consumed,
                        proceeds_allocated=portion_gross,
                        fee_allocated=portion_fee,
                        realized_pnl=realized_pnl,
                        created_at=tx.created_at,
                    )
                    consumptions.append(consumption)

                    lot.remaining_quantity -= consume_qty
                    lot.total_cost_basis -= basis_consumed
                    if lot.remaining_quantity <= Decimal("0"):
                        lot.remaining_quantity = Decimal("0")
                        lot.total_cost_basis = Decimal("0")
                        lot.is_fully_disposed = True
                        lot.disposed_at = tx.trade_date

                    lot.updated_at = tx.created_at
                    needed -= consume_qty

                # Cash ledger
                cash_entry = PortfolioCashLedgerEntry(
                    id=f"cle_{tx.id}",
                    portfolio_id=portfolio_id,
                    account_id=tx.account_id,
                    transaction_id=tx.id,
                    currency=tx.cash_currency,
                    amount=net_proceeds,
                    balance_type=CashBalanceType.POSTED_CASH,
                    effective_date=tx.trade_date,
                    description=f"Sell {qty} {tx.symbol or ''} @ {unit_price}",
                    created_at=tx.created_at,
                )
                cash_entries.append(cash_entry)

                cash_acc[acc_cur]["posted"] += net_proceeds
                if tx.settlement_date <= now:
                    cash_acc[acc_cur]["settled"] += net_proceeds
                else:
                    cash_acc[acc_cur]["unsettled_rec"] += net_proceeds

            elif tx.transaction_type == TransactionType.STOCK_SPLIT_ADJUSTMENT:
                split_ratio = tx.unit_price or Decimal("1")
                if split_ratio <= Decimal("0"):
                    raise PortfolioTransactionAccountingFailedError("Stock split ratio must be strictly positive.")

                # Adjust all open lots for this instrument in this account
                for lot in lots:
                    if (
                        lot.account_id == tx.account_id
                        and lot.instrument_id == tx.instrument_id
                        and not lot.is_fully_disposed
                    ):
                        lot.original_quantity *= split_ratio
                        lot.remaining_quantity *= split_ratio
                        # Total cost basis is preserved; per-share unit cost basis is divided by split ratio
                        lot.unit_cost_basis = lot.total_cost_basis / lot.remaining_quantity
                        lot.updated_at = tx.created_at

            elif tx.transaction_type in (
                TransactionType.CASH_DEPOSIT,
                TransactionType.CASH_DIVIDEND,
                TransactionType.CASH_INTEREST,
                TransactionType.CASH_TRANSFER_IN,
            ):
                amount = tx.gross_amount or Decimal("0")
                net_amount = amount - tx.fee - tx.tax
                tx.net_cash_amount = net_amount

                cash_entry = PortfolioCashLedgerEntry(
                    id=f"cle_{tx.id}",
                    portfolio_id=portfolio_id,
                    account_id=tx.account_id,
                    transaction_id=tx.id,
                    currency=tx.cash_currency,
                    amount=net_amount,
                    balance_type=CashBalanceType.POSTED_CASH,
                    effective_date=tx.trade_date,
                    description=f"{tx.transaction_type.value}: {tx.notes or ''}",
                    created_at=tx.created_at,
                )
                cash_entries.append(cash_entry)

                cash_acc[acc_cur]["posted"] += net_amount
                if tx.settlement_date <= now:
                    cash_acc[acc_cur]["settled"] += net_amount
                else:
                    cash_acc[acc_cur]["unsettled_rec"] += net_amount

            elif tx.transaction_type in (
                TransactionType.CASH_WITHDRAWAL,
                TransactionType.ACCOUNT_FEE,
                TransactionType.WITHHOLDING_TAX,
                TransactionType.CASH_TRANSFER_OUT,
            ):
                amount = tx.gross_amount or Decimal("0")
                total_deduction = amount + tx.fee + tx.tax
                tx.net_cash_amount = -total_deduction

                cash_entry = PortfolioCashLedgerEntry(
                    id=f"cle_{tx.id}",
                    portfolio_id=portfolio_id,
                    account_id=tx.account_id,
                    transaction_id=tx.id,
                    currency=tx.cash_currency,
                    amount=-total_deduction,
                    balance_type=CashBalanceType.POSTED_CASH,
                    effective_date=tx.trade_date,
                    description=f"{tx.transaction_type.value}: {tx.notes or ''}",
                    created_at=tx.created_at,
                )
                cash_entries.append(cash_entry)

                cash_acc[acc_cur]["posted"] -= total_deduction
                if tx.settlement_date <= now:
                    cash_acc[acc_cur]["settled"] -= total_deduction
                else:
                    cash_acc[acc_cur]["unsettled_pay"] += total_deduction

        # 3. Build Cash Balances
        cash_balances: list[PortfolioCashBalance] = []
        for (acc_id, cur), bals in cash_acc.items():
            posted = bals["posted"]
            settled = bals["settled"]
            unsettled_rec = bals["unsettled_rec"]
            unsettled_pay = bals["unsettled_pay"]
            available = settled - unsettled_pay

            cash_balances.append(
                PortfolioCashBalance(
                    account_id=acc_id,
                    currency=cur,
                    posted_cash=posted,
                    settled_cash=settled,
                    unsettled_receivable=unsettled_rec,
                    unsettled_payable=unsettled_pay,
                    available_cash=available,
                    as_of=now,
                )
            )

        # 4. Build Positions aggregated by (account_id, instrument_id)
        # and also aggregate at portfolio level
        positions_by_key: dict[tuple[Optional[str], str], dict[str, Any]] = {}

        # First collect all instruments encountered in transactions
        instruments_info: dict[str, dict[str, str]] = {}
        for tx in active_txs:
            if tx.instrument_id:
                instruments_info[tx.instrument_id] = {
                    "symbol": tx.symbol or tx.instrument_id,
                    "exchange": tx.exchange or "UNKNOWN",
                    "company_name": tx.company_name or "",
                    "currency": tx.cash_currency,
                }

        # Calculate realized P&L per instrument and per account
        realized_pnl_by_acc_inst: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
        for lc in consumptions:
            matching_lot = next((l for l in lots if l.id == lc.lot_id), None)
            if matching_lot:
                key = (matching_lot.account_id, matching_lot.instrument_id)
                realized_pnl_by_acc_inst[key] += lc.realized_pnl

        # Group open lots
        for (inst_id, info) in instruments_info.items():
            # Account-level positions
            account_ids = {tx.account_id for tx in active_txs if tx.instrument_id == inst_id}
            for acc_id in account_ids:
                acc_open_lots = [
                    l for l in lots
                    if l.account_id == acc_id
                    and l.instrument_id == inst_id
                    and not l.is_fully_disposed
                    and l.remaining_quantity > Decimal("0")
                ]
                acc_qty = sum((l.remaining_quantity for l in acc_open_lots), Decimal("0"))
                acc_basis = sum((l.total_cost_basis for l in acc_open_lots), Decimal("0"))
                acc_avg_cost = (acc_basis / acc_qty) if acc_qty > Decimal("0") else None
                acc_realized = realized_pnl_by_acc_inst[(acc_id, inst_id)]

                pos = PortfolioPosition(
                    portfolio_id=portfolio_id,
                    account_id=acc_id,
                    instrument_id=inst_id,
                    symbol=info["symbol"],
                    exchange=info["exchange"],
                    company_name=info["company_name"],
                    quantity=acc_qty,
                    open_lot_count=len(acc_open_lots),
                    remaining_cost_basis=acc_basis,
                    cost_basis_currency=info["currency"],
                    average_unit_cost=acc_avg_cost,
                    realized_pnl=acc_realized,
                    as_of=now,
                )
                positions_by_key[(acc_id, inst_id)] = pos

        positions = list(positions_by_key.values())
        return positions, cash_balances, lots, cash_entries, consumptions

    @classmethod
    def reconcile(
        cls,
        portfolio_id: str,
        transactions: list[PortfolioTransaction],
        positions: list[PortfolioPosition],
        cash_balances: list[PortfolioCashBalance],
        lots: list[PortfolioSecurityLot],
        cash_entries: list[PortfolioCashLedgerEntry],
    ) -> PortfolioReconciliationResult:
        """Audit reconciliation between ledger transactions, tax lots, holdings, and cash balances."""
        discrepancies: list[str] = []
        warnings: list[str] = []

        # 1. Total quantity of open lots must exactly match position quantity
        open_lots_by_acc_inst: dict[tuple[Optional[str], str], Decimal] = defaultdict(Decimal)
        for lot in lots:
            if not lot.is_fully_disposed:
                if lot.remaining_quantity < Decimal("0"):
                    discrepancies.append(f"Lot '{lot.id}' has negative remaining quantity: {lot.remaining_quantity}")
                open_lots_by_acc_inst[(lot.account_id, lot.instrument_id)] += lot.remaining_quantity

        for pos in positions:
            lot_qty = open_lots_by_acc_inst.get((pos.account_id, pos.instrument_id), Decimal("0"))
            if pos.quantity != lot_qty:
                discrepancies.append(
                    f"Position quantity mismatch for instrument {pos.symbol} in account {pos.account_id}: "
                    f"position has {pos.quantity}, sum of lots is {lot_qty}."
                )

        # 2. Cash balance posted cash must equal sum of cash ledger entries
        cash_entries_by_acc_cur: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
        for cle in cash_entries:
            cash_entries_by_acc_cur[(cle.account_id, cle.currency)] += cle.amount

        for cb in cash_balances:
            cle_sum = cash_entries_by_acc_cur.get((cb.account_id, cb.currency), Decimal("0"))
            if cb.posted_cash != cle_sum:
                discrepancies.append(
                    f"Cash ledger discrepancy in account {cb.account_id} ({cb.currency}): "
                    f"posted balance is {cb.posted_cash}, ledger sum is {cle_sum}."
                )

        # 3. Check for negative cash warnings
        for cb in cash_balances:
            if cb.settled_cash < Decimal("0"):
                warnings.append(
                    f"Account {cb.account_id} has negative settled cash ({cb.settled_cash} {cb.currency})."
                )

        is_balanced = len(discrepancies) == 0
        status = ReconciliationStatus.RECONCILED if is_balanced else ReconciliationStatus.OUT_OF_BALANCE
        if is_balanced and warnings:
            status = ReconciliationStatus.RECONCILIATION_WARNING

        return PortfolioReconciliationResult(
            portfolio_id=portfolio_id,
            status=status,
            reconciliation_timestamp=datetime.utcnow(),
            total_transactions_checked=len(transactions),
            total_lots_checked=len(lots),
            total_positions_checked=len(positions),
            total_cash_entries_checked=len(cash_entries),
            discrepancies=discrepancies,
            warnings=warnings,
            is_balanced=is_balanced,
        )
