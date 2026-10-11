# ATLAS

**AI-native financial intelligence, markets, research, trading, geospatial intelligence, portfolio analytics, risk, data, and autonomous-agent operating system.**

**Current implementation stage:** Stage 2 — Monorepo Foundation

**Warning:** Production implementation has not started. This repository currently contains the structural foundation and product specification. No frontend pages, backend APIs, databases, or production functionalities are active yet.

## About
ATLAS is designed as a professional, desktop-first financial operating environment combining concepts from institutional terminals, advanced geospatial platforms, and autonomous AI-agent workforces.

## Repository Structure
ATLAS uses a monorepo architecture:
- `apps/web`: Frontend application (Stage 3+)
- `apps/api`: Backend application API (Stage 11+)
- `python/atlas/`: Python domain packages (Modular Monolith)
- `packages/`: Shared frontend packages
- `agents/`, `workflows/`, `mcp/`: Configuration and definition assets
- `infrastructure/`: Infrastructure configurations
- `docs/`: Full documentation

## Setup
- **Python**: Use `uv` with python 3.12 (`python/atlas/pyproject.toml`, `apps/api/pyproject.toml`)
- **Node**: Use `pnpm` workspaces (`pnpm-workspace.yaml`, `package.json`)

## Database Architecture
- **PostgreSQL**: Authoritative source of truth for entities, relationships, configuration, and capabilities.
- **ClickHouse**: High-volume, immutable analytical data (Market Data, Event Streams).
- **Valkey**: Ephemeral low-latency state, caching, and real-time coordination.

## Run
To run the full stack locally:

```bash
# Terminal A (Frontend):
pnpm run dev:web

# Terminal B (Backend):
cd apps/api
uv run uvicorn atlas_api.main:app --reload

# Terminal C (Infrastructure):
pnpm clickhouse-up
pnpm valkey-up
```
The full product specification is located in the `docs/` directory. Check the [Documentation Index](docs/README.md) for more details.

## Global Search (Stage 45)
- Open via center search bar in AppShell TopBar.
- Backed by PostgreSQL indexed search (`entities`, `entity_aliases`, `entity_identifiers`).
- Searches canonical entities with deterministic exact, prefix, and trigram fuzzy matching.
- Selecting an entity updates global selected entity context without auto-navigating.
- Run tests: `pytest apps/api/tests/search/test_global_search.py`

## Command Palette (Stage 46)
- **Shortcut**: `Cmd + K` (macOS) / `Ctrl + K` (Windows/Linux) or click the shortcut badge in the TopBar.
- **Commands**: Discover and execute explicitly registered navigation commands across all 20 modules, global settings, section settings, search entity handoff, and entity selection clearance.
- **Execution**: 100% frontend-local deterministic filtering with 0 backend queries, 0 Provider calls, and 0 LLM calls.
- **Adding a Command**: Register in `apps/web/src/lib/commands/registry.ts` with a unique ID, human-readable label, category, optional keywords/aliases, and typed `execute` handler.
- **Run tests**: `npx.cmd tsx --test apps/web/tests/commands.test.ts`

## Command Parsing (Stage 47)
- **Syntax**: ATLAS Command Language v1 supports structured slash syntax and Bloomberg-style shorthand:
  - `/markets` — Module navigation
  - `/charts NVDA` or `/charts open NVDA` — Select NVDA security and navigate to Charts
  - `NVDA CHART` — Shorthand to select NVDA and navigate to Charts
  - `NVDA NEWS` — Shorthand to select NVDA and navigate to News
  - `MAP TSMC` — Shorthand to select TSMC entity and navigate to Maps
  - `OPTIONS NVDA` — Shorthand to select NVDA and navigate to Options
  - `NVDA FA` — Reserved recognized shorthand (unavailable in current stage)
  - `PORT RISK` — Reserved recognized shorthand (unavailable in current stage)
- **Deterministic Pipeline**: Pure Lexer -> Parser -> AST -> Binder -> Stage 22 Entity Resolver -> Authorization -> Command Preview.
- **Strict Boundaries**: 0 LLM calls, 0 vector search, 0 embeddings, 0 shell execution, 0 DB writes.
- **Testing**:
  - Backend: `pytest apps/api/tests/commands/test_command_parsing.py`
  - Frontend: `npx.cmd tsx apps/web/tests/commands-parser.test.ts`

## Natural-Language Command Interpretation (Stage 48)
- **Natural Phrasing**: Single-turn interpretation translating human instructions into deterministic Stage 47 syntax:
  - `"take me to markets"` -> `/markets`
  - `"show me NVDA's chart"` -> `/charts "NVDA"`
  - `"open NVIDIA Corporation in companies"` -> `/companies "NVIDIA Corporation"`
  - `"open settings"` -> `/settings`
- **Safety Boundary**: The model may interpret intent, but it may **never** directly execute anything. 0 tools provided, 0 direct command IDs from model, 0 autonomous agents, no multi-step planner, no conversation memory, no DB writes.
- **Developer Configuration**:
  - `ATLAS_NL_COMMAND_ENABLED=true`: Enable natural-language interpretation.
  - `ATLAS_NL_COMMAND_MOCK_MODE=true`: Enable deterministic offline mock model client for tests & local dev.
  - `ATLAS_NL_COMMAND_MODEL_BASE_URL`: Server-side endpoint URL (default `https://api.openai.com/v1`).
  - `ATLAS_NL_COMMAND_MODEL_NAME`: Configured model identifier (default `gpt-4o-mini`).
  - `ATLAS_NL_COMMAND_MODEL_API_KEY`: Server-side model credential (never exposed to frontend).
  - `ATLAS_NL_COMMAND_TIMEOUT_SECONDS=10.0`: Model request timeout.
- **Testing**:
  - Backend: `pytest apps/api/tests/commands/test_natural_language_interpretation.py`
  - Frontend: `npx.cmd tsx --test apps/web/tests/commands-interpreter.test.ts`

## The 20 Modules
1. Home
2. Markets
3. Charts
4. Watchlists
5. Screeners
6. Companies
7. Economics
8. News
9. Research
10. Maps
11. Intelligence
12. Options
13. Trading
14. Portfolios
15. Risk
16. AI Assistant
17. Data
18. Saved
19. Workspaces
20. Agents


