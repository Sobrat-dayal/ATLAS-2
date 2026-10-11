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
