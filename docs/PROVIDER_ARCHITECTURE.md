# Provider Architecture

This document describes the ATLAS Provider Architecture introduced in Stage 28.

## Overview
ATLAS uses a generic Provider abstraction to standardize external data integrations.
Providers are registered in the `ProviderRegistry` and instantiated lazily by the `ProviderResolver`.

## Market Data Provider Capabilities (Stage 33)
Stage 33 introduced explicit capability boundaries for Providers operating within `ProviderDomain.MARKET_DATA`.
Simply declaring support for the Market Data domain does NOT imply support for all operations.

- `MarketDataOperation`: Defines granular canonical operations (e.g., `quote`, `historical_bars`, `trades`, `order_book`, `snapshot`).
- `MarketDataProviderCapabilities`: A statically declared metadata object specifying exactly which canonical operations the adapter supports.
- **Typed Protocols**: Adapters implement strongly typed protocols (e.g., `QuoteMarketDataProvider`, `HistoricalBarsMarketDataProvider`) instead of relying on a generic `execute(operation, payload)` dictionary-based interface.

## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.

## Valkey
Stage 38 introduces no Provider state or caching in Valkey.
