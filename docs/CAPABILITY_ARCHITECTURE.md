# Capability Architecture

This document describes the ATLAS Capability Architecture introduced in Stage 27.

## Overview
Capabilities encapsulate execution of Domain Services securely.
They enforce arguments validation, capability registration, and routing via the `CapabilityGateway`.

## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.

## ClickHouse
Stage 37 introduces no direct ClickHouse Capability Gateway actions.

## Valkey
Stage 38 introduces no direct Valkey Capability Gateway actions.

## Command Parsing (Stage 47)
Stage 47 command parsing is system infrastructure rather than a user business Capability.
- It does **not** register a generic `commands.execute` capability.
- It is **not** exposed as an AI tool, Agent tool, or MCP tool.

## Natural-Language Command Interpretation (Stage 48)
Stage 48 natural-language command interpretation is an interpretation aid, NOT an executable Capability:
- It does **not** register a generic executable Capability.
- It cannot invoke Capabilities, Agents, or Workflows.
- The interpretation model receives **0 tools** (zero Capability tools, zero Provider tools, zero database tools).
- Execution remains strictly bound to deterministic Stage 46 local commands and Stage 47 validated commands upon explicit user confirmation.

## Persistent Notifications (Stage 49)
Stage 49 notification operations and center interactions are application APIs rather than general business Capabilities:
- Notification user mutations (`mark_read`, `mark_unread`, `mark_all_read`, `archive`) are personal application state interactions, not business capabilities.
- Notifications cannot execute Capabilities, trade operations, or approval actions.
- Future backend ATLAS subsystems and producers call `NotificationService.create_notification(...)` directly within their domain workflows or transactions, rather than routing through the public API.

## Bottom Taskbar (Stage 50)
Stage 50 taskbar and workspace panel UI interactions are local application-shell operations, not backend Capabilities:
- Taskbar panel toggling, resizing, and switching are local presentation state transitions.
- Future panels (Tasks, Agents, Jobs) will connect to authoritative domain capabilities in their respective roadmap stages.



