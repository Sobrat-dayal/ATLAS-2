# OpenBB Integration

This document describes the OpenBB integration implemented during Stage 29.

## OpenBB Role
OpenBB is an ATLAS provider-framework integration.
It is not ATLAS's universal domain model.
It is not ATLAS's Provenance system.
It is not ATLAS's UI.

## Architecture
```text
ATLAS Capability
       │
       ▼
Domain Service
       │
       ▼
ATLAS Provider Interface
       │
       ▼
OpenBB Provider Adapter
       │
       ▼
OpenBB Runtime
       │
       ▼
OpenBB Provider Extension
       │
       ▼
External Source
```

## In-Process Decision
Stage 29 uses the **OpenBB Python runtime** running in-process inside the ATLAS Python backend.
We do not use an OpenBB REST API sidecar. The sidecar creates unnecessary network hops, duplicated API infrastructure, duplicated authentication boundaries, and more deployment complexity. In-process integration provides the most direct and efficient data access while keeping architectural boundaries clean.

## Dependency Strategy
- **Package Installed**: `openbb-core`
- **Version Constraint**: `>=2.0.0` (as resolved in lockfile)
- **Resolved Version**: `2.0.1`
- **Python Compatibility**: Python 3.12+
- **Lockfile**: Managed and pinned via `uv`

## OpenBB Build Process
OpenBB V4/Core V2 does not require explicit static interface generation steps like earlier major versions unless extensions are added. The `openbb-core` runtime generates its command maps dynamically. If a build step becomes required in the future, it should occur during Docker build or development setup, not on every request.

## OpenBB Runtime
The `OpenBBRuntime` provides an isolated facade over the raw OpenBB SDK. 
Responsibilities:
- Detect OpenBB runtime version and validate major version compatibility (Core V2).
- Inspect local coverage (installed providers and commands).
- Encapsulate imports and errors.

## OpenBB Provider Adapter
- **Provider Key**: `openbb`
- **Adapter Version**: `1`
- **Declared Domains**: `market_data`, `fundamentals`, `economics`, `news`
OpenBB is registered as a single Framework Provider, representing the entrypoint to its ecosystem of underlying extensions.

## Sub-Provider Concept
OpenBB Provider extensions (e.g., Fred, FMP) are treated as internal OpenBB sources.
OpenBB Provider extensions != automatically registered ATLAS Providers.
We do not auto-promote OpenBB's internal providers into ATLAS Providers. This maintains deliberate control over credentials, licensing, and schema.

## Coverage Inspector
The `OpenBBCoverageInspector` dynamically inspects the OpenBB runtime's available extensions and commands using `obb.coverage`.
- It reads only local runtime metadata.
- It makes **no external data request**.
- Coverage is not Provider health; it merely reflects which Python extensions are locally installed.

## No Generic Executor
We do **not** support generic arbitrary string-based command execution like:
```python
OpenBBRuntime.execute("equity.price.historical", payload)
```
This is forbidden to prevent untrusted execution, ensure strict type safety, and enforce proper schema normalization.

## Result Boundary
```text
OpenBB structured result
        │
        ▼
OpenBB adapter normalization
        │
        ▼
ATLAS canonical model
```

## Metadata Preservation
Future OpenBB adapters must preserve the actual OpenBB provider identifier, warnings, and response metadata from the raw OpenBB envelope until canonical normalization is complete.

## Provenance Boundary
OpenBB = retrieval/integration framework
Underlying provider/source = potential provenance source
Stage 29 creates no automatic Provenance Source or Record for OpenBB.

## Credential Boundary
- **Stage 29**: OpenBB framework integration (no credentials).
- **Stage 30**: Provider configuration + credential management.

## Multi-User Safety
Future per-user OpenBB credentials must not be implemented through unsafe process-global mutation. We avoid setting credentials globally on `obb.user` because that leaks state across concurrent user requests.

## Health Boundary
OpenBB runtime available != provider healthy.
Stage 31 handles true Provider health monitoring.

## Fallback Boundary
OpenBB registered != OpenBB default.
OpenBB is not implicitly selected for all requests. Stage 32 handles routing.

## Canonical Data Boundary
Stage 33 (Market Data) introduced the canonical models and typed Provider protocols.
OpenBB now has a canonical ATLAS Market Data boundary available, but because no actual OpenBB data fetchers have been fully implemented yet, its `MarketDataProviderCapabilities.operations` remains empty, and it performs no Stage 33 data calls.

Future stages (Stage 34 for Fundamentals, Stage 35 for Economics, Stage 36 for News/Research) will handle mapping additional OpenBB responses into strict ATLAS models.
