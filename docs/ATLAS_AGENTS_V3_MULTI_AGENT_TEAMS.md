# ATLAS Stage 148: Multi-Agent Team Definition Foundation

Stage 148 currently adds a governed team-definition boundary over the existing
Stage 146 agent registry. It does not claim autonomous multi-agent execution.

## Implemented

- Typed team definitions and memberships.
- Explicit `COORDINATOR`, `SPECIALIST`, and `REVIEWER` roles.
- Validation that referenced agents belong to the same tenant and are published.
- Exactly one coordinator per team.
- Duplicate-member, member-count, and concurrency-limit validation.
- Tenant/owner-scoped in-memory team registry.
- Draft, published, and disabled team lifecycle states.
- API endpoints under `/api/v1/agents/teams` for list, create, inspect, publish,
  and disable operations.
- Team responses explicitly expose `execution_enabled=false`.

## Runtime Truthfulness

Teams are configuration records only. They do not dispatch tasks, invoke models,
send agent messages, execute workflows, schedule work, or claim active workers.
This reflects the current repository state: Stage 146 runs are queued with
execution disabled, and Stage 147 workflows are definitions and validators with
no execution worker.

## Deferred Requirements

Durable team/task/project persistence, PostgreSQL RLS, task planning and
delegation, queues and leases, agent messaging, shared context, reviews,
consensus, approvals, budget enforcement, retries, recovery, realtime
monitoring, department templates, operations dashboards, and team UI remain
future work. Stage 149 and Stage 150 are not implemented or certified.