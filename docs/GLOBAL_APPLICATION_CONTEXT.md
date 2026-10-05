# Global Application Context

## Purpose
The **Global Application Context** represents the shared semantic working context for ATLAS. It acts as the single source of truth for high-level parameters that describe "what the user is currently looking at or analyzing." 

It is **NOT** a dump for all global frontend state. Authentication, layout geometry, settings, and UI themes are handled by independent infrastructure providers. 

## Context Architecture
```text
ATLAS Application Context
        │
        ├── Selected Entity (Functional)
        ├── Time Range (Functional)
        ├── Portfolio Ref (Foundation Only)
        ├── Workspace Ref (Foundation Only)
        ├── Map Context (Foundation Only)
        ├── Filters (Foundation Only)
        └── Selected Object (Foundation Only)
```

## Data Ownership
- **Context stores:** Identifiers, parameters, and structural references (e.g., `entityId`, `mapCenter`).
- **Query/Data Layers store:** API responses, domain models, and live market data.

*Context dictates WHAT to query, but does not cache the payload itself beyond simple display metadata.*

## Selected Entity Migration (Stage 25 -> 26)
Stage 25's `selectedEntityId` was gracefully migrated into the Global Application Context storage.
```text
Stage 25
atlas.selectedEntity.v1
        ↓ migrate
Stage 26
atlas.applicationContext.v1
```
`selectedEntityId` remains the canonical Entity context pointer. The legacy `useSelectedEntity()` hook is preserved as a focused slice over the new root context, ensuring zero breakage for Stage 25 components.

## Time Range
The Time Range slice represents the global analysis period.
- **Model:** Presets (e.g., 1d, 1m, 1y) and Custom (start/end ISO timestamps).
- **Default:** `1m`
- **Validation:** Custom ranges must ensure `start <= end`.
- **Module Interpretation:** Modules may inherit the global time range by default, but remain free to introduce local time overrides when specific UX demands it.

## Foundations
Several fields are prepared for future stages but lack backing domain infrastructure today:
- **Portfolio Context:** Foundation only until Stage 110. No fake Portfolio UI is exposed.
- **Workspace Context:** Foundation only until Stage 120.
- **Map Context:** State contract only. No map engine (MapLibre/Cesium) is integrated yet.
- **Filters:** Minimal typed structure (`entityTypes`, `assetClasses`, `regions`, `tags`).
- **Selected Object:** Distinct from Universal Entity to support future non-entity domains (like an individual order or a saved chart layout).

## Session Persistence
Context is stored in `sessionStorage` under `atlas.applicationContext.v1`.
- **Tab Isolation:** Each browser tab maintains its own independent context, allowing parallel analysis of different entities.
- **Hydration:** State is restored immediately upon client-side mount.
- **Resilience:** Partial corruption strips only the invalid slice. Total corruption resets to factory defaults. Unknown storage versions fail safely.

## Future Capability Snapshot
The context structure prepares for Stage 27 (Capability / Service Layer).
```text
Global Application Context
        │
        ▼
Context Snapshot
        │
        ▼
Stage 27 Capability Layer
```
AI Agents, the Terminal, and autonomous workflows will receive a serialized, read-only snapshot of this context to inform their autonomous queries and commands.
