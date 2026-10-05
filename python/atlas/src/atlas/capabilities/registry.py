from typing import Callable, Coroutine, Any
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.capabilities.definition import CapabilityDefinition, TInput, TOutput
from atlas.capabilities.types import CapabilityExposure
from atlas.capabilities.context import CapabilityExecutionContext
from atlas.capabilities.errors import CapabilityNotFoundError, CapabilityVersionNotFoundError

CapabilityHandlerType = Callable[[CapabilityExecutionContext, TInput], Coroutine[Any, Any, TOutput]]
CapabilityHandlerFactory = Callable[[AsyncSession], CapabilityHandlerType]

class CapabilityRegistry:
    def __init__(self):
        self._definitions: dict[tuple[str, int], CapabilityDefinition] = {}
        self._factories: dict[tuple[str, int], CapabilityHandlerFactory] = {}
        self._frozen = False

    def register(self, definition: CapabilityDefinition, factory: CapabilityHandlerFactory):
        if self._frozen:
            raise RuntimeError("Cannot register capability: registry is frozen")
            
        key_tuple = (definition.key, definition.version)
        if key_tuple in self._definitions:
            raise ValueError(f"Capability '{definition.key}' version {definition.version} is already registered")
            
        self._definitions[key_tuple] = definition
        self._factories[key_tuple] = factory

    def freeze(self):
        self._frozen = True

    def get_definition(self, key: str, version: int = 1) -> CapabilityDefinition:
        key_tuple = (key, version)
        if key_tuple not in self._definitions:
            if any(k == key for k, v in self._definitions.keys()):
                raise CapabilityVersionNotFoundError(key, version)
            raise CapabilityNotFoundError(key, version)
        return self._definitions[key_tuple]

    def get_handler_factory(self, key: str, version: int = 1) -> CapabilityHandlerFactory:
        key_tuple = (key, version)
        if key_tuple not in self._factories:
            if any(k == key for k, v in self._factories.keys()):
                raise CapabilityVersionNotFoundError(key, version)
            raise CapabilityNotFoundError(key, version)
        return self._factories[key_tuple]
        
    def list_capabilities(self, exposure: CapabilityExposure | None = None) -> list[CapabilityDefinition]:
        defs = list(self._definitions.values())
        if exposure:
            defs = [d for d in defs if d.exposure == exposure]
            
        return sorted(defs, key=lambda d: (d.category, d.key, d.version))
