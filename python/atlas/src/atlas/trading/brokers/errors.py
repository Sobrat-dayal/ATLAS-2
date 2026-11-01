"""Broker Abstraction Error Types — Stage 145."""


class BrokerAbstractionError(Exception):
    """Base exception for broker abstraction layer."""


class BrokerNotFoundError(BrokerAbstractionError):
    """Broker provider not registered."""


class ConnectionNotFoundError(BrokerAbstractionError):
    """No active connection for this broker."""


class UnsupportedCapabilityError(BrokerAbstractionError):
    """Broker does not support the requested capability."""


class CredentialEncryptionError(BrokerAbstractionError):
    """Credential encryption or decryption failed."""


class SandboxFirewallError(BrokerAbstractionError):
    """Attempt to connect to a production broker host blocked."""


class SSRFProtectionError(BrokerAbstractionError):
    """SSRF protection triggered on host validation."""


class RateLimitError(BrokerAbstractionError):
    """Broker rate limit exceeded."""


class BrokerAuthError(BrokerAbstractionError):
    """Broker authentication failed."""


class ReconciliationError(BrokerAbstractionError):
    """Order or position reconciliation mismatch."""


class CrossTenantConnectionError(BrokerAbstractionError):
    """Cross-tenant connection access denied."""


class InvalidCredentialError(BrokerAbstractionError):
    """Credential is missing or malformed."""


class LiveBrokerBlockedError(BrokerAbstractionError):
    """Live broker endpoint is blocked in sandbox mode."""
