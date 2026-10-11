# Valkey Infrastructure Architecture

**Selected implementation:** Valkey

Valkey was selected as the Redis-compatible infrastructure for ATLAS because it provides an open-source, highly compatible, and performant backend for caching, low-latency state, and distributed coordination.

## Core Data Architecture

- **PostgreSQL** = Transactional durable source of truth
- **ClickHouse** = Analytical durable high-volume data
- **Valkey** = Ephemeral low-latency state

**Critical Invariant:** ATLAS must remain recoverable if every Valkey key is lost. Valkey is non-authoritative infrastructure.

## Current Stage 38 State

Valkey infrastructure exists. No ATLAS production business cache, state, locks, or queues have been implemented yet. Stage 38 only establishes the robust client and container infrastructure.

## Deployment Layout

- **Server product:** Valkey
- **Server version:** 8.0.2 (Pinned explicitly, `latest` is not used)
- **Container image:** `valkey/valkey:8.0.2`
- **Service name:** `valkey`
- **Container port:** 6379
- **Host port:** 127.0.0.1:6379 (Bound to loopback only)
- **Networks:** Default docker compose internal network
- **Volumes:** `valkey_data` mapped to `/data`
- **Healthcheck:** `valkey-cli PING` via application user
- **Persistence:** RDB defaults apply, but ATLAS correctness does not depend on Valkey persistence.

## Networking

**Public Internet exposure:** None. Valkey must reside on a private internal network.
**Browser Access:** Browsers must never connect directly to Valkey. Browser → ATLAS API → Valkey.

## Authentication and Security

- **Application user:** `atlas_app`
- **Default-user policy:** Disabled/restricted (restricted to internal loopback only without password capability).
- **Authentication required:** Yes.
- **Empty passwords:** Denied.

### Secret Handling
- Passwords are provided via runtime environment variables (e.g. `ATLAS_VALKEY_PASSWORD`).
- No password is ever committed to Git.
- The `.env.example` file contains no working secrets.
- Passwords are automatically redacted from `repr()` and `str()` outputs in the settings model.
- Secrets are absent from all application logs and frontend bundles.

### Access Control List (ACL)

| Command / Category | Allowed? | Reason |
| :--- | :--- | :--- |
| `PING` | Yes | Health checking |
| `GET`, `SET`, `DEL`, `TTL` | Yes | Standard caching and coordination |
| `SCAN` | Yes | Safe key discovery |
| `KEYS` | Yes | Used for small bounded testing, `SCAN` preferred otherwise |
| `CONFIG` | No | Prevents runtime security downgrade |
| `ACL` | No | Prevents privilege escalation |
| `FLUSHDB`, `FLUSHALL` | No | Prevents catastrophic destructive resets |
| `SHUTDOWN` | No | Prevents denial of service |
| `MODULE` | No | Prevents arbitrary code loading |
| `EVAL` | No | Scripting disabled until specifically required |
| `PUBLISH`, `XADD` | No | Pub/Sub and Streams disabled until Stage 42 |

### Serialization Policy

**`pickle` is strictly forbidden.** Deserializing untrusted Python objects is an arbitrary code execution risk. Future payload serialization must use UTF-8 text, JSON, or MessagePack. No generic business serializer framework was implemented in Stage 38.

## Key Design Boundary

- **Namespace:** `atlas:<environment>:` (e.g., `atlas:dev:`)
- **Logical Database Policy:** Database `0` is strictly enforced. ATLAS does not use multiple logical databases (e.g., `DB 1`, `DB 2`) for module isolation because DB 0 is cleaner, easier to inspect, and cluster-compatible.
- **Business Keys:** Stage 38 defines no production business-specific key schema.

### TTL Policy

Future cache keys should generally use explicit Time-To-Live (TTL) values. Stage 38 did not introduce any feature-specific TTLs.

### Eviction Policy

Server default (typically `noeviction` or standard LRU defaults based on maxmemory). ATLAS does not assume an aggressive eviction policy is final for all workloads. Future coordination/cache needs may require segregated instances if policies conflict.

## Application Client configuration

| Field | Type | Default | Sensitive? | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `enabled` | `bool` | `False` | No | Prevents network connections during unit tests |
| `host` | `str` | `127.0.0.1` | No | Server hostname |
| `port` | `int` | `6379` | No | Server TCP port |
| `database` | `int` | `0` | No | Logical database (must be 0) |
| `username` | `str` | `atlas_app` | No | Dedicated ACL user |
| `password` | `SecretStr` | None | Yes | User password |
| `secure` | `bool` | `False` | No | Enforces TLS |
| `verify_tls` | `bool` | `True` | No | Verifies certificates |
| `connect_timeout_seconds` | `int` | `5` | No | Timeout for initial handshake |
| `socket_timeout_seconds` | `int` | `5` | No | Timeout for socket operations |
| `max_connections` | `int` | `100` | No | Connection pool size |
| `key_prefix` | `str` | `atlas:dev:` | No | Validated namespace prefix |

### TLS Behavior

- **Local behavior:** Plaintext TCP over trusted Docker bridge.
- **Production support:** Fully supported via `secure=True`.
- **Certificate verification:** Enabled by default when secure.

### Connection Lifecycle

```text
ATLAS process
      │
      ▼
settings
      │
      ▼
pool/client
      │
      ▼
reuse
      │
      ▼
shutdown
      │
      ▼
close
```

- **Import-Time Behavior:** `0` network calls.
- **Python Client:** `valkey` >= `6.1.1` (asyncio mode via `valkey.asyncio`).
- **Connection Pool:** Shared pool per process, properly disconnected on shutdown.

### Unavailability and Misconfiguration

- **Disabled mode:** Explicitly avoids any connection attempt.
- **Misconfiguration:** (e.g. missing password) Fast-fails with `ValkeyConfigurationError`.
- **Unavailable server:** Fast-fails with `ValkeyUnavailableError`.

## Health Service

The Valkey health service relies entirely on a safe, read-only `PING` operation and a lightweight `INFO server` fetch to verify connectivity. 

**Mutation Audit:** `SET: 0`, `DEL: 0`, `HSET: 0`, `XADD: 0`.

**Provider Health Boundary:** Valkey health is entirely distinct from Provider Health. Valkey is not a Provider and is not included in Provider Routing or external Provider APIs.

## Future Roadmap

- **Stage 39**: Historical Market Data Ingestion (ClickHouse, likely skips Valkey).
- **Stage 41**: Live Quote Ingestion (may cache latest quote state in Valkey).
- **Stage 42**: Live Event Pipeline (may leverage Valkey Pub/Sub or Streams).
- **Stage 43**: WebSockets (may use Valkey for fanout).
- **Future Agents/Workflows**: Execution state, distributed locking, and queues.

## Persistent Notifications (Stage 49)

Stage 49 introduces **0** new Redis/Valkey business-state requirements:
- 0 notification Redis lists or sets.
- 0 notification unread counters in Redis.
- 0 notification Pub/Sub channels.
- 0 notification Redis Streams.
- 0 notification caches in Valkey.
- Notifications are durable, user-scoped records authoritative in PostgreSQL. Stage 49 explicitly avoids coupling notifications to Valkey.

