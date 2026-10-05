import uuid
from typing import Any
from pydantic import BaseModel
from atlas.auth import AuthPrincipal
from atlas.capabilities.types import CapabilityInvocationSource

class CapabilityApplicationContextSnapshot(BaseModel):
    """Snapshot of Stage 26 Global Application Context to be used by capabilities"""
    selected_entity_id: str | None = None
    time_range: dict | None = None
    selected_portfolio_id: str | None = None
    selected_workspace_id: str | None = None
    map_context: dict | None = None
    filters: dict | None = None
    selected_object: dict | None = None
    active_module_id: str | None = None

    model_config = {"extra": "forbid"}

class CapabilityExecutionContext(BaseModel):
    """Context under which a Capability is executed"""
    principal: AuthPrincipal
    invocation_source: CapabilityInvocationSource
    request_id: str
    correlation_id: str | None = None
    application_context: CapabilityApplicationContextSnapshot | None = None

    model_config = {"extra": "forbid", "arbitrary_types_allowed": True}
