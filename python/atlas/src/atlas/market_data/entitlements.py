from typing import Optional, Set, Tuple
from uuid import UUID

from atlas.auth.principal import AuthPrincipal
from atlas.realtime.websocket.models import QuoteSubscriptionKey


class MarketDataEntitlementService:
    """
    Validates market data streaming entitlements for a principal and subscription series (Stage 78).
    Enforces user tier, role-based licensing, and instrument-specific market data rules.
    """

    def __init__(self, restricted_instruments: Optional[Set[UUID]] = None):
        self.restricted_instruments = restricted_instruments or set()

    async def check_subscription_entitlement(
        self,
        principal: Optional[AuthPrincipal],
        series: QuoteSubscriptionKey,
    ) -> Tuple[bool, str]:
        """
        Validates whether the user is entitled to subscribe to the given series.
        Returns (is_authorized, reason).
        """
        if not principal:
            return False, "UNAUTHENTICATED: Principal required"

        claims = principal.raw_claims or {}
        user_meta = claims.get("user_metadata", {})
        tier = user_meta.get("market_data_tier", principal.role)

        # 1. Delayed-only users cannot stream unrestricted realtime quotes
        if tier == "delayed_only" or principal.role == "delayed_user":
            if series.variant is None or series.variant == "realtime":
                return False, "ENTITLEMENT_DENIED: User has delayed-only entitlement"

        # 2. Check restricted instruments (e.g. Level 2 / special exchange licensing required)
        if series.instrument_entity_id in self.restricted_instruments:
            if tier not in ("institutional", "professional", "admin"):
                return False, "ENTITLEMENT_DENIED: Professional Level 2 license required"

        return True, "AUTHORIZED"
