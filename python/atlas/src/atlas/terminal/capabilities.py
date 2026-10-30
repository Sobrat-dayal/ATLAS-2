"""Declarative capability catalog and static CLI specs for Stage 122 Terminal Shell."""

from typing import Any, Dict, List, Optional

from .enums import TerminalType
from .models import ExecutionCapabilityDefinition, TerminalCapability

TERMINAL_CAPABILITIES_CATALOG: Dict[TerminalType, TerminalCapability] = {
    TerminalType.ATLAS_CLI: TerminalCapability(
        terminal_type=TerminalType.ATLAS_CLI,
        display_label="ATLAS CLI",
        description="Structured financial commands, system inspections, and platform workflows.",
        icon_name="Terminal",
        supports_multiline=False,
        supports_draft_persistence=True,
        supports_real_read_data=True,
        supports_arbitrary_execution=False,
        execution_status_notice="Command execution is not enabled in Stage 122. Sandboxed execution belongs to Stage 123.",
        stage_122_status="INPUT_COMPOSITION_AND_HELP_READY",
    ),
    TerminalType.PYTHON: TerminalCapability(
        terminal_type=TerminalType.PYTHON,
        display_label="Python",
        description="Quantitative analysis, financial data modeling, and mathematical scratchpad.",
        icon_name="Code2",
        supports_multiline=True,
        supports_draft_persistence=True,
        supports_real_read_data=False,
        supports_arbitrary_execution=False,
        execution_status_notice="Python execution is not enabled in Stage 122. Stage 123 provides approved sandboxed runtimes.",
        stage_122_status="MULTILINE_EDITOR_READY",
    ),
    TerminalType.SQL: TerminalCapability(
        terminal_type=TerminalType.SQL,
        display_label="SQL",
        description="Direct relational queries, time-series analysis, and analytical data inspection.",
        icon_name="Database",
        supports_multiline=True,
        supports_draft_persistence=True,
        supports_real_read_data=True,  # Schema metadata only
        supports_arbitrary_execution=False,
        execution_status_notice="Direct database SQL execution is not enabled in Stage 122. Stage 123 provides sandboxed query policies.",
        stage_122_status="MULTILINE_EDITOR_READY",
    ),
    TerminalType.LOGS: TerminalCapability(
        terminal_type=TerminalType.LOGS,
        display_label="Logs",
        description="Real-time application logs, operational diagnostics, and error reporting.",
        icon_name="ScrollText",
        supports_multiline=False,
        supports_draft_persistence=False,
        supports_real_read_data=True,  # Real authorized logs
        supports_arbitrary_execution=False,
        execution_status_notice="Read-only diagnostic feed. Execution not applicable.",
        stage_122_status="REAL_DIAGNOSTICS_READY",
    ),
    TerminalType.AGENTS: TerminalCapability(
        terminal_type=TerminalType.AGENTS,
        display_label="Agents",
        description="Operational status inspector for registered background and autonomous agents.",
        icon_name="Bot",
        supports_multiline=False,
        supports_draft_persistence=False,
        supports_real_read_data=True,  # Real registered agent status
        supports_arbitrary_execution=False,
        execution_status_notice="Read-only status monitor. Agent task execution is disabled in Stage 122.",
        stage_122_status="READ_ONLY_STATUS_MONITOR",
    ),
    TerminalType.MCP: TerminalCapability(
        terminal_type=TerminalType.MCP,
        display_label="MCP",
        description="Model Context Protocol server registry, connection states, and capability inspection.",
        icon_name="Network",
        supports_multiline=False,
        supports_draft_persistence=False,
        supports_real_read_data=True,  # Real configured MCP connections
        supports_arbitrary_execution=False,
        execution_status_notice="Read-only MCP inspector. Tool invocation is disabled in Stage 122.",
        stage_122_status="READ_ONLY_REGISTRY_INSPECTOR",
    ),
}

# ============================================================================
# Registered ATLAS CLI Commands (Static Schema & Help)
# ============================================================================

REGISTERED_CLI_COMMANDS: List[Dict[str, Any]] = [
    {
        "command": "help",
        "syntax": "help [command]",
        "summary": "Display documented command syntax and registered capability information.",
        "example": "help markets",
        "category": "Builtin",
    },
    {
        "command": "clear",
        "syntax": "clear",
        "summary": "Clear local terminal output scrollback buffer.",
        "example": "clear",
        "category": "Builtin",
    },
    {
        "command": "status",
        "syntax": "status",
        "summary": "Show system version, authenticated user ID, and active workspace desk.",
        "example": "status",
        "category": "Diagnostics",
    },
    {
        "command": "version",
        "syntax": "version",
        "summary": "Display ATLAS terminal shell build version and roadmap milestone (Stage 122).",
        "example": "version",
        "category": "Diagnostics",
    },
    {
        "command": "workspace",
        "syntax": "workspace [list|info]",
        "summary": "Inspect active Stage 120 workspace desk or list accessible desks.",
        "example": "workspace info",
        "category": "Navigation",
    },
    {
        "command": "context",
        "syntax": "context [show|channels]",
        "summary": "Display Stage 121 global financial context dimensions and active link channels.",
        "example": "context show",
        "category": "Navigation",
    },
    {
        "command": "markets",
        "syntax": "markets [equities|fx|crypto|bonds|funds|movers]",
        "summary": "Navigate to Markets module or inspect asset class overview (Future Execution in Stage 123).",
        "example": "markets fx",
        "category": "Financial",
    },
    {
        "command": "instrument",
        "syntax": "instrument inspect <symbol>",
        "summary": "Inspect canonical security metadata (Future Execution in Stage 123).",
        "example": "instrument inspect AAPL",
        "category": "Financial",
    },
    {
        "command": "portfolio",
        "syntax": "portfolio [list|summary <portfolio_id>]",
        "summary": "List investment portfolios or inspect allocation summaries (Future Execution in Stage 123).",
        "example": "portfolio list",
        "category": "Financial",
    },
    {
        "command": "risk",
        "syntax": "risk [var|factors|concentration]",
        "summary": "Query multi-factor risk models and portfolio factor sensitivity (Future Execution in Stage 123).",
        "example": "risk factors",
        "category": "Financial",
    },
]


def get_capability_profile(terminal_type: TerminalType) -> TerminalCapability:
    """Retrieve capability profile for a console type."""
    return TERMINAL_CAPABILITIES_CATALOG.get(
        terminal_type,
        TerminalCapability(
            terminal_type=terminal_type,
            display_label=terminal_type.value,
            description="Unknown terminal console type.",
            icon_name="Terminal",
            supports_multiline=False,
            supports_draft_persistence=False,
            supports_real_read_data=False,
            supports_arbitrary_execution=False,
            execution_status_notice="Execution unavailable.",
            stage_122_status="UNSUPPORTED",
        ),
    )


def get_cli_help(command_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve CLI command help definition(s)."""
    if not command_name:
        return REGISTERED_CLI_COMMANDS
    cmd_lower = command_name.lower().strip()
    return [c for c in REGISTERED_CLI_COMMANDS if c["command"].lower() == cmd_lower]


def get_stage_123_contracts() -> Dict[str, Any]:
    """Retrieve Stage 123 preparatory execution capability contracts."""
    return {
        "execution_milestone": "Stage 123 - Sandboxed Terminal Execution",
        "capabilities": [
            ExecutionCapabilityDefinition(
                capability_id="exec.python.sandbox.v1",
                terminal_type=TerminalType.PYTHON,
                supported=False,
                enabled=False,
                requires_sandbox=True,
                required_permissions=["terminal.python.execute"],
                resource_limits_reference="limits.python.standard_v1",
            ),
            ExecutionCapabilityDefinition(
                capability_id="exec.sql.sandbox.v1",
                terminal_type=TerminalType.SQL,
                supported=False,
                enabled=False,
                requires_sandbox=True,
                required_permissions=["terminal.sql.execute"],
                resource_limits_reference="limits.sql.readonly_v1",
            ),
            ExecutionCapabilityDefinition(
                capability_id="exec.cli.sandbox.v1",
                terminal_type=TerminalType.ATLAS_CLI,
                supported=False,
                enabled=False,
                requires_sandbox=True,
                required_permissions=["terminal.cli.execute"],
                resource_limits_reference="limits.cli.standard_v1",
            ),
        ],
        "notice": (
            "All command execution capabilities are strictly disabled in Stage 122. "
            "Stage 123 implements approved isolation sandboxes, resource quotas, and PTY processes."
        ),
    }
