"""FastAPI REST Router for Paper Trading Simulation Engine (Stage 144).

PAPER TRADING ONLY — All accounts and executions are strictly simulated.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from atlas.auth import AuthPrincipal
from atlas.trading.paper.domain import (
    AssetClass,
    PaperAccount,
    PaperOrder,
    PaperOrderSide,
    PaperOrderStatus,
    PaperOrderType,
    PaperPosition,
    TimeInForce,
)
from atlas.trading.paper.errors import (
    AccountNotFoundError,
    CrossTenantAccessError,
    DuplicateOrderError,
    KillSwitchActiveError,
    LiveBrokerFirewallError,
    MarketClosedError,
    OrderNotFoundError,
    RiskPolicyViolationError,
    StaleMarketDataError,
)
from atlas.trading.paper.service import AtlasPaperTradingService
from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/trading/paper", tags=["Trading - Paper Simulation"])

_paper_service = AtlasPaperTradingService()


def get_paper_service() -> AtlasPaperTradingService:
    return _paper_service


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    tenant_id = str(principal.raw_claims.get("tenant_id", principal.sub))
    owner_id = principal.user_id
    return tenant_id, owner_id


def _serialize_account(a: PaperAccount) -> Dict[str, Any]:
    return {
        "account_id": a.account_id,
        "tenant_id": a.tenant_id,
        "name": a.label,
        "label": a.label,
        "currency": a.currency,
        "initial_cash": a.initial_cash,
        "cash_balance": a.cash,
        "cash": a.cash,
        "buying_power": a.buying_power,
        "equity": a.equity,
        "margin_used": a.margin_used,
        "realized_pnl": a.daily_realized_pnl,
        "daily_realized_pnl": a.daily_realized_pnl,
        "is_active": a.is_active,
        "kill_switch_active": a.kill_switch_active,
        "description": a.description,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }


def _serialize_order(o: PaperOrder) -> Dict[str, Any]:
    avg_fill = None
    if o.fills:
        total_qty = sum(f.qty for f in o.fills)
        if total_qty > 0:
            avg_fill = sum(f.price * f.qty for f in o.fills) / total_qty
    return {
        "order_id": o.order_id,
        "account_id": o.account_id,
        "symbol": o.symbol,
        "side": o.side.value if hasattr(o.side, "value") else str(o.side),
        "order_type": o.order_type.value if hasattr(o.order_type, "value") else str(o.order_type),
        "quantity": o.qty,
        "qty": o.qty,
        "filled_quantity": o.filled_qty,
        "filled_qty": o.filled_qty,
        "status": o.status.value if hasattr(o.status, "value") else str(o.status),
        "limit_price": o.limit_price,
        "stop_price": o.stop_price,
        "average_fill_price": avg_fill,
        "asset_class": o.asset_class.value if hasattr(o.asset_class, "value") else str(o.asset_class),
        "time_in_force": o.time_in_force.value if hasattr(o.time_in_force, "value") else str(o.time_in_force),
        "client_order_id": o.client_order_id,
        "submitted_at": o.submitted_at.isoformat(),
        "updated_at": o.updated_at.isoformat(),
    }


def _serialize_position(p: PaperPosition) -> Dict[str, Any]:
    return {
        "position_id": p.position_id,
        "account_id": p.account_id,
        "symbol": p.symbol,
        "asset_class": p.asset_class.value if hasattr(p.asset_class, "value") else str(p.asset_class),
        "side": p.side.value if hasattr(p.side, "value") else str(p.side),
        "quantity": p.qty,
        "qty": p.qty,
        "cost_basis": p.avg_cost * p.qty,
        "average_entry_price": p.avg_cost,
        "avg_cost": p.avg_cost,
        "current_price": p.current_price,
        "market_value": p.current_price * p.qty,
        "unrealized_pnl": p.unrealized_pnl,
        "realized_pnl": p.realized_pnl,
        "opened_at": p.opened_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


# Schemas
class CreateAccountRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    initial_cash: float = Field(default=100_000.0, ge=1.0)
    currency: str = Field(default="USD")
    description: str = Field(default="")


class SubmitOrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    side: str = Field(..., description="BUY or SELL")
    order_type: str = Field(default="MARKET", description="MARKET, LIMIT, STOP, STOP_LIMIT")
    quantity: float = Field(..., gt=0.0)
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = Field(default="DAY")
    client_order_id: Optional[str] = None


class KillSwitchRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=256)


class FeedPriceRequest(BaseModel):
    symbol: str
    bid: float
    ask: float
    market_open: bool = True


@router.get("/accounts")
def list_accounts(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> List[Dict[str, Any]]:
    tenant_id, _ = _identity(principal)
    accounts = svc.list_accounts(tenant_id=tenant_id)
    return [_serialize_account(a) for a in accounts]


@router.post("/accounts", status_code=status.HTTP_201_CREATED)
def create_account(
    req: CreateAccountRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    acc = svc.create_account(
        tenant_id=tenant_id,
        label=req.name,
        initial_cash=req.initial_cash,
        currency=req.currency,
        description=req.description,
    )
    return _serialize_account(acc)


@router.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    try:
        acc = svc.get_account(account_id=account_id, tenant_id=tenant_id)
        return _serialize_account(acc)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Paper account not found.")
    except CrossTenantAccessError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant account access.")


@router.post("/accounts/{account_id}/kill-switch")
def activate_kill_switch(
    account_id: str,
    req: KillSwitchRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> Dict[str, Any]:
    tenant_id, owner_id = _identity(principal)
    try:
        evt = svc.activate_kill_switch(
            account_id=account_id,
            tenant_id=tenant_id,
            reason=req.reason,
            triggered_by=owner_id,
        )
        return {
            "account_id": account_id,
            "kill_switch_active": True,
            "reason": evt.reason,
            "triggered_by": evt.triggered_by,
            "triggered_at": evt.triggered_at.isoformat(),
        }
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Paper account not found.")
    except CrossTenantAccessError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")


@router.get("/accounts/{account_id}/orders")
def list_orders(
    account_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> List[Dict[str, Any]]:
    tenant_id, _ = _identity(principal)
    try:
        orders = svc.list_orders(account_id=account_id, tenant_id=tenant_id)
        return [_serialize_order(o) for o in orders]
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Paper account not found.")
    except CrossTenantAccessError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")


@router.post("/accounts/{account_id}/orders", status_code=status.HTTP_201_CREATED)
def submit_order(
    account_id: str,
    req: SubmitOrderRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    try:
        side = PaperOrderSide(req.side.upper())
        order_type = PaperOrderType(req.order_type.upper())
        tif = TimeInForce(req.time_in_force.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid order parameters: {e}")

    try:
        order = svc.submit_order(
            account_id=account_id,
            tenant_id=tenant_id,
            symbol=req.symbol.upper(),
            side=side,
            order_type=order_type,
            qty=req.quantity,
            limit_price=req.limit_price,
            stop_price=req.stop_price,
            time_in_force=tif,
            client_order_id=req.client_order_id,
        )
        return _serialize_order(order)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Paper account not found.")
    except CrossTenantAccessError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")
    except KillSwitchActiveError:
        raise HTTPException(status_code=400, detail="Account kill switch is active. Orders blocked.")
    except StaleMarketDataError as e:
        raise HTTPException(status_code=400, detail=f"Stale market data: {e}")
    except MarketClosedError as e:
        raise HTTPException(status_code=400, detail=f"Market is closed: {e}")
    except RiskPolicyViolationError as e:
        raise HTTPException(status_code=400, detail=f"Risk policy violation: {e}")
    except DuplicateOrderError as e:
        raise HTTPException(status_code=409, detail=f"Duplicate order: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accounts/{account_id}/orders/{order_id}/cancel")
def cancel_order(
    account_id: str,
    order_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    try:
        o = svc.cancel_order(order_id=order_id, account_id=account_id, tenant_id=tenant_id)
        return {"order_id": o.order_id, "status": o.status.value if hasattr(o.status, "value") else str(o.status)}
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Paper account not found.")
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Paper order not found.")
    except CrossTenantAccessError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")


@router.get("/accounts/{account_id}/positions")
def list_positions(
    account_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> List[Dict[str, Any]]:
    tenant_id, _ = _identity(principal)
    try:
        positions = svc.list_positions(account_id=account_id, tenant_id=tenant_id)
        return [_serialize_position(p) for p in positions]
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Paper account not found.")
    except CrossTenantAccessError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")


@router.post("/feed")
def feed_market_data(
    req: FeedPriceRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[AtlasPaperTradingService, Depends(get_paper_service)],
) -> Dict[str, Any]:
    try:
        svc.update_market_data(
            symbol=req.symbol.upper(),
            bid=req.bid,
            ask=req.ask,
            market_open=req.market_open,
        )
        return {"symbol": req.symbol.upper(), "bid": req.bid, "ask": req.ask, "status": "UPDATED"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
