# apps/api

Backend API for the ATLAS financial intelligence platform, built with Python and FastAPI.

## Requirements
- Python 3.12+
- `uv` (Fast Python package manager)

## Install
```bash
cd apps/api
uv sync --extra dev
```

## Run
Development server with hot-reload:
```bash
uv run uvicorn atlas_api.main:app --reload
```
The server will run on `http://127.0.0.1:8000`.

## Test
```bash
uv run pytest tests/
```

## Code Quality
Format code and check for lint errors:
```bash
uv run ruff format .
uv run ruff check .
```

## Environment
Configuration is driven by `ATLAS_*` prefixed environment variables. Refer to the root `.env.example` file for configurable parameters (e.g., `ATLAS_API_PORT`, `ATLAS_CORS_ORIGINS`).

## API Docs
When running locally with `ATLAS_DEBUG=true`, Swagger UI documentation is available at:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
