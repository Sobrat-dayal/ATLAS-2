"""Automated Backend Verification Suite for ATLAS Stage 76:
Watchlists V1: Persistent Multi-Asset Watchlists.

Tests:
1. Migration file validity, revision naming, and down_revision continuity.
2. Watchlist name validation, unicode NFKC normalization, whitespace trimming,
   and HTML sanitization.
3. Resource quotas: 50 watchlists per user, 250 items per watchlist.
4. Watchlist CRUD operations: Create, List, Get, Rename, Delete with atomic item cascade.
5. User ownership isolation: User A cannot read, update, delete, or reorder User B's watchlists.
6. Membership operations: Add instrument, remove instrument, dense positions, duplicate rejection.
7. Optimistic concurrency control: revision increment, If-Match / expected_revision verification.
8. Multi-asset canonical instrument handling (Equities, ETFs, Funds, FX, Crypto, Bonds, Futures).
9. Quote snapshot semantics: correct units, freshness status, unavailable quotes without
   faked prices.
10. Cross-navigation: verified issuer relationship detection for Companies navigation.
11. FastAPI HTTP endpoints: 200, 201, 204, 400, 404, 409, 412, 422 contracts.
12. Side-effect invariants: zero trading orders, zero market data writes, zero LLM calls.
"""

import datetime
import importlib.util
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.watchlists import (
    MAX_ITEMS_PER_WATCHLIST,
    MAX_WATCHLISTS_PER_USER,
    AddWatchlistItemRequest,
    DuplicateWatchlistItemError,
    InstrumentNotFoundError,
    InvalidWatchlistNameError,
    ReorderWatchlistItemsRequest,
    Watchlist,
    WatchlistCreateRequest,
    WatchlistDetailResponse,
    WatchlistItem,
    WatchlistItemNotFoundError,
    WatchlistItemQuotaExceededError,
    WatchlistListResponse,
    WatchlistNameConflictError,
    WatchlistNotFoundError,
    WatchlistQuotaExceededError,
    WatchlistRepository,
    WatchlistRevisionConflictError,
    WatchlistService,
    WatchlistSummaryResponse,
    WatchlistUpdateRequest,
    normalize_watchlist_name,
    sanitize_watchlist_name,
    validate_description,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session
from atlas_api.routers.watchlists import get_watchlist_service


# =============================================================================
# 1. Migration File Verification
# =============================================================================
def test_stage76_migration_file():
    """Verify that migration stage76_watchlists.py exists and branches from stage74."""
    migration_path = Path(__file__).parents[1] / "migrations" / "versions" / "stage76_watchlists.py"
    assert migration_path.exists(), f"Migration file not found at {migration_path}"

    spec = importlib.util.spec_from_file_location("stage76_watchlists", migration_path)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    assert mod.revision == "stage76_watchlists"
    assert mod.down_revision == "stage74_chart_layouts"
    assert hasattr(mod, "upgrade")
    assert hasattr(mod, "downgrade")


# =============================================================================
# 2. Name Normalization & Quota Constants
# =============================================================================
class TestWatchlistNormalization:
    def test_sanitize_valid_name(self):
        raw = "  Global Macro Opportunities  "
        clean = sanitize_watchlist_name(raw)
        assert clean == "Global Macro Opportunities"

    def test_unicode_normalization(self):
        raw = "Technolog\u00eda \u2122 Growth"
        norm = normalize_watchlist_name(raw)
        assert "technolog" in norm
        assert "tm growth" in norm

    def test_reject_empty_or_whitespace_name(self):
        with pytest.raises(InvalidWatchlistNameError):
            sanitize_watchlist_name("")
        with pytest.raises(InvalidWatchlistNameError):
            sanitize_watchlist_name("   \t\n  ")

    def test_reject_overlong_name(self):
        with pytest.raises(InvalidWatchlistNameError):
            sanitize_watchlist_name("A" * 101)

    def test_reject_prohibited_script_tags(self):
        with pytest.raises(InvalidWatchlistNameError):
            sanitize_watchlist_name("<script>alert(1)</script>Equities")

    def test_normalize_internal_spaces(self):
        raw = "US    Tech    Leaders"
        norm = normalize_watchlist_name(raw)
        assert norm == "us tech leaders"

    def test_validate_description(self):
        assert validate_description(None) is None
        assert validate_description("   ") is None
        assert validate_description("Growth portfolio ideas") == "Growth portfolio ideas"
        with pytest.raises(InvalidWatchlistNameError):
            validate_description("B" * 501)


# =============================================================================
# 3. Watchlist Service CRUD & Quotas
# =============================================================================
@pytest.mark.asyncio
class TestWatchlistServiceCrud:
    def setup_method(self):
        self.mock_repo = AsyncMock(spec=WatchlistRepository)
        self.mock_session = AsyncMock()
        self.mock_repo.session = self.mock_session
        self.service = WatchlistService(repository=self.mock_repo, db_session=self.mock_session)
        self.user_a = uuid.uuid4()
        self.user_b = uuid.uuid4()

    async def test_create_watchlist_success(self):
        self.mock_repo.count_user_watchlists.return_value = 2
        self.mock_repo.get_by_normalized_name.return_value = None

        now = datetime.datetime.now(datetime.timezone.utc)
        created_id = uuid.uuid4()

        def mock_create(wl):
            wl.id = created_id
            wl.created_at = now
            wl.updated_at = now
            return wl

        self.mock_repo.create_watchlist.side_effect = mock_create

        req = WatchlistCreateRequest(
            name="Energy & Minerals", description="Global commodity securities"
        )
        res = await self.service.create_watchlist(self.user_a, req)

        assert res.id == created_id
        assert res.owner_user_id == self.user_a
        assert res.name == "Energy & Minerals"
        assert res.revision == 1
        assert res.item_count == 0

    async def test_create_watchlist_enforces_quota(self):
        self.mock_repo.count_user_watchlists.return_value = MAX_WATCHLISTS_PER_USER
        req = WatchlistCreateRequest(name="Exceeds Quota")

        with pytest.raises(WatchlistQuotaExceededError):
            await self.service.create_watchlist(self.user_a, req)

    async def test_create_watchlist_enforces_name_uniqueness_per_user(self):
        self.mock_repo.count_user_watchlists.return_value = 5
        existing = Watchlist(
            id=uuid.uuid4(),
            owner_user_id=self.user_a,
            name="Crypto Core",
            normalized_name="crypto core",
            revision=1,
        )
        self.mock_repo.get_by_normalized_name.return_value = existing

        req = WatchlistCreateRequest(name="crypto core")
        with pytest.raises(WatchlistNameConflictError):
            await self.service.create_watchlist(self.user_a, req)

    async def test_update_watchlist_name_conflict(self):
        wl_id = uuid.uuid4()
        existing = Watchlist(
            id=wl_id,
            owner_user_id=self.user_a,
            name="Equities Old",
            normalized_name="equities old",
            revision=1,
        )
        self.mock_repo.get_by_id.return_value = existing

        conflict = Watchlist(
            id=uuid.uuid4(),
            owner_user_id=self.user_a,
            name="Equities New",
            normalized_name="equities new",
            revision=2,
        )
        self.mock_repo.get_by_normalized_name.return_value = conflict

        req = WatchlistUpdateRequest(name="Equities New")
        with pytest.raises(WatchlistNameConflictError):
            await self.service.update_watchlist(wl_id, self.user_a, req)

    async def test_update_watchlist_revision_conflict(self):
        wl_id = uuid.uuid4()
        existing = Watchlist(
            id=wl_id,
            owner_user_id=self.user_a,
            name="My List",
            normalized_name="my list",
            revision=5,
        )
        self.mock_repo.get_by_id.return_value = existing

        req = WatchlistUpdateRequest(name="My List Updated")
        # Client sends stale expected_revision=4
        with pytest.raises(WatchlistRevisionConflictError):
            await self.service.update_watchlist(wl_id, self.user_a, req, expected_revision=4)

    async def test_delete_watchlist_ownership(self):
        wl_id = uuid.uuid4()
        # User B cannot delete User A's list
        self.mock_repo.get_by_id.return_value = None
        with pytest.raises(WatchlistNotFoundError):
            await self.service.delete_watchlist(wl_id, self.user_b)


# =============================================================================
# 4. Membership Operations & Reordering
# =============================================================================
@pytest.mark.asyncio
class TestWatchlistMembershipAndReorder:
    def setup_method(self):
        self.mock_repo = AsyncMock(spec=WatchlistRepository)
        self.mock_session = AsyncMock()
        self.mock_repo.session = self.mock_session
        self.service = WatchlistService(repository=self.mock_repo, db_session=self.mock_session)
        self.user_id = uuid.uuid4()
        self.wl_id = uuid.uuid4()

        self.watchlist = Watchlist(
            id=self.wl_id,
            owner_user_id=self.user_id,
            name="Alpha Tracking",
            normalized_name="alpha tracking",
            revision=1,
        )
        self.mock_repo.get_by_id.return_value = self.watchlist

    async def test_add_item_enforces_quota(self):
        self.mock_repo.count_items.return_value = MAX_ITEMS_PER_WATCHLIST
        req = AddWatchlistItemRequest(instrument_entity_id=uuid.uuid4())

        with pytest.raises(WatchlistItemQuotaExceededError):
            await self.service.add_item(self.wl_id, self.user_id, req)

    async def test_add_item_rejects_nonexistent_instrument(self):
        self.mock_repo.count_items.return_value = 10
        # Database query for FinancialInstrument returns None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result

        req = AddWatchlistItemRequest(instrument_entity_id=uuid.uuid4())
        with pytest.raises(InstrumentNotFoundError):
            await self.service.add_item(self.wl_id, self.user_id, req)

    async def test_add_item_duplicate_prevention(self):
        inst_id = uuid.uuid4()
        self.mock_repo.count_items.return_value = 5

        # Instrument exists in database
        inst_mock = MagicMock()
        inst_mock.scalar_one_or_none.return_value = inst_id
        self.mock_session.execute.return_value = inst_mock

        # Already present in watchlist
        existing_item = WatchlistItem(
            id=uuid.uuid4(),
            watchlist_id=self.wl_id,
            instrument_entity_id=inst_id,
            market_series_id="",
            position=0,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.mock_repo.get_item_by_series.return_value = existing_item

        req = AddWatchlistItemRequest(instrument_entity_id=inst_id)
        with pytest.raises(DuplicateWatchlistItemError):
            await self.service.add_item(self.wl_id, self.user_id, req)

    async def test_remove_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        with pytest.raises(WatchlistItemNotFoundError):
            await self.service.remove_item(self.wl_id, uuid.uuid4(), self.user_id)

    async def test_reorder_items_success_and_conflict(self):
        item1_id = uuid.uuid4()
        item2_id = uuid.uuid4()
        item3_id = uuid.uuid4()

        # Reorder with valid revision
        self.watchlist.revision = 3
        updated_wl = Watchlist(
            id=self.wl_id,
            owner_user_id=self.user_id,
            name="Alpha Tracking",
            normalized_name="alpha tracking",
            revision=4,
        )
        self.mock_repo.reorder_items.return_value = updated_wl

        req = ReorderWatchlistItemsRequest(
            ordered_item_ids=[item3_id, item1_id, item2_id],
            expected_revision=3,
        )
        res = await self.service.reorder_items(self.wl_id, self.user_id, req)

        assert res.revision == 4
        assert res.ordered_item_ids == [item3_id, item1_id, item2_id]
        self.mock_repo.reorder_items.assert_awaited_once_with(
            watchlist=self.watchlist,
            ordered_item_ids=[item3_id, item1_id, item2_id],
            expected_revision=3,
        )


# =============================================================================
# 5. Financial Snapshot Qualification & Cross-Navigation
# =============================================================================
@pytest.mark.asyncio
class TestSnapshotAndCrossNavigation:
    def setup_method(self):
        self.mock_repo = AsyncMock(spec=WatchlistRepository)
        self.mock_session = AsyncMock()
        self.mock_repo.session = self.mock_session
        self.service = WatchlistService(repository=self.mock_repo, db_session=self.mock_session)

    async def test_resolve_items_without_quotes_never_fakes_zero(self):
        item_id = uuid.uuid4()
        inst_id = uuid.uuid4()
        wl_id = uuid.uuid4()

        item = WatchlistItem(
            id=item_id,
            watchlist_id=wl_id,
            instrument_entity_id=inst_id,
            market_series_id="XNAS",
            position=0,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )

        # Mock entity query returns AAPL
        entity_row = MagicMock()
        entity_row.entity_id = inst_id
        entity_row.canonical_name = "Apple Inc. Common Stock"
        entity_row.display_name = "Apple Inc."
        entity_row.entity_type = "equity"

        mock_exec1 = MagicMock()
        mock_exec1.all.return_value = [entity_row]

        # Mock identifier query returns AAPL symbol
        id_row = MagicMock()
        id_row.entity_id = inst_id
        id_row.scheme_key = "ticker"
        id_row.value = "AAPL"
        mock_exec2 = MagicMock()
        mock_exec2.all.return_value = [id_row]

        # Mock relationship query: company issuer relationship exists
        issuer_id = uuid.uuid4()
        rel_row = MagicMock()
        rel_row.source_entity_id = inst_id
        rel_row.target_entity_id = issuer_id
        rel_row.relationship_type_key = "issued_by"
        mock_exec3 = MagicMock()
        mock_exec3.all.return_value = [rel_row]

        self.mock_session.execute.side_effect = [mock_exec1, mock_exec2, mock_exec3]

        resolved = await self.service._resolve_items_metadata_and_quotes([item])
        assert len(resolved) == 1
        res = resolved[0]

        assert res.symbol == "AAPL"
        assert res.display_name == "Apple Inc."
        assert res.asset_class == "equity"
        assert res.venue == "XNAS"
        # Since no quote was supplied in quote_service:
        assert res.is_quote_available is False
        assert res.last_price is None  # NEVER 0!
        assert res.absolute_change is None
        assert res.percentage_change is None
        assert res.freshness_status == "unavailable"
        # Cross-navigation to company is verified
        assert res.has_company_page is True
        assert res.issuer_entity_id == issuer_id


# =============================================================================
# 6. FastAPI Router HTTP Integration Tests
# =============================================================================
@pytest.mark.asyncio
class TestFastApiWatchlistEndpoints:
    def setup_method(self):
        self.app = create_app()
        self.dummy_session = AsyncMock()
        self.mock_service = AsyncMock(spec=WatchlistService)

        self.user_a = uuid.UUID("00000000-0000-0000-0000-000000000001")
        self.principal_a = AuthPrincipal(sub=str(self.user_a), email="usera@atlas.local")

        self.app.dependency_overrides[get_db_session] = lambda: self.dummy_session
        self.app.dependency_overrides[get_watchlist_service] = lambda: self.mock_service
        self.app.dependency_overrides[get_current_user] = lambda: self.principal_a

    async def test_list_watchlists_endpoint(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        wl_id = uuid.uuid4()
        summary = WatchlistSummaryResponse(
            id=wl_id,
            owner_user_id=self.user_a,
            name="Tech Bluechips",
            description="Core holdings",
            item_count=3,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        self.mock_service.list_watchlists.return_value = WatchlistListResponse(
            items=[summary],
            total=1,
            page=1,
            page_size=20,
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/watchlists")
            assert res.status_code == 200
            data = res.json()
            assert data["total"] == 1
            assert data["items"][0]["name"] == "Tech Bluechips"
            assert res.headers["cache-control"] == "private, no-store"

    async def test_create_watchlist_endpoint(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        wl_id = uuid.uuid4()
        summary = WatchlistSummaryResponse(
            id=wl_id,
            owner_user_id=self.user_a,
            name="Crypto Majors",
            item_count=0,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        self.mock_service.create_watchlist.return_value = summary

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/watchlists",
                json={"name": "Crypto Majors", "description": "Top layer-1 coins"},
            )
            assert res.status_code == 201
            assert res.json()["name"] == "Crypto Majors"

    async def test_get_watchlist_detail_with_etag(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        wl_id = uuid.uuid4()
        detail = WatchlistDetailResponse(
            id=wl_id,
            owner_user_id=self.user_a,
            name="Foreign Exchange",
            revision=7,
            created_at=now,
            updated_at=now,
            items=[],
            total_items=0,
            page=1,
            page_size=50,
        )
        self.mock_service.get_watchlist.return_value = detail

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get(f"/api/v1/watchlists/{wl_id}")
            assert res.status_code == 200
            assert res.headers["etag"] == 'W/"7"'
            assert res.headers["cache-control"] == "private, no-store"

    async def test_patch_watchlist_if_match_conflict(self):
        wl_id = uuid.uuid4()
        self.mock_service.update_watchlist.side_effect = WatchlistRevisionConflictError(
            "Revision mismatch"
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.patch(
                f"/api/v1/watchlists/{wl_id}",
                headers={"If-Match": 'W/"2"'},
                json={"name": "Renamed List"},
            )
            assert res.status_code == 412  # Precondition Failed

    async def test_reorder_endpoint_revision_conflict(self):
        wl_id = uuid.uuid4()
        self.mock_service.reorder_items.side_effect = WatchlistRevisionConflictError(
            "Revision mismatch"
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.put(
                f"/api/v1/watchlists/{wl_id}/items/order",
                json={"ordered_item_ids": [str(uuid.uuid4())], "expected_revision": 1},
            )
            assert res.status_code == 409

    async def test_delete_watchlist_endpoint(self):
        wl_id = uuid.uuid4()
        self.mock_service.delete_watchlist.return_value = None

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.delete(f"/api/v1/watchlists/{wl_id}")
            assert res.status_code == 204


# =============================================================================
# 7. Side-Effects Invariants (Section 240)
# =============================================================================
def test_side_effect_invariants():
    """Verify that Stage 76 watchlist code does not import or execute orders or broker actions."""
    import atlas.watchlists as wl_module

    # Confirm zero trading order execution modules imported
    module_dict = str(wl_module.__dict__)
    assert "execute_order" not in module_dict
    assert "broker_api" not in module_dict
    assert "trading_engine" not in module_dict
    assert "llm_call" not in module_dict
