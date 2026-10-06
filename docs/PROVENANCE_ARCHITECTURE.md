# Provenance Architecture

This document describes the ATLAS Provenance Architecture introduced in Stage 21.

## Overview
The Provenance system records the lineage of data items, linking them to sources and entities via `ProvenanceSource`, `ProvenanceRecord`, and `ProvenanceLink`.

## Market Data Origin vs Provenance (Stage 33)
Stage 33 introduces `MarketDataOrigin` attached to canonical Market Data responses.
- `MarketDataOrigin` is **lightweight runtime lineage metadata** representing the source, retrieval time, and timeliness of a specific API response.
- `Provenance` is the **persistent source/evidence lineage**.
- Stage 33 does NOT create database Provenance records during Market Data model construction. Future ingestion pipelines (e.g. Stage 39) will convert `MarketDataOrigin` into persisted `Provenance` records.

## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.
