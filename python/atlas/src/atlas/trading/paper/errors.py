"""Paper Trading Engine Error Types (Stage 144)."""


class PaperTradingError(Exception):
    """Base exception for paper trading engine."""


class AccountNotFoundError(PaperTradingError):
    """Account does not exist or is inaccessible."""


class AccountInactiveError(PaperTradingError):
    """Account has been deactivated."""


class KillSwitchActiveError(PaperTradingError):
    """Kill switch is active; all new orders are blocked."""


class InsufficientBuyingPowerError(PaperTradingError):
    """Insufficient buying power for requested order."""


class OrderNotFoundError(PaperTradingError):
    """Order does not exist."""


class DuplicateOrderError(PaperTradingError):
    """Order with this client_order_id already exists."""


class RiskPolicyViolationError(PaperTradingError):
    """Order would violate risk policy."""


class MarketClosedError(PaperTradingError):
    """Market is closed; order rejected."""


class StaleMarketDataError(PaperTradingError):
    """Market data is stale; cannot fill order reliably."""


class LiveBrokerFirewallError(PaperTradingError):
    """Attempt to connect to live broker in paper mode blocked."""


class CrossTenantAccessError(PaperTradingError):
    """Cross-tenant access denied."""


class InvalidContractError(PaperTradingError):
    """Invalid or unrecognized option contract specification."""


class StrategyDeploymentError(PaperTradingError):
    """Strategy deployment failed or unauthorized."""
