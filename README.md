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
- **Python**: Use `uv` with python 3.12 (`python/atlas/pyproject.toml`)
- **Node**: Use `pnpm` workspaces (`pnpm-workspace.yaml`, `package.json`)

## Documentation
The full product specification is located in the `docs/` directory. Check the [Documentation Index](docs/README.md) for more details.

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
