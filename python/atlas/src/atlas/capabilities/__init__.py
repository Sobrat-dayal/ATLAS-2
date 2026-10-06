from .context import CapabilityApplicationContextSnapshot, CapabilityExecutionContext
from .gateway import CapabilityGateway
from .handlers import register_all_handlers
from .registry import CapabilityRegistry
from .types import (
    CapabilityExposure,
    CapabilityInvocationSource,
    CapabilityPermissionClass,
    CapabilityRef,
)

# Global Registry instance
registry = CapabilityRegistry()
register_all_handlers(registry)
registry.freeze()

__all__ = [
    "registry",
    "CapabilityRegistry",
    "CapabilityGateway",
    "CapabilityRef",
    "CapabilityInvocationSource",
    "CapabilityExposure",
    "CapabilityPermissionClass",
    "CapabilityExecutionContext",
    "CapabilityApplicationContextSnapshot",
]
