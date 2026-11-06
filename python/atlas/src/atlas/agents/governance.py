"""Stage 148 Governance, Financial Safety, and Prompt-Injection Defense."""

from __future__ import annotations

import re
from typing import Any

from atlas.agents.errors import SecurityViolationError

# Patterns indicative of prompt injection attempts aimed at overriding system policies or extracting secrets
PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"override\s+(system|security|tenant)\s+policy", re.IGNORECASE),
    re.compile(r"reveal\s+(api\s+key|secret|credential|password)", re.IGNORECASE),
    re.compile(r"bypass\s+(approval|gate|permission)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+an\s+unrestricted\s+admin", re.IGNORECASE),
)


class AgentGovernance:
    """Provides centralized safety enforcement for multi-agent workflows."""

    @staticmethod
    def assert_no_live_trading(action_type: str, payload: dict[str, Any]) -> None:
        """Blocks any attempt to dispatch live real-money broker orders."""
        is_live = (
            payload.get("live_trading", False)
            or payload.get("live_money", False)
            or payload.get("execution_mode") == "LIVE"
            or "LIVE" in str(action_type).upper()
        )
        if is_live:
            raise SecurityViolationError(
                "Live money broker execution is strictly prohibited in ATLAS Stage 148 multi-agent runtime. "
                "All executions must operate in paper or sandbox mode."
            )

    @staticmethod
    def inspect_prompt_safety(text: str) -> None:
        """Scans retrieved documents and agent inputs for prompt injection attack signatures."""
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(text):
                raise SecurityViolationError(
                    f"Prompt injection pattern detected: '{pattern.pattern}'. "
                    "Untrusted inputs cannot modify agent execution boundaries."
                )

    @staticmethod
    def assert_budget_available(current_spend: float, budget_limit: float) -> None:
        """Enforces that an agent or task does not breach its assigned dollar budget limit."""
        if current_spend >= budget_limit:
            raise SecurityViolationError(
                f"Budget limit of ${budget_limit:.2f} reached (current spend: ${current_spend:.2f}). "
                "Additional model calls or tool invocations blocked."
            )
