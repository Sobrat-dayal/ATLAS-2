"""Semantic binder for ATLAS Command Language v1."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .ast import AtlasCommandAst
from .enums import AtlasCommandErrorCode, AtlasCommandParseStatus, AtlasCommandSourceKind
from .errors import AtlasCommandBinderError
from .specs import COMMAND_SPEC_REGISTRY, AtlasCommandSpecRegistry


@dataclass
class BoundAtlasCommand:
    """Semantically validated command ready for target resolution and authorization."""

    command_id: str
    source_kind: AtlasCommandSourceKind
    module_id: Optional[str] = None
    action: Optional[str] = None
    raw_target: Optional[str] = None
    target_required: bool = False
    allowed_target_entity_types: Optional[List[str]] = None
    available: bool = True
    unavailable_reason: Optional[str] = None
    required_permission: Optional[str] = None
    arguments: Dict[str, Any] = field(default_factory=dict)


class AtlasCommandBinder:
    """Binds syntax tree to static command specifications, checking grammar rules,
    parameters, target requirements, and availability.
    """

    def __init__(self, registry: Optional[AtlasCommandSpecRegistry] = None):
        self.registry = registry or COMMAND_SPEC_REGISTRY

    def bind(self, ast: AtlasCommandAst) -> BoundAtlasCommand:
        """Binds an AtlasCommandAst to a BoundAtlasCommand.

        Raises:
            AtlasCommandBinderError on unknown modules, unknown actions,
            unknown parameters, or missing target entities.
        """
        # Disallow unsupported parameters in v1
        if ast.parameters:
            first_param = next(iter(ast.parameters.keys()))
            raise AtlasCommandBinderError(
                error_code=AtlasCommandErrorCode.UNKNOWN_PARAMETER,
                message=(
                    f"Unknown parameter '--{first_param}'. "
                    "Parameter options are not supported in ATLAS v1."
                ),
                raw_token=first_param,
            )

        if ast.source_kind == AtlasCommandSourceKind.SLASH:
            return self._bind_slash(ast)
        else:
            return self._bind_shorthand(ast)

    def _bind_slash(self, ast: AtlasCommandAst) -> BoundAtlasCommand:
        name = ast.command_name or ""

        # 1. Check utility specs
        util_spec = self.registry.resolve_utility_by_name_or_alias(name)
        if util_spec:
            if ast.target is not None:
                raise AtlasCommandBinderError(
                    error_code=AtlasCommandErrorCode.UNEXPECTED_TOKEN,
                    message=(
                        f"Utility command '/{util_spec.canonical_slash_name}' "
                        "does not accept a target."
                    ),
                    raw_token=ast.target,
                )
            return BoundAtlasCommand(
                command_id=util_spec.command_id,
                source_kind=ast.source_kind,
                module_id=None,
                action=ast.action,
                raw_target=None,
                target_required=False,
                available=True,
                required_permission=None,
            )

        # 2. Check module specs
        mod_spec = self.registry.resolve_module_by_name_or_alias(name)
        if not mod_spec:
            raise AtlasCommandBinderError(
                error_code=AtlasCommandErrorCode.UNKNOWN_MODULE,
                message=f"Unknown module or command '/{name}'.",
                raw_token=name,
            )

        # Check action & target combination
        if ast.action == "open" and ast.target is None:
            raise AtlasCommandBinderError(
                error_code=AtlasCommandErrorCode.MISSING_TARGET,
                message=f"Target entity required for '/{mod_spec.canonical_slash_name} open'.",
                status=AtlasCommandParseStatus.INCOMPLETE,
            )

        if ast.target:
            if not mod_spec.supports_entity_context or not mod_spec.entity_command_id:
                raise AtlasCommandBinderError(
                    error_code=AtlasCommandErrorCode.UNEXPECTED_TOKEN,
                    message=f"Module '{mod_spec.module_id}' does not support an entity target.",
                    raw_token=ast.target,
                )
            return BoundAtlasCommand(
                command_id=mod_spec.entity_command_id,
                source_kind=ast.source_kind,
                module_id=mod_spec.module_id,
                action=ast.action or mod_spec.default_action,
                raw_target=ast.target,
                target_required=True,
                allowed_target_entity_types=mod_spec.allowed_target_entity_types,
                available=True,
                required_permission=mod_spec.required_permission,
            )
        else:
            return BoundAtlasCommand(
                command_id=mod_spec.command_id,
                source_kind=ast.source_kind,
                module_id=mod_spec.module_id,
                action=ast.action,
                raw_target=None,
                target_required=False,
                available=True,
                required_permission=mod_spec.required_permission,
            )

    def _bind_shorthand(self, ast: AtlasCommandAst) -> BoundAtlasCommand:
        # Match against shorthand specs
        raw_upper = " ".join(ast.raw_text.strip().upper().split())

        # Exact match
        exact_spec = self.registry.find_shorthand_exact(raw_upper)
        if exact_spec:
            mod_spec = self.registry.modules_by_id.get(exact_spec.module_id)
            req_perm = mod_spec.required_permission if mod_spec else None
            return BoundAtlasCommand(
                command_id=exact_spec.command_id,
                source_kind=ast.source_kind,
                module_id=exact_spec.module_id,
                action=exact_spec.action,
                raw_target=None,
                target_required=False,
                available=exact_spec.available,
                unavailable_reason=exact_spec.unavailable_reason,
                required_permission=req_perm,
            )

        # Suffix match
        if ast.action:
            for spec in self.registry.shorthand_specs:
                if spec.syntax_kind == "suffix" and spec.action == ast.action:
                    mod_spec = self.registry.modules_by_id.get(spec.module_id)
                    req_perm = mod_spec.required_permission if mod_spec else None
                    return BoundAtlasCommand(
                        command_id=spec.command_id,
                        source_kind=ast.source_kind,
                        module_id=spec.module_id,
                        action=spec.action,
                        raw_target=ast.target,
                        target_required=spec.target_required,
                        allowed_target_entity_types=spec.allowed_target_entity_types,
                        available=spec.available,
                        unavailable_reason=spec.unavailable_reason,
                        required_permission=req_perm,
                    )

        # Prefix match
        for spec in self.registry.shorthand_specs:
            if spec.syntax_kind == "prefix" and spec.module_id == ast.command_name:
                mod_spec = self.registry.modules_by_id.get(spec.module_id)
                req_perm = mod_spec.required_permission if mod_spec else None
                return BoundAtlasCommand(
                    command_id=spec.command_id,
                    source_kind=ast.source_kind,
                    module_id=spec.module_id,
                    action=spec.action,
                    raw_target=ast.target,
                    target_required=spec.target_required,
                    allowed_target_entity_types=spec.allowed_target_entity_types,
                    available=spec.available,
                    unavailable_reason=spec.unavailable_reason,
                    required_permission=req_perm,
                )

        raise AtlasCommandBinderError(
            error_code=AtlasCommandErrorCode.UNKNOWN_COMMAND,
            message="Unable to bind unrecognized command structure.",
        )
