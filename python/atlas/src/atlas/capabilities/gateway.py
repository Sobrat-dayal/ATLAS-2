import time
import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from atlas.capabilities.context import CapabilityExecutionContext
from atlas.capabilities.registry import CapabilityRegistry
from atlas.capabilities.types import CapabilityRef
from atlas.capabilities.errors import (
    CapabilityInputInvalidError,
    CapabilityOutputInvalidError,
    CapabilityForbiddenError,
    CapabilityConfirmationRequiredError,
    CapabilityExecutionFailedError
)
from atlas.authorization.service import AuthorizationContext

logger = logging.getLogger(__name__)

class CapabilityGateway:
    def __init__(self, registry: CapabilityRegistry, authz_context: AuthorizationContext, session: AsyncSession):
        self._registry = registry
        self._authz_context = authz_context
        self._session = session

    async def execute(
        self, 
        ref: CapabilityRef, 
        payload: dict[str, Any], 
        execution_context: CapabilityExecutionContext
    ) -> Any:
        start_time = time.monotonic()
        
        logger.info(
            "capability.execution.started",
            extra={
                "capability_key": ref.key,
                "capability_version": ref.version,
                "invocation_source": execution_context.invocation_source.value,
                "request_id": execution_context.request_id,
                "correlation_id": execution_context.correlation_id,
            }
        )

        try:
            definition = self._registry.get_definition(ref.key, ref.version)

            for req_perm in definition.required_permissions:
                if not self._authz_context.has_permission(req_perm):
                    logger.warning(
                        "capability.execution.forbidden",
                        extra={
                            "capability_key": ref.key,
                            "capability_version": ref.version,
                            "request_id": execution_context.request_id,
                            "missing_permission": req_perm,
                        }
                    )
                    raise CapabilityForbiddenError(f"Missing required permission: {req_perm}")

            if definition.requires_confirmation:
                raise CapabilityConfirmationRequiredError()

            try:
                input_model = definition.input_model.model_validate(payload)
            except ValidationError as e:
                raise CapabilityInputInvalidError(details=e.errors())

            factory = self._registry.get_handler_factory(ref.key, ref.version)
            handler = factory(self._session)
            
            try:
                result = await handler(execution_context, input_model)
            except Exception as e:
                from atlas.core.exceptions import AtlasError
                if isinstance(e, AtlasError):
                    raise
                
                logger.error(
                    "capability.execution.failed",
                    exc_info=True,
                    extra={
                        "capability_key": ref.key,
                        "capability_version": ref.version,
                        "request_id": execution_context.request_id,
                    }
                )
                raise CapabilityExecutionFailedError() from e

            try:
                if not isinstance(result, definition.output_model):
                    result = definition.output_model.model_validate(result)
            except ValidationError as e:
                logger.error(
                    "capability.execution.output_invalid",
                    extra={
                        "capability_key": ref.key,
                        "capability_version": ref.version,
                        "request_id": execution_context.request_id,
                        "details": e.errors()
                    }
                )
                raise CapabilityOutputInvalidError(details=e.errors())

            duration_ms = (time.monotonic() - start_time) * 1000
            logger.info(
                "capability.execution.completed",
                extra={
                    "capability_key": ref.key,
                    "capability_version": ref.version,
                    "permission_class": definition.permission_class.value,
                    "invocation_source": execution_context.invocation_source.value,
                    "request_id": execution_context.request_id,
                    "correlation_id": execution_context.correlation_id,
                    "duration_ms": duration_ms,
                    "status": "success",
                }
            )

            return result
            
        except Exception as e:
            duration_ms = (time.monotonic() - start_time) * 1000
            if not getattr(e, "_logged", False):
                logger.error(
                    "capability.execution.failed",
                    extra={
                        "capability_key": ref.key,
                        "capability_version": ref.version,
                        "request_id": execution_context.request_id,
                        "duration_ms": duration_ms,
                        "status": "failed",
                        "error_type": type(e).__name__
                    }
                )
                e._logged = True
            raise
