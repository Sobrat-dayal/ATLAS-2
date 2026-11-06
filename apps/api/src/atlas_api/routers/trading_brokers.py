"""FastAPI REST Router for Broker Sandbox Abstraction (Stage 145).

STRICT SANDBOX ONLY — Real-money and live broker order execution are categorically blocked.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas.auth import AuthPrincipal
from atlas.trading.brokers import (
    BrokerConnectionRegistry,
    BrokerExecutionGateway,
    BrokerProviderRegistry,
    NormalizedOrderRequest,
    SecretVault,
)
from atlas.trading.brokers.domain import (
    BrokerCapability,
    BrokerEnvironment,
    ProviderStatus,
)
from atlas.trading.brokers.errors import (
    BrokerNotFoundError,
    ConnectionNotFoundError,
    CrossTenantConnectionError,
    LiveBrokerBlockedError,
    SandboxFirewallError,
    UnsupportedCapabilityError,
)
from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/trading/brokers", tags=["Trading - Broker Sandbox"])

# Singleton instances for sandbox broker management
_provider_registry = BrokerProviderRegistry()
_vault = SecretVault(Fernet.generate_key())
_connection_registry = BrokerConnectionRegistry(_provider_registry, _vault)


def get_broker_registries() -> tuple[BrokerProviderRegistry, BrokerConnectionRegistry]:
    return _provider_registry, _connection_registry


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    tenant_id = str(principal.raw_claims.get("tenant_id", principal.sub))
    owner_id = principal.user_id
    return tenant_id, owner_id


# Schemas
class CreateBrokerConnectionRequest(BaseModel):
    provider_id: str = Field(..., description="ALPACA_PAPER, UPSTOX_SANDBOX, TRADIER_SANDBOX, etc.")
    secret: str = Field(..., min_length=4, description="Sandbox API secret or token")
    account_id: str = Field(default="sandbox-acc-default")
    display_name: Optional[str] = None


class BrokerOrderPreviewRequest(BaseModel):
    connection_id: str
    symbol: str
    side: str = Field(..., description="BUY or SELL")
    order_type: str = Field(default="MARKET")
    quantity: float = Field(..., gt=0.0)
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = Field(default="DAY")
    client_order_id: Optional[str] = None


class BrokerOrderSubmitRequest(BaseModel):
    connection_id: str
    symbol: str
    side: str = Field(..., description="BUY or SELL")
    order_type: str = Field(default="MARKET")
    quantity: float = Field(..., gt=0.0)
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = Field(default="DAY")
    client_order_id: Optional[str] = None


@router.get("/providers")
def list_providers(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    regs: Annotated[
        tuple[BrokerProviderRegistry, BrokerConnectionRegistry],
        Depends(get_broker_registries),
    ],
) -> List[Dict[str, Any]]:
    providers, _ = regs
    return [
        {
            "provider_id": p.provider_id,
            "display_name": p.display_name,
            "environment": p.environment.value,
            "execution_host": p.execution_host,
            "allowed_hosts": list(p.allowed_hosts),
            "status": p.status.value,
            "is_sandbox": True,
            "capabilities": {
                "supports_order_preview": p.capabilities.supports(BrokerCapability.ORDER_PREVIEW),
                "supports_order_submit": p.capabilities.supports(BrokerCapability.ORDER_SUBMIT),
                "supports_order_cancel": p.capabilities.supports(BrokerCapability.ORDER_CANCEL),
                "supports_order_read": p.capabilities.supports(BrokerCapability.ORDER_READ),
                "supports_order_modify": p.capabilities.supports(BrokerCapability.ORDER_MODIFY),
            },
        }
        for p in providers.list()
    ]


@router.get("/connections")
def list_connections(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    regs: Annotated[
        tuple[BrokerProviderRegistry, BrokerConnectionRegistry],
        Depends(get_broker_registries),
    ],
) -> List[Dict[str, Any]]:
    tenant_id, _ = _identity(principal)
    _, connections = regs
    conns = [c for c in connections._connections.values() if c.tenant_id == tenant_id]
    return [
        {
            "connection_id": c.connection_id,
            "tenant_id": c.tenant_id,
            "provider_id": c.provider_id,
            "account_id": c.account_id,
            "environment": c.environment.value,
            "status": c.status.value,
            "created_at": c.created_at.isoformat(),
            "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None,
        }
        for c in conns
    ]


@router.post("/connections", status_code=status.HTTP_201_CREATED)
def create_connection(
    req: CreateBrokerConnectionRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    regs: Annotated[
        tuple[BrokerProviderRegistry, BrokerConnectionRegistry],
        Depends(get_broker_registries),
    ],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    providers, connections = regs
    try:
        conn = connections.create(
            tenant_id=tenant_id,
            provider_id=req.provider_id.upper(),
            secret=req.secret,
            account_id=req.account_id,
        )
        return {
            "connection_id": conn.connection_id,
            "tenant_id": conn.tenant_id,
            "provider_id": conn.provider_id,
            "account_id": conn.account_id,
            "environment": conn.environment.value,
            "status": conn.status.value,
            "created_at": conn.created_at.isoformat(),
        }
    except (BrokerNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/connections/{connection_id}/verify")
def verify_connection(
    connection_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    regs: Annotated[
        tuple[BrokerProviderRegistry, BrokerConnectionRegistry],
        Depends(get_broker_registries),
    ],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    providers, connections = regs
    try:
        conn = connections.get(connection_id, tenant_id)
    except ConnectionNotFoundError:
        raise HTTPException(status_code=404, detail="Broker connection not found.")
    except CrossTenantConnectionError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant connection access.")

    adapter = providers.create_adapter(conn)
    verified = adapter.validate_connection()
    updated = connections.mark_verified(connection_id, tenant_id, verified.status)

    return {
        "connection_id": connection_id,
        "status": updated.status.value,
        "last_verified_at": updated.last_verified_at.isoformat() if updated.last_verified_at else None,
    }


@router.post("/orders/preview")
def preview_broker_order(
    req: BrokerOrderPreviewRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    regs: Annotated[
        tuple[BrokerProviderRegistry, BrokerConnectionRegistry],
        Depends(get_broker_registries),
    ],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    providers, connections = regs
    try:
        conn = connections.get(req.connection_id, tenant_id)
    except ConnectionNotFoundError:
        raise HTTPException(status_code=404, detail="Broker connection not found.")
    except CrossTenantConnectionError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")

    adapter = providers.create_adapter(conn)
    gateway = BrokerExecutionGateway(adapter)

    order_req = NormalizedOrderRequest(
        symbol=req.symbol.upper(),
        side=req.side.upper(),
        order_type=req.order_type.upper(),
        quantity=req.quantity,
        limit_price=req.limit_price,
        stop_price=req.stop_price,
        time_in_force=req.time_in_force,
        client_order_id=req.client_order_id or f"prev-{req.symbol}",
    )

    try:
        preview = gateway.preview(order_req)
        return {"preview": preview, "sandbox_environment": True}
    except SandboxFirewallError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LiveBrokerBlockedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UnsupportedCapabilityError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/submit", status_code=status.HTTP_201_CREATED)
def submit_broker_order(
    req: BrokerOrderSubmitRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    regs: Annotated[
        tuple[BrokerProviderRegistry, BrokerConnectionRegistry],
        Depends(get_broker_registries),
    ],
) -> Dict[str, Any]:
    tenant_id, _ = _identity(principal)
    providers, connections = regs
    try:
        conn = connections.get(req.connection_id, tenant_id)
    except ConnectionNotFoundError:
        raise HTTPException(status_code=404, detail="Broker connection not found.")
    except CrossTenantConnectionError:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access.")

    adapter = providers.create_adapter(conn)
    gateway = BrokerExecutionGateway(adapter)

    order_req = NormalizedOrderRequest(
        symbol=req.symbol.upper(),
        side=req.side.upper(),
        order_type=req.order_type.upper(),
        quantity=req.quantity,
        limit_price=req.limit_price,
        stop_price=req.stop_price,
        time_in_force=req.time_in_force,
        client_order_id=req.client_order_id or f"ord-{req.symbol}",
    )

    try:
        order = gateway.submit(order_req)
        return {
            "external_order_id": order.external_order_id,
            "provider_id": order.provider_id,
            "client_order_id": order.client_order_id,
            "symbol": req.symbol.upper(),
            "side": req.side.upper(),
            "order_type": req.order_type.upper(),
            "quantity": req.quantity,
            "status": order.status,
            "is_sandbox": True,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
        }
    except SandboxFirewallError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LiveBrokerBlockedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UnsupportedCapabilityError as e:
        raise HTTPException(status_code=400, detail=str(e))
