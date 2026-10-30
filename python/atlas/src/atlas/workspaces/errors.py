"""
Typed Domain Exceptions for ATLAS Workspaces Architecture (Stage 120).
"""

from typing import Any, Optional


class WorkspaceError(Exception):
    """Base exception for all workspace errors."""

    def __init__(
        self,
        message: str,
        code: str = "WORKSPACE_ERROR",
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class WorkspaceNotFoundError(WorkspaceError):
    def __init__(self, workspace_id: str):
        super().__init__(
            f"Workspace '{workspace_id}' was not found.",
            code="WORKSPACE_NOT_FOUND",
            status_code=404,
            details={"workspace_id": workspace_id},
        )


class WorkspaceAccessDeniedError(WorkspaceError):
    def __init__(self, workspace_id: str, user_id: str):
        super().__init__(
            f"User '{user_id}' does not have permission to access workspace '{workspace_id}'.",
            code="WORKSPACE_ACCESS_DENIED",
            status_code=403,
            details={"workspace_id": workspace_id, "user_id": user_id},
        )


class WorkspaceNameInvalidError(WorkspaceError):
    def __init__(self, reason: str):
        super().__init__(
            f"Invalid workspace name: {reason}",
            code="WORKSPACE_NAME_INVALID",
            status_code=400,
            details={"reason": reason},
        )


class WorkspaceLimitExceededError(WorkspaceError):
    def __init__(self, limit: int, current: int):
        super().__init__(
            f"Workspace limit exceeded. Maximum allowed: {limit}, current: {current}.",
            code="WORKSPACE_LIMIT_EXCEEDED",
            status_code=400,
            details={"limit": limit, "current": current},
        )


class WorkspaceLayoutSchemaInvalidError(WorkspaceError):
    def __init__(self, reason: str):
        super().__init__(
            f"Workspace layout schema is invalid: {reason}",
            code="WORKSPACE_LAYOUT_SCHEMA_INVALID",
            status_code=422,
            details={"reason": reason},
        )


class WorkspaceLayoutCycleError(WorkspaceError):
    def __init__(self, node_id: str):
        super().__init__(
            f"Cycle detected in workspace layout tree at node '{node_id}'.",
            code="WORKSPACE_LAYOUT_CYCLE_DETECTED",
            status_code=422,
            details={"node_id": node_id},
        )


class WorkspaceLayoutPanelDuplicateError(WorkspaceError):
    def __init__(self, panel_instance_id: str):
        super().__init__(
            f"Duplicate panel instance '{panel_instance_id}' found in multiple layout nodes.",
            code="WORKSPACE_LAYOUT_PANEL_DUPLICATE",
            status_code=422,
            details={"panel_instance_id": panel_instance_id},
        )


class WorkspaceLayoutPanelOrphanError(WorkspaceError):
    def __init__(self, panel_instance_id: str):
        super().__init__(
            f"Panel instance '{panel_instance_id}' referenced in layout tree does not exist in workspace definition.",
            code="WORKSPACE_LAYOUT_PANEL_ORPHAN",
            status_code=422,
            details={"panel_instance_id": panel_instance_id},
        )


class WorkspaceLayoutDepthExceededError(WorkspaceError):
    def __init__(self, depth: int, max_depth: int):
        super().__init__(
            f"Workspace layout nesting depth {depth} exceeds maximum allowable depth of {max_depth}.",
            code="WORKSPACE_LAYOUT_DEPTH_EXCEEDED",
            status_code=422,
            details={"depth": depth, "max_depth": max_depth},
        )


class WorkspaceLayoutSizeInvalidError(WorkspaceError):
    def __init__(self, reason: str):
        super().__init__(
            f"Workspace layout split sizing is invalid: {reason}",
            code="WORKSPACE_LAYOUT_SIZE_INVALID",
            status_code=422,
            details={"reason": reason},
        )


class WorkspaceLayoutRevisionConflictError(WorkspaceError):
    def __init__(self, workspace_id: str, expected_revision: int, actual_revision: int):
        super().__init__(
            f"Optimistic concurrency conflict on workspace '{workspace_id}'. Expected revision {expected_revision}, but server is at revision {actual_revision}.",
            code="WORKSPACE_LAYOUT_REVISION_CONFLICT",
            status_code=409,
            details={
                "workspace_id": workspace_id,
                "expected_revision": expected_revision,
                "actual_revision": actual_revision,
            },
        )


class WorkspacePanelTypeUnsupportedError(WorkspaceError):
    def __init__(self, panel_type_id: str):
        super().__init__(
            f"Workspace panel type '{panel_type_id}' is not recognized or supported.",
            code="WORKSPACE_PANEL_TYPE_UNSUPPORTED",
            status_code=400,
            details={"panel_type_id": panel_type_id},
        )


class WorkspacePanelNotFoundError(WorkspaceError):
    def __init__(self, panel_instance_id: str):
        super().__init__(
            f"Panel instance '{panel_instance_id}' was not found in the workspace.",
            code="WORKSPACE_PANEL_NOT_FOUND",
            status_code=404,
            details={"panel_instance_id": panel_instance_id},
        )


class WorkspacePanelConfigInvalidError(WorkspaceError):
    def __init__(self, panel_type_id: str, reason: str):
        super().__init__(
            f"Invalid configuration for panel type '{panel_type_id}': {reason}",
            code="WORKSPACE_PANEL_CONFIG_INVALID",
            status_code=422,
            details={"panel_type_id": panel_type_id, "reason": reason},
        )


class WorkspacePanelLimitExceededError(WorkspaceError):
    def __init__(self, limit: int, current: int):
        super().__init__(
            f"Workspace panel limit exceeded. Maximum allowable panels per desk: {limit}, requested/current: {current}.",
            code="WORKSPACE_PANEL_LIMIT_EXCEEDED",
            status_code=400,
            details={"limit": limit, "current": current},
        )


class WorkspaceLinkGroupNotFoundError(WorkspaceError):
    def __init__(self, link_group_id: str):
        super().__init__(
            f"Link group '{link_group_id}' was not found in workspace.",
            code="WORKSPACE_LINK_GROUP_NOT_FOUND",
            status_code=404,
            details={"link_group_id": link_group_id},
        )


class WorkspaceTemplateNotFoundError(WorkspaceError):
    def __init__(self, template_id: str):
        super().__init__(
            f"Workspace template '{template_id}' was not found in registry.",
            code="WORKSPACE_TEMPLATE_NOT_FOUND",
            status_code=404,
            details={"template_id": template_id},
        )


class WorkspaceContextLoopError(WorkspaceError):
    def __init__(self, dimension: str, cycle_path: list[str]):
        super().__init__(
            f"Context propagation cycle prevented for dimension '{dimension}' across panels: {' -> '.join(cycle_path)}.",
            code="WORKSPACE_CONTEXT_LOOP_PREVENTED",
            status_code=422,
            details={"dimension": dimension, "cycle_path": cycle_path},
        )
