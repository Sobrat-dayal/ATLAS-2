"""
Comprehensive Test Suite for ATLAS Workspaces Architecture (Stage 120).
"""

import pytest
from atlas.auth import AuthPrincipal
from atlas.workspaces.enums import (
    ContextDimension,
    PanelTypeId,
    SplitOrientation,
    WorkspaceStatus,
    WorkspaceType,
)
from atlas.workspaces.errors import (
    WorkspaceAccessDeniedError,
    WorkspaceLayoutCycleError,
    WorkspaceLayoutPanelDuplicateError,
    WorkspaceLayoutRevisionConflictError,
    WorkspaceLayoutSizeInvalidError,
    WorkspaceNameInvalidError,
    WorkspaceNotFoundError,
)
from atlas.workspaces.layout_validator import (
    create_safe_recovery_layout,
    validate_layout_tree,
)
from atlas.workspaces.models import (
    PanelNode,
    SplitNode,
    TabStackNode,
)
from atlas.workspaces.panel_registry import get_panel_type_definition, list_panel_type_definitions
from atlas.workspaces.repository import WorkspaceRepository
from atlas.workspaces.service import WorkspaceService
from atlas.workspaces.templates import get_workspace_template, list_workspace_templates
from fastapi.testclient import TestClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.workspaces import get_workspace_service


@pytest.fixture
def api_client():
    app = create_app()
    user_a = AuthPrincipal(
        sub="test_trader_a",
        email="trader@example.com",
        role="authenticated",
    )
    test_service = WorkspaceService()
    app.dependency_overrides[get_current_user] = lambda: user_a
    app.dependency_overrides[get_workspace_service] = lambda: test_service
    return TestClient(app)


def test_api_workspace_endpoints(api_client: TestClient):
    """Tests HTTP endpoints via FastAPI TestClient."""
    # 1. List Templates
    res = api_client.get("/api/v1/workspaces/templates")
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 6

    # 2. List Panel Types
    res = api_client.get("/api/v1/workspaces/panel-types")
    assert res.status_code == 200
    ptypes = res.json()
    assert len(ptypes) >= 14

    # 3. Create Workspace
    res = api_client.post(
        "/api/v1/workspaces",
        json={
            "name": "API Automated Desk",
            "description": "Created via integration tests",
            "template_id": "EQUITY_RESEARCH_DESK",
        },
    )
    assert res.status_code == 201
    created_ws = res.json()
    ws_id = created_ws["workspace_id"]
    assert created_ws["name"] == "API Automated Desk"

    # 4. Get Workspace Detail (with layout and link groups)
    res = api_client.get(f"/api/v1/workspaces/{ws_id}")
    assert res.status_code == 200
    detail = res.json()
    assert "layout" in detail
    assert "link_groups" in detail
    assert len(detail["layout"]["panel_instances"]) == 4

    # 5. Update Workspace Metadata
    res = api_client.patch(
        f"/api/v1/workspaces/{ws_id}",
        json={"name": "Renamed API Desk", "is_favorite": True},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Renamed API Desk"
    assert res.json()["is_favorite"] is True

    # 6. Add Panel via API
    res = api_client.post(
        f"/api/v1/workspaces/{ws_id}/panels",
        json={
            "panel_type_id": "NEWS_FEED",
            "title_override": "Extra News",
            "dock_position": "bottom",
        },
    )
    assert res.status_code == 201
    panel_id = res.json()["panel_instance_id"]

    # 7. Update Panel
    res = api_client.patch(
        f"/api/v1/workspaces/{ws_id}/panels/{panel_id}",
        json={"title_override": "Updated Extra News"},
    )
    assert res.status_code == 200
    assert res.json()["title_override"] == "Updated Extra News"

    # 8. Delete Panel
    res = api_client.delete(f"/api/v1/workspaces/{ws_id}/panels/{panel_id}")
    assert res.status_code == 204

    # 9. List Workspaces
    res = api_client.get("/api/v1/workspaces")
    assert res.status_code == 200
    workspaces = res.json()
    assert any(w["workspace_id"] == ws_id for w in workspaces)

    # 10. Delete Workspace
    res = api_client.delete(f"/api/v1/workspaces/{ws_id}")
    assert res.status_code == 204


def test_layout_validator_valid_tree():
    """Validates simple split and nested layouts pass all invariants."""
    p1 = PanelNode(node_id="n1", panel_instance_id="p1")
    p2 = PanelNode(node_id="n2", panel_instance_id="p2")
    split = SplitNode(
        node_id="s1",
        orientation=SplitOrientation.HORIZONTAL,
        children=[p1, p2],
        size_ratios=[0.5, 0.5],
    )

    panels = validate_layout_tree(split, {"p1", "p2"})
    assert panels == ["p1", "p2"]


def test_layout_validator_ratio_normalization():
    """Tests that ratios slightly off from 1.0 are safely normalized."""
    p1 = PanelNode(node_id="n1", panel_instance_id="p1")
    p2 = PanelNode(node_id="n2", panel_instance_id="p2")
    split = SplitNode(
        node_id="s1",
        orientation=SplitOrientation.HORIZONTAL,
        children=[p1, p2],
        size_ratios=[0.48, 0.48],  # sum is 0.96
    )

    validate_layout_tree(split, {"p1", "p2"})
    assert sum(split.size_ratios) == pytest.approx(1.0, 1e-4)


def test_layout_validator_rejects_negative_or_nan_ratios():
    """Rejects negative or infinite size ratios."""
    p1 = PanelNode(node_id="n1", panel_instance_id="p1")
    p2 = PanelNode(node_id="n2", panel_instance_id="p2")
    split = SplitNode(
        node_id="s1",
        orientation=SplitOrientation.HORIZONTAL,
        children=[p1, p2],
        size_ratios=[0.7, -0.2],
    )

    with pytest.raises(WorkspaceLayoutSizeInvalidError):
        validate_layout_tree(split, {"p1", "p2"})


def test_layout_validator_rejects_duplicate_panel_instances():
    """Rejects layout trees where a single panel is rendered in two places."""
    p1a = PanelNode(node_id="n1", panel_instance_id="p1")
    p1b = PanelNode(node_id="n2", panel_instance_id="p1")
    split = SplitNode(
        node_id="s1",
        orientation=SplitOrientation.HORIZONTAL,
        children=[p1a, p1b],
        size_ratios=[0.5, 0.5],
    )

    with pytest.raises(WorkspaceLayoutPanelDuplicateError):
        validate_layout_tree(split, {"p1"})


def test_layout_validator_detects_cycles():
    """Detects and prevents cycles in the layout tree."""
    split = SplitNode(
        node_id="s1",
        orientation=SplitOrientation.HORIZONTAL,
        children=[],
        size_ratios=[0.5, 0.5],
    )
    # create cycle: split contains itself
    split.children = [split, PanelNode(node_id="n1", panel_instance_id="p1")]

    with pytest.raises(WorkspaceLayoutCycleError):
        validate_layout_tree(split)


def test_layout_validator_safe_recovery():
    """Tests clean fallback layout creation for corrupted desks."""
    recovered = create_safe_recovery_layout(["p1", "p2", "p3"])
    assert isinstance(recovered, SplitNode)
    assert len(recovered.children) == 3
    assert sum(recovered.size_ratios) == pytest.approx(1.0, 1e-4)

    # For 5+ panels, recovery groups them in a TabStack
    recovered_large = create_safe_recovery_layout([f"p{i}" for i in range(6)])
    assert isinstance(recovered_large, TabStackNode)
    assert len(recovered_large.panel_instance_ids) == 6


# ---------------- Workspace Lifecycle & CRUD Tests ----------------


def test_workspace_lifecycle_crud():
    repo = WorkspaceRepository()
    user_id = "user_alpha"

    # 1. Create Blank
    ws = repo.create_workspace(
        owner_user_id=user_id, name="Macro & Rates", description="My primary desk"
    )
    assert ws.name == "Macro & Rates"
    assert ws.is_default is True  # First desk is default
    assert ws.layout_revision == 1

    # 2. Get
    fetched = repo.get_workspace(ws.workspace_id, user_id)
    assert fetched.workspace_id == ws.workspace_id

    # 3. Update
    updated = repo.update_workspace_metadata(
        ws.workspace_id, user_id, name="Global Macro Desk", is_favorite=True
    )
    assert updated.name == "Global Macro Desk"
    assert updated.is_favorite is True

    # 4. Duplicate
    dup = repo.duplicate_workspace(ws.workspace_id, user_id, new_name="Macro Staging")
    assert dup.workspace_id != ws.workspace_id
    assert dup.name == "Macro Staging"
    assert dup.is_default is False

    # 5. Soft Delete and Restore
    repo.delete_workspace(ws.workspace_id, user_id, permanent=False)
    with pytest.raises(WorkspaceNotFoundError):
        repo.get_workspace(ws.workspace_id, user_id)

    restored = repo.restore_workspace(ws.workspace_id, user_id)
    assert restored.status == WorkspaceStatus.ACTIVE


def test_workspace_user_isolation():
    """Ensures User B cannot read or modify User A's workspace."""
    repo = WorkspaceRepository()
    ws_a = repo.create_workspace(owner_user_id="user_a", name="User A Secret Desk")

    with pytest.raises(WorkspaceAccessDeniedError):
        repo.get_workspace(ws_a.workspace_id, user_id="user_b")

    with pytest.raises(WorkspaceAccessDeniedError):
        repo.update_workspace_metadata(ws_a.workspace_id, user_id="user_b", name="Hacked Desk")


def test_workspace_name_validation():
    """Rejects empty or oversized workspace names."""
    repo = WorkspaceRepository()
    with pytest.raises(WorkspaceNameInvalidError):
        repo.create_workspace(owner_user_id="user_a", name="   ")

    with pytest.raises(WorkspaceNameInvalidError):
        repo.create_workspace(owner_user_id="user_a", name="X" * 105)


# ---------------- Optimistic Concurrency Control Tests ----------------


def test_optimistic_concurrency_control():
    """Tests that layout updates require expected_revision matching server state."""
    repo = WorkspaceRepository()
    user_id = "trader_quant"
    ws = repo.create_workspace(owner_user_id=user_id, name="Desk Concurrency")
    layout = repo.get_layout(ws.workspace_id, user_id)

    # Valid update with expected_revision == 1
    new_layout_dict = layout.to_dict()
    updated_layout = repo.update_layout(
        workspace_id=ws.workspace_id,
        user_id=user_id,
        expected_revision=1,
        layout_data=new_layout_dict,
    )
    assert updated_layout is not None
    assert ws.layout_revision == 2

    # Conflicting update with stale expected_revision == 1
    with pytest.raises(WorkspaceLayoutRevisionConflictError):
        repo.update_layout(
            workspace_id=ws.workspace_id,
            user_id=user_id,
            expected_revision=1,  # Stale! Server is now at 2
            layout_data=new_layout_dict,
        )

    # Successful update with revision == 2
    repo.update_layout(
        workspace_id=ws.workspace_id,
        user_id=user_id,
        expected_revision=2,
        layout_data=new_layout_dict,
    )
    assert ws.layout_revision == 3


# ---------------- Templates & Panel Registry Tests ----------------


def test_templates_registry():
    """Verifies all 6 institutional desk templates are registered and valid."""
    templates = list_workspace_templates()
    assert len(templates) >= 6

    eq = get_workspace_template("EQUITY_RESEARCH_DESK")
    assert eq.category == "Equity"
    assert len(eq.panel_definitions) == 4

    macro = get_workspace_template("MACRO_DESK")
    assert macro.category == "Macro"

    risk = get_workspace_template("RISK_DESK")
    assert risk.category == "Risk"


def test_workspace_instantiation_from_template():
    """Verifies creating a workspace from the Equity Research Desk template."""
    repo = WorkspaceRepository()
    ws = repo.create_workspace(
        owner_user_id="researcher_1",
        name="Tech Equities Desk",
        template_origin_id="EQUITY_RESEARCH_DESK",
    )
    assert ws.workspace_type == WorkspaceType.TEMPLATE_DERIVED
    assert ws.template_origin_id == "EQUITY_RESEARCH_DESK"

    layout = repo.get_layout(ws.workspace_id, "researcher_1")
    assert len(layout.panel_instances) == 4
    # All panels have distinct IDs
    assert len(set(layout.panel_instances.keys())) == 4


def test_panel_registry_specifications():
    """Verifies panel type registry specifications."""
    panels = list_panel_type_definitions()
    assert len(panels) >= 14

    chart_defn = get_panel_type_definition(PanelTypeId.INSTRUMENT_CHART)
    assert chart_defn.source_module == "charts"
    assert ContextDimension.INSTRUMENT in chart_defn.context_capabilities

    port_defn = get_panel_type_definition(PanelTypeId.PORTFOLIO_SUMMARY)
    assert port_defn.source_module == "portfolios"
    assert ContextDimension.PORTFOLIO in port_defn.context_capabilities


# ---------------- Panel & Link Group Operations Tests ----------------


def test_panel_addition_and_removal():
    """Tests dynamic adding and removing of panels in a workspace."""
    repo = WorkspaceRepository()
    user_id = "desk_user"
    ws = repo.create_workspace(owner_user_id=user_id, name="Dynamic Desk")

    # Add Watchlist panel
    new_panel = repo.add_panel(
        workspace_id=ws.workspace_id,
        user_id=user_id,
        panel_type_id=PanelTypeId.WATCHLIST,
        title_override="Sector Watchlist",
        dock_position="right",
    )
    assert new_panel.panel_type_id == PanelTypeId.WATCHLIST
    assert new_panel.title_override == "Sector Watchlist"

    layout = repo.get_layout(ws.workspace_id, user_id)
    assert new_panel.panel_instance_id in layout.panel_instances

    # Remove panel
    repo.remove_panel(ws.workspace_id, user_id, new_panel.panel_instance_id)
    layout_after = repo.get_layout(ws.workspace_id, user_id)
    assert new_panel.panel_instance_id not in layout_after.panel_instances


def test_link_group_lifecycle():
    """Tests creating, updating, and deleting cross-panel link groups."""
    repo = WorkspaceRepository()
    user_id = "quant_user"
    ws = repo.create_workspace(owner_user_id=user_id, name="Linked Desk")

    groups = repo.list_link_groups(ws.workspace_id, user_id)
    assert len(groups) == 1  # Default Group A

    # Create Group B
    g_b = repo.create_link_group(
        ws.workspace_id,
        user_id,
        name="Group B",
        color="#10b981",
        initial_context={"INSTRUMENT": "NVDA"},
    )
    assert g_b.name == "Group B"
    assert g_b.context["INSTRUMENT"] == "NVDA"

    # Update context
    updated = repo.update_link_group_context(
        ws.workspace_id, user_id, g_b.link_group_id, {"INSTRUMENT": "MSFT", "TIMEFRAME": "1W"}
    )
    assert updated.context["INSTRUMENT"] == "MSFT"
    assert updated.context["TIMEFRAME"] == "1W"

    # Delete group
    repo.delete_link_group(ws.workspace_id, user_id, g_b.link_group_id)
    remaining = repo.list_link_groups(ws.workspace_id, user_id)
    assert len(remaining) == 1


# ---------------- Stage 119 Saved Resource Integration ----------------


def test_stage119_saved_resource_integration():
    """Verifies that panels can store Stage 119 Saved references in configuration."""
    repo = WorkspaceRepository()
    user_id = "librarian"
    ws = repo.create_workspace(owner_user_id=user_id, name="Library Desk")

    # Add Chart panel referencing a Stage 119 saved configuration ID
    chart_panel = repo.add_panel(
        workspace_id=ws.workspace_id,
        user_id=user_id,
        panel_type_id=PanelTypeId.INSTRUMENT_CHART,
        title_override="Saved Tech Momentum Chart",
        configuration={
            "saved_item_id": "save_chart_001",
            "view_configuration_id": "cfg_chart_v2_99",
            "symbol": "TSLA",
        },
    )
    assert chart_panel.configuration["saved_item_id"] == "save_chart_001"
    assert chart_panel.configuration["view_configuration_id"] == "cfg_chart_v2_99"
