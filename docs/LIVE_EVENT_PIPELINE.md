# Stage 42 - Live Event Pipeline

## Architecture

```text
Canonical Quote
      │
      ▼
Live Quote Processor
      │
      ▼
Atomic Routed State / Event Commit
      │
      ├──────────────► Routed Latest Quote
      │
      └──────────────► Live Market Event Stream
                                  │
                                  ▼
                          Internal Event Reader
```

### Stage 41 / Stage 42 Boundary
- **Stage 41**: Obtain and validate live Quotes from providers.
- **Stage 42**: Transport accepted routed Quote changes via Redis Streams.

### Stage 42 / Stage 43 Boundary
- **Stage 42**: Backend Event Stream implementation (internal transport).
- **Stage 43**: Frontend WebSocket infrastructure (future work).

### Transport Event vs Universal Event
**Stage 42 LiveEvent != Stage 135 Universal Event**

Stage 42 LiveEvents are short-retention backend state-transition transports. They simply emit what just happened internally. They are not the highly enriched, cross-referenced, severity-scored Universal Events envisioned for Stage 135.

## Initial Event Types
| Event Type | Implemented? |
| --- | --- |
| `market.quote.updated` | Yes |

### Event Emission Semantics
`market.quote.updated` is emitted **only** when a newer routed quote is accepted by the state store.

#### No-Event Conditions
- **Older Quote**: Rejected; no event.
- **Identical Duplicate**: Refresh TTL (if applicable) but no event.
- **Provider-specific-only update**: Does not change routed state; no event.
- **Invalid Quote**: Rejected; no event.
- **Unknown Target**: Rejected; no event.
- **Provider Mismatch**: Rejected; no event.

## Live Event Envelope
| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | int | Yes | Event schema version (currently `1`). |
| `event_id` | UUID | Yes | Unique ID for the event, stable across redeliveries. |
| `event_type` | LiveEventType | Yes | Event type classification (e.g. `market.quote.updated`). |
| `emitted_at` | datetime (UTC) | Yes | Time when ATLAS emitted the live transport event. |
| `instrument_entity_id` | UUID | Yes | The canonical Instrument UUID. |
| `provider_key` | str | Yes | The origin Provider. |
| `payload` | dict | Yes | Typed payload specific to the event type. |

### Event ID vs Stream ID
- `event_id`: A UUID representing ATLAS's internal identity for this exact event. Stable across reads.
- `stream_id`: A Redis cursor (e.g., `1760000000000-0`) representing the event's location in the transport stream.

### Timestamp Semantics
| Timestamp | Meaning |
| --- | --- |
| **Quote source time** | Timestamp attached by the Provider to the actual quote payload. |
| **ATLAS received_at** | Time when the Quote worker received the Quote. |
| **Event emitted_at** | Time when the Event Pipeline appended the event to the stream. |
| **cache time (cached_at)** | Time the payload was inserted into the state store. |

### Quote Payload
For `market.quote.updated`, the payload corresponds directly to `MarketQuoteUpdatedPayload` which wraps a Decimal-safe `Quote` object, preserving all canonical fields without precision loss.

### Event Serialization
- **Format**: JSON (UTF-8)
- **Decimal encoding**: Native string/float matching Pydantic defaults; Decimal values preserved.
- **UUID encoding**: String format.
- **Datetime encoding**: ISO-8601 UTC.
- **null encoding**: Standard JSON `null`.
- **NaN / Infinity**: Strictly rejected (`allow_inf_nan=False`).

### Event Size Limit
Events are strictly bounded to prevent abuse or memory spikes.
- **Max Bytes**: `131072` (128 KiB).
- **Oversized Behavior**: Rejected entirely; not truncated.

## Stream Backend
- **Server**: Valkey / Redis (Stage 38 infrastructure)
- **Transport**: Redis Streams (`XADD` / `XREAD`)
- **Stream command family**: Basic stream operations (no consumer groups).

### Live Market Stream Key
**Pattern**: `atlas:events:live:market` (Configurable environment prefix)
**Stage 38 Prefix Reuse**: True.

### Stream Topology
- **Market Streams**: `1` global stream for the initial pipeline to avoid widespread key proliferation and scanning overhead.
- **Stream Sharding**: Not implemented yet.

### Stream Retention
- **Maximum Length**: Configurable (default `100000`).
- **Trim Semantics**: Approximate trim (`~`).
- **Event-count retention != Guaranteed time retention**.

### Event Stream Authority
**Not authoritative history.** The stream can be trimmed or lost. Truth lives in historical ClickHouse storage and real-time state snapshots in Redis.

## Atomic Routed-State / Event Commit
Implemented using a static **Lua Script** registered with Redis.

### Atomic Commit Flow
```text
incoming Quote
      │
      ▼
compare ordering
      │
      ├── reject → no state, no event
      │
      └── accept
             │
             ▼
      atomic transaction
             │
      ┌──────┴──────┐
      ▼             ▼
routed state       XADD event
```

### Split-Brain Failure Protection
Because the update and `XADD` are packaged in a single Lua script, it's impossible for ATLAS to intentionally commit a routed-state change without a corresponding event append, or vice versa. The transaction succeeds as a whole or fails as a whole.

### Provider-Specific State
Maintained identically to Stage 41, integrated safely outside the core atomic transaction if separate, or naturally updated through the primary Quote processor.

### Atomic Commit Result
`LiveQuoteEventCommitResult` returns boolean flags `routed_state_updated`, `event_emitted`, and the generated `stream_id` + `event_id` if successful.

## Live Event Reader
- **Redis Read Mechanism**: `XREAD`
- **Consumer Groups**: Not implemented.
- **Redis Pub/Sub**: Not implemented.

### Event Cursor
- **Type**: `LiveEventCursor`
- **Format**: `milliseconds-sequence` (e.g., `1760000000000-0`).
- **Validation**: Numerical parsing; invalid strings rejected.
- **Comparison**: Strictly numeric (milliseconds, then sequence).
- **Empty Stream Cursor**: `0-0`

### Tail Cursor & Bounds
- **Tail Cursor**: Determined via `XINFO STREAM`. Returns `0-0` if empty.
- **Stream Bounds**: `(first_cursor, last_cursor, length)`.

### Read API
```python
read_after(cursor: str, count: int, block_ms: int) -> List[LiveEventMessage]
```
- **Read Count Limits**: Bounded between `1` and `max_read_count` (e.g., 2048).
- **Blocking Limits**: Bounded up to `max_block_milliseconds` (e.g., 30000 ms).
- **Infinite Blocking**: Not exposed.

### Replay Semantics
- **Ordering**: Oldest to newest.
- **Cursor Expiration**: Explicitly detected via bounds comparison. `LiveEventCursorExpired` is raised if a reader asks for a cursor that has already been trimmed.

### Snapshot + Event Handshake Foundation
The pipeline is designed for the future Stage 43 pattern:
```text
tail cursor
    │
    ▼
latest state snapshot
    │
    ▼
read events after tail cursor
```

### Delivery Semantics
- **No exactly-once delivery.** Delivery is at-least-once-friendly. Consumers must rely on `event_id` to deduplicate if they overlap reads.

### Event Stream Loss / Redis Loss
If Redis goes down or the stream is wiped:
- Existing active worker targets are preserved in PostgreSQL.
- Historical data in ClickHouse is untouched.
- When Redis recovers, future incoming quotes will naturally recreate the stream and repopulate the state cache.

## Redis / Valkey Commands Used
| Command | Used? | Purpose |
| --- | --- | --- |
| `XADD` | Yes | Appending to stream inside Lua script |
| `XREAD` | Yes | Event Reader |
| `XINFO` | Yes | Inspecting stream bounds and tail |
| `XLEN` | No | (Covered by XINFO) |
| `PUBLISH` | No | Unused |
| `SUBSCRIBE` | No | Unused |
| `XGROUP` | No | Unused |
| `XREADGROUP` | No | Unused |
| `XACK` | No | Unused |

### Lua Security
The Lua script is **repository-owned, static, and explicitly registered**. There is no user script access, no dynamic eval, and no arbitrary shell execution.

## Event Logging & Metrics
- **Per-Event INFO Logging**: Disabled to prevent flood.
- **Raw Payload Logging**: Disabled.
- **Metrics**: Minimal core pipeline metrics (failures, sizes) can be hooked in generically. No high-cardinality labels (like tickers or user IDs).

## PostgreSQL / ClickHouse Changes
- **No Stage 42 PostgreSQL migration.**
- **No live Event table.**
- **No Stage 42 ClickHouse migration.**
- **No live Event history table.**
- **No per-event Provenance records.**
