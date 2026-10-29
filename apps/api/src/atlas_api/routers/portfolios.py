"""FastAPI Router for Portfolios V1 (Stage 110).

Exposes institutional portfolio accounting, investment accounts, transaction journal,
security positions, FIFO tax lots, multi-currency cash balances, marked valuation,
and ledger reconciliation.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.portfolios import (
    AccountCreateRequest,
    AccountListResponse,
    AccountResponse,
    AccountUpdateRequest,
    CashBalanceResponse,
    CashLedgerEntryResponse,
    CashValuationResponse,
    LotListResponse,
    LotResponse,
    PortfolioCreateRequest,
    PortfolioError,
    PortfolioListResponse,
    PortfolioResponse,
    PortfolioService,
    PortfolioUpdateRequest,
    PositionListResponse,
    PositionResponse,
    PositionValuationResponse,
    ReconciliationResponse,
    TransactionCorrectRequest,
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionPreviewResponse,
    TransactionResponse,
    TransactionReverseRequest,
    TransactionType,
    ValuationResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

# Singleton service instance for in-memory persistence across requests
_service_instance: Optional[PortfolioService] = None


def get_portfolio_service(request: Request) -> PortfolioService:
    global _service_instance
    if _service_instance is None:
        _service_instance = PortfolioService()
    return _service_instance


def _handle_error(e: Exception) -> None:
    if isinstance(e, PortfolioError):
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message},
        )
    logger.exception("Unexpected error in portfolios router: %s", e)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "INTERNAL_SERVER_ERROR", "message": str(e)},
    )


# ---------------------------------------------------------------------------
# Portfolio CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=PortfolioListResponse)
async def list_portfolios(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PortfolioListResponse:
    """List all active portfolios owned by the authenticated principal."""
    try:
        ports, total = service.list_portfolios(current_user.sub, limit=limit, offset=offset)
        items = []
        for p in ports:
            accs = service.list_accounts(p.id, current_user.sub)
            items.append(
                PortfolioResponse(
                    id=p.id,
                    user_id=p.user_id,
                    name=p.name,
                    portfolio_type=p.portfolio_type,
                    base_currency=p.base_currency,
                    status=p.status,
                    cost_basis_method=p.cost_basis_method,
                    description=p.description,
                    account_count=len(accs),
                    revision=p.revision,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
            )
        return PortfolioListResponse(items=items, total=total)
    except Exception as e:
        _handle_error(e)


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: PortfolioCreateRequest,
) -> PortfolioResponse:
    """Create a new portfolio with a primary investment account."""
    try:
        p = service.create_portfolio(current_user.sub, payload)
        accs = service.list_accounts(p.id, current_user.sub)
        return PortfolioResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            base_currency=p.base_currency,
            status=p.status,
            cost_basis_method=p.cost_basis_method,
            description=p.description,
            account_count=len(accs),
            revision=p.revision,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PortfolioResponse:
    """Retrieve details for an owned portfolio."""
    try:
        p = service.get_portfolio(portfolio_id, current_user.sub)
        accs = service.list_accounts(p.id, current_user.sub)
        return PortfolioResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            base_currency=p.base_currency,
            status=p.status,
            cost_basis_method=p.cost_basis_method,
            description=p.description,
            account_count=len(accs),
            revision=p.revision,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    except Exception as e:
        _handle_error(e)


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: PortfolioUpdateRequest,
) -> PortfolioResponse:
    """Update portfolio metadata with optimistic revision protection."""
    try:
        p = service.update_portfolio(portfolio_id, current_user.sub, payload)
        accs = service.list_accounts(p.id, current_user.sub)
        return PortfolioResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            portfolio_type=p.portfolio_type,
            base_currency=p.base_currency,
            status=p.status,
            cost_basis_method=p.cost_basis_method,
            description=p.description,
            account_count=len(accs),
            revision=p.revision,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
    except Exception as e:
        _handle_error(e)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> None:
    """Archive a portfolio if it does not have unarchived accounts with active transactions."""
    try:
        service.delete_portfolio(portfolio_id, current_user.sub)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Account Endpoints
# ---------------------------------------------------------------------------


@router.get("/{portfolio_id}/accounts", response_model=AccountListResponse)
async def list_accounts(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> AccountListResponse:
    """List all investment accounts in a portfolio."""
    try:
        accs = service.list_accounts(portfolio_id, current_user.sub)
        items = [AccountResponse.model_validate(a) for a in accs]
        return AccountListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: AccountCreateRequest,
) -> AccountResponse:
    """Create a new investment account in a portfolio."""
    try:
        acc = service.create_account(portfolio_id, current_user.sub, payload)
        return AccountResponse.model_validate(acc)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> AccountResponse:
    """Retrieve details for a specific investment account."""
    try:
        acc = service.get_account(account_id, current_user.sub)
        return AccountResponse.model_validate(acc)
    except Exception as e:
        _handle_error(e)


@router.patch("/{portfolio_id}/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: AccountUpdateRequest,
) -> AccountResponse:
    """Update investment account details."""
    try:
        acc = service.update_account(account_id, current_user.sub, payload)
        return AccountResponse.model_validate(acc)
    except Exception as e:
        _handle_error(e)


@router.delete("/{portfolio_id}/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> None:
    """Archive an investment account if it has no posted transactions."""
    try:
        service.delete_account(account_id, current_user.sub)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Transaction Endpoints
# ---------------------------------------------------------------------------


def _fmt_2(val: Optional[Decimal]) -> str:
    if val is None:
        return "0.00"
    return f"{Decimal(str(val)):.2f}"


def _map_tx_to_response(t) -> TransactionResponse:
    return TransactionResponse(
        id=t.id,
        portfolio_id=t.portfolio_id,
        account_id=t.account_id,
        user_id=t.user_id,
        transaction_type=t.transaction_type,
        status=t.status,
        cash_currency=t.cash_currency,
        trade_date=t.trade_date,
        settlement_date=t.settlement_date,
        instrument_id=t.instrument_id,
        symbol=t.symbol,
        exchange=t.exchange,
        company_name=t.company_name,
        quantity=str(t.quantity) if t.quantity is not None else None,
        unit_price=str(t.unit_price) if t.unit_price is not None else None,
        gross_amount=_fmt_2(t.gross_amount) if t.gross_amount is not None else None,
        fee=_fmt_2(t.fee),
        tax=_fmt_2(t.tax),
        net_cash_amount=_fmt_2(t.net_cash_amount),
        idempotency_key=t.idempotency_key,
        notes=t.notes,
        reverses_transaction_id=t.reverses_transaction_id,
        reversed_by_transaction_id=t.reversed_by_transaction_id,
        created_at=t.created_at,
    )


@router.get("/{portfolio_id}/transactions", response_model=TransactionListResponse)
async def list_transactions(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    account_id: Optional[str] = Query(default=None),
    instrument_id: Optional[str] = Query(default=None),
    tx_type: Optional[TransactionType] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> TransactionListResponse:
    """List transaction history with optional filters."""
    try:
        txs, total = service.list_transactions(
            portfolio_id=portfolio_id,
            user_id=current_user.sub,
            account_id=account_id,
            instrument_id=instrument_id,
            tx_type=tx_type,
            limit=limit,
            offset=offset,
        )
        items = [_map_tx_to_response(t) for t in txs]
        return TransactionListResponse(items=items, total=total)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions/preview", response_model=TransactionPreviewResponse)
async def preview_transaction(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionCreateRequest,
) -> TransactionPreviewResponse:
    """Preview accounting and cash effects of a candidate transaction without posting."""
    try:
        return service.preview_transaction(portfolio_id, current_user.sub, payload)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def post_transaction(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionCreateRequest,
) -> TransactionResponse:
    """Post an immutable transaction to the portfolio ledger."""
    try:
        tx = service.post_transaction(portfolio_id, current_user.sub, payload)
        return _map_tx_to_response(tx)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    portfolio_id: str,
    transaction_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> TransactionResponse:
    """Retrieve details for a single posted transaction."""
    try:
        tx = service.get_transaction(portfolio_id, transaction_id, current_user.sub)
        return _map_tx_to_response(tx)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions/{transaction_id}/reverse", response_model=TransactionResponse)
async def reverse_transaction(
    portfolio_id: str,
    transaction_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionReverseRequest,
) -> TransactionResponse:
    """Controlled reversal of a posted transaction."""
    try:
        reversal = service.reverse_transaction(
            portfolio_id, transaction_id, current_user.sub, payload
        )
        return _map_tx_to_response(reversal)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/transactions/{transaction_id}/correct", response_model=TransactionResponse)
async def correct_transaction(
    portfolio_id: str,
    transaction_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    payload: TransactionCorrectRequest,
) -> TransactionResponse:
    """Controlled correction: atomically reverses original and posts replacement."""
    try:
        replacement = service.correct_transaction(
            portfolio_id, transaction_id, current_user.sub, payload
        )
        return _map_tx_to_response(replacement)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Holdings & Lots Endpoints
# ---------------------------------------------------------------------------


def _map_pos_to_response(p) -> PositionResponse:
    return PositionResponse(
        portfolio_id=p.portfolio_id,
        account_id=p.account_id,
        instrument_id=p.instrument_id,
        symbol=p.symbol,
        exchange=p.exchange,
        company_name=p.company_name,
        quantity=str(p.quantity),
        open_lot_count=p.open_lot_count,
        remaining_cost_basis=str(p.remaining_cost_basis),
        cost_basis_currency=p.cost_basis_currency,
        average_unit_cost=str(p.average_unit_cost) if p.average_unit_cost is not None else None,
        realized_pnl=str(p.realized_pnl),
        unrealized_pnl=str(p.unrealized_pnl) if p.unrealized_pnl is not None else None,
        as_of=p.as_of,
    )


@router.get("/{portfolio_id}/positions", response_model=PositionListResponse)
async def get_portfolio_positions(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PositionListResponse:
    """Get security positions derived deterministically from the transaction ledger."""
    try:
        positions = service.get_positions(portfolio_id, current_user.sub)
        items = [_map_pos_to_response(p) for p in positions]
        return PositionListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}/positions", response_model=PositionListResponse)
async def get_account_positions(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> PositionListResponse:
    """Get security positions for an individual account."""
    try:
        positions = service.get_positions(portfolio_id, current_user.sub, account_id=account_id)
        items = [_map_pos_to_response(p) for p in positions]
        return PositionListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/positions/{instrument_id}/lots", response_model=LotListResponse)
async def get_instrument_lots(
    portfolio_id: str,
    instrument_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    account_id: Optional[str] = Query(default=None),
) -> LotListResponse:
    """Get individual FIFO tax-lots for an instrument."""
    try:
        lots = service.get_lots(portfolio_id, current_user.sub, instrument_id, account_id=account_id)
        items = [
            LotResponse(
                id=l.id,
                portfolio_id=l.portfolio_id,
                account_id=l.account_id,
                instrument_id=l.instrument_id,
                acquisition_transaction_id=l.acquisition_transaction_id,
                acquisition_date=l.acquisition_date,
                original_quantity=str(l.original_quantity),
                remaining_quantity=str(l.remaining_quantity),
                unit_cost_basis=str(l.unit_cost_basis),
                total_cost_basis=str(l.total_cost_basis),
                currency=l.currency,
                is_fully_disposed=l.is_fully_disposed,
                disposed_at=l.disposed_at,
            )
            for l in lots
        ]
        return LotListResponse(items=items, total=len(items))
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Cash Endpoints
# ---------------------------------------------------------------------------


def _map_cb_to_response(c) -> CashBalanceResponse:
    return CashBalanceResponse(
        account_id=c.account_id,
        currency=c.currency,
        posted_cash=_fmt_2(c.posted_cash),
        settled_cash=_fmt_2(c.settled_cash),
        unsettled_receivable=_fmt_2(c.unsettled_receivable),
        unsettled_payable=_fmt_2(c.unsettled_payable),
        available_cash=_fmt_2(c.available_cash),
        as_of=c.as_of,
    )


@router.get("/{portfolio_id}/cash", response_model=list[CashBalanceResponse])
async def get_portfolio_cash(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> list[CashBalanceResponse]:
    """Get cash balances across all accounts in a portfolio."""
    try:
        bals = service.get_cash_balances(portfolio_id, current_user.sub)
        return [_map_cb_to_response(b) for b in bals]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}/cash", response_model=list[CashBalanceResponse])
async def get_account_cash(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> list[CashBalanceResponse]:
    """Get cash balances for a specific account."""
    try:
        bals = service.get_cash_balances(portfolio_id, current_user.sub, account_id=account_id)
        return [_map_cb_to_response(b) for b in bals]
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/accounts/{account_id}/cash-ledger", response_model=list[CashLedgerEntryResponse])
async def get_account_cash_ledger(
    portfolio_id: str,
    account_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> list[CashLedgerEntryResponse]:
    """Get detailed cash ledger audit entries for an account."""
    try:
        entries = service.get_cash_ledger(portfolio_id, current_user.sub, account_id=account_id)
        return [
            CashLedgerEntryResponse(
                id=e.id,
                account_id=e.account_id,
                transaction_id=e.transaction_id,
                currency=e.currency,
                amount=str(e.amount),
                balance_type=e.balance_type.value,
                effective_date=e.effective_date,
                description=e.description,
                created_at=e.created_at,
            )
            for e in entries
        ]
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Valuation Endpoints
# ---------------------------------------------------------------------------


def _map_val_to_response(val) -> ValuationResponse:
    pos_vals = [
        PositionValuationResponse(
            instrument_id=pv.instrument_id,
            symbol=pv.symbol,
            exchange=pv.exchange,
            quantity=str(pv.quantity),
            remaining_basis=str(pv.remaining_basis),
            basis_currency=pv.basis_currency,
            valuation_status=pv.valuation_status,
            quote_freshness=pv.quote_freshness,
            account_id=pv.account_id,
            company_name=pv.company_name,
            mark_price=str(pv.mark_price) if pv.mark_price is not None else None,
            price_currency=pv.price_currency,
            mark_as_of=pv.mark_as_of,
            mark_source=pv.mark_source,
            native_market_value=str(pv.native_market_value) if pv.native_market_value is not None else None,
            fx_rate_to_base=str(pv.fx_rate_to_base) if pv.fx_rate_to_base is not None else None,
            fx_pair=pv.fx_pair,
            fx_as_of=pv.fx_as_of,
            base_market_value=str(pv.base_market_value) if pv.base_market_value is not None else None,
            unrealized_pnl=str(pv.unrealized_pnl) if pv.unrealized_pnl is not None else None,
        )
        for pv in val.position_valuations
    ]
    cash_vals = [
        CashValuationResponse(
            account_id=cv.account_id,
            currency=cv.currency,
            posted_cash=str(cv.posted_cash),
            settled_cash=str(cv.settled_cash),
            unsettled_receivable=str(cv.unsettled_receivable),
            unsettled_payable=str(cv.unsettled_payable),
            available_cash=str(cv.available_cash),
            fx_rate_to_base=str(cv.fx_rate_to_base),
            base_cash_value=str(cv.base_cash_value),
            as_of=cv.as_of,
        )
        for cv in val.cash_valuations
    ]
    return ValuationResponse(
        id=val.id,
        portfolio_id=val.portfolio_id,
        as_of=val.as_of,
        base_currency=val.base_currency,
        valuation_status=val.valuation_status,
        known_valued_subtotal=str(val.known_valued_subtotal),
        verified_total_portfolio_value=str(val.verified_total_portfolio_value) if val.verified_total_portfolio_value is not None else None,
        total_positions_market_value=str(val.total_positions_market_value) if val.total_positions_market_value is not None else None,
        total_cash_market_value=str(val.total_cash_market_value),
        total_cost_basis=str(val.total_cost_basis),
        total_unrealized_pnl=str(val.total_unrealized_pnl) if val.total_unrealized_pnl is not None else None,
        total_realized_pnl=str(val.total_realized_pnl),
        missing_prices_count=val.missing_prices_count,
        missing_fx_count=val.missing_fx_count,
        stale_quotes_count=val.stale_quotes_count,
        position_valuations=pos_vals,
        cash_valuations=cash_vals,
        source_manifest=val.source_manifest,
        calculation_version=val.calculation_version,
        created_at=val.created_at,
    )


@router.get("/{portfolio_id}/valuation", response_model=ValuationResponse)
async def get_valuation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ValuationResponse:
    """Retrieve the latest marked portfolio valuation."""
    try:
        val = service.get_latest_valuation(portfolio_id, current_user.sub)
        return _map_val_to_response(val)
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/valuations", response_model=ValuationResponse, status_code=status.HTTP_201_CREATED)
async def recalculate_valuation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ValuationResponse:
    """Trigger an explicit recomputation of portfolio valuation."""
    try:
        val = service.calculate_portfolio_valuation(portfolio_id, current_user.sub)
        return _map_val_to_response(val)
    except Exception as e:
        _handle_error(e)


@router.get("/{portfolio_id}/valuations/{valuation_id}", response_model=ValuationResponse)
async def get_valuation_snapshot(
    portfolio_id: str,
    valuation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ValuationResponse:
    """Retrieve a specific historical valuation snapshot."""
    try:
        val = service.repository.get_valuation(valuation_id, current_user.sub)
        if not val or val.portfolio_id != portfolio_id:
            raise HTTPException(status_code=404, detail="Valuation snapshot not found.")
        return _map_val_to_response(val)
    except Exception as e:
        _handle_error(e)


# ---------------------------------------------------------------------------
# Reconciliation Endpoints
# ---------------------------------------------------------------------------


@router.get("/{portfolio_id}/reconciliation", response_model=ReconciliationResponse)
async def get_reconciliation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ReconciliationResponse:
    """Audit and verify ledger integrity and position balances."""
    try:
        rec = service.reconcile_portfolio(portfolio_id, current_user.sub)
        return ReconciliationResponse(
            portfolio_id=rec.portfolio_id,
            status=rec.status,
            reconciliation_timestamp=rec.reconciliation_timestamp,
            total_transactions_checked=rec.total_transactions_checked,
            total_lots_checked=rec.total_lots_checked,
            total_positions_checked=rec.total_positions_checked,
            total_cash_entries_checked=rec.total_cash_entries_checked,
            discrepancies=rec.discrepancies,
            warnings=rec.warnings,
            is_balanced=rec.is_balanced,
        )
    except Exception as e:
        _handle_error(e)


@router.post("/{portfolio_id}/reconciliation/check", response_model=ReconciliationResponse)
async def check_reconciliation(
    portfolio_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ReconciliationResponse:
    """Trigger explicit ledger reconciliation audit."""
    try:
        rec = service.reconcile_portfolio(portfolio_id, current_user.sub)
        return ReconciliationResponse(
            portfolio_id=rec.portfolio_id,
            status=rec.status,
            reconciliation_timestamp=rec.reconciliation_timestamp,
            total_transactions_checked=rec.total_transactions_checked,
            total_lots_checked=rec.total_lots_checked,
            total_positions_checked=rec.total_positions_checked,
            total_cash_entries_checked=rec.total_cash_entries_checked,
            discrepancies=rec.discrepancies,
            warnings=rec.warnings,
            is_balanced=rec.is_balanced,
        )
    except Exception as e:
        _handle_error(e)
