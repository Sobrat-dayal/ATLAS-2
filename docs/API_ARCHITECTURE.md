# ATLAS API Backend Architecture

This document describes the architectural foundation for the FastAPI backend (Stage 11).

## FastAPI Application Architecture
The backend uses a standard modular FastAPI structure located in `apps/api/src/atlas_api`.
- **Application Factory**: `app.py` exposes `create_app()` to initialize the FastAPI app. This ensures testability and avoids global state side-effects.
- **Entry Point**: `main.py` is the entry point, creating the app instance for Uvicorn to serve (`uv run uvicorn atlas_api.main:app`).
- **Lifespan**: Modern `lifespan` context managers are used in `lifecycle.py` for startup/shutdown events, initializing resources like logging.
- **API Versioning**: All general routes are prefixed with `/api/v1` to ensure stable future expansion without breaking clients.
- **Router Structure**: Clean hierarchical router registration in `routers/__init__.py`. Currently houses system endpoints (`/health`, `/ready`, `/system/version`). Future domains will have independent routers (e.g., `/markets`, `/companies`).
- **Errors**: `AtlasError` serves as the base exception. `error_handling.py` normalizes all errors (including FastAPI/Pydantic errors) into a stable standard envelope format.
- **Request IDs**: `RequestIdMiddleware` injects/validates `X-Request-ID` to trace logs and responses securely.
- **Logging**: Configured in `logging.py`. Includes structured output with timestamps, request IDs, execution durations, and standard severity levels.
- **Configuration**: Strongly typed `pydantic-settings` manages environment config. Defaults prioritize local development (`ATLAS_ENV=development`, `ATLAS_DEBUG=true`).
- **Testing**: Organized in `tests/` using `pytest` and `httpx.AsyncClient` alongside application-factory instantiation for isolated unit/integration tests without a running server.

## Architectural Boundaries & Capabilities
- **Domain Logic**: Business rules must NOT reside in routers. Routers are strictly for HTTP concerns, parameter parsing, and serialization.
- **Capability Layer**: Future features (e.g., Agents, UI, Workflows) will route operations through a Shared Capability Layer that handles permissions and orchestrates access to Domain Packages.
- **Dependency Direction**:
  ```text
  Frontend -> API Router -> Application/Service Layer -> Repository Layer -> Persistence/Providers
  ```
  Example (Entities):
  ```text
  Entity Router -> EntityService -> EntityRepository -> PostgreSQL
  ```
- **Future Expansions**:
  - *Authentication*: Not yet implemented (Stage 13).
  - *WebSockets*: Not yet implemented. Will likely use `/api/v1/ws` (Stage 43).
  - *Database/Providers*: Deferred to later stages.
  - *Market Data*: Stage 33 introduces canonical models but no public Market Data REST endpoints yet.

*(Note: Stage 25/26 Global Application Context uses existing endpoints and introduces no new backend endpoints.)*


## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.

## ClickHouse
Stage 37 introduces no public ClickHouse API.

## Valkey
Stage 38 introduces no public Valkey caching or state API.

## Command Parsing API (Stage 47)
- **Endpoint**: `POST /api/v1/commands/parse`
- **Method**: `POST` (protects query payloads from appearing in URLs/logs)
- **Nature**: Deterministic, side-effect free, read-only
- **Auth**: Requires valid session token + `atlas.access` permission
- **Behavior**: Lexes, parses, binds, resolves entity targets via Stage 22, and checks module permissions.
- **Database/Storage**: 0 PostgreSQL writes, 0 Redis calls, 0 ClickHouse queries, 0 provider calls, 0 LLM calls. No command history stored.

## Natural-Language Command Interpretation API (Stage 48)
- **Endpoint**: `POST /api/v1/commands/interpret`
- **Method**: `POST` (protects natural-language queries from appearing in access URLs or logs)
- **Nature**: Single-turn, bounded, side-effect free, read-only
- **Auth**: Requires valid session token (Stage 13) + `atlas.access` permission (Stage 14)
- **Behavior**: Validates user text, invokes configured model once for structured intent classification, compiles allowed intent into Stage 47 syntax, reparses and binds via Stage 47, resolves entities via Stage 22, and returns structured preview.

## Persistent Notifications API (Stage 49)
Stage 49 introduces authenticated, user-scoped endpoints for the persistent Notification Center:
- **`GET /api/v1/notifications`**: Keyset-paginated notification listing (`filter=all|unread|archived`, `limit=1..100`, `cursor`). Ordered by `created_at DESC, notification_id DESC`.
- **`GET /api/v1/notifications/unread-count`**: Lightweight unread count endpoint for AppShell badge polling.
- **`POST /api/v1/notifications/{id}/read`**: Idempotently marks notification as read.
- **`POST /api/v1/notifications/{id}/unread`**: Marks notification as unread (rejects if archived).
- **`POST /api/v1/notifications/read-all`**: Marks all active unread notifications as read.
- **`POST /api/v1/notifications/{id}/archive`**: Archives notification (simultaneously marks read if unread).
- **Security & Privacy**:
  - Requires authenticated session + `atlas.access`.
  - Recipient derived exclusively from authentication (`principal.user_id`).
  - No public create endpoint, no hard delete endpoint.
  - Cross-user mutations return HTTP 404 (no existence leakage).
  - All responses set `Cache-Control: private, no-store`.
  - Raw notification titles and messages are excluded from INFO logging.

- **Execution**: The endpoint **never** executes commands. Execution remains an explicit user action via the Stage 46 frontend executor.
- **Database/Storage**: 0 PostgreSQL writes, 0 Redis calls, 0 ClickHouse queries, 0 market data provider calls, 0 chat/interpretation history saved. Raw natural-language input is never logged at INFO.

## Stage 50 — Bottom Taskbar Shell

- **No New API Endpoints**: Stage 50 builds the frontend persistent taskbar and workspace panel shell. It adds 0 new FastAPI endpoints.
- **Data Policy**: Inactive placeholder panels make 0 backend requests on panel toggles or switches.


