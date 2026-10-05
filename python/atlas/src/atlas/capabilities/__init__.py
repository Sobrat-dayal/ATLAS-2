from .registry import CapabilityRegistry
from .gateway import CapabilityGateway
from .types import CapabilityRef, CapabilityInvocationSource, CapabilityExposure, CapabilityPermissionClass
from .context import CapabilityExecutionContext, CapabilityApplicationContextSnapshot
from .handlers import register_all_handlers

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
