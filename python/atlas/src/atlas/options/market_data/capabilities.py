"""Provider Capabilities and Entitlements for Options Market Data (Stage 141).

Enforces authorized access, delayed vs real-time rights, and dynamic source revocation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class OptionsProviderCapabilities(BaseModel):
    """Registered capabilities and supported market dimensions for an options data feed."""
    provider_id: str
    name: str
    markets: List[str]
    has_contract_discovery: bool = True
    has_realtime_quotes: bool = False
    has_delayed_quotes: bool = True
    delay_minutes: int = 15
    has_volume: bool = True
    has_open_interest: bool = True
    has_implied_volatility: bool = True
    has_greeks: bool = True
    has_historical_chains: bool = True
    redistribution_licensed: bool = False


CANONICAL_PROVIDERS: Dict[str, OptionsProviderCapabilities] = {
    "SRC_CBOE_AUTHORIZED": OptionsProviderCapabilities(
        provider_id="SRC_CBOE_AUTHORIZED",
        name="CBOE LiveVol Market Data Feed",
        markets=["US_OPTIONS"],
        has_realtime_quotes=True,
        has_delayed_quotes=True,
        delay_minutes=0,
        has_volume=True,
        has_open_interest=True,
        has_implied_volatility=True,
        has_greeks=True,
        has_historical_chains=True,
    ),
    "SRC_DELAYED_PUBLIC_OPRA": OptionsProviderCapabilities(
        provider_id="SRC_DELAYED_PUBLIC_OPRA",
        name="OPRA 15-Minute Delayed Options Feed",
        markets=["US_OPTIONS"],
        has_realtime_quotes=False,
        has_delayed_quotes=True,
        delay_minutes=15,
        has_volume=True,
        has_open_interest=True,
        has_implied_volatility=True,
        has_greeks=False,  # Provider does not supply Greeks! (Fixture L)
        has_historical_chains=True,
    ),
    "SRC_NSE_INDIA_DERIVATIVES": OptionsProviderCapabilities(
        provider_id="SRC_NSE_INDIA_DERIVATIVES",
        name="NSE India Equity Derivatives Feed",
        markets=["NSE_DERIVATIVES"],
        has_realtime_quotes=False,
        has_delayed_quotes=True,
        delay_minutes=5,
        has_volume=True,
        has_open_interest=True,
        has_implied_volatility=True,
        has_greeks=True,
        has_historical_chains=True,
    ),
}


class OptionsEntitlementRegistry:
    """Manages active user/tenant market data entitlements and revocations."""

    def __init__(self):
        # Default granted entitlements
        self._granted_sources: Set[str] = {"SRC_CBOE_AUTHORIZED", "SRC_DELAYED_PUBLIC_OPRA", "SRC_NSE_INDIA_DERIVATIVES"}
        self._revoked_sources: Set[str] = set()

    def is_entitled(self, source_id: str) -> bool:
        if source_id in self._revoked_sources:
            return False
        return source_id in self._granted_sources

    def revoke_source(self, source_id: str) -> None:
        """Revoke a market data feed license (Fixture Q)."""
        self._revoked_sources.add(source_id)

    def restore_source(self, source_id: str) -> None:
        self._revoked_sources.discard(source_id)
        self._granted_sources.add(source_id)

