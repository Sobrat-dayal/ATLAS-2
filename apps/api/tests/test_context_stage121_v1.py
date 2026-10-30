"""
Comprehensive Backend Integration Tests for ATLAS Stage 121: Global Workspace Linking.

Validates:
1. Channel CRUD, ownership, and scope isolation (WORKSPACE vs. USER_APPLICATION).
2. Panel subscription / membership lifecycle and duplicate prevention.
3. Optimistic concurrency control on context state revisions.
4. Canonical entity resolution (Instruments, Companies, Portfolios, Benchmarks, Economic Series).
5. Cross-entity transformations (Instrument -> Company, Company -> Primary Listing, Portfolio -> Benchmark).
6. Event dispatching with deduplication, loop prevention, and monotonic revision validation.
7. REST API endpoints mounted under /context.
"""

import pytest
from atlas.auth import AuthPrincipal
from atlas.context.enums import (
    ContextDimension,
    ContextScope,
    SubscriptionMode,
    TransformationType,
)
from atlas.context.errors import (
    ContextChannelAccessDeniedError,
    ContextChannelLimitExceededError,
    ContextChannelNotFoundError,
    ContextEventStaleError,
    ContextMembershipDuplicateError,
    ContextRevisionConflictError,
)
from atlas.context.models import ContextSelectionEvent
from atlas.context.repository import ContextRepository
from atlas.context.service import ContextLinkingService
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers.context import get_context_service


@pytest.fixture
def repo() -> ContextRepository:
    return ContextRepository()


@pytest.fixture
def service(repo: ContextRepository) -> ContextLinkingService:
    return ContextLinkingService(repository=repo)


@pytest.fixture
def mock_principal() -> AuthPrincipal:
    return AuthPrincipal(
        sub="usr_quant_trader_121",
        email="trader@institutional.com",
        role="authenticated",
    )


@pytest.fixture
def api_client(mock_principal: AuthPrincipal, service: ContextLinkingService) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_context_service] = lambda: service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ---------------- 1. Channel Lifecycle & Ownership ----------------


def test_channel_lifecycle(service: ContextLinkingService):
    user_id = "usr_lead_analyst"

    # Create Channel
    ch = service.create_channel(
        user_id=user_id,
        name="Channel Alpha (Blue)",
        display_color_token="#3B82F6",
        workspace_id="ws_equity_101",
        scope=ContextScope.WORKSPACE,
        initial_context={"INSTRUMENT": "AAPL", "TIMEFRAME": "1D"},
    )
    assert ch.channel_id.startswith("chan_")
    assert ch.name == "Channel Alpha (Blue)"
    assert ch.revision == 1
    assert ch.context_snapshot["INSTRUMENT"] == "AAPL"

    # Get Channel
    fetched = service.get_channel(ch.channel_id, user_id)
    assert fetched.channel_id == ch.channel_id

    # Update Channel
    updated = service.update_channel(
        channel_id=ch.channel_id,
        user_id=user_id,
        name="Channel Alpha Prime",
        display_color_token="#2563EB",
    )
    assert updated.name == "Channel Alpha Prime"
    assert updated.display_color_token == "#2563EB"

    # List Channels
    channels = service.list_channels(user_id, workspace_id="ws_equity_101")
    assert any(c.channel_id == ch.channel_id for c in channels)

    # Delete Channel
    service.delete_channel(ch.channel_id, user_id)
    with pytest.raises(ContextChannelNotFoundError):
        service.get_channel(ch.channel_id, user_id)


def test_channel_user_isolation(service: ContextLinkingService):
    user_a = "usr_user_a"
    user_b = "usr_user_b"

    ch = service.create_channel(user_id=user_a, name="Private Channel A")

    # User B should be denied access to User A's channel
    with pytest.raises(ContextChannelAccessDeniedError):
        service.get_channel(ch.channel_id, user_b)

    with pytest.raises(ContextChannelAccessDeniedError):
        service.update_channel(ch.channel_id, user_b, name="Hacked Name")

    with pytest.raises(ContextChannelAccessDeniedError):
        service.delete_channel(ch.channel_id, user_b)


def test_channel_limit_enforcement(service: ContextLinkingService):
    user_id = "usr_heavy_builder"

    # Max channels per scope is 32
    for i in range(32):
        service.create_channel(user_id=user_id, name=f"Channel {i}", workspace_id="ws_dense")

    with pytest.raises(ContextChannelLimitExceededError):
        service.create_channel(
            user_id=user_id, name="Channel 33 (Exceeded)", workspace_id="ws_dense"
        )


# ---------------- 2. Subscriptions & Memberships ----------------


def test_membership_lifecycle(service: ContextLinkingService):
    user_id = "usr_trader_1"
    ch = service.create_channel(user_id=user_id, name="Group A")

    # Add Panel Subscriptions
    sub1 = service.add_membership(
        channel_id=ch.channel_id,
        user_id=user_id,
        panel_instance_id="panel_chart_1",
        mode=SubscriptionMode.SUBSCRIBE,
        inbound_dimensions=[ContextDimension.INSTRUMENT, ContextDimension.TIMEFRAME],
    )
    assert sub1.panel_instance_id == "panel_chart_1"
    assert sub1.mode == SubscriptionMode.SUBSCRIBE

    sub2 = service.add_membership(
        channel_id=ch.channel_id,
        user_id=user_id,
        panel_instance_id="panel_watchlist_1",
        mode=SubscriptionMode.PUBLISH,
        outbound_dimensions=[ContextDimension.INSTRUMENT],
    )
    assert sub2.panel_instance_id == "panel_watchlist_1"

    # Duplicate membership check
    with pytest.raises(ContextMembershipDuplicateError):
        service.add_membership(
            channel_id=ch.channel_id,
            user_id=user_id,
            panel_instance_id="panel_chart_1",
        )

    # List memberships
    memberships = service.list_memberships(ch.channel_id, user_id)
    assert len(memberships) == 2

    # Update membership
    updated = service.update_membership(
        subscription_id=sub1.subscription_id,
        user_id=user_id,
        mode=SubscriptionMode.BIDIRECTIONAL,
    )
    assert updated.mode == SubscriptionMode.BIDIRECTIONAL

    # Remove membership
    service.remove_membership(sub1.subscription_id, user_id)
    assert len(service.list_memberships(ch.channel_id, user_id)) == 1


# ---------------- 3. Concurrency & Optimistic Revisions ----------------


def test_context_state_optimistic_concurrency(service: ContextLinkingService):
    user_id = "usr_pm_concurrency"
    ch = service.create_channel(user_id=user_id, name="Synced Group")
    assert ch.revision == 1

    # First update succeeds
    updated = service.update_channel_state(
        channel_id=ch.channel_id,
        user_id=user_id,
        context_updates={"INSTRUMENT": "MSFT"},
        expected_revision=1,
    )
    assert updated.revision == 2
    assert updated.context_snapshot["INSTRUMENT"] == "MSFT"

    # Stale expected revision fails with conflict
    with pytest.raises(ContextRevisionConflictError):
        service.update_channel_state(
            channel_id=ch.channel_id,
            user_id=user_id,
            context_updates={"INSTRUMENT": "NVDA"},
            expected_revision=1,  # Stale! Server is at 2
        )


# ---------------- 4. Canonical Entity Resolution & Transformations ----------------


def test_canonical_entity_resolution(service: ContextLinkingService):
    # Instrument resolution
    aapl = service.resolve_entity("AAPL", entity_type="INSTRUMENT")
    assert aapl.entity_id == "inst_aapl_us"
    assert aapl.symbol == "AAPL"
    assert aapl.exchange == "NASDAQ"
    assert aapl.currency == "USD"

    # Company resolution
    apple = service.resolve_entity("comp_apple_us", entity_type="COMPANY")
    assert apple.entity_id == "comp_apple_us"
    assert "Apple" in apple.canonical_name

    # Portfolio resolution
    port = service.resolve_entity("port_institutional_alpha", entity_type="PORTFOLIO")
    assert port.entity_id == "port_institutional_alpha"
    assert port.currency == "USD"

    # Macro series resolution
    cpi = service.resolve_entity("CPI", entity_type="ECONOMIC_SERIES")
    assert cpi.entity_id == "CPI"
    assert cpi.country == "USA"


def test_cross_entity_transformations(service: ContextLinkingService):
    # Instrument -> Company
    comp = service.resolve_entity(
        query="AAPL",
        entity_type="INSTRUMENT",
        target_transformation=TransformationType.INSTRUMENT_TO_COMPANY,
    )
    assert comp.entity_type == "COMPANY"
    assert comp.entity_id == "comp_apple_us"

    # Company -> Primary Listing
    inst = service.resolve_entity(
        query="comp_microsoft_us",
        entity_type="COMPANY",
        target_transformation=TransformationType.COMPANY_TO_PRIMARY_LISTING,
    )
    assert inst.entity_type == "INSTRUMENT"
    assert inst.symbol == "MSFT"

    # Portfolio -> Benchmark
    bench = service.resolve_entity(
        query="port_institutional_alpha",
        entity_type="PORTFOLIO",
        target_transformation=TransformationType.PORTFOLIO_TO_BENCHMARK,
    )
    assert bench.entity_type == "BENCHMARK"
    assert bench.symbol == "SPX"


# ---------------- 5. Event Dispatching, Stale Dropping & Loop Prevention ----------------


def test_event_dispatch_to_compatible_subscribers(service: ContextLinkingService):
    user_id = "usr_dispatch_test"
    ch = service.create_channel(user_id=user_id, name="Test Dispatch Channel")

    # Add Publisher
    service.add_membership(
        channel_id=ch.channel_id,
        user_id=user_id,
        panel_instance_id="panel_screener_origin",
        mode=SubscriptionMode.PUBLISH,
        outbound_dimensions=[ContextDimension.INSTRUMENT],
    )

    # Add 2 Subscribers
    service.add_membership(
        channel_id=ch.channel_id,
        user_id=user_id,
        panel_instance_id="panel_chart_subscriber",
        mode=SubscriptionMode.SUBSCRIBE,
        inbound_dimensions=[ContextDimension.INSTRUMENT],
    )
    service.add_membership(
        channel_id=ch.channel_id,
        user_id=user_id,
        panel_instance_id="panel_news_subscriber",
        mode=SubscriptionMode.SUBSCRIBE,
        inbound_dimensions=[ContextDimension.INSTRUMENT],
    )

    # Add 1 Incompatible Subscriber (subscribes only to TIMEFRAME)
    service.add_membership(
        channel_id=ch.channel_id,
        user_id=user_id,
        panel_instance_id="panel_macro_subscriber",
        mode=SubscriptionMode.SUBSCRIBE,
        inbound_dimensions=[ContextDimension.TIMEFRAME],
    )

    # Dispatch INSTRUMENT Selection Event
    event = ContextSelectionEvent(
        origin_user_id=user_id,
        origin_panel_instance_id="panel_screener_origin",
        channel_id=ch.channel_id,
        dimension=ContextDimension.INSTRUMENT,
        canonical_target_id="inst_nvda_us",
        payload={"symbol": "NVDA"},
        context_revision=1,
    )

    res = service.dispatch_event(event)
    assert res["status"] == "DELIVERED"
    assert res["delivered_count"] == 2
    assert "panel_chart_subscriber" in res["delivered_panel_ids"]
    assert "panel_news_subscriber" in res["delivered_panel_ids"]
    assert "panel_macro_subscriber" not in res["delivered_panel_ids"]
    assert "panel_screener_origin" not in res["delivered_panel_ids"]


def test_stale_event_dropped(service: ContextLinkingService):
    user_id = "usr_stale_test"
    ch = service.create_channel(user_id=user_id, name="Stale Channel")

    # Advance channel revision to 3
    service.update_channel_state(ch.channel_id, user_id, {"INSTRUMENT": "AAPL"})
    service.update_channel_state(ch.channel_id, user_id, {"INSTRUMENT": "MSFT"})

    # Event with older revision 1 should raise ContextEventStaleError
    stale_event = ContextSelectionEvent(
        origin_user_id=user_id,
        channel_id=ch.channel_id,
        dimension=ContextDimension.INSTRUMENT,
        canonical_target_id="inst_aapl_us",
        context_revision=1,
    )

    with pytest.raises(ContextEventStaleError):
        service.dispatch_event(stale_event)


def test_event_deduplication(service: ContextLinkingService):
    user_id = "usr_dedup_test"
    ch = service.create_channel(user_id=user_id, name="Dedup Channel")

    event = ContextSelectionEvent(
        event_id="evt_fixed_unique_101",
        origin_user_id=user_id,
        channel_id=ch.channel_id,
        dimension=ContextDimension.INSTRUMENT,
        canonical_target_id="inst_aapl_us",
        context_revision=1,
    )

    # First dispatch delivers
    res1 = service.dispatch_event(event)
    assert res1["status"] == "DELIVERED"

    # Second dispatch with identical event_id is dropped as duplicate
    res2 = service.dispatch_event(event)
    assert res2["status"] == "DUPLICATE_DROPPED"
    assert res2["delivered_count"] == 0


# ---------------- 6. Capabilities Catalog ----------------


def test_capabilities_catalog(service: ContextLinkingService):
    caps = service.get_capabilities()
    assert len(caps) >= 14

    chart_cap = service.get_capabilities(panel_type_id="INSTRUMENT_CHART")
    assert len(chart_cap) == 1
    assert ContextDimension.INSTRUMENT in chart_cap[0].subscribable_dimensions
    assert ContextDimension.TIMEFRAME in chart_cap[0].subscribable_dimensions
    assert chart_cap[0].supports_as_of is True


# ---------------- 7. REST API Endpoints ----------------


def test_api_context_endpoints(api_client: TestClient):
    # 1. List channels (seeds defaults if empty)
    res = api_client.get("/api/v1/context/channels")
    assert res.status_code == 200

    # 2. Create channel
    res = api_client.post(
        "/api/v1/context/channels",
        json={
            "name": "Integration Link Alpha",
            "display_color_token": "#3B82F6",
            "scope": "WORKSPACE",
            "workspace_id": "ws_integration_test",
            "initial_context": {"INSTRUMENT": "AAPL"},
        },
    )
    assert res.status_code == 201
    data = res.json()
    channel_id = data["channel_id"]
    assert data["name"] == "Integration Link Alpha"

    # 3. Add panel membership
    res = api_client.post(
        f"/api/v1/context/channels/{channel_id}/memberships",
        json={
            "panel_instance_id": "panel_chart_api_1",
            "mode": "BIDIRECTIONAL",
            "inbound_dimensions": ["INSTRUMENT", "TIMEFRAME"],
        },
    )
    assert res.status_code == 201
    sub_id = res.json()["subscription_id"]
    assert sub_id.startswith("sub_")

    # 4. Update channel state
    res = api_client.put(
        f"/api/v1/context/channels/{channel_id}/state",
        json={
            "context_updates": {"INSTRUMENT": "MSFT", "TIMEFRAME": "1D"},
            "expected_revision": 1,
        },
    )
    assert res.status_code == 200
    assert res.json()["revision"] == 2

    # 5. Entity resolution endpoint
    res = api_client.post(
        "/api/v1/context/resolve",
        json={
            "query": "AAPL",
            "entity_type": "INSTRUMENT",
            "target_transformation": "INSTRUMENT_TO_COMPANY",
        },
    )
    assert res.status_code == 200
    assert res.json()["entity_type"] == "COMPANY"
    assert res.json()["entity_id"] == "comp_apple_us"

    # 6. Capabilities endpoint
    res = api_client.get("/api/v1/context/capabilities")
    assert res.status_code == 200
    assert len(res.json()) >= 14

    # 7. Dispatch event
    res = api_client.post(
        "/api/v1/context/events",
        json={
            "channel_id": channel_id,
            "dimension": "INSTRUMENT",
            "canonical_target_id": "inst_nvda_us",
            "origin_panel_instance_id": "panel_other_origin",
            "context_revision": 2,
            "payload": {"symbol": "NVDA"},
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "DELIVERED"
    assert "panel_chart_api_1" in res.json()["delivered_panel_ids"]
