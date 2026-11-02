# ATLAS Stage 146: Agents V1 Foundation

Stage 146 currently provides a tenant-scoped Agent Registry and a truthful run
ledger behind `/api/v1/agents`.

## Implemented

- Agent definitions with immutable version records in the current service
  boundary.
- Validation against the existing approved model registry.
- Validation against the existing ATLAS AI Tool Registry.
- Explicit draft and published lifecycle states.
- Tenant and owner checks for agent and run reads.
- Run records pinned to the published agent version.
- Run event records beginning with `RUN_QUEUED`.
- API endpoints for listing, creating, publishing, and inspecting agents and runs.
- No autonomous execution, arbitrary code execution, shell access, broker access,
  or tool bypass.

## Runtime Truthfulness

Runs are accepted into a ledger with `status=QUEUED` and
`execution_enabled=false`. The event metadata records
`EXECUTION_WORKER_UNAVAILABLE`. This is intentional: the repository does not
yet contain a general durable queue, worker lease protocol, persistent agent
repository, or checkpoint store.

## Reuse

Model eligibility comes from the existing AI provider registry. Tool eligibility
comes from the existing Stage 126 tool registry. Authentication uses the
existing `get_current_user` dependency. No duplicate model credentials or tool
execution path is introduced.

## Deferred Boundary

Durable PostgreSQL persistence and RLS, workflow graphs and compilation, node
executors, schedules, event triggers, approvals, MCP, memory, model invocation,
tool dispatch, retries, cancellation, recovery, realtime run updates, and the
visual workflow editor remain incomplete. Stage 147+ specialized agent work and
Stage 150 launch hardening are not claimed.