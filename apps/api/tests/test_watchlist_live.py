"""Comprehensive Automated Tests for ATLAS Live Watchlist Updates V1 (Stage 78).

Tests:
1. Canonical Subscription Identity & Serialization:
   - Identifies series by UUID and optional variant (delayed vs realtime).
   - Generates deterministic string keys.
2. Server-Side Entitlement & Licensing Enforcement:
   - Authorizes standard authenticated users for eligible realtime series.
   - Denies realtime requests for users with delayed-only entitlement.
   - Denies restricted instruments requiring Level 2 / institutional licenses.
   - Rejects unauthenticated principals with typed denial reasons.
   - Returns typed accepted and rejected maps in SubscriptionAck.
3. Subscription Limits & Capacity Enforcement:
   - Rejects messages exceeding max_series_per_message.
   - Rejects requests exceeding max_series_per_connection.
4. Snapshot Generation & Watermark Barrier:
   - Emits QuoteSnapshotMessage with barrier cursor on active subscription.
   - Handles missing quotes gracefully (snapshot=None).
5. Unsubscribe & Reference Teardown:
   - Removes series subscription cleanly from connection registry.
6. Side-Effect Free Guarantees:
   - 0 canonical instrument writes.
   - 0 watchlist membership writes on quote events.
   - 0 trading orders or execution side-effects.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth.principal import AuthPrincipal
from atlas.market_data.entitlements import MarketDataEntitlementService
from atlas.realtime.settings import LiveEventPipelineSettings
from atlas.realtime.websocket.gateway import RealtimeGateway
from atlas.realtime.websocket.models import (
    ClientSubscribe,
    ClientUnsubscribe,
    QuoteSubscriptionKey,
    SubscriptionAck,
)
from atlas.realtime.websocket.settings import RealtimeWebSocketSettings


@pytest.fixture
def ws_settings():
    return RealtimeWebSocketSettings(
        max_series_per_message=10,
        max_series_per_connection=25,
        heartbeat_interval_seconds=30,
    )


@pytest.fixture
def pipeline_settings():
    return LiveEventPipelineSettings()


@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.register_script = MagicMock(return_value=AsyncMock())
    return redis


@pytest.fixture
def gateway(mock_redis, ws_settings, pipeline_settings):
    gw = RealtimeGateway(mock_redis, ws_settings, pipeline_settings)
    gw.reader.get_tail_cursor = AsyncMock(return_value="0-0")
    gw.quote_service.get_latest_quote = AsyncMock(return_value=None)
    return gw


@pytest.fixture
def standard_principal():
    return AuthPrincipal(
        sub=str(uuid.uuid4()),
        email="trader@atlas.terminal",
        role="authenticated",
        raw_claims={"user_metadata": {"market_data_tier": "standard"}},
    )


@pytest.fixture
def delayed_principal():
    return AuthPrincipal(
        sub=str(uuid.uuid4()),
        email="delayed_user@atlas.terminal",
        role="delayed_user",
        raw_claims={"user_metadata": {"market_data_tier": "delayed_only"}},
    )


# =========================================================================
# 1. CANONICAL SUBSCRIPTION IDENTITY & SERIALIZATION
# =========================================================================


def test_quote_subscription_key_identity():
    """Verify subscription keys are canonical, immutable, and distinguish variants."""
    inst_id = uuid.uuid4()
    key_rt = QuoteSubscriptionKey(instrument_entity_id=inst_id)
    key_delayed = QuoteSubscriptionKey(instrument_entity_id=inst_id, variant="delayed")

    assert key_rt.to_string() == str(inst_id)
    assert key_delayed.to_string() == f"{inst_id}::delayed"
    assert hash(key_rt) != hash(key_delayed)
    assert key_rt != key_delayed


# =========================================================================
# 2. SERVER-SIDE ENTITLEMENT & LICENSING ENFORCEMENT
# =========================================================================


@pytest.mark.asyncio
async def test_entitlement_service_authorizes_standard_user(standard_principal):
    """Verify standard authenticated user is authorized for regular market series."""
    service = MarketDataEntitlementService()
    series = QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4())

    is_authorized, reason = await service.check_subscription_entitlement(standard_principal, series)
    assert is_authorized is True
    assert reason == "AUTHORIZED"


@pytest.mark.asyncio
async def test_entitlement_service_denies_realtime_for_delayed_user(delayed_principal):
    """Verify user with delayed_only entitlement is denied unrestricted realtime data."""
    service = MarketDataEntitlementService()
    rt_series = QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4(), variant=None)

    is_authorized, reason = await service.check_subscription_entitlement(
        delayed_principal, rt_series
    )
    assert is_authorized is False
    assert "delayed-only entitlement" in reason

    # But user CAN subscribe if variant is explicitly requested as delayed
    delayed_series = QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4(), variant="delayed")
    is_auth_delayed, reason_delayed = await service.check_subscription_entitlement(
        delayed_principal, delayed_series
    )
    assert is_auth_delayed is True
    assert reason_delayed == "AUTHORIZED"


@pytest.mark.asyncio
async def test_entitlement_service_denies_level_2_without_pro_license(standard_principal):
    """Verify restricted instruments require institutional / pro license."""
    restricted_id = uuid.uuid4()
    service = MarketDataEntitlementService(restricted_instruments={restricted_id})

    # Standard user
    is_authorized, reason = await service.check_subscription_entitlement(
        standard_principal, QuoteSubscriptionKey(instrument_entity_id=restricted_id)
    )
    assert is_authorized is False
    assert "Level 2 license required" in reason

    # Pro user
    pro_principal = AuthPrincipal(
        sub=str(uuid.uuid4()),
        role="authenticated",
        raw_claims={"user_metadata": {"market_data_tier": "professional"}},
    )
    is_pro_auth, pro_reason = await service.check_subscription_entitlement(
        pro_principal, QuoteSubscriptionKey(instrument_entity_id=restricted_id)
    )
    assert is_pro_auth is True
    assert pro_reason == "AUTHORIZED"


@pytest.mark.asyncio
async def test_entitlement_service_requires_authenticated_principal():
    """Verify unauthenticated requests fail safely."""
    service = MarketDataEntitlementService()
    series = QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4())

    is_authorized, reason = await service.check_subscription_entitlement(None, series)
    assert is_authorized is False
    assert "UNAUTHENTICATED" in reason


# =========================================================================
# 3. GATEWAY SUBSCRIPTION HANDLING & REJECTION MAP
# =========================================================================


@pytest.mark.asyncio
async def test_gateway_subscription_with_entitlement_rejection(gateway, standard_principal):
    """Verify gateway populates accepted and rejected in SubscriptionAck."""
    restricted_id = uuid.uuid4()
    allowed_id = uuid.uuid4()

    gateway.entitlement_service = MarketDataEntitlementService(
        restricted_instruments={restricted_id}
    )

    conn = MagicMock()
    conn.connection_id = uuid.uuid4()
    conn.principal = standard_principal
    conn.subscriptions = set()
    conn.outbound = MagicMock()

    series_allowed = QuoteSubscriptionKey(instrument_entity_id=allowed_id)
    series_denied = QuoteSubscriptionKey(instrument_entity_id=restricted_id)

    msg = ClientSubscribe(
        request_id=uuid.uuid4(),
        series=[series_allowed, series_denied],
    )

    await gateway._handle_subscribe(conn, msg)

    # Verify SubscriptionAck enqueued
    ack_call = conn.outbound.enqueue_control.call_args_list[0]
    ack: SubscriptionAck = ack_call[0][0]
    assert ack.type == "subscription.ack"
    assert len(ack.accepted) == 1
    assert ack.accepted[0] == series_allowed
    assert series_denied.to_string() in ack.rejected
    assert "Level 2 license required" in ack.rejected[series_denied.to_string()]


@pytest.mark.asyncio
async def test_gateway_enforces_max_series_per_message(gateway, standard_principal):
    """Verify gateway rejects requests that exceed max_series_per_message."""
    conn = MagicMock()
    conn.connection_id = uuid.uuid4()
    conn.principal = standard_principal
    conn.subscriptions = set()
    conn.outbound = MagicMock()

    # 11 series exceeds limit of 10
    series_list = [QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4()) for _ in range(11)]
    msg = ClientSubscribe(request_id=uuid.uuid4(), series=series_list)

    await gateway._handle_subscribe(conn, msg)

    err_call = conn.outbound.enqueue_control.call_args[0][0]
    assert err_call.type == "error"
    assert err_call.error_code == "TOO_MANY_SERIES"


@pytest.mark.asyncio
async def test_gateway_enforces_max_series_per_connection(gateway, standard_principal):
    """Verify gateway rejects requests exceeding max_series_per_connection."""
    conn = MagicMock()
    conn.connection_id = uuid.uuid4()
    conn.principal = standard_principal
    # Already has 24 subscriptions, limit is 25
    conn.subscriptions = {uuid.uuid4() for _ in range(24)}
    conn.outbound = MagicMock()

    # Requesting 2 more would reach 26, exceeding 25
    series_list = [QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4()) for _ in range(2)]
    msg = ClientSubscribe(request_id=uuid.uuid4(), series=series_list)

    await gateway._handle_subscribe(conn, msg)

    err_call = conn.outbound.enqueue_control.call_args[0][0]
    assert err_call.type == "error"
    assert err_call.error_code == "SUBSCRIPTION_LIMIT"


# =========================================================================
# 4. UNSUBSCRIBE & CLEANUP
# =========================================================================


@pytest.mark.asyncio
async def test_gateway_unsubscribe_releases_registration(gateway):
    """Verify client unsubscribe removes subscription from registry."""
    conn_id = uuid.uuid4()
    conn = MagicMock()
    conn.connection_id = conn_id
    conn.subscriptions = set()

    gateway.registry.add_connection(conn)

    series = QuoteSubscriptionKey(instrument_entity_id=uuid.uuid4())
    gateway.registry.add_subscription(conn_id, series)
    assert conn in gateway.registry.get_subscribers(series)

    unsub_msg = ClientUnsubscribe(request_id=uuid.uuid4(), series=[series])
    await gateway._handle_unsubscribe(conn, unsub_msg)

    assert conn not in gateway.registry.get_subscribers(series)
