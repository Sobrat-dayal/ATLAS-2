"""Unit and Integration Test Suite for ATLAS Stage 119 - Universal Saved System."""

from __future__ import annotations

import time

import pytest
from atlas.auth import AuthPrincipal
from atlas.saved.configurations import (
    compute_payload_hash,
)
from atlas.saved.enums import (
    ResourceAvailabilityStatus,
    SavedBulkActionType,
    SavedModule,
    SavedReferenceSemantics,
    SavedSortOption,
    SavedTargetType,
    ViewConfigurationType,
)
from atlas.saved.errors import (
    SavedCollectionDuplicateNameError,
    SavedCollectionHierarchyCycleError,
    SavedConfigurationInvalidError,
    SavedItemAccessDeniedError,
    SavedItemAlreadyExistsError,
    SavedItemNotFoundError,
    SavedItemVersionConflictError,
    SavedTargetAccessDeniedError,
)
from atlas.saved.registry import (
    build_safe_deep_link,
    get_target_definition,
    list_supported_target_types,
)
from atlas.saved.repository import SavedRepository
from atlas.saved.resolvers import TargetResolver
from atlas.saved.schemas import (
    CreateSavedCollectionRequest,
    CreateSavedConfigurationRequest,
    CreateSavedItemRequest,
    SavedBulkActionRequest,
    UpdateSavedCollectionRequest,
    UpdateSavedItemRequest,
    ValidateConfigurationRequest,
)
from atlas.saved.service import SavedService
from fastapi.testclient import TestClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.saved import get_saved_service


@pytest.fixture
def service() -> SavedService:
    repo = SavedRepository()
    return SavedService(repository=repo)


# =============================================================================
# 1. Target Catalog & Safe Deep Links
# =============================================================================


def test_target_catalog_completeness():
    types = list_supported_target_types()
    assert len(types) >= 22
    for t in SavedTargetType:
        defn = get_target_definition(t)
        assert defn is not None
        assert defn.target_type == t
        assert defn.module is not None
        assert defn.display_name


def test_safe_deep_link_builder_internal_only():
    # Valid targets
    inst_link = build_safe_deep_link(SavedTargetType.INSTRUMENT, "AAPL")
    assert inst_link == "/markets?instrument_id=AAPL"

    chart_link = build_safe_deep_link(SavedTargetType.CHART_CONFIG, "layout_123")
    assert chart_link == "/charts?config_id=layout_123"

    report_link = build_safe_deep_link(
        SavedTargetType.RESEARCH_REPORT, "rep_456", target_revision_id="rev_2"
    )
    assert report_link == "/research?report_id=rep_456&revision_id=rev_2"

    portfolio_link = build_safe_deep_link(SavedTargetType.PORTFOLIO_REFERENCE, "port_789")
    assert portfolio_link == "/portfolios?portfolio_id=port_789"

    risk_link = build_safe_deep_link(SavedTargetType.RISK_RUN, "run_101")
    assert risk_link == "/risk?run_id=run_101"

    # Malicious injection attempt: pseudo protocols or external URLs
    malicious = "javascript:alert(1)"
    safe = build_safe_deep_link(SavedTargetType.INSTRUMENT, malicious)
    assert not safe.startswith("javascript:")
    assert "javascript" in safe
    assert safe.startswith("/markets?instrument_id=")

    external = "https://evil.com/phish"
    safe_ext = build_safe_deep_link(SavedTargetType.COMPANY, external)
    assert not safe_ext.startswith("https://")
    assert safe_ext.startswith("/companies?id=")


# =============================================================================
# 2. Canonical Target Resolvers & Runtime Availability
# =============================================================================


def test_resolvers_runtime_availability():
    user_id = "user_1"

    # Available
    res_aapl = TargetResolver.resolve_target(user_id, SavedTargetType.INSTRUMENT, "AAPL")
    assert res_aapl.exists is True
    assert res_aapl.authorized is True
    assert res_aapl.status == ResourceAvailabilityStatus.AVAILABLE
    assert "Apple Inc." in res_aapl.canonical_title

    # Delisted with warning
    res_delisted = TargetResolver.resolve_target(
        user_id, SavedTargetType.INSTRUMENT, "DELISTED_CORP"
    )
    assert res_delisted.status == ResourceAvailabilityStatus.AVAILABLE_WITH_WARNINGS
    assert len(res_delisted.warnings) > 0

    # Target Not Found
    res_nf = TargetResolver.resolve_target(user_id, SavedTargetType.COMPANY, "NOT_FOUND_CO")
    assert res_nf.status == ResourceAvailabilityStatus.TARGET_NOT_FOUND
    assert res_nf.exists is False

    # Target Deleted
    res_del = TargetResolver.resolve_target(user_id, SavedTargetType.RISK_RUN, "DELETED_RUN_1")
    assert res_del.status == ResourceAvailabilityStatus.TARGET_DELETED

    # Unauthorized
    res_unauth = TargetResolver.resolve_target(
        user_id, SavedTargetType.PORTFOLIO_REFERENCE, "FORBIDDEN_PORTFOLIO"
    )
    assert res_unauth.status == ResourceAvailabilityStatus.PERMISSION_REVOKED
    assert res_unauth.authorized is False

    # Source Restricted without pro tier
    res_rest = TargetResolver.resolve_target(
        user_id, SavedTargetType.NEWS_ARTICLE, "RESTRICTED_SOURCE_ARTICLE"
    )
    assert res_rest.status == ResourceAvailabilityStatus.SOURCE_RESTRICTED
    assert res_rest.entitled is False

    # Superseded revision
    res_super = TargetResolver.resolve_target(
        user_id, SavedTargetType.RESEARCH_REPORT, "rep_1", requested_revision_id="rev_old"
    )
    assert res_super.status == ResourceAvailabilityStatus.TARGET_SUPERSEDED
    assert res_super.latest_revision_id == "rev_2_approved"


# =============================================================================
# 3. Save Item Lifecycle, Duplicates, and Idempotency
# =============================================================================


def test_save_item_crud_and_idempotency(service: SavedService):
    user_id = "user_alpha"

    # Save
    req = CreateSavedItemRequest(
        target_type=SavedTargetType.INSTRUMENT,
        target_id="AAPL",
        user_note="Key long-term holding.",
        favorite=True,
        tags=["Core", "Tech"],
        idempotency_key="key_123",
    )
    item = service.save_item(user_id, req)
    assert item.display_title == "Apple Inc. (AAPL · NASDAQ)"
    assert item.favorite is True
    assert item.user_note == "Key long-term holding."
    assert "Core" in item.tags
    assert item.availability_status == ResourceAvailabilityStatus.AVAILABLE

    # Idempotent repeat: returns existing item
    repeated = service.save_item(user_id, req)
    assert repeated.saved_item_id == item.saved_item_id

    # Duplicate without idempotency key raises SavedItemAlreadyExistsError
    req_no_key = CreateSavedItemRequest(
        target_type=SavedTargetType.INSTRUMENT,
        target_id="AAPL",
    )
    with pytest.raises(SavedItemAlreadyExistsError):
        service.save_item(user_id, req_no_key)

    # Update metadata
    update_req = UpdateSavedItemRequest(
        display_title_override="Apple Inc. (Overweight)",
        user_note="Updated investment thesis.",
        pinned=True,
        expected_row_version=item.row_version,
    )
    updated = service.update_item(item.saved_item_id, user_id, update_req)
    assert updated.display_title == "Apple Inc. (Overweight)"
    assert updated.user_note == "Updated investment thesis."
    assert updated.pinned is True
    assert updated.row_version == 2

    # Optimistic concurrency conflict check
    stale_req = UpdateSavedItemRequest(display_title_override="Stale", expected_row_version=1)
    with pytest.raises(SavedItemVersionConflictError):
        service.update_item(item.saved_item_id, user_id, stale_req)

    # Soft delete
    service.soft_delete_item(item.saved_item_id, user_id)
    with pytest.raises(SavedItemNotFoundError):
        service.get_item(item.saved_item_id, user_id)

    # Restore
    restored = service.restore_item(item.saved_item_id, user_id)
    assert restored.saved_item_id == item.saved_item_id
    assert restored.deleted_at is None


def test_cannot_save_unauthorized_target(service: SavedService):
    user_id = "user_beta"
    req = CreateSavedItemRequest(
        target_type=SavedTargetType.PORTFOLIO_REFERENCE,
        target_id="FORBIDDEN_PORTFOLIO_99",
    )
    with pytest.raises(SavedTargetAccessDeniedError):
        service.save_item(user_id, req)


def test_cross_user_isolation(service: SavedService):
    user_1 = "user_1"
    user_2 = "user_2"

    req = CreateSavedItemRequest(target_type=SavedTargetType.COMPANY, target_id="MSFT")
    item = service.save_item(user_1, req)

    # User 2 cannot access user 1's saved item
    with pytest.raises(SavedItemAccessDeniedError):
        service.get_item(item.saved_item_id, user_2)

    with pytest.raises(SavedItemAccessDeniedError):
        service.update_item(item.saved_item_id, user_2, UpdateSavedItemRequest(user_note="hacked"))

    with pytest.raises(SavedItemAccessDeniedError):
        service.soft_delete_item(item.saved_item_id, user_2)


# =============================================================================
# 4. Collections Hierarchy, Cycles, and Memberships
# =============================================================================


def test_collections_hierarchy_and_cycles(service: SavedService):
    user_id = "user_cols"

    # Create root collection
    c1 = service.create_collection(user_id, CreateSavedCollectionRequest(name="Equities Research"))
    assert c1.name == "Equities Research"

    # Duplicate name check
    with pytest.raises(SavedCollectionDuplicateNameError):
        service.create_collection(user_id, CreateSavedCollectionRequest(name="Equities Research"))

    # Child collection
    c2 = service.create_collection(
        user_id,
        CreateSavedCollectionRequest(name="Big Tech", parent_collection_id=c1.collection_id),
    )
    assert c2.parent_collection_id == c1.collection_id

    # Grandchild collection
    c3 = service.create_collection(
        user_id,
        CreateSavedCollectionRequest(name="Semiconductors", parent_collection_id=c2.collection_id),
    )

    # Cycle check: attempting to make c1 a child of c3
    with pytest.raises(SavedCollectionHierarchyCycleError):
        service.update_collection(
            c1.collection_id,
            user_id,
            UpdateSavedCollectionRequest(parent_collection_id=c3.collection_id),
        )

    # Tree check
    tree = service.get_collection_tree(user_id)
    assert len(tree) == 1
    assert tree[0].collection.collection_id == c1.collection_id
    assert len(tree[0].children) == 1
    assert tree[0].children[0].collection.collection_id == c2.collection_id


def test_collection_membership(service: SavedService):
    user_id = "user_mem"
    col = service.create_collection(user_id, CreateSavedCollectionRequest(name="Tech Focus"))
    item = service.save_item(
        user_id, CreateSavedItemRequest(target_type=SavedTargetType.COMPANY, target_id="MSFT")
    )

    # Add item to collection
    service.add_items_to_collection(col.collection_id, user_id, [item.saved_item_id])
    assert service.repository.get_collection_item_count(col.collection_id) == 1
    assert col.collection_id in service.repository.get_item_collection_ids(item.saved_item_id)

    # Delete collection: collection removed, but item remains
    service.delete_collection(col.collection_id, user_id)
    retrieved_item = service.get_item(item.saved_item_id, user_id)
    assert retrieved_item is not None
    assert col.collection_id not in retrieved_item.collection_ids


# =============================================================================
# 5. Tags and Notes
# =============================================================================


def test_tags_and_notes(service: SavedService):
    user_id = "user_tags"
    item = service.save_item(
        user_id, CreateSavedItemRequest(target_type=SavedTargetType.INSTRUMENT, target_id="NVDA")
    )

    # Assign tags
    t1 = service.assign_tag(item.saved_item_id, user_id, "Semiconductors")
    t2 = service.assign_tag(
        item.saved_item_id, user_id, "semiconductors"
    )  # Case insensitive normalization
    assert t1.tag_id == t2.tag_id

    service.assign_tag(item.saved_item_id, user_id, "AI-Hardware")

    tags = service.list_tags(user_id)
    assert len(tags) == 2
    names = [t.name for t in tags]
    assert "Semiconductors" in names
    assert "AI-Hardware" in names

    # Remove tag
    service.remove_tag(item.saved_item_id, user_id, t1.tag_id)
    updated_tags = service.repository.get_item_tag_names(item.saved_item_id)
    assert "Semiconductors" not in updated_tags
    assert "AI-Hardware" in updated_tags


# =============================================================================
# 6. View Configurations, Secret Redaction, and Migrations
# =============================================================================


def test_view_configuration_validation_and_secret_redaction(service: SavedService):
    user_id = "user_configs"

    # Valid Chart Config with secrets embedded
    chart_payload = {
        "timeframe": "1D",
        "chart_type": "CANDLESTICK",
        "indicators": [{"type": "RSI", "period": 14}],
        "api_key": "secret_api_key_12345",
        "nested": {"token": "bearer_token_xyz"},
    }

    config = service.save_configuration(
        user_id,
        CreateSavedConfigurationRequest(
            configuration_type=ViewConfigurationType.CHART,
            schema_version=1,
            payload=chart_payload,
            target_module=SavedModule.CHARTS,
        ),
    )

    # Verify secrets were redacted
    assert config.payload["api_key"] == "[REDACTED_SECRET]"
    assert config.payload["nested"]["token"] == "[REDACTED_SECRET]"
    assert config.payload["timeframe"] == "1D"
    assert config.payload_hash == compute_payload_hash(config.payload)

    # Link config to saved item
    item = service.save_item(
        user_id,
        CreateSavedItemRequest(
            target_type=SavedTargetType.CHART_CONFIG,
            target_id="layout_master",
            view_configuration_id=config.configuration_id,
        ),
    )
    assert item.view_configuration_id == config.configuration_id
    assert item.semantics == SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION


def test_configuration_migration(service: SavedService):
    user_id = "user_mig"

    v1_payload = {
        "timeframe": "1W",
        "chart_type": "LINE",
    }

    val_res = service.validate_configuration(
        user_id,
        ValidateConfigurationRequest(
            configuration_type=ViewConfigurationType.CHART,
            schema_version=1,
            payload=v1_payload,
            target_version=2,
        ),
    )
    assert val_res.valid is True
    assert val_res.migrated_version == 2
    assert val_res.migrated_payload["timezone"] == "UTC"
    assert val_res.migrated_payload["indicators"] == []


def test_configuration_forbids_raw_sql(service: SavedService):
    user_id = "user_sec"
    bad_payload = {
        "query_name": "custom_query",
        "raw_sql": "SELECT * FROM users; DROP TABLE portfolios;",
    }
    with pytest.raises(SavedConfigurationInvalidError):
        service.save_configuration(
            user_id,
            CreateSavedConfigurationRequest(
                configuration_type=ViewConfigurationType.DATA_QUERY,
                schema_version=1,
                payload=bad_payload,
                target_module=SavedModule.DATA,
            ),
        )


# =============================================================================
# 7. Search, Filtering, and Sorting
# =============================================================================


def test_search_filtering_sorting(service: SavedService):
    user_id = "user_search"

    # Seed 3 items
    i1 = service.save_item(
        user_id,
        CreateSavedItemRequest(
            target_type=SavedTargetType.INSTRUMENT,
            target_id="AAPL",
            display_title_override="Apple Tech Giant",
            user_note="Consumer electronic ecosystem",
            favorite=True,
            pinned=False,
            tags=["MegaCap"],
        ),
    )
    i2 = service.save_item(
        user_id,
        CreateSavedItemRequest(
            target_type=SavedTargetType.COMPANY,
            target_id="MSFT",
            display_title_override="Microsoft Cloud Leader",
            user_note="Azure enterprise software",
            favorite=False,
            pinned=True,
            tags=["Cloud"],
        ),
    )
    i3 = service.save_item(
        user_id,
        CreateSavedItemRequest(
            target_type=SavedTargetType.RESEARCH_REPORT,
            target_id="rep_ai",
            display_title_override="AI Sector Quarterly Deep Dive",
            user_note="Generative AI capex trends",
            favorite=True,
            pinned=False,
            tags=["Research"],
        ),
    )

    # 1. Free text search on note
    res_note = service.list_items(user_id, search="ecosystem")
    assert res_note.total_count == 1
    assert res_note.items[0].saved_item_id == i1.saved_item_id

    # 2. Search by tag
    res_tag = service.list_items(user_id, tag="Cloud")
    assert res_tag.total_count == 1
    assert res_tag.items[0].saved_item_id == i2.saved_item_id

    # 3. Filter by favorite
    res_fav = service.list_items(user_id, favorite=True)
    assert res_fav.total_count == 2

    # 4. Filter by resource type
    res_type = service.list_items(user_id, target_type=SavedTargetType.RESEARCH_REPORT)
    assert res_type.total_count == 1
    assert res_type.items[0].saved_item_id == i3.saved_item_id

    # 5. Sorting: pinned items precede others
    res_all = service.list_items(user_id, sort_by=SavedSortOption.RECENTLY_SAVED)
    assert res_all.total_count == 3
    # MSFT is pinned -> should appear first
    assert res_all.items[0].saved_item_id == i2.saved_item_id


# =============================================================================
# 8. Bulk Actions
# =============================================================================


def test_bulk_operations(service: SavedService):
    user_id = "user_bulk"
    item1 = service.save_item(
        user_id, CreateSavedItemRequest(target_type=SavedTargetType.INSTRUMENT, target_id="AAPL")
    )
    item2 = service.save_item(
        user_id, CreateSavedItemRequest(target_type=SavedTargetType.COMPANY, target_id="MSFT")
    )
    col = service.create_collection(user_id, CreateSavedCollectionRequest(name="Portfolio Core"))

    # Bulk favorite
    res_fav = service.execute_bulk_action(
        user_id,
        SavedBulkActionRequest(
            action=SavedBulkActionType.FAVORITE,
            saved_item_ids=[item1.saved_item_id, item2.saved_item_id],
        ),
    )
    assert res_fav.succeeded_count == 2
    assert res_fav.failed_count == 0

    # Bulk add to collection
    res_col = service.execute_bulk_action(
        user_id,
        SavedBulkActionRequest(
            action=SavedBulkActionType.ADD_TO_COLLECTION,
            saved_item_ids=[item1.saved_item_id, item2.saved_item_id],
            collection_id=col.collection_id,
        ),
    )
    assert res_col.succeeded_count == 2

    # Partial failure check: include a non-existent ID
    res_partial = service.execute_bulk_action(
        user_id,
        SavedBulkActionRequest(
            action=SavedBulkActionType.DELETE,
            saved_item_ids=[item1.saved_item_id, "non_existent_uuid"],
        ),
    )
    assert res_partial.succeeded_count == 1
    assert res_partial.failed_count == 1
    assert res_partial.results[1].success is False


@pytest.fixture
def api_client(service: SavedService):
    app = create_app()
    user_a = AuthPrincipal(
        sub="test_user_a",
        email="user_a@example.com",
        role="authenticated",
    )
    app.dependency_overrides[get_current_user] = lambda: user_a
    app.dependency_overrides[get_saved_service] = lambda: service
    return TestClient(app)


def test_api_saved_endpoints(api_client: TestClient):
    # 1. GET /api/v1/saved/types
    res_types = api_client.get("/api/v1/saved/types")
    assert res_types.status_code == 200
    types = res_types.json()
    assert len(types) >= 22

    # 2. POST /api/v1/saved (save instrument)
    save_req = {
        "target_type": "INSTRUMENT",
        "target_id": "AAPL",
        "user_note": "Via API test.",
        "favorite": True,
        "pinned": True,
        "tags": ["Tech", "Core"],
    }
    res_save = api_client.post("/api/v1/saved", json=save_req)
    assert res_save.status_code == 201
    item_data = res_save.json()
    item_id = item_data["saved_item_id"]
    assert item_data["display_title"] == "Apple Inc. (AAPL · NASDAQ)"
    assert item_data["favorite"] is True
    assert item_data["pinned"] is True

    # 3. GET /api/v1/saved
    res_list = api_client.get("/api/v1/saved")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total_count"] == 1
    assert list_data["items"][0]["saved_item_id"] == item_id

    # 4. GET /api/v1/saved/{id}
    res_get = api_client.get(f"/api/v1/saved/{item_id}")
    assert res_get.status_code == 200
    assert res_get.json()["saved_item_id"] == item_id

    # 5. PUT /api/v1/saved/{id}/favorite toggle
    res_unfav = api_client.delete(f"/api/v1/saved/{item_id}/favorite")
    assert res_unfav.status_code == 200
    assert res_unfav.json()["favorite"] is False

    # 6. POST /api/v1/saved/collections
    col_req = {"name": "API Collection", "description": "Created in test"}
    res_col = api_client.post("/api/v1/saved/collections", json=col_req)
    assert res_col.status_code == 201
    col_id = res_col.json()["collection_id"]

    # 7. POST /api/v1/saved/collections/{id}/items
    res_add = api_client.post(
        f"/api/v1/saved/collections/{col_id}/items", json={"saved_item_ids": [item_id]}
    )
    assert res_add.status_code == 200

    # 8. POST /api/v1/saved/configurations
    cfg_req = {
        "configuration_type": "CHART",
        "schema_version": 1,
        "payload": {"timeframe": "1D", "chart_type": "CANDLESTICK"},
        "target_module": "charts",
    }
    res_cfg = api_client.post("/api/v1/saved/configurations", json=cfg_req)
    assert res_cfg.status_code == 201
    assert "configuration_id" in res_cfg.json()

    # 9. GET /api/v1/saved/summary
    res_sum = api_client.get("/api/v1/saved/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["total_saved_items"] == 1
    assert sum_data["collection_count"] == 1

    # 10. DELETE /api/v1/saved/{id}
    res_del = api_client.delete(f"/api/v1/saved/{item_id}")
    assert res_del.status_code == 204

    # 11. POST /api/v1/saved/{id}/restore
    res_restore = api_client.post(f"/api/v1/saved/{item_id}/restore")
    assert res_restore.status_code == 200
    assert res_restore.json()["deleted_at"] is None


def test_synthetic_scale_performance(service: SavedService):
    user_id = "user_scale"
    start_time = time.time()

    # Seed 200 items rapidly
    for i in range(200):
        req = CreateSavedItemRequest(
            target_type=SavedTargetType.INSTRUMENT,
            target_id=f"TICKER_{i}",
            display_title_override=f"Synthetic Instrument {i}",
            tags=[f"Tag_{i % 5}"],
            favorite=(i % 3 == 0),
        )
        service.save_item(user_id, req)

    save_duration = time.time() - start_time
    assert save_duration < 2.0  # 200 saves under 2 seconds

    # Query with search & filter
    query_start = time.time()
    res = service.list_items(user_id, search="Instrument 1", page=1, page_size=20)
    query_duration = time.time() - query_start
    assert query_duration < 0.1  # search & pagination under 100ms
    assert res.total_count > 0

    # Summary KPI calculation
    summary_start = time.time()
    summary = service.get_library_summary(user_id)
    summary_duration = time.time() - summary_start
    assert summary_duration < 0.05
    assert summary.total_saved_items == 200
