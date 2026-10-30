"""Typed Domain Errors for Stage 126: ATLAS AI Tool Gateway.

Implements the standard error hierarchy with stable machine-readable error codes.
"""

from typing import Optional


class AiToolError(Exception):
    """Base domain exception for all AI tool operations."""

    def __init__(self, message: str, code: str = "AI_TOOL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class AiToolNotFoundError(AiToolError):
    """Raised when an unapproved or unregistered tool ID is proposed."""

    def __init__(self, tool_id: str):
        super().__init__(
            f"AI tool '{tool_id}' is not registered in the ATLAS tool registry.",
            code="AI_TOOL_NOT_FOUND",
        )
        self.tool_id = tool_id


class AiToolDisabledError(AiToolError):
    """Raised when attempting to execute a tool that is administratively or user disabled."""

    def __init__(self, tool_id: str, reason: str = "Disabled by policy"):
        super().__init__(
            f"AI tool '{tool_id}' is currently disabled: {reason}",
            code="AI_TOOL_DISABLED",
        )
        self.tool_id = tool_id


class AiToolNotAuthorizedError(AiToolError):
    """Raised when the user lacks required permission scope for the tool."""

    def __init__(self, tool_id: str, required_scope: str):
        super().__init__(
            f"User is not authorized to execute tool '{tool_id}'. Required scope: {required_scope}",
            code="AI_TOOL_NOT_AUTHORIZED",
        )
        self.tool_id = tool_id
        self.required_scope = required_scope


class AiToolResourceAccessDeniedError(AiToolError):
    """Raised when attempting to access a specific resource (e.g. Portfolio/Risk run) without ownership or ACL."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            f"Access denied to {resource_type} '{resource_id}'. Resource not found or permission denied.",
            code="AI_TOOL_RESOURCE_ACCESS_DENIED",
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class AiToolProviderDisclosureDeniedError(AiToolError):
    """Raised when data licensing or privacy policy prohibits sending tool output to the model provider."""

    def __init__(self, tool_id: str, reason: str):
        super().__init__(
            f"Disclosure of tool '{tool_id}' data to LLM provider is restricted: {reason}",
            code="AI_TOOL_PROVIDER_DISCLOSURE_DENIED",
        )
        self.tool_id = tool_id


class AiToolArgumentInvalidError(AiToolError):
    """Raised when model-proposed arguments fail schema validation or contain disallowed parameters."""

    def __init__(self, tool_id: str, details: str):
        super().__init__(
            f"Invalid arguments for tool '{tool_id}': {details}",
            code="AI_TOOL_ARGUMENT_INVALID",
        )
        self.tool_id = tool_id
        self.details = details


class AiToolApprovalRequiredError(AiToolError):
    """Raised when an operation requires explicit human confirmation before execution."""

    def __init__(self, tool_id: str, approval_request_id: str):
        super().__init__(
            f"Tool '{tool_id}' requires explicit user confirmation. Approval request: {approval_request_id}",
            code="AI_TOOL_APPROVAL_REQUIRED",
        )
        self.tool_id = tool_id
        self.approval_request_id = approval_request_id


class AiToolApprovalDeniedError(AiToolError):
    """Raised when a user or administrator denies an approval request."""

    def __init__(self, approval_request_id: str, reason: Optional[str] = None):
        super().__init__(
            f"Approval request '{approval_request_id}' was denied: {reason or 'Denied by user'}",
            code="AI_TOOL_APPROVAL_DENIED",
        )
        self.approval_request_id = approval_request_id


class AiToolApprovalExpiredError(AiToolError):
    """Raised when attempting to execute with an approval token whose TTL has lapsed."""

    def __init__(self, approval_request_id: str):
        super().__init__(
            f"Approval request '{approval_request_id}' has expired. Re-approval required.",
            code="AI_TOOL_APPROVAL_EXPIRED",
        )
        self.approval_request_id = approval_request_id


class AiToolApprovalMismatchError(AiToolError):
    """Raised when execution arguments do not match the hash bound to the approval request."""

    def __init__(self, approval_request_id: str):
        super().__init__(
            f"Arguments for approval '{approval_request_id}' do not match approved signature. Argument swap rejected.",
            code="AI_TOOL_APPROVAL_MISMATCH",
        )
        self.approval_request_id = approval_request_id


class AiToolQuotaExceededError(AiToolError):
    """Raised when user or tenant execution quotas are exceeded."""

    def __init__(self, message: str = "Execution quota exceeded"):
        super().__init__(message, code="AI_TOOL_QUOTA_EXCEEDED")


class AiToolRateLimitedError(AiToolError):
    """Raised when per-minute tool execution velocity is breached."""

    def __init__(self, tool_id: str):
        super().__init__(
            f"Tool '{tool_id}' rate limit exceeded. Please retry later.",
            code="AI_TOOL_RATE_LIMITED",
        )
        self.tool_id = tool_id


class AiToolTimeoutError(AiToolError):
    """Raised when tool execution exceeds its allotted timeout."""

    def __init__(self, tool_id: str, timeout_seconds: float):
        super().__init__(
            f"Tool '{tool_id}' execution timed out after {timeout_seconds} seconds.",
            code="AI_TOOL_TIMEOUT",
        )
        self.tool_id = tool_id
        self.timeout_seconds = timeout_seconds


class AiToolCancelledError(AiToolError):
    """Raised when a tool execution is cancelled mid-flight."""

    def __init__(self, tool_id: str):
        super().__init__(
            f"Tool '{tool_id}' execution was cancelled.",
            code="AI_TOOL_CANCELLED",
        )
        self.tool_id = tool_id


class AiToolResultTooLargeError(AiToolError):
    """Raised when tool output payload exceeds the safe context boundary."""

    def __init__(self, tool_id: str, size_bytes: int, max_bytes: int):
        super().__init__(
            f"Tool '{tool_id}' result size ({size_bytes} bytes) exceeds limit of {max_bytes} bytes.",
            code="AI_TOOL_RESULT_TOO_LARGE",
        )
        self.tool_id = tool_id


class AiToolSequenceLimitExceededError(AiToolError):
    """Raised when model enters an infinite tool-calling loop or exceeds sequence limits."""

    def __init__(self, max_calls: int):
        super().__init__(
            f"Generation exceeded maximum tool call limit of {max_calls} per turn. Halting execution loop.",
            code="AI_TOOL_SEQUENCE_LIMIT_EXCEEDED",
        )
        self.max_calls = max_calls


class AiToolExecutionFailedError(AiToolError):
    """Raised when an internal error occurs during tool adapter execution."""

    def __init__(self, tool_id: str, reason: str):
        super().__init__(
            f"Tool '{tool_id}' failed during execution: {reason}",
            code="AI_TOOL_EXECUTION_FAILED",
        )
        self.tool_id = tool_id

