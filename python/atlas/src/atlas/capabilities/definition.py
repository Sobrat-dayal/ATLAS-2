import re
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from atlas.capabilities.types import CapabilityPermissionClass, CapabilityExposure

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)

class CapabilityDefinition(Generic[TInput, TOutput]):
    def __init__(
        self,
        key: str,
        version: int,
        title: str,
        description: str,
        category: str,
        permission_class: CapabilityPermissionClass,
        required_permissions: list[str],
        exposure: CapabilityExposure,
        requires_confirmation: bool,
        input_model: Type[TInput],
        output_model: Type[TOutput],
        deprecated: bool = False,
        replacement: str | None = None,
    ):
        if not re.match(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$", key):
            raise ValueError(f"Invalid capability key format: {key}")
            
        if version < 1:
            raise ValueError(f"Capability version must be >= 1, got {version}")
            
        if permission_class == CapabilityPermissionClass.CRITICAL and not requires_confirmation:
            raise ValueError(f"Capability {key} is CRITICAL but does not require confirmation")
            
        self.key = key
        self.version = version
        self.title = title
        self.description = description
        self.category = category
        self.permission_class = permission_class
        self.required_permissions = required_permissions
        self.exposure = exposure
        self.requires_confirmation = requires_confirmation
        self.input_model = input_model
        self.output_model = output_model
        self.deprecated = deprecated
        self.replacement = replacement
