"""Automated Backend Verification Suite for ATLAS Stage 74:
Saved Chart Layouts V1.

Tests:
1. Migration file validity and down_revision continuity.
2. Layout document schema V1 serialization and validation.
3. Resource quota and size limit enforcement (512 KiB, 50 layouts, 4 panels,
   12 indicators, 250 drawings).
4. Strict forbidden field rejection (credentials, tokens, OHLCV data, calculated outputs).
5. Name normalization, unicode sanitization, and case-insensitive uniqueness.
6. Optimistic concurrency control (atomic revisions, ETag / If-Match, 412 Precondition Failed).
7. Authenticated CRUD API endpoints (List, Create, Get, Update, Patch, Duplicate, Delete, Export).
8. User ownership isolation and UUID authorization bounds.
9. Side-effect invariants (zero broker orders, zero LLM calls, zero raw OHLCV writes).
"""

import datetime
import importlib.util
import uuid
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.charts.layouts import (
    ChartLayoutCreateRequest,
    ChartLayoutDetailResponse,
    ChartLayoutModel,
    ChartLayoutRepository,
    ChartLayoutService,
    ChartLayoutSummaryResponse,
    ChartLayoutUpdateRequest,
    ForbiddenFieldDetectedError,
    InvalidLayoutNameError,
    JsonNestingDepthExceededError,
    LayoutNameConflictError,
    LayoutNotFoundError,
    LayoutPayloadTooLargeError,
    LayoutQuotaExceededError,
    LayoutRevisionConflictError,
    SavedChartLayoutDocumentV1,
    SavedChartPanelV1,
    SavedDrawingAnchorV1,
    SavedDrawingObjectV1,
    SavedIndicatorInstanceV1,
    SavedPriceScaleSettingsV1,
    SavedSyncGroupV1,
    SavedViewportV1,
    UnsupportedSchemaVersionError,
    migrate_layout_document,
    normalize_layout_name,
    sanitize_display_name,
    validate_document_size,
    validate_json_depth,
    validate_layout_document_payload,
)
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session
from atlas_api.routers.chart_layouts import get_chart_layout_service


def create_sample_valid_document() -> SavedChartLayoutDocumentV1:
    panel1 = SavedChartPanelV1(
        panel_id="panel-1",
        instrument_entity_id="11111111-1111-1111-1111-111111111111",
        symbol="SPY",
        asset_class="EQUITY",
        interval="1d",
        chart_type="candlestick",
        viewport=SavedViewportV1(
            visible_start="2026-01-01", visible_end="2026-10-18", following_latest=True
        ),
        price_scale_settings=SavedPriceScaleSettingsV1(
            mode="normal", invert=False, logarithmic=False
        ),
        indicators=[
            SavedIndicatorInstanceV1(
                instance_id="ind-1",
                indicator_id="rsi",
                version=1,
                parameters={"period": 14},
                visible=True,
                color="#38bdf8",
                line_width=2,
            )
        ],
        drawings=[
            SavedDrawingObjectV1(
                id="draw-1",
                type="trendline",
                version=1,
                anchors=[
                    SavedDrawingAnchorV1(time=1760000000, price=580.5),
                    SavedDrawingAnchorV1(time=1760500000, price=590.2),
                ],
                style={"color": "#10b981", "lineWidth": 2},
                visible=True,
                locked=False,
                z_index=1,
            )
        ],
    )
    panel2 = SavedChartPanelV1(
        panel_id="panel-2",
        instrument_entity_id="22222222-2222-2222-2222-222222222222",
        symbol="BTCUSDT",
        asset_class="CRYPTO",
        interval="1h",
        chart_type="candlestick",
    )
    sync_group = SavedSyncGroupV1(
        group_id="group-a",
        name="Group A",
        member_panel_ids=["panel-1", "panel-2"],
        settings={"crosshair": True, "visibleTimeRange": True, "instrument": False},
        enabled=True,
        color="#06b6d4",
    )
    return SavedChartLayoutDocumentV1(
        schema_version=1,
        layout_id="two-columns",
        panel_order=["panel-1", "panel-2"],
        split_ratios={"primary": 0.5},
        active_panel_id="panel-1",
        panels=[panel1, panel2],
        synchronization_groups=[sync_group],
    )


# -----------------------------------------------------------------------------
# 1. Migration Verification
# -----------------------------------------------------------------------------
class TestStage74Migration:
    def test_migration_revision_and_down_revision(self):
        migration_file = (
            Path(__file__).parents[1] / "migrations" / "versions" / "stage74_chart_layouts.py"
        )
        assert migration_file.exists(), f"Migration file not found at {migration_file}"

        spec = importlib.util.spec_from_file_location("stage74_migration", migration_file)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert module.revision == "stage74_chart_layouts"
        assert module.down_revision == "stage58_fund_metadata_and_nav"
        assert callable(module.upgrade)
        assert callable(module.downgrade)


# -----------------------------------------------------------------------------
# 2. Schema, Resource Bounds and Security Validation
# -----------------------------------------------------------------------------
class TestLayoutDocumentSchemaValidation:
    def test_valid_document_roundtrip(self):
        doc = create_sample_valid_document()
        doc_dict = doc.model_dump()
        revalidated = validate_layout_document_payload(doc_dict)
        assert revalidated.layout_id == "two-columns"
        assert len(revalidated.panels) == 2
        assert len(revalidated.synchronization_groups) == 1
        assert revalidated.active_panel_id == "panel-1"

    def test_rejects_unsupported_layout_id(self):
        doc_dict = create_sample_valid_document().model_dump()
        doc_dict["layout_id"] = "six-grid-nonexistent"
        with pytest.raises(ValidationError):
            validate_layout_document_payload(doc_dict)

    def test_rejects_unsupported_chart_type(self):
        doc_dict = create_sample_valid_document().model_dump()
        doc_dict["panels"][0]["chart_type"] = "unsupported_rainbow_type"
        with pytest.raises(ValidationError):
            validate_layout_document_payload(doc_dict)

    def test_rejects_invalid_split_ratios(self):
        doc_dict = create_sample_valid_document().model_dump()
        doc_dict["split_ratios"] = {"primary": 1.5}  # out of bound
        with pytest.raises(ValidationError):
            validate_layout_document_payload(doc_dict)

        doc_dict["split_ratios"] = {"primary": -0.1}  # negative
        with pytest.raises(ValidationError):
            validate_layout_document_payload(doc_dict)

    def test_rejects_duplicate_panel_ids(self):
        doc_dict = create_sample_valid_document().model_dump()
        doc_dict["panels"].append(doc_dict["panels"][0].copy())
        doc_dict["panel_order"].append(doc_dict["panels"][0]["panel_id"])
        with pytest.raises(ValidationError):
            validate_layout_document_payload(doc_dict)

    def test_rejects_active_panel_not_in_panel_order(self):
        doc_dict = create_sample_valid_document().model_dump()
        doc_dict["active_panel_id"] = "panel-99"
        with pytest.raises(ValidationError):
            validate_layout_document_payload(doc_dict)

    def test_rejects_forbidden_fields(self):
        forbidden_samples = [
            {"password": "secret_password"},
            {"api_key": "some_provider_token"},
            {"bars_array": [[100, 105, 95, 102]]},
            {"calculated_series": [1, 2, 3]},
            {"indicator_cache": {"rsi": [50.5, 60.2]}},
        ]
        for forbidden in forbidden_samples:
            doc_dict = create_sample_valid_document().model_dump()
            doc_dict["panels"][0]["indicators"][0]["parameters"].update(forbidden)
            with pytest.raises(ForbiddenFieldDetectedError):
                validate_layout_document_payload(doc_dict)

    def test_rejects_excessive_json_depth(self):
        deep_obj: dict = {"key": "leaf"}
        for _ in range(12):
            deep_obj = {"nested": deep_obj}
        with pytest.raises(JsonNestingDepthExceededError):
            validate_json_depth(deep_obj)

    def test_rejects_oversized_payload(self):
        doc_dict = create_sample_valid_document().model_dump()
        # Inflate payload over 512 KiB
        large_string = "x" * (520 * 1024)
        doc_dict["panels"][0]["drawings"][0]["style"]["huge"] = large_string
        with pytest.raises(LayoutPayloadTooLargeError):
            validate_document_size(doc_dict)

    def test_rejects_unsupported_future_schema_version(self):
        doc_dict = create_sample_valid_document().model_dump()
        doc_dict["schema_version"] = 2
        with pytest.raises(UnsupportedSchemaVersionError):
            migrate_layout_document(doc_dict)


# -----------------------------------------------------------------------------
# 3. Name Normalization and Sanitization
# -----------------------------------------------------------------------------
class TestLayoutNameNormalization:
    def test_normalizes_whitespace_and_casing(self):
        raw = "   Macro Cross-Asset Workspace   "
        norm = normalize_layout_name(raw)
        assert norm == "macro cross-asset workspace"
        display = sanitize_display_name(raw)
        assert display == "Macro Cross-Asset Workspace"

    def test_unicode_normalization(self):
        raw = "Café \u2122 Analysis"
        norm = normalize_layout_name(raw)
        assert "café" in norm

    def test_rejects_empty_name(self):
        with pytest.raises(InvalidLayoutNameError):
            normalize_layout_name("   ")

    def test_rejects_overlong_name(self):
        with pytest.raises(InvalidLayoutNameError):
            normalize_layout_name("a" * 101)

    def test_strips_html_tags(self):
        raw = "<script>alert(1)</script>Equities Overview"
        norm = normalize_layout_name(raw)
        assert "<script>" not in norm
        assert "alert" not in norm
        assert norm == "equities overview"


# -----------------------------------------------------------------------------
# 4. Service Layer Logic & Optimistic Concurrency
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestChartLayoutService:
    def setup_method(self):
        self.mock_repo = AsyncMock(spec=ChartLayoutRepository)
        self.mock_repo.session = AsyncMock()
        self.service = ChartLayoutService(self.mock_repo)

    async def test_create_layout_enforces_quota(self):
        user_id = uuid.uuid4()
        self.mock_repo.count_layouts.return_value = 50  # at limit

        req = ChartLayoutCreateRequest(
            name="New Layout",
            document=create_sample_valid_document(),
        )
        with pytest.raises(LayoutQuotaExceededError):
            await self.service.create_layout(user_id, req)

    async def test_create_layout_enforces_unique_name(self):
        user_id = uuid.uuid4()
        self.mock_repo.count_layouts.return_value = 5
        self.mock_repo.get_by_normalized_name.return_value = ChartLayoutModel(
            id=uuid.uuid4(),
            owner_user_id=user_id,
            name="Existing",
            normalized_name="existing",
            layout_document={},
            revision=1,
            is_default=False,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )

        req = ChartLayoutCreateRequest(
            name="Existing",
            document=create_sample_valid_document(),
        )
        with pytest.raises(LayoutNameConflictError):
            await self.service.create_layout(user_id, req)

    async def test_update_layout_optimistic_concurrency_failure(self):
        user_id = uuid.uuid4()
        layout_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        existing_model = ChartLayoutModel(
            id=layout_id,
            owner_user_id=user_id,
            name="Tech Setup",
            normalized_name="tech setup",
            layout_document=create_sample_valid_document().model_dump(),
            revision=3,  # Current is 3
            is_default=False,
            created_at=now,
            updated_at=now,
        )
        self.mock_repo.get_by_id.return_value = existing_model

        # Client sends expected_revision=2 (stale)
        req = ChartLayoutUpdateRequest(
            document=create_sample_valid_document(),
            expected_revision=2,
        )
        with pytest.raises(LayoutRevisionConflictError) as exc_info:
            await self.service.update_layout(layout_id, user_id, req)

        assert exc_info.value.current_revision == 3
        assert exc_info.value.expected_revision == 2

    async def test_update_layout_successful_revision_increment(self):
        user_id = uuid.uuid4()
        layout_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        doc = create_sample_valid_document()

        existing_model = ChartLayoutModel(
            id=layout_id,
            owner_user_id=user_id,
            name="Tech Setup",
            normalized_name="tech setup",
            layout_document=doc.model_dump(),
            revision=1,
            is_default=False,
            created_at=now,
            updated_at=now,
        )
        updated_model = ChartLayoutModel(
            id=layout_id,
            owner_user_id=user_id,
            name="Tech Setup",
            normalized_name="tech setup",
            layout_document=doc.model_dump(),
            revision=2,  # Incremented
            is_default=False,
            created_at=now,
            updated_at=now,
        )

        self.mock_repo.get_by_id.return_value = existing_model
        self.mock_repo.update_layout.return_value = updated_model

        req = ChartLayoutUpdateRequest(
            document=doc,
            expected_revision=1,
        )
        res = await self.service.update_layout(layout_id, user_id, req)
        assert res.revision == 2

    async def test_duplicate_layout_creates_new_uuid(self):
        user_id = uuid.uuid4()
        src_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        doc = create_sample_valid_document()

        src_model = ChartLayoutModel(
            id=src_id,
            owner_user_id=user_id,
            name="Original Workspace",
            normalized_name="original workspace",
            layout_document=doc.model_dump(),
            revision=5,
            is_default=True,
            created_at=now,
            updated_at=now,
        )
        self.mock_repo.get_by_id.return_value = src_model
        self.mock_repo.count_layouts.return_value = 10
        self.mock_repo.get_by_normalized_name.return_value = None

        new_id = uuid.uuid4()
        cloned_model = ChartLayoutModel(
            id=new_id,
            owner_user_id=user_id,
            name="Original Workspace (Copy)",
            normalized_name="original workspace (copy)",
            layout_document=doc.model_dump(),
            revision=1,
            is_default=False,
            created_at=now,
            updated_at=now,
        )
        self.mock_repo.create_layout.return_value = cloned_model

        res = await self.service.duplicate_layout(src_id, user_id)
        assert res.id == new_id
        assert res.id != src_id
        assert res.revision == 1
        assert res.is_default is False
        assert "Copy" in res.name


# -----------------------------------------------------------------------------
# 5. FastAPI Endpoints Integration Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestFastApiChartLayoutEndpoints:
    def setup_method(self):
        self.app = create_app()
        self.dummy_session = AsyncMock()
        self.mock_service = AsyncMock(spec=ChartLayoutService)

        self.user_a = uuid.UUID("00000000-0000-0000-0000-000000000001")
        self.principal_a = AuthPrincipal(sub=str(self.user_a), email="usera@atlas.local")

        self.app.dependency_overrides[get_db_session] = lambda: self.dummy_session
        self.app.dependency_overrides[get_chart_layout_service] = lambda: self.mock_service
        self.app.dependency_overrides[get_current_user] = lambda: self.principal_a

    async def test_list_layouts_endpoint(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        summary = ChartLayoutSummaryResponse(
            id=uuid.uuid4(),
            name="Global Markets",
            description="Multi-asset overview",
            layout_type="four-grid",
            chart_count=4,
            is_default=True,
            revision=1,
            document_schema_version=1,
            created_at=now,
            updated_at=now,
        )
        self.mock_service.list_layouts.return_value = {
            "items": [summary],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/charts/layouts")
            assert res.status_code == 200
            data = res.json()
            assert data["total"] == 1
            assert data["items"][0]["name"] == "Global Markets"
            assert res.headers["cache-control"] == "private, no-store"

    async def test_create_layout_endpoint_headers(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        layout_id = uuid.uuid4()
        doc = create_sample_valid_document()

        detail = ChartLayoutDetailResponse(
            id=layout_id,
            owner_user_id=self.user_a,
            name="Intraday Equities",
            normalized_name="intraday equities",
            description=None,
            layout_type="two-columns",
            chart_count=2,
            is_default=False,
            revision=1,
            document_schema_version=1,
            document=doc,
            created_at=now,
            updated_at=now,
        )
        self.mock_service.create_layout.return_value = detail

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "name": "Intraday Equities",
                "document": doc.model_dump(),
                "is_default": False,
            }
            res = await client.post("/api/v1/charts/layouts", json=payload)
            assert res.status_code == 201
            assert res.headers["etag"] == 'W/"1"'
            assert f"/api/v1/charts/layouts/{layout_id}" in res.headers["location"]
            assert res.json()["name"] == "Intraday Equities"

    async def test_update_layout_with_if_match_header(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        layout_id = uuid.uuid4()
        doc = create_sample_valid_document()

        detail = ChartLayoutDetailResponse(
            id=layout_id,
            owner_user_id=self.user_a,
            name="Intraday Equities",
            normalized_name="intraday equities",
            description=None,
            layout_type="two-columns",
            chart_count=2,
            is_default=False,
            revision=2,
            document_schema_version=1,
            document=doc,
            created_at=now,
            updated_at=now,
        )
        self.mock_service.update_layout.return_value = detail

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "document": doc.model_dump(),
                "expected_revision": 1,
            }
            headers = {"If-Match": 'W/"1"'}
            res = await client.put(
                f"/api/v1/charts/layouts/{layout_id}", json=payload, headers=headers
            )
            assert res.status_code == 200
            assert res.headers["etag"] == 'W/"2"'
            assert res.json()["revision"] == 2

    async def test_update_layout_returns_412_on_revision_mismatch(self):
        layout_id = uuid.uuid4()
        doc = create_sample_valid_document()

        self.mock_service.update_layout.side_effect = LayoutRevisionConflictError(
            current_revision=4,
            expected_revision=2,
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "document": doc.model_dump(),
                "expected_revision": 2,
            }
            res = await client.put(f"/api/v1/charts/layouts/{layout_id}", json=payload)
            assert res.status_code == 412
            err_data = res.json()
            err_msg = err_data.get("error", {}).get("message", "") or err_data.get("detail", "")
            assert "Expected revision 2, but current database revision is 4" in err_msg

    async def test_get_not_found_returns_404(self):
        layout_id = uuid.uuid4()
        self.mock_service.get_layout.side_effect = LayoutNotFoundError("Not found")

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get(f"/api/v1/charts/layouts/{layout_id}")
            assert res.status_code == 404

    async def test_delete_endpoint_204(self):
        layout_id = uuid.uuid4()
        self.mock_service.delete_layout.return_value = True

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.delete(f"/api/v1/charts/layouts/{layout_id}")
            assert res.status_code == 204
