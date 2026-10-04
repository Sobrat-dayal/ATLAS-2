# ATLAS Product Principles

This document defines the core design, architecture, and implementation principles that all subsequent stages of ATLAS must adhere to.

## Design Principles

ATLAS is designed for serious financial workflows. It must be:
- Professional, information-dense, fast, and keyboard-friendly.
- Desktop-first, modular, customizable, and context-aware.
- AI-native and data-driven.
- Transparent about its sources.

**Avoid at all costs:**
- The "purple gradient" generic AI aesthetic.
- Excessive rounded-pill controls, huge empty hero sections, and unnecessary animations.
- Fake metrics, fake reviews, or stock AI imagery.
- Decorative clutter and excessive whitespace.
- Mobile-first simplification of complex desktop workflows.
- Visually inconsistent modules.
- Duplicated implementations of core capabilities.

## Architecture Principles

### 1. Modular Monolith First
ATLAS should begin as a clean modular monolith on the backend (Python). Logical module boundaries must exist, but microservices should only be extracted later when scale requires it (e.g., market-data service, AI/agent execution, geospatial service). 

### 2. Python-First Principle
Python is the primary language for backend, business logic, AI, analytics, data ingestion, quant/financial calculations, workflows, and risk.
Web-native visualization and frontend UI should utilize web-native technologies (TypeScript, React, Next.js). Do not force Python into browser UI tasks where TypeScript is superior.

### 3. Shared Capability Principle
A core capability (e.g., `get_company()`) must be reusable by the normal UI, ATLAS AI, Agents, Workflow Builder, Terminal, MCP, and external APIs. Do not implement the same business functionality separately in multiple places.

### 4. Safety and High-Risk Actions
Actions with significant external consequences (live trading, external comms, deleting data, prod deployments) must have strict controls.
Flow: `Permissions -> Policy Checks -> Risk Checks -> Confirmation/Approval -> Execution -> Audit Log`.
Agent autonomy does not imply unrestricted authority.

### 5. Source and Data Transparency
ATLAS must preserve and display provider, source, timestamp, retrieval time, data freshness, confidence scores, and licensing metadata. AI-generated claims must point back to supporting sources.

## Future Core Technologies
*(Note: These are identified for future stages. Do not install them in Stage 1)*

**Frontend:** Next.js, React, TypeScript, Tailwind, TanStack, Monaco Editor.
**Backend:** Python, FastAPI, Pydantic, SQLAlchemy.
**Databases/Analytics:** PostgreSQL/Supabase, ClickHouse, DuckDB, Polars.
**Cache/Vectors:** Redis/Valkey, pgvector, Qdrant.
**Geospatial:** PostGIS, H3, MapLibre, CesiumJS, deck.gl.
**Charts:** TradingView Lightweight Charts, Apache ECharts.
**Financial/Quant:** OpenBB, TA-Lib, QuantLib, Qlib, PyPortfolioOpt, Riskfolio-Lib, NautilusTrader, CCXT, QuickFIX.
**Infrastructure:** Docker, Object Storage, Vercel (Frontend), Persistent Compute (Backend).
