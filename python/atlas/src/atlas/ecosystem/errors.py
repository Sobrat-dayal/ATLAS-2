"""
Typed exceptions for the ATLAS Stage 149 Ecosystem.
"""

from __future__ import annotations


class EcosystemError(Exception):
    """Base class for all ecosystem exceptions."""
    def __init__(self, message: str, code: str = "ECOSYSTEM_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


# --- MCP Exceptions ---
class MCPServerNotFoundError(EcosystemError):
    def __init__(self, message: str = "MCP server not found") -> None:
        super().__init__(message, code="MCP_SERVER_NOT_FOUND")


class MCPConnectionError(EcosystemError):
    def __init__(self, message: str = "MCP connection failed") -> None:
        super().__init__(message, code="MCP_CONNECTION_ERROR")


class MCPSSRFSecurityError(EcosystemError):
    def __init__(self, message: str = "MCP endpoint blocked: private/loopback/cloud metadata SSRF violation") -> None:
        super().__init__(message, code="MCP_SSRF_SECURITY_VIOLATION")


# --- Plugin Exceptions ---
class PluginNotFoundError(EcosystemError):
    def __init__(self, message: str = "Plugin not found") -> None:
        super().__init__(message, code="PLUGIN_NOT_FOUND")


class PluginValidationError(EcosystemError):
    def __init__(self, message: str = "Plugin manifest or dependency validation failed") -> None:
        super().__init__(message, code="PLUGIN_VALIDATION_ERROR")


class PluginRevokedError(EcosystemError):
    def __init__(self, message: str = "Plugin has been revoked and cannot be executed") -> None:
        super().__init__(message, code="PLUGIN_REVOKED")


# --- Package Exceptions ---
class PackageNotFoundError(EcosystemError):
    def __init__(self, message: str = "Agent package not found") -> None:
        super().__init__(message, code="PACKAGE_NOT_FOUND")


class PackageValidationError(EcosystemError):
    def __init__(self, message: str = "Package validation failed") -> None:
        super().__init__(message, code="PACKAGE_VALIDATION_ERROR")


class PackageIntegrityError(EcosystemError):
    def __init__(self, message: str = "Package integrity verification failed: checksum mismatch or corrupted archive") -> None:
        super().__init__(message, code="PACKAGE_INTEGRITY_ERROR")


class PackageSecurityError(EcosystemError):
    def __init__(self, message: str = "Package security check failed: zip slip, secret leakage or malicious script") -> None:
        super().__init__(message, code="PACKAGE_SECURITY_VIOLATION")


# --- Custom Tool Exceptions ---
class CustomToolNotFoundError(EcosystemError):
    def __init__(self, message: str = "Custom tool not found") -> None:
        super().__init__(message, code="CUSTOM_TOOL_NOT_FOUND")


class CustomToolValidationError(EcosystemError):
    def __init__(self, message: str = "Custom tool schema or contract invalid") -> None:
        super().__init__(message, code="CUSTOM_TOOL_VALIDATION_ERROR")


class CustomToolExecutionError(EcosystemError):
    def __init__(self, message: str = "Custom tool execution failed") -> None:
        super().__init__(message, code="CUSTOM_TOOL_EXECUTION_ERROR")


# --- Developer & API Exceptions ---
class DeveloperAppNotFoundError(EcosystemError):
    def __init__(self, message: str = "Developer application not found") -> None:
        super().__init__(message, code="DEVELOPER_APP_NOT_FOUND")


class DeveloperCredentialRevokedError(EcosystemError):
    def __init__(self, message: str = "Developer API credential has been revoked") -> None:
        super().__init__(message, code="DEVELOPER_CREDENTIAL_REVOKED")


class DeveloperRateLimitExceededError(EcosystemError):
    def __init__(self, message: str = "Developer API rate limit exceeded") -> None:
        super().__init__(message, code="DEVELOPER_RATE_LIMIT_EXCEEDED")


# --- Governance & Security Exceptions ---
class PermissionDeniedEcosystemError(EcosystemError):
    def __init__(self, message: str = "Permission denied: caller lacks required ecosystem scope") -> None:
        super().__init__(message, code="ECOSYSTEM_PERMISSION_DENIED")


class ResourceQuotaExceededError(EcosystemError):
    def __init__(self, message: str = "Ecosystem resource quota exceeded") -> None:
        super().__init__(message, code="ECOSYSTEM_QUOTA_EXCEEDED")


class FinancialSafetyViolationError(EcosystemError):
    def __init__(self, message: str = "Ecosystem extensions are prohibited from executing live financial market orders") -> None:
        super().__init__(message, code="FINANCIAL_SAFETY_VIOLATION")

