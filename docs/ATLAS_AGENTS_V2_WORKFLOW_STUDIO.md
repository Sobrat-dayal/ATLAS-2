# ATLAS Stage 147: Workflow Definition Foundation

Stage 147 currently provides the first executable backend contract for typed
workflow definitions. It is intentionally narrower than a complete visual
Workflow Studio because Stage 146 does not yet provide durable agent or workflow
execution infrastructure.

## Implemented

- Typed workflow nodes, edges, port types, graphs, and version records.
- Supported node types for manual triggers, AI agents, ATLAS tools, conditions,
  and returns.
- Deterministic graph validation and topological compilation.
- Single-trigger and return-node requirements.
- Duplicate ID, unknown-node, self-edge, type-mismatch, cycle, reachability, and
  graph-size checks.
- Validation of AI node model IDs against the existing model registry.
- Validation of ATLAS tool node IDs against the existing Stage 126 registry.
- Tenant/owner-scoped workflow registry and API routes under `/api/v1/workflows`.
- Draft and published workflow status with published graph validation.
- Focused tests for graph semantics, capability checks, publishing, and tenant isolation.

## API Boundary

Implemented endpoints are:

- `GET /api/v1/workflows`
- `POST /api/v1/workflows`
- `GET /api/v1/workflows/{workflow_id}`
- `POST /api/v1/workflows/{workflow_id}/validate`
- `POST /api/v1/workflows/{workflow_id}/publish`

The current registry is in-memory. It is a definition and validation boundary,
not evidence of durable storage or workflow execution.

## Explicitly Deferred

PostgreSQL persistence and RLS, draft editing, immutable multi-version history,
workflow execution, node executors, model invocation, tool dispatch, MCP,
scheduling, approvals, retries, cancellation, checkpoints, worker recovery,
realtime run events, import/export, templates, reusable subworkflows, and the
visual editor remain incomplete. No workflow run is claimed or started by this
stage.

Stage 148, Stage 149, and Stage 150 are not implemented or certified.
