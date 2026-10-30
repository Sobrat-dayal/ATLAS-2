"""Typed error classes for Stage 125 AI Context Awareness Engine."""

from typing import Any, Dict, Optional

from atlas.ai.errors import AiError


class AiContextError(AiError):
    """Base exception for all AI Context operations."""

    def __init__(
        self,
        message: str,
        code: str = "AI_CONTEXT_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class AiContextUnavailableError(AiContextError):
    def __init__(self, reason: str = "Context service is temporarily unavailable"):
        super().__init__(message=reason, code="AI_CONTEXT_UNAVAILABLE", status_code=503)


class AiContextTypeUnsupportedError(AiContextError):
    def __init__(self, context_type: str):
        super().__init__(
            message=f"Context type '{context_type}' is not supported.",
            code="AI_CONTEXT_TYPE_UNSUPPORTED",
            status_code=400,
            details={"context_type": context_type},
        )


class AiContextReferenceInvalidError(AiContextError):
    def __init__(self, reference: str, reason: str = "Invalid reference format"):
        super().__init__(
            message=f"Context reference '{reference}' is invalid: {reason}",
            code="AI_CONTEXT_REFERENCE_INVALID",
            status_code=400,
            details={"reference": reference, "reason": reason},
        )


class AiContextTargetNotFoundError(AiContextError):
    def __init__(self, target_type: str, target_id: str):
        super().__init__(
            message=f"Context target '{target_id}' of type '{target_type}' was not found.",
            code="AI_CONTEXT_TARGET_NOT_FOUND",
            status_code=404,
            details={"target_type": target_type, "target_id": target_id},
        )


class AiContextTargetAccessDeniedError(AiContextError):
    def __init__(self, target_type: str, target_id: str):
        super().__init__(
            message=f"Access denied to {target_type} '{target_id}' for AI context assembly.",
            code="AI_CONTEXT_TARGET_ACCESS_DENIED",
            status_code=403,
            details={"target_type": target_type, "target_id": target_id},
        )


class AiContextProviderDisclosureDeniedError(AiContextError):
    def __init__(self, target_type: str, target_id: str, provider: str):
        super().__init__(
            message=f"Data provider licensing prohibits transmitting {target_type} '{target_id}' to external model provider '{provider}'.",
            code="AI_CONTEXT_PROVIDER_DISCLOSURE_DENIED",
            status_code=403,
            details={"target_type": target_type, "target_id": target_id, "provider": provider},
        )


class AiContextConsentRequiredError(AiContextError):
    def __init__(self, target_type: str, target_id: str):
        super().__init__(
            message=f"Explicit user consent is required before sharing sensitive {target_type} '{target_id}' with the AI Assistant.",
            code="AI_CONTEXT_CONSENT_REQUIRED",
            status_code=403,
            details={"target_type": target_type, "target_id": target_id},
        )


class AiContextScopeInvalidError(AiContextError):
    def __init__(self, scope: str):
        super().__init__(
            message=f"Context scope '{scope}' is invalid.",
            code="AI_CONTEXT_SCOPE_INVALID",
            status_code=400,
            details={"scope": scope},
        )


class AiContextAmbiguousEntityError(AiContextError):
    def __init__(self, query: str, candidates: list[str]):
        super().__init__(
            message=f"Entity '{query}' is ambiguous between candidates: {', '.join(candidates)}.",
            code="AI_CONTEXT_AMBIGUOUS_ENTITY",
            status_code=409,
            details={"query": query, "candidates": candidates},
        )


class AiContextEntityResolutionFailedError(AiContextError):
    def __init__(self, query: str, entity_type: str):
        super().__init__(
            message=f"Failed to resolve '{query}' to a canonical {entity_type}.",
            code="AI_CONTEXT_ENTITY_RESOLUTION_FAILED",
            status_code=404,
            details={"query": query, "entity_type": entity_type},
        )


class AiContextSourceUnavailableError(AiContextError):
    def __init__(self, source_module: str, reason: str):
        super().__init__(
            message=f"Context source from module '{source_module}' is unavailable: {reason}",
            code="AI_CONTEXT_SOURCE_UNAVAILABLE",
            status_code=502,
            details={"source_module": source_module, "reason": reason},
        )


class AiContextSourceStaleError(AiContextError):
    def __init__(self, source_reference: str, as_of: str):
        super().__init__(
            message=f"Context source '{source_reference}' is stale (as_of: {as_of}).",
            code="AI_CONTEXT_SOURCE_STALE",
            status_code=400,
            details={"source_reference": source_reference, "as_of": as_of},
        )


class AiContextSourceRestrictedError(AiContextError):
    def __init__(self, source_module: str, reason: str):
        super().__init__(
            message=f"Context source '{source_module}' is restricted: {reason}",
            code="AI_CONTEXT_SOURCE_RESTRICTED",
            status_code=403,
            details={"source_module": source_module, "reason": reason},
        )


class AiContextDataQualityInsufficientError(AiContextError):
    def __init__(self, quality_status: str, details_msg: str):
        super().__init__(
            message=f"Data quality is insufficient ({quality_status}): {details_msg}",
            code="AI_CONTEXT_DATA_QUALITY_INSUFFICIENT",
            status_code=422,
            details={"quality_status": quality_status, "reason": details_msg},
        )


class AiContextAsOfIncompatibleError(AiContextError):
    def __init__(self, requested_as_of: str, source_as_of: str):
        super().__init__(
            message=f"Historical as-of date '{requested_as_of}' is incompatible with source as-of date '{source_as_of}'.",
            code="AI_CONTEXT_AS_OF_INCOMPATIBLE",
            status_code=422,
            details={"requested_as_of": requested_as_of, "source_as_of": source_as_of},
        )


class AiContextCurrencyIncompatibleError(AiContextError):
    def __init__(self, currency_a: str, currency_b: str):
        super().__init__(
            message=f"Currencies '{currency_a}' and '{currency_b}' cannot be combined without explicit FX normalization.",
            code="AI_CONTEXT_CURRENCY_INCOMPATIBLE",
            status_code=422,
            details={"currency_a": currency_a, "currency_b": currency_b},
        )


class AiContextRevisionConflictError(AiContextError):
    def __init__(self, expected_rev: int, actual_rev: int):
        super().__init__(
            message=f"Context revision conflict: expected {expected_rev}, current is {actual_rev}.",
            code="AI_CONTEXT_REVISION_CONFLICT",
            status_code=409,
            details={"expected_revision": expected_rev, "actual_revision": actual_rev},
        )


class AiContextAdapterFailedError(AiContextError):
    def __init__(self, adapter_id: str, error_msg: str):
        super().__init__(
            message=f"Context adapter '{adapter_id}' failed: {error_msg}",
            code="AI_CONTEXT_ADAPTER_FAILED",
            status_code=500,
            details={"adapter_id": adapter_id, "error": error_msg},
        )


class AiContextTooLargeError(AiContextError):
    def __init__(self, estimated_tokens: int, budget: int):
        super().__init__(
            message=f"Assembled context ({estimated_tokens} tokens) exceeds token budget ({budget} tokens).",
            code="AI_CONTEXT_TOO_LARGE",
            status_code=400,
            details={"estimated_tokens": estimated_tokens, "budget": budget},
        )


class AiContextTokenBudgetExceededError(AiContextError):
    def __init__(self, budget: int):
        super().__init__(
            message=f"Context token budget of {budget} tokens exceeded.",
            code="AI_CONTEXT_TOKEN_BUDGET_EXCEEDED",
            status_code=400,
            details={"budget": budget},
        )


class AiContextManifestNotFoundError(AiContextError):
    def __init__(self, manifest_id: str):
        super().__init__(
            message=f"Context source manifest '{manifest_id}' was not found.",
            code="AI_CONTEXT_MANIFEST_NOT_FOUND",
            status_code=404,
            details={"manifest_id": manifest_id},
        )


class AiContextManifestAccessDeniedError(AiContextError):
    def __init__(self, manifest_id: str):
        super().__init__(
            message=f"Access denied to context source manifest '{manifest_id}'.",
            code="AI_CONTEXT_MANIFEST_ACCESS_DENIED",
            status_code=403,
            details={"manifest_id": manifest_id},
        )


class AiContextSnapshotUnavailableError(AiContextError):
    def __init__(self, snapshot_id: str):
        super().__init__(
            message=f"Context snapshot '{snapshot_id}' is unavailable.",
            code="AI_CONTEXT_SNAPSHOT_UNAVAILABLE",
            status_code=404,
            details={"snapshot_id": snapshot_id},
        )


class AiContextPersistenceFailedError(AiContextError):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Context persistence failed: {reason}",
            code="AI_CONTEXT_PERSISTENCE_FAILED",
            status_code=500,
            details={"reason": reason},
        )


class AiContextPrivacyPolicyDeniedError(AiContextError):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Context sharing blocked by privacy policy: {reason}",
            code="AI_CONTEXT_PRIVACY_POLICY_DENIED",
            status_code=403,
            details={"reason": reason},
        )
