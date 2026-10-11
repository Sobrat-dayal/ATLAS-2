# ATLAS Repository Architecture

This document describes the structure of the ATLAS monorepo and its dependency rules.

## Purpose
ATLAS uses a monorepo structure to centrally manage the web frontend, Python backend, shared libraries, data pipelines, AI workflows, and infrastructure. This ensures that a single source of truth governs the entire platform, while avoiding the overhead of multi-repo microservices for a solo developer. 

## Major Directories

- `apps/web`: The primary Next.js/React web frontend application.
  - `apps/web/src/hooks/application-context`: Contains the Global Application Context provider and logic.
  - `apps/web/src/hooks/entity`: Contains the legacy compatibility adapter hook.
  - `apps/web/src/lib/commands`: Stage 46 registry, Stage 47 detector, and Stage 48 natural-language interpreter client.
  - `apps/web/src/components/command-palette`: Command Palette UI with local matching, structured preview, and natural-language interpretation.
- `apps/api`: The structural home for the FastAPI backend application entry point and HTTP infrastructure (Stage 11).
  - `apps/api/src/atlas_api/routers/commands.py`: Endpoints for `POST /api/v1/commands/parse` (Stage 47) and `POST /api/v1/commands/interpret` (Stage 48).
- `packages/`: Shared frontend packages (`ui`, `config`, `types`, `schemas`).
- `python/atlas/`: The core Python modular monolith, split into domain subpackages.
  - `python/atlas/src/atlas/entities`: Universal entity domain (Stage 16).
  - `python/atlas/src/atlas/commands`: ATLAS Command Language v1 lexer, parser, binder, resolver, and models (Stage 47).
  - `python/atlas/src/atlas/commands/natural_language`: ATLAS Natural-Language Command Interpreter v1, prompt builder, compiler, and bounded model clients (Stage 48).
  - `python/atlas/src/atlas/market_data`: Canonical Market Data models and protocols (Stage 33).
  - `python/atlas/src/atlas/infrastructure/clickhouse`: Backend ClickHouse package.
  - `python/atlas/src/atlas/infrastructure/valkey`: Backend Valkey package.
- `workers/`: Placeholder for future background workers (e.g., market-worker, ai-worker).
- `agents/`: Built-in agent manifests, templates, and downloadable agent packages.
- `workflows/`: Portable visual-workflow definitions and templates.
- `mcp/`: Future Model Context Protocol (MCP) servers and config templates.
- `notebooks/`: Quantitative experiments and research prototypes.
- `infrastructure/`: Local development, Docker, and deployment configurations.
  - `infrastructure/clickhouse`: Local ClickHouse configuration.
- `scripts/`: Repository-level automation utilities.
- `tests/`: Cross-domain Python unit, integration, and e2e tests.
- `docs/`: Product specification and repository architecture documentation.

## Dependency Rules

### Monorepo Dependency Direction
```
apps
  ↓
domain/application packages
  ↓
atlas_core
```

### Python Dependency Direction
```
atlas_core
      ↑
domain packages
      ↑
application/API layer
```
Domain packages may depend on `atlas_core`. `atlas_core` must not depend on high-level domains (e.g., `atlas_core` → `atlas_trading` is prohibited).

### Cross-Domain Dependencies
Avoid direct tangled imports (e.g., `atlas_news` → `atlas_portfolio` → `atlas_geo` → `atlas_news`). Use shared contracts, application services, or capability interfaces instead.

### Agent Dependency Rule
Agents must not bypass ATLAS architecture to directly access raw databases. 
```
Agent
   ↓
Capability / Tool
   ↓
ATLAS Domain
   ↓
Provider/Data
```

### Workflow Dependency Rule
Future workflows should orchestrate agents, tools, capabilities, and approved code nodes. They should not duplicate domain business logic.


## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.

## Natural-Language Command Interpretation Package (Stage 48)

Stage 48 introduces the `atlas.commands.natural_language` package under `python/atlas/src/atlas/commands/natural_language`:

```text
python/atlas/src/atlas/commands/natural_language/
├── __init__.py           # Package exports & public API
├── enums.py              # NaturalLanguageCommandIntent, UnsupportedActionReason, InterpretationStatus
├── errors.py             # InterpreterError hierarchy (Unavailable, InvalidOutput, Timeout)
├── settings.py           # NaturalLanguageCommandSettings (Pydantic settings)
├── models.py             # Strict model output (extra="forbid") & interpretation response models
├── prompt.py             # NaturalLanguageCommandPromptBuilder (PROMPT_VERSION = 1)
├── model_client.py       # CommandInterpretationModelClient interface, OpenAICompatible & Mock client
├── compiler.py           # NaturalLanguageIntentCompiler (escaped Stage 47 syntax generator)
└── interpreter.py        # NaturalLanguageCommandInterpreter (single-turn pipeline)
```

## Persistent Notifications Architecture (Stage 49)

Stage 49 establishes the persistent notification infrastructure:

### Backend Domain Package
```text
python/atlas/src/atlas/notifications/
├── __init__.py           # Package exports & public API
├── enums.py              # NotificationCategory, Severity, ActionKind, ListFilter
├── errors.py             # NotificationError hierarchy (NotFound, Archived, DedupeConflict, ActionError, CursorError)
├── models.py             # NotificationModel (SQLAlchemy model with indexes and check constraints)
├── repository.py         # NotificationRepository (keyset pagination, cursor encode/decode, atomic mutations)
├── schemas.py            # CreateNotification, NotificationResponse, List/Count responses, route allowlist
└── service.py            # NotificationService (canonical creation, dedupe idempotency, action validation)
```

### API Routing Layer
- `apps/api/src/atlas_api/routers/notifications.py`: Public FastAPI endpoints for listing, unread count, read, unread, read-all, and archive.
- `apps/api/migrations/versions/7e8f9012abcd_stage49_notifications.py`: Alembic migration for the `notifications` table, indexes, and constraints.

### Frontend Components & State
- `apps/web/src/lib/notifications/types.ts`: TypeScript interfaces for notifications.
- `apps/web/src/lib/notifications/constants.ts`: Allowed internal routes set and relative time formatter.
- `apps/web/src/lib/notifications/client.ts`: Typed fetch API client for `/api/v1/notifications/*`.
- `apps/web/src/lib/notifications/useNotifications.tsx`: React Context, Hook, 30s unread count polling, and optimistic mutations.
- `apps/web/src/components/notifications/NotificationTrigger.tsx`: TopBar bell trigger with unread badge (hidden at 0, 99+ at >= 100).
- `apps/web/src/components/notifications/NotificationCenter.tsx`: Accessible slide-over/popover panel with tabs, mark all read, and keyset pagination.
- `apps/web/src/components/notifications/NotificationRow.tsx`: Plain text notification row with severity badge, relative time, action navigation, and row controls.

## Bottom Taskbar Architecture (Stage 50)

Stage 50 establishes the persistent bottom taskbar and expandable bottom workspace panel:

### Frontend Components & State
```text
apps/web/src/
├── lib/bottom-taskbar/
│   ├── types.ts              # BottomPanelId, BottomPanelDefinition, Controller, State
│   ├── registry.ts           # PANEL_DEFINITIONS static registry & runtime validator
│   ├── layout.ts             # Height clamping helpers (min 160, max 45% viewport)
│   └── index.ts              # Package barrel
├── hooks/bottom-taskbar/
│   ├── useBottomPanel.ts     # Hook providing typed BottomPanelController
│   └── index.ts              # Package barrel
└── components/bottom-taskbar/
    ├── BottomTaskbar.tsx             # Persistent bottom bar with primary & trailing items
    ├── BottomTaskbarItem.tsx         # Accessible taskbar button with active state & tooltips
    ├── BottomTaskbarOverflowMenu.tsx # Responsive overflow menu on narrow viewports
    ├── BottomPanelHost.tsx           # Workspace panel container with error isolation
    ├── BottomPanelHeader.tsx         # Panel title, description, and close controls
    ├── BottomPanelResizeHandle.tsx   # Pointer-capturing and keyboard resize handle
    ├── ReservedPanelState.tsx        # Factual, grounded placeholder component
    └── panels/                       # Canonical 7 panel shell implementations
        ├── TasksPanel.tsx
        ├── AgentsPanel.tsx
        ├── JobsPanel.tsx
        ├── AlertsPanel.tsx
        ├── DownloadsPanel.tsx
        ├── SystemHealthPanel.tsx
        ├── TerminalPanel.tsx
        └── index.ts
```

