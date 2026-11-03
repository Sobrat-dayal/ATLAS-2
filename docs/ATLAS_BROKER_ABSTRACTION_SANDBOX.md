# ATLAS Stage 145: Broker Abstraction and Sandbox Boundary

Stage 145 currently provides the first executable broker boundary over the
existing trading package. It is sandbox-only and does not enable production
broker routing.

## Implemented

- Stable provider definitions for Alpaca Paper, Upstox Sandbox, and Tradier Sandbox.
- Typed provider capabilities, connections, normalized order requests, and orders.
- Encrypted in-memory credential storage with tenant checks.
- Fixed provider host allowlists with HTTPS and private-address rejection.
- Default provider factories backed by a deterministic `MockBrokerAdapter`.
- Explicit `VERIFIED_WITH_MOCK` connection state before order operations.
- Gateway checks for sandbox environment and verified connection status.
- Focused tests for provider construction, verification gating, tenant isolation,
  mock submission, and production-host rejection.

## Verification Status

The default adapters are mock-only. No provider credentials were used, and no
provider sandbox was contacted. A mock-verified adapter must not be presented as
connected or provider-sandbox verified.

## Current Boundary

The current package is an in-memory domain and contract layer. Durable
connections, order intents, fills, reconciliation records, FastAPI routes,
provider HTTP adapters, migrations/RLS, streaming, webhooks, and the Broker
Integration Lab UI remain follow-up work. Stage 144 internal paper accounts are
not merged with external broker state.

## Safety Rule

Execution hosts are selected by registered providers. User-supplied execution
URLs are not accepted. Production hosts must fail the sandbox allowlist check,
and unverified connections cannot submit, modify, cancel, or preview orders.
