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
