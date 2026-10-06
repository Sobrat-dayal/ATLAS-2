from typing import Any

from pydantic import BaseModel

from atlas.capabilities.types import CapabilityExposure, CapabilityPermissionClass


class CapabilityCatalogEntry(BaseModel):
    key: str
    version: int
    title: str
    description: str
    category: str
    permission_class: CapabilityPermissionClass
    required_permissions: list[str]
    exposure: CapabilityExposure
    requires_confirmation: bool
    deprecated: bool = False
    replacement: str | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
