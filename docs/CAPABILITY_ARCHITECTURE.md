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

