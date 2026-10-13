"""Authoritative allowlists and configuration constants for Approval Requests (Stage 54)."""

import datetime

# Strict allowlist of trusted originating backend producers
TRUSTED_PRODUCERS: frozenset[str] = frozenset(
    {
        "system.ops",
        "trading.risk",
        "workflow.engine",
        "agent.supervisor",
        "compliance.governance",
        "test.producer",
    }
)

# Strict allowlist of permitted action categories
ALLOWED_ACTION_KINDS: frozenset[str] = frozenset(
    {
        "resource.modify",
        "order.confirm",
        "workflow.step_approve",
        "agent.tool_permission",
        "config.update",
        "test.action",
    }
)

# Lifetime bounds
DEFAULT_APPROVAL_LIFETIME = datetime.timedelta(hours=24)
MAX_APPROVAL_LIFETIME = datetime.timedelta(days=7)
