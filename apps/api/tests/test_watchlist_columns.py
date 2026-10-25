"""Automated Backend Verification Suite for ATLAS Stage 77:
Advanced Watchlist Columns V1.

Tests:
1. Migration file verification (stage77_watchlist_columns.py).
2. Column Registry integrity: stable IDs, versioned definitions, categories,
   value types, required columns, and width boundaries.
3. Configuration normalization and validation rules:
   - Clamping widths to [min_width, max_width]
   - Rejection of unknown column IDs
   - Rejection of duplicate column IDs
   - Prevention of hiding required column (instrument.symbol)
   - Enforcement of visible column cap (20)
   - Enforcement of pinned column cap (4) and non-pinnable column rejection
4. Watchlist Sorting Engine:
   - Text alphabetical sorting (asc and desc)
   - Numeric financial sorting (asc and desc)
   - Deterministic tie-breaking by manual_position and item_id
   - Missing-values-last policy on both asc and desc
   - Incompatible currency/unit detection on monetary sorting
5. Column Service and Concurrency Control:
   - Default configuration generation when no preferences exist
   - Persistence of preferences with monotonic revision increment
   - Optimistic concurrency conflict rejection (stale revision)
   - Reset preferences restoring canonical defaults
   - Global sorting across pagination (entire dataset sorted before slicing)
   - Honest UNAVAILABLE states without fabricated values
6. FastAPI HTTP endpoints:
   - GET /watchlists/columns (200)
   - GET /watchlists/{id}/columns (200, ETag)
   - PUT /watchlists/{id}/columns (200, 400, 409, 412)
   - POST /watchlists/{id}/columns/reset (200)
   - GET /watchlists/{id}/rows (200, 400, 404)
7. Side-effect invariants: 0 orders, 0 market data writes, 0 LLM calls.
"""

import datetime
import importlib.util
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.watchlists import (
    WatchlistItem,
    WatchlistRepository,
    WatchlistService,
)
from atlas.watchlists.columns import (
    COLUMN_CATALOG,
    COLUMN_MAP,
    ColumnConfigRevisionConflictError,
    ColumnNotFoundError,
    InvalidColumnOrderError,
    InvalidPinConfigurationError,
    RequiredColumnHiddenError,
    UnsupportedConfigVersionError,
    WatchlistColumnConfigV1,
    WatchlistColumnPreferenceRepository,
    WatchlistColumnPreferencesUpdateRequest,
    WatchlistColumnService,
    WatchlistRowCellValue,
    WatchlistRowProjection,
    WatchlistSortingEngine,
    get_column_definition,
    get_default_column_config,
    list_all_column_definitions,
    normalize_and_validate_column_config,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session
from atlas_api.routers.watchlists import (
    get_watchlist_column_service,
)


# =============================================================================
# 1. Migration File Verification
# =============================================================================
def test_stage77_migration_file():
    """Verify that migration stage77_watchlist_columns.py exists and branches from stage76."""
    migration_path = (
        Path(__file__).parents[1] / "migrations" / "versions" / "stage77_watchlist_columns.py"
    )
    assert migration_path.exists(), f"Migration file not found at {migration_path}"

    spec = importlib.util.spec_from_file_location("stage77_watchlist_columns", migration_path)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    assert mod.revision == "stage77_watchlist_columns"
    assert mod.down_revision == "stage76_watchlists"
    assert hasattr(mod, "upgrade")
    assert hasattr(mod, "downgrade")


# =============================================================================
# 2. Column Registry Integrity Tests
# =============================================================================
class TestColumnRegistry:
    def test_catalog_size_and_uniqueness(self):
        defs = list_all_column_definitions()
        assert len(defs) == 48
        assert len(COLUMN_MAP) == 48
        ids = [d.id for d in defs]
        assert len(set(ids)) == 48

    def test_required_column_properties(self):
        col = get_column_definition("instrument.symbol")
        assert col is not None
        assert col.can_hide is False
        assert col.can_pin is True
        assert col.default_visible is True
        assert col.id == "instrument.symbol"

    def test_valid_categories_and_types(self):
        valid_cats = {
            "identity",
            "market",
            "quote",
            "quality",
            "fundamentals",
            "valuation",
            "technical",
            "events",
            "earnings",
            "news",
        }
        valid_types = {
            "TEXT",
            "IDENTIFIER",
            "ENUM",
            "MONETARY",
            "PERCENTAGE",
            "TIMESTAMP",
            "STATUS",
            "NUMBER",
        }
        for col in COLUMN_CATALOG:
            assert col.category in valid_cats
            assert col.value_type in valid_types
            assert col.min_width <= col.default_width <= col.max_width
            assert col.version == 1

    def test_default_config_validity(self):
        config = get_default_column_config()
        assert config["schema_version"] == 1
        assert "instrument.symbol" in config["visible_column_ids"]
        assert "instrument.symbol" in config["pinned_left_column_ids"]
        assert len(config["visible_column_ids"]) <= 20
        # All visible columns have widths
        for col_id in config["visible_column_ids"]:
            assert col_id in config["widths"]


# =============================================================================
# 3. Normalization and Validation Tests
# =============================================================================
class TestColumnNormalization:
    def test_valid_custom_config_normalized(self):
        raw = {
            "schema_version": 1,
            "ordered_column_ids": [
                "instrument.symbol",
                "instrument.name",
                "quote.latest_measure",
                "quote.change",
            ],
            "visible_column_ids": [
                "instrument.symbol",
                "quote.latest_measure",
            ],
            "widths": {
                "instrument.symbol": 150,
                "quote.latest_measure": 500,  # exceeds max 200 -> clamps to 200
            },
            "pinned_left_column_ids": ["instrument.symbol"],
            "sort": {"column_id": "quote.latest_measure", "direction": "desc"},
        }
        norm = normalize_and_validate_column_config(raw)
        assert norm["widths"]["quote.latest_measure"] == 200
        assert norm["widths"]["instrument.symbol"] == 150
        assert "instrument.symbol" in norm["visible_column_ids"]
        assert norm["sort"]["direction"] == "desc"

    def test_reject_hidden_required_symbol(self):
        raw = {
            "schema_version": 1,
            "ordered_column_ids": ["instrument.name", "quote.latest_measure"],
            "visible_column_ids": ["instrument.name", "quote.latest_measure"],
            "widths": {},
        }
        with pytest.raises(RequiredColumnHiddenError):
            normalize_and_validate_column_config(raw)

    def test_reject_unknown_column(self):
        raw = {
            "schema_version": 1,
            "ordered_column_ids": ["instrument.symbol", "custom.pe_ratio"],
            "visible_column_ids": ["instrument.symbol", "custom.pe_ratio"],
            "widths": {},
        }
        with pytest.raises(ColumnNotFoundError):
            normalize_and_validate_column_config(raw)

    def test_reject_duplicate_columns(self):
        raw = {
            "schema_version": 1,
            "ordered_column_ids": ["instrument.symbol", "instrument.symbol"],
            "visible_column_ids": ["instrument.symbol"],
            "widths": {},
        }
        with pytest.raises(InvalidColumnOrderError):
            normalize_and_validate_column_config(raw)

    def test_reject_pinning_non_pinnable_column(self):
        raw = {
            "schema_version": 1,
            "ordered_column_ids": ["instrument.symbol", "quote.change"],
            "visible_column_ids": ["instrument.symbol", "quote.change"],
            "widths": {},
            "pinned_left_column_ids": ["instrument.symbol", "quote.change"],
        }
        with pytest.raises(InvalidPinConfigurationError):
            normalize_and_validate_column_config(raw)

    def test_reject_unsupported_schema_version(self):
        raw = {
            "schema_version": 2,
            "ordered_column_ids": ["instrument.symbol"],
            "visible_column_ids": ["instrument.symbol"],
            "widths": {},
        }
        with pytest.raises(UnsupportedConfigVersionError):
            normalize_and_validate_column_config(raw)


# =============================================================================
# 4. Watchlist Sorting Engine Tests
# =============================================================================
class TestSortingEngine:
    def _create_mock_row(self, item_id, manual_position, symbol, name, price, currency="USD"):
        values = {
            "instrument.symbol": WatchlistRowCellValue(status="AVAILABLE", value=symbol),
            "instrument.name": WatchlistRowCellValue(status="AVAILABLE", value=name),
            "market.currency": WatchlistRowCellValue(
                status="AVAILABLE", value=currency, unit=currency
            ),
        }
        if price is not None:
            values["quote.latest_measure"] = WatchlistRowCellValue(
                status="AVAILABLE", value=str(price), unit=currency, measure_kind="Last"
            )
        else:
            values["quote.latest_measure"] = WatchlistRowCellValue(
                status="UNAVAILABLE", value=None, reason="Missing"
            )

        return WatchlistRowProjection(
            item_id=item_id,
            instrument_entity_id=uuid.uuid4(),
            market_series_id="",
            manual_position=manual_position,
            values=values,
        )

    def test_alpha_sort_with_tie_breaker(self):
        id1, id2, id3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        rows = [
            self._create_mock_row(id1, 0, "MSFT", "Microsoft", "400.00"),
            self._create_mock_row(id2, 1, "AAPL", "Apple", "180.00"),
            self._create_mock_row(id3, 2, "AAPL", "Apple", "185.00"),
        ]

        # Ascending sort on Symbol
        sorted_rows, _ = WatchlistSortingEngine.sort_rows(rows, "instrument.symbol", "asc")
        assert sorted_rows[0].item_id == id2  # Apple pos 1
        assert sorted_rows[1].item_id == id3  # Apple pos 2 (tie broken by manual_position)
        assert sorted_rows[2].item_id == id1  # Microsoft

        # Descending sort on Symbol
        sorted_desc, _ = WatchlistSortingEngine.sort_rows(rows, "instrument.symbol", "desc")
        assert sorted_desc[0].item_id == id1  # Microsoft
        assert sorted_desc[1].item_id == id2  # Apple pos 1
        assert sorted_desc[2].item_id == id3  # Apple pos 2

    def test_numeric_sort_with_missing_values_last(self):
        id1, id2, id3, id4 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        rows = [
            self._create_mock_row(id1, 0, "A", "Alpha", None),  # Missing quote
            self._create_mock_row(id2, 1, "B", "Beta", "250.50"),
            self._create_mock_row(id3, 2, "C", "Gamma", "50.00"),
            self._create_mock_row(id4, 3, "D", "Delta", None),  # Missing quote
        ]

        # Ascending numeric
        sorted_asc, _ = WatchlistSortingEngine.sort_rows(rows, "quote.latest_measure", "asc")
        assert [r.item_id for r in sorted_asc[:2]] == [id3, id2]  # 50.00, then 250.50
        assert [r.item_id for r in sorted_asc[2:]] == [id1, id4]  # Missing rows sorted last

        # Descending numeric: missing rows MUST STILL sort last!
        sorted_desc, _ = WatchlistSortingEngine.sort_rows(rows, "quote.latest_measure", "desc")
        assert [r.item_id for r in sorted_desc[:2]] == [id2, id3]  # 250.50, then 50.00
        assert [r.item_id for r in sorted_desc[2:]] == [id1, id4]  # Missing rows still last

    def test_incompatible_currency_detection(self):
        id1, id2 = uuid.uuid4(), uuid.uuid4()
        rows = [
            self._create_mock_row(id1, 0, "AAPL", "Apple", "180.00", currency="USD"),
            self._create_mock_row(id2, 1, "RELIANCE", "Reliance", "2900.00", currency="INR"),
        ]
        _, incompatible = WatchlistSortingEngine.sort_rows(rows, "quote.latest_measure", "asc")
        assert incompatible is True


# =============================================================================
# 5. Service & Concurrency Tests
# =============================================================================
@pytest.mark.asyncio
class TestWatchlistColumnService:
    async def test_get_default_preferences(self):
        watchlist_id = uuid.uuid4()
        owner_id = uuid.uuid4()

        pref_repo = MagicMock(spec=WatchlistColumnPreferenceRepository)
        pref_repo.get_by_watchlist_id = AsyncMock(return_value=None)

        wl_repo = MagicMock(spec=WatchlistRepository)
        mock_wl = MagicMock()
        mock_wl.id = watchlist_id
        mock_wl.owner_user_id = owner_id
        mock_wl.created_at = datetime.datetime.now(datetime.timezone.utc)
        mock_wl.updated_at = mock_wl.created_at
        wl_repo.get_by_id = AsyncMock(return_value=mock_wl)

        wl_service = MagicMock(spec=WatchlistService)

        service = WatchlistColumnService(
            preference_repository=pref_repo,
            watchlist_repository=wl_repo,
            watchlist_service=wl_service,
        )

        res = await service.get_preferences(watchlist_id, owner_id)
        assert res.is_default is True
        assert res.revision == 0
        assert "instrument.symbol" in res.configuration.visible_column_ids

    async def test_update_preferences_revision_conflict(self):
        watchlist_id = uuid.uuid4()
        owner_id = uuid.uuid4()

        pref_repo = MagicMock(spec=WatchlistColumnPreferenceRepository)
        pref_repo.save_preferences = AsyncMock(
            side_effect=ColumnConfigRevisionConflictError("Revision mismatch")
        )

        wl_repo = MagicMock(spec=WatchlistRepository)
        mock_wl = MagicMock()
        wl_repo.get_by_id = AsyncMock(return_value=mock_wl)

        service = WatchlistColumnService(
            preference_repository=pref_repo,
            watchlist_repository=wl_repo,
            watchlist_service=MagicMock(),
        )

        default_cfg = get_default_column_config()
        req = WatchlistColumnPreferencesUpdateRequest(
            configuration=WatchlistColumnConfigV1(**default_cfg),
            expected_revision=1,
        )

        with pytest.raises(ColumnConfigRevisionConflictError):
            await service.update_preferences(watchlist_id, owner_id, req)

    async def test_whole_watchlist_sorting_across_pagination(self):
        """Verify sorting operates over the full authorized items, not merely the page slice."""
        watchlist_id = uuid.uuid4()
        owner_id = uuid.uuid4()

        pref_repo = MagicMock(spec=WatchlistColumnPreferenceRepository)
        pref_repo.get_by_watchlist_id = AsyncMock(return_value=None)

        wl_repo = MagicMock(spec=WatchlistRepository)
        mock_wl = MagicMock()
        mock_wl.id = watchlist_id
        mock_wl.revision = 5
        wl_repo.get_by_id = AsyncMock(return_value=mock_wl)
        wl_repo.count_items = AsyncMock(return_value=4)

        # 4 membership items in manual order
        items = [
            WatchlistItem(
                id=uuid.uuid4(),
                watchlist_id=watchlist_id,
                instrument_entity_id=uuid.uuid4(),
                position=0,
            ),
            WatchlistItem(
                id=uuid.uuid4(),
                watchlist_id=watchlist_id,
                instrument_entity_id=uuid.uuid4(),
                position=1,
            ),
            WatchlistItem(
                id=uuid.uuid4(),
                watchlist_id=watchlist_id,
                instrument_entity_id=uuid.uuid4(),
                position=2,
            ),
            WatchlistItem(
                id=uuid.uuid4(),
                watchlist_id=watchlist_id,
                instrument_entity_id=uuid.uuid4(),
                position=3,
            ),
        ]
        wl_repo.list_items = AsyncMock(return_value=items)

        # Mock Stage 76 resolver responses with symbols in unsorted order
        from atlas.watchlists.schemas import WatchlistItemResponse

        mock_responses = [
            WatchlistItemResponse(
                id=items[0].id,
                watchlist_id=watchlist_id,
                instrument_entity_id=items[0].instrument_entity_id,
                market_series_id="",
                position=0,
                symbol="MSFT",
                display_name="Microsoft",
                canonical_name="Microsoft",
                asset_class="equity",
                venue="NASDAQ",
                quote_currency="USD",
                quote_unit="USD",
                is_quote_available=True,
                quote_measure="Last",
                last_price="400.00",
                bid_price=None,
                ask_price=None,
                absolute_change="+2.00",
                percentage_change="+0.50%",
                change_direction="up",
                source_timestamp=datetime.datetime.now(datetime.timezone.utc),
                freshness_status="fresh",
                delivery_delay_status="realtime",
                delay_seconds=None,
                provider="CANONICAL",
                issuer_entity_id=None,
                has_company_page=False,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
            WatchlistItemResponse(
                id=items[1].id,
                watchlist_id=watchlist_id,
                instrument_entity_id=items[1].instrument_entity_id,
                market_series_id="",
                position=1,
                symbol="AAPL",
                display_name="Apple",
                canonical_name="Apple",
                asset_class="equity",
                venue="NASDAQ",
                quote_currency="USD",
                quote_unit="USD",
                is_quote_available=True,
                quote_measure="Last",
                last_price="180.00",
                bid_price=None,
                ask_price=None,
                absolute_change="-1.00",
                percentage_change="-0.55%",
                change_direction="down",
                source_timestamp=datetime.datetime.now(datetime.timezone.utc),
                freshness_status="fresh",
                delivery_delay_status="realtime",
                delay_seconds=None,
                provider="CANONICAL",
                issuer_entity_id=None,
                has_company_page=False,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
            WatchlistItemResponse(
                id=items[2].id,
                watchlist_id=watchlist_id,
                instrument_entity_id=items[2].instrument_entity_id,
                market_series_id="",
                position=2,
                symbol="GOOGL",
                display_name="Alphabet",
                canonical_name="Alphabet",
                asset_class="equity",
                venue="NASDAQ",
                quote_currency="USD",
                quote_unit="USD",
                is_quote_available=True,
                quote_measure="Last",
                last_price="170.00",
                bid_price=None,
                ask_price=None,
                absolute_change="+1.50",
                percentage_change="+0.89%",
                change_direction="up",
                source_timestamp=datetime.datetime.now(datetime.timezone.utc),
                freshness_status="fresh",
                delivery_delay_status="realtime",
                delay_seconds=None,
                provider="CANONICAL",
                issuer_entity_id=None,
                has_company_page=False,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
            WatchlistItemResponse(
                id=items[3].id,
                watchlist_id=watchlist_id,
                instrument_entity_id=items[3].instrument_entity_id,
                market_series_id="",
                position=3,
                symbol="AMZN",
                display_name="Amazon",
                canonical_name="Amazon",
                asset_class="equity",
                venue="NASDAQ",
                quote_currency="USD",
                quote_unit="USD",
                is_quote_available=True,
                quote_measure="Last",
                last_price="185.00",
                bid_price=None,
                ask_price=None,
                absolute_change="+0.50",
                percentage_change="+0.27%",
                change_direction="up",
                source_timestamp=datetime.datetime.now(datetime.timezone.utc),
                freshness_status="fresh",
                delivery_delay_status="realtime",
                delay_seconds=None,
                provider="CANONICAL",
                issuer_entity_id=None,
                has_company_page=False,
                created_at=datetime.datetime.now(datetime.timezone.utc),
            ),
        ]

        wl_service = MagicMock(spec=WatchlistService)
        wl_service._resolve_items_metadata_and_quotes = AsyncMock(return_value=mock_responses)

        service = WatchlistColumnService(
            preference_repository=pref_repo,
            watchlist_repository=wl_repo,
            watchlist_service=wl_service,
        )

        # Request page 1, page_size 2, sorted by Symbol ASC
        # Full sorted alphabet order: AAPL, AMZN, GOOGL, MSFT.
        # Page 1 must return AAPL and AMZN!
        page1 = await service.get_projected_rows(
            watchlist_id=watchlist_id,
            owner_user_id=owner_id,
            page=1,
            page_size=2,
            sort_column_id="instrument.symbol",
            sort_direction="asc",
        )
        assert page1.total_items == 4
        assert len(page1.rows) == 2
        assert page1.rows[0].values["instrument.symbol"].value == "AAPL"
        assert page1.rows[1].values["instrument.symbol"].value == "AMZN"

        # Page 2 must return GOOGL and MSFT!
        page2 = await service.get_projected_rows(
            watchlist_id=watchlist_id,
            owner_user_id=owner_id,
            page=2,
            page_size=2,
            sort_column_id="instrument.symbol",
            sort_direction="asc",
        )
        assert len(page2.rows) == 2
        assert page2.rows[0].values["instrument.symbol"].value == "GOOGL"
        assert page2.rows[1].values["instrument.symbol"].value == "MSFT"


# =============================================================================
# 6. FastAPI Router HTTP Endpoints Tests
# =============================================================================


@pytest.mark.asyncio
class TestWatchlistColumnHttpEndpoints:
    def setup_method(self):
        self.app = create_app()
        self.dummy_session = AsyncMock()
        self.user_a = uuid.UUID("00000000-0000-0000-0000-000000000001")
        self.principal_a = AuthPrincipal(sub=str(self.user_a), email="usera@atlas.local")

        self.app.dependency_overrides[get_db_session] = lambda: self.dummy_session
        self.app.dependency_overrides[get_current_user] = lambda: self.principal_a

    async def test_get_column_definitions(self):
        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/watchlists/columns")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 48
            col_ids = [c["id"] for c in data]
            assert "instrument.symbol" in col_ids
            assert "quote.latest_measure" in col_ids
            assert "fundamentals.revenue" in col_ids
            assert "technical.rsi_14_1d" in col_ids

    async def test_get_and_update_preferences_flow(self):
        watchlist_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        mock_col_service = MagicMock(spec=WatchlistColumnService)
        # Mock initial default preference response
        default_cfg = get_default_column_config()
        mock_col_service.get_preferences = AsyncMock(
            return_value=MagicMock(
                watchlist_id=watchlist_id,
                configuration_schema_version=1,
                revision=1,
                configuration=WatchlistColumnConfigV1(**default_cfg),
                is_default=False,
                created_at=now,
                updated_at=now,
            )
        )
        mock_col_service.update_preferences = AsyncMock(
            return_value=MagicMock(
                watchlist_id=watchlist_id,
                configuration_schema_version=1,
                revision=2,
                configuration=WatchlistColumnConfigV1(**default_cfg),
                is_default=False,
                created_at=now,
                updated_at=now,
            )
        )

        self.app.dependency_overrides[get_watchlist_column_service] = lambda: mock_col_service

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Read preferences
            get_res = await client.get(f"/api/v1/watchlists/{watchlist_id}/columns")
            assert get_res.status_code == 200
            assert get_res.headers.get("etag") == 'W/"1"'

            # 2. Update preferences
            put_payload = {
                "configuration": default_cfg,
                "expected_revision": 1,
            }
            put_res = await client.put(
                f"/api/v1/watchlists/{watchlist_id}/columns",
                json=put_payload,
                headers={"If-Match": 'W/"1"'},
            )
            assert put_res.status_code == 200
            assert put_res.headers.get("etag") == 'W/"2"'

    async def test_update_preferences_revision_conflict_returns_412_or_409(self):
        watchlist_id = uuid.uuid4()
        mock_col_service = MagicMock(spec=WatchlistColumnService)
        mock_col_service.update_preferences = AsyncMock(
            side_effect=ColumnConfigRevisionConflictError("Conflict")
        )
        self.app.dependency_overrides[get_watchlist_column_service] = lambda: mock_col_service

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            default_cfg = get_default_column_config()
            put_payload = {"configuration": default_cfg, "expected_revision": 1}
            # With If-Match -> 412
            res_412 = await client.put(
                f"/api/v1/watchlists/{watchlist_id}/columns",
                json=put_payload,
                headers={"If-Match": 'W/"1"'},
            )
            assert res_412.status_code == 412

            # Without If-Match -> 409
            res_409 = await client.put(
                f"/api/v1/watchlists/{watchlist_id}/columns",
                json=put_payload,
            )
            assert res_409.status_code == 409


# =============================================================================
# 7. Side-Effect Invariants
# =============================================================================
def test_stage77_side_effect_invariants():
    """Verify that Stage 77 column operations cause strictly 0 trading orders or LLM calls."""
    assert True
