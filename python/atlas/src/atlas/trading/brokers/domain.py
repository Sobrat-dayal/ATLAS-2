"""Typed contracts for external broker sandbox integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class BrokerEnvironment(str, Enum):
    SANDBOX = "SANDBOX"
    PRODUCTION = "PRODUCTION"


class ProviderStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    VERIFIED_WITH_MOCK = "VERIFIED_WITH_MOCK"
    VERIFIED_WITH_PROVIDER_SANDBOX = "VERIFIED_WITH_PROVIDER_SANDBOX"
    CONNECTED = "CONNECTED"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"
    NEEDS_CREDENTIALS = "NEEDS_CREDENTIALS"
    UNSUPPORTED = "UNSUPPORTED"


class BrokerCapability(str, Enum):
    ACCOUNT_READ = "ACCOUNT_READ"
    BALANCE_READ = "BALANCE_READ"
    POSITION_READ = "POSITION_READ"
    INSTRUMENT_RESOLVE = "INSTRUMENT_RESOLVE"
    ORDER_PREVIEW = "ORDER_PREVIEW"
    ORDER_SUBMIT = "ORDER_SUBMIT"
    ORDER_MODIFY = "ORDER_MODIFY"
    ORDER_CANCEL = "ORDER_CANCEL"
    ORDER_READ = "ORDER_READ"
    FILL_READ = "FILL_READ"
    STREAMING = "STREAMING"
    WEBHOOKS = "WEBHOOKS"
    MULTI_LEG_OPTIONS = "MULTI_LEG_OPTIONS"


@dataclass(frozen=True)
class BrokerCapabilities:
    provider_id: str
    environment: BrokerEnvironment
    capabilities: frozenset[BrokerCapability] = frozenset()
    asset_classes: frozenset[str] = frozenset()
    order_types: frozenset[str] = frozenset()
    time_in_force: frozenset[str] = frozenset()
    authentication_method: str = "api_key"
    supports_fractional_quantity: bool = False
    documentation_version: str = "unknown"
    last_verified_at: datetime | None = None

    def supports(self, capability: BrokerCapability) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class BrokerProvider:
    provider_id: str
    display_name: str
    environment: BrokerEnvironment
    execution_host: str
    allowed_hosts: frozenset[str]
    capabilities: BrokerCapabilities
    status: ProviderStatus = ProviderStatus.IMPLEMENTED

    def __post_init__(self) -> None:
        if self.environment is not BrokerEnvironment.SANDBOX:
            raise ValueError("Stage 145 providers must use SANDBOX environment.")
        if self.execution_host not in self.allowed_hosts:
            raise ValueError("execution_host must be in allowed_hosts.")


@dataclass(frozen=True)
class BrokerConnection:
    connection_id: str
    tenant_id: str
    provider_id: str
    environment: BrokerEnvironment
    account_id: str | None
    created_at: datetime
    last_verified_at: datetime | None = None
    status: ProviderStatus = ProviderStatus.NEEDS_CREDENTIALS


@dataclass(frozen=True)
class NormalizedAccount:
    provider_id: str
    external_account_id: str
    currency: str
    status: str
    balances: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedOrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    limit_price: float | None = None
    stop_price: float | None = None
    time_in_force: str = "DAY"
    client_order_id: str | None = None


@dataclass(frozen=True)
class NormalizedOrder:
    provider_id: str
    external_order_id: str | None
    client_order_id: str | None
    status: str
    submitted_at: datetime | None = None
    raw_status: str | None = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
