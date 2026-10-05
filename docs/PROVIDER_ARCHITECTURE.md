# Provider Architecture

This document describes the ATLAS Provider Architecture introduced in Stage 28.

## Overview
ATLAS uses a generic Provider abstraction to standardize external data integrations.
Providers are registered in the `ProviderRegistry` and instantiated lazily by the `ProviderResolver`.

## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.
