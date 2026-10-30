"""Typed exception classes for Stage 124 AI Assistant V1."""

from typing import Any, Dict, Optional


class AiError(Exception):
    """Base exception for all AI Assistant operations."""

    def __init__(
        self,
        message: str,
        code: str = "AI_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AiConversationNotFoundError(AiError):
    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation '{conversation_id}' was not found or has been deleted.",
            code="AI_CONVERSATION_NOT_FOUND",
            status_code=404,
            details={"conversation_id": conversation_id},
        )


class AiMessageNotFoundError(AiError):
    def __init__(self, message_id: str):
        super().__init__(
            message=f"Message '{message_id}' was not found.",
            code="AI_MESSAGE_NOT_FOUND",
            status_code=404,
            details={"message_id": message_id},
        )


class AiMessageTooLargeError(AiError):
    def __init__(self, char_count: int, max_chars: int = 16000):
        super().__init__(
            message=f"Message length ({char_count} chars) exceeds the maximum allowed length ({max_chars} chars).",
            code="AI_MESSAGE_TOO_LARGE",
            status_code=400,
            details={"char_count": char_count, "max_chars": max_chars},
        )


class AiConversationEmptyError(AiError):
    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation '{conversation_id}' does not contain any messages to regenerate.",
            code="AI_CONVERSATION_EMPTY",
            status_code=400,
            details={"conversation_id": conversation_id},
        )


class AiGenerationRunNotFoundError(AiError):
    def __init__(self, generation_id: str):
        super().__init__(
            message=f"Generation run '{generation_id}' was not found.",
            code="AI_GENERATION_RUN_NOT_FOUND",
            status_code=404,
            details={"generation_id": generation_id},
        )


class AiGenerationInProgressError(AiError):
    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"A generation is already in progress for conversation '{conversation_id}'.",
            code="AI_GENERATION_IN_PROGRESS",
            status_code=409,
            details={"conversation_id": conversation_id},
        )


class AiGenerationTimeoutError(AiError):
    def __init__(self, timeout_seconds: float):
        super().__init__(
            message=f"AI generation timed out after {timeout_seconds} seconds.",
            code="AI_GENERATION_TIMEOUT",
            status_code=504,
            details={"timeout_seconds": timeout_seconds},
        )


class AiGenerationCancelledError(AiError):
    def __init__(self, generation_id: str):
        super().__init__(
            message=f"Generation run '{generation_id}' was cancelled by the user.",
            code="AI_GENERATION_CANCELLED",
            status_code=400,
            details={"generation_id": generation_id},
        )


class AiModelNotFoundError(AiError):
    def __init__(self, model_id: str):
        super().__init__(
            message=f"AI Model '{model_id}' is not supported or recognized.",
            code="AI_MODEL_NOT_FOUND",
            status_code=404,
            details={"model_id": model_id},
        )


class AiModelNotAuthorizedError(AiError):
    def __init__(self, model_id: str):
        super().__init__(
            message=f"User is not entitled or authorized to access AI model '{model_id}'.",
            code="AI_MODEL_NOT_AUTHORIZED",
            status_code=403,
            details={"model_id": model_id},
        )


class AiProviderError(AiError):
    def __init__(self, provider: str, error_message: str):
        super().__init__(
            message=f"AI provider '{provider}' encountered an error: {error_message}",
            code="AI_PROVIDER_ERROR",
            status_code=502,
            details={"provider": provider, "provider_error": error_message},
        )


class AiRateLimitExceededError(AiError):
    def __init__(self, reset_seconds: int = 60):
        super().__init__(
            message="AI request quota or rate limit exceeded. Please wait before submitting another query.",
            code="AI_RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"reset_seconds": reset_seconds},
        )


class AiAccessDeniedError(AiError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"Access denied to {resource_type} '{resource_id}'.",
            code="AI_PERMISSION_DENIED",
            status_code=403,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )
