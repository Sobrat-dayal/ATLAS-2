# ATLAS Stage 1 & 2 Decisions Log

This document records the major architectural and product decisions established. These decisions are binding for future implementation stages.

## Stage 11: Backend Foundation
13. **FastAPI**: Primary ATLAS backend HTTP framework, maintaining modular monolith structure.
14. **Configuration**: Uses `pydantic-settings` for typed environment configurations.
15. **Observability**: Request IDs and unified structured logging are mandatory.
16. **Errors**: Errors use a stable ATLAS error envelope format (`AtlasError`).
17. **Separation**: Domain logic is decoupled from HTTP routers.

## Stage 1: Core Product & Navigation
1. The 20-module navigation structure is strictly frozen.
2. The `Home` module is the default launch page and serves as the operational command center.
3. The platform's layout is a desktop-first, information-dense terminal environment.
4. Custom backgrounds and watermarks are a native part of the UX.

## Stage 1: Architecture
5. ATLAS will begin as a clean **modular monolith**. Microservices are deferred until scale demands them.
6. Python is the primary language for backend, analytics, AI, and business logic.
7. React/Next.js (with TypeScript) is the expected stack for the browser UI.
8. The **Universal Entity architecture** is foundational.
9. **Global Context** is foundational.
10. The **Shared Capability Layer** ensures that core functions are implemented once.
11. A persistent, sandboxed bottom terminal is part of the core product.
12. Settings exist at Global, Section, Workspace, and Widget levels.

## Stage 1: Intelligence & Capabilities
13. The ATLAS AI overlay and the AI Assistant module are distinct surfaces.
14. God's Eye/Maps is a financial and geopolitical intelligence system.

## Stage 1: Agents & Workflows
15. Agents operate as a first-class top-level module within ATLAS.
16. The Agents system includes an n8n-style visual workflow builder.
17. Agents may contain their own internal workflows.
18. Workflows may recursively contain agents and sub-workflows.
19. MCP (Model Context Protocol) is treated as a first-class citizen.
20. High-risk external actions require strict permissions.

## Stage 1: Implementation Guardrails
21. Development will strictly follow the defined staged architecture.
22. Stage 1 implements no production code.

## Stage 2: Monorepo Architecture
23. ATLAS uses a monorepo structure orchestrated by `pnpm` for Node spaces and `uv`/`hatchling` for Python.
24. Python code is organized by logical domain package inside a single `python/atlas` workspace package to optimize for solo developer maintainability while preserving domain boundaries.
25. The backend explicitly starts as a modular monolith.
26. `apps/web` is the primary web application location.
27. `apps/api` is the future API application entry point.
28. Worker deployments are deferred.
29. Agent definitions are separate from runtime code.
30. Workflows are separate portable assets.
31. MCP integrations have a dedicated repository area (`mcp/`).
32. Infrastructure is isolated from application logic.
33. Package/dependency management is standardized (`pnpm`, `pyproject.toml`).
34. Unnecessary orchestration/build tools (e.g., Turborepo, Nx) are avoided initially to keep complexity low.

## Stage 3: Application Shell
35. ATLAS uses a persistent desktop application shell, avoiding traditional browser-level scrolling.
36. The Shell consists of Sidebar, TopBar, MainWorkspace, AgentDock, and BottomTaskbar.
37. Main module content scrolls independently from the application chrome within the MainWorkspace.
38. The Agent Dock is a global shell feature for tracking agent activity and executing autonomous workflows.
39. Bottom panel architecture is primed for Terminal, Tasks, Agents, Jobs, Alerts, and System features.
40. Shell visual preferences (Sidebar collapse, Dock open/width, active bottom panel) persist locally.
41. ATLAS remains inherently desktop-first in layout design.
42. Module pages are isolated and may request standard, dense, or full-bleed layouts (via container usage).
43. No business or domain logic belongs in the UI shell layer (e.g. market data ticker uses mock fixture pending Stage 17 integration).

## Stage 4: Navigation Architecture
44. ATLAS core navigation consists of exactly 20 modules defined in code (not a database).
45. Stable machine-readable module IDs and a canonical route structure are strictly enforced.
46. Module registry is the single source of truth for routing, icons, labels, aliases, and settings namespaces.
47. The Sidebar dynamically renders items directly from the central module registry to ensure absolute consistency.
48. Missing core modules render a clean `ModuleFoundation.tsx` page to avoid 404s and accurately reflect the future architecture.
49. Legacy/singular routes (e.g., `/screener`, `/economy`, `/map`, `/portfolio`, `/analytics`) are permanently redirected to their canonical plural/current equivalents (`/screeners`, `/economics`, `/maps`, `/portfolios`, `/risk`).
50. Shell surfaces like Agent Dock and ATLAS AI top-bar overlay are strictly separate concepts from the full `/agents` and `/ai` workstation modules.
51. Existing functionality (like the Home screen) is preserved, while foundation pages are injected seamlessly for the remaining unbuilt modules.
52. The root route `/` performs a permanent redirect to `/home`.
53. Future permissions, commands, and contexts will directly consume this established module registry.

## Stage 16: Universal Entity Architecture
80. ATLAS uses a Universal Entity identity model.
81. Every entity receives an immutable internal UUID `entity_id`.
82. External identifiers are not primary keys.
83. Tickers are not primary keys.
84. Companies and their securities are explicitly separate entities.
85. Entity types are defined through a canonical registry (`entity_types`).
86. Each entity has one primary entity type.
87. Type hierarchy is represented through parent type keys.
88. The base entity table stays intentionally small.
89. Specialized attributes live in future specialization tables.
90. Specialized tables should generally use `entity_id` as PK/FK.
91. Generic JSON metadata is not used as a substitute for domain schemas in the base entity table.
92. Canonical names are not globally unique.
93. Duplicate names are allowed.
94. Generic entity type changes are not exposed.
95. Generic public entity creation and deletion are not exposed.
96. Identifiers, Aliases, Relationships, and Provenance are deferred to Stages 21-24.
97. Global Context and Search are deferred to Stages 25, 26, and 45.
98. Provider integration remains deferred.
99. Entity master data lives in PostgreSQL.
100. Entity creation must support atomic future specialization transactions without premature auto-commits.

## Stage 25: Global Selected Entity Context
101. ATLAS now has one global selected Universal Entity context.
102. The canonical selected value is `entity_id`.
103. Tickers, names, aliases and provider IDs are never canonical selection keys.
104. Company and Security remain distinct selectable Entities.
105. Selected Entity Context supports all Universal Entity types.
106. Global selected Entity is distinct from local table/list selection.
107. Hover/focus does not change global Entity context.
108. Global selection changes only through deliberate semantic selection actions.
109. Initial selected Entity is null.
110. No fake default Entity exists.
111. One browser tab supports zero or one global selected Entity.
112. Stage 25 does not support global multi-selection.
113. Selected Entity Context is mounted once at App Shell level.
114. Modules must not create competing global Entity stores.
115. The context persists across module navigation.
116. Sidebar route changes do not clear Entity selection.
117. App fullscreen does not clear selection.
118. Agent Dock/Terminal toggles do not clear selection.
119. Stage 25 uses the Stage 16 Entity endpoint for metadata.
120. Selected context stores only Entity ID as durable session state.
121. Base Entity metadata remains query-cache owned.
122. Full Entity payloads are not persisted to browser storage.
123. Session persistence uses sessionStorage by default.
124. Selected Entity is transient context, not a user preference.
125. Selected Entity is not persisted in PostgreSQL.
126. Selected Entity is not stored in JWT/session claims.
127. Selected Entity is not globally synchronized between browser tabs.
128. Selected Entity is not automatically serialized into all URLs.
129. Existing Entity detail routes may deliberately set selection if they already exist.
130. Logout clears selected Entity.
131. Authenticated account changes clear selected Entity.
132. Temporary API failures do not automatically clear selection.
133. Stale 404 selections are cleared.
134. Client-selected Entity ID never bypasses backend authorization.
135. Stage 22 Resolver remains responsible for converting strings/symbols into Entity IDs.
136. SelectedEntityProvider accepts Entity IDs, not free-form symbols.
137. Ambiguous resolution never changes global selection automatically.
138. Not-found resolution does not destroy existing selection.
139. Selected Entity Context does not automatically load Identifiers, Aliases, Relationships, or Provenance.
140. Selected Entity Context does not load domain market/fundamental data.
141. Selected Entity Context is a pointer, not a global data warehouse.
142. Modules may decide whether the selected Entity type is relevant without clearing it.
143. The Top Bar exposes selected Entity identity compactly.
144. Selected Entity UI follows the ATLAS design system.
145. No new top-level navigation item is created.
146. No database migration is normally required for Stage 25.
147. Stage 26 composed Selected Entity into the broader Global Application Context.

## Stage 26: Global Application Context
148. ATLAS now has one Global Application Context architecture.
149. Global Application Context represents semantic working context, not all frontend global state.
150. Authentication remains outside Global Application Context.
151. Appearance remains outside Global Application Context.
152. Settings remain outside Global Application Context.
153. Layout geometry remains outside Global Application Context.
154. Stage 25 selected Entity becomes a focused slice of Stage 26 context.
155. `selectedEntityId` remains the canonical Entity context pointer.
156. Stage 25 `useSelectedEntity()` compatibility is preserved.
157. No second selected Entity store exists.
158. Global Application Context stores references and analysis parameters, not domain datasets.
159. Query/cache layers remain authoritative for API data.
160. Global Time Range is introduced as shared analysis context.
161. Global Time Range is not a market-session engine.
162. Global Time Range does not equal chart candle interval.
163. Global Time Range supports presets and custom ranges.
164. The chosen default Time Range is documented centrally (1m).
165. Portfolio context is foundation-only until Stage 110.
166. Workspace context is foundation-only until Stage 120.
167. Stage 26 does not create Portfolio or Workspace domain data.
168. Map Context is foundation-only until Stage 129.
169. Stage 26 does not integrate MapLibre/Cesium/deck.gl.
170. Map Context stores viewport/layer references, not map features.
171. Global Filter Context is typed and intentionally minimal.
172. Stage 26 avoids arbitrary global `Record<string, any>` filter storage.
173. Selected Object foundation is distinct from Selected Entity.
174. Universal Entity remains first-class in context.
175. Initial selected object is null.
176. Global context uses versioned sessionStorage persistence.
177. Context is isolated per browser tab.
178. No cross-tab synchronization exists.
179. No backend application-context table exists.
180. No application-context API exists.
181. No context is stored in JWT/auth claims.
182. Logout resets Global Application Context.
183. Authenticated principal changes reset Global Application Context.
184. Stage 25 storage is safely migrated into Stage 26 storage.
185. Entity ID is preserved during Stage 25-to-26 migration.
186. New context storage becomes authoritative after migration.
187. Context storage is validated before use.
188. Corrupt context storage cannot crash ATLAS.
189. Storage failure falls back to in-memory context.
190. Context reset does not reset Settings, Appearance, Auth or Layout.
191. Context changes do not mutate backend domain data.
192. Context changes do not automatically trigger AI, Agents, or trades.
193. Stage 26 does not implement context history, cloud sync, or shareable context URLs.
194. Stage 26 does not automatically serialize context into routes.
195. Stage 26 prepares a read-only serializable context snapshot for future Stage 27 capabilities.

## Stage 29: Integrate OpenBB as Provider Framework

1. OpenBB is integrated behind the Stage 28 Provider abstraction.
2. ATLAS domain code does not import OpenBB directly.
3. OpenBB integration uses the Python runtime in-process.
4. Stage 29 does not deploy OpenBB as a REST sidecar.
5. Stage 29 does not expose OpenBB REST routes.
6. Stage 29 does not integrate OpenBB Workspace.
7. Stage 29 does not integrate OpenBB MCP.
8. Stage 29 uses a minimal OpenBB runtime dependency rather than installing every provider automatically.
9. The OpenBB dependency is version-constrained and lockfile-pinned.
10. OpenBB major-version compatibility is validated.
11. Incompatible OpenBB generations are not mixed.
12. OpenBB build/interface preparation occurs before normal request handling where required.
13. OpenBB is not rebuilt on each request.
14. OpenBB is not rebuilt for each Capability execution.
15. OpenBB imports are isolated to the OpenBB integration package.
16. `provider_key = openbb`.
17. Initial OpenBB adapter version is 1.
18. OpenBB is registered through the existing Stage 28 Provider Registry.
19. No second Provider Registry is created.
20. OpenBB registration is explicit.
21. OpenBB Provider extensions are not automatically promoted to ATLAS Providers.
22. OpenBB Provider construction uses the Stage 28 ProviderFactory architecture.
23. Provider Catalog listing does not instantiate OpenBB adapters.
24. OpenBB adapter construction is lazy.
25. OpenBB Provider registration does not fetch external data.
26. OpenBB Runtime provides an isolated integration boundary.
27. OpenBB Coverage Inspector reads only local runtime metadata.
28. Stage 29 does not expose a generic OpenBB command executor.
29. Arbitrary command paths are never accepted from users.
30. Stage 29 does not use `eval` or `exec`.
31. Future OpenBB data calls must be explicitly implemented through typed Provider methods.
32. OpenBB-specific result objects must not leak into Domain Services.
33. OpenBB-specific result objects must not leak into Capability outputs.
34. OpenBB-specific result objects must not leak into FastAPI schemas.
35. OpenBB-specific result objects must not leak into the frontend.
36. Future OpenBB results should retain source/provider metadata long enough for provenance handling.
37. OpenBB itself is not automatically treated as the underlying Provenance Source.
38. OpenBB Provider registration creates no Provenance Source record.
39. OpenBB Provider registration creates no Provenance Record.
40. Stage 29 does not create canonical Market Data models.
41. Stage 29 does not create canonical Fundamental models.
42. Stage 29 does not create canonical Economic models.
43. Stage 29 does not create canonical News/Research models.
44. Stage 29 performs no real financial-data fetch in production integration code.
45. Stage 29 requires no Provider API keys.
46. OpenBB credentials remain Stage 30.
47. Per-user OpenBB credentials must not be implemented through unsafe process-global mutation.
48. OpenBB global runtime preferences must not be used to leak one user's settings to another.
49. OpenBB runtime availability is not Provider health.
50. Provider health remains Stage 31.
51. OpenBB registration does not make OpenBB the default Provider.
52. Automatic Provider routing remains Stage 32.
53. OpenBB failure does not trigger automatic fallback during Stage 29.
54. Stage 29 adds no retries.
55. Stage 29 adds no circuit breakers.
56. Stage 29 adds no rate-limit architecture.
57. Stage 29 adds no Provider cost tracking.
58. Stage 29 adds no quota tracking.
59. Stage 29 adds no OpenBB data cache.
60. Stage 29 adds no Redis dependency.
61. Stage 29 adds no ClickHouse integration.
62. Stage 29 adds no ingestion workers.
63. Stage 29 adds no live feeds.
64. Stage 29 adds no WebSocket infrastructure.
65. OpenBB package/runtime diagnostics contain no secrets.
66. Unit tests remain offline.
67. CI does not depend on public financial APIs.
68. At least one real OpenBB import/runtime smoke test exists.
69. OpenBB registration appears through existing `provider.list` and `provider.get`.
70. Stage 30 remains responsible for Provider configuration and credentials.

## Stage 30: Provider Configuration and Credential Management

1. Provider configuration defaults to `enabled=false`.
2. Configuration is strictly user-scoped and not globally applied.
3. ATLAS must never store Provider secret values in plaintext application tables.
4. Secret values are write-only through user-facing APIs. Users may set, replace, or delete, but never GET.
5. Supabase Vault is the preferred production secret backend.
6. The `SecretStore` abstraction handles the underlying Vault interactions.
7. `ProviderConfiguration` models define the configuration state in the database.
8. `ProviderCredentialBinding` maps credentials to Vault UUIDs, never storing the raw value.
9. No generic secret stores are implemented.
10. No plaintext fallback exists.
11. Decrypted secrets are not cached in the application layer.
12. Multi-user isolation is enforced by keeping credential handling within the ATLAS Service layer rather than mutating process-global OpenBB runtime state.

## Stage 33 - Canonical Market Data Models
1. ATLAS owns canonical Market Data models.
2. Provider-specific Market Data objects must not leak into domain code.
3. Canonical Market Data identity uses existing instrument/entity UUIDs.
4. Ticker is not canonical Market Data identity.
5. Stage 33 does not create a new symbol-resolution system.
6. Financial prices use Decimal.
7. Financial sizes use Decimal.
8. Financial volumes use Decimal where fractional values may occur.
9. Binary float is not the canonical financial numeric type.
10. Non-finite Decimal values are rejected.
11. Canonical financial numeric values are not globally rounded.
12. Decimal JSON serialization preserves precision.
13. All canonical Market Data timestamps are timezone-aware.
14. All canonical Market Data timestamps are UTC-normalized.
15. Naive datetime values are rejected.
16. Timestamp source semantics are represented where implemented.
17. Market Data timeliness distinguishes real-time, delayed, end-of-day, historical and unknown states.
18. MarketDataOrigin represents lightweight runtime source metadata.
19. MarketDataOrigin is not a Stage 24 Provenance Record.
20. MarketDataOrigin contains no credentials.
21. Market session metadata is canonicalized.
22. Trade aggressor side is represented only when known.
23. Historical price adjustment semantics are explicit.
24. Provider-default adjustment is not accepted as canonical request semantics.
25. Bar intervals use ATLAS canonical values.
26. Provider-specific interval strings remain inside adapters.
27. Stage 33 does not resample bars.
28. Quote contains bid/ask state only.
29. Last trade price is not duplicated inside Quote.
30. Quote must contain at least bid or ask.
31. Quote sizes require their corresponding prices.
32. Crossed quotes remain representable.
33. Trade contains canonical price, size and timestamp.
34. Trade size must be positive.
35. Negative trade price is not globally forbidden.
36. Trade IDs are source-local metadata, not global identity.
37. OHLCVBar has explicit interval and UTC time bounds.
38. OHLCV high/low consistency is validated.
39. Negative prices are not globally forbidden for OHLCV.
40. Missing Market Data must not be represented by fabricated zeros.
41. Technical indicators are not stored in OHLCVBar.
42. OrderBookLevel uses Decimal price and size.
43. Canonical bids are sorted highest-to-lowest.
44. Canonical asks are sorted lowest-to-highest.
45. Duplicate price levels are rejected after normalization.
46. Crossed order books remain representable.
47. MarketSnapshot is a point-in-time aggregate of canonical Market Data fields.
48. MarketSnapshot does not store redundant change/change-percent fields.
49. Nested Snapshot Quote/Trade identity must match the Snapshot instrument.
50. Stage 33 defines MarketDataOperation.
51. Initial operations are quote, historical_bars, trades, order_book and snapshot.
52. ProviderDomain.MARKET_DATA does not imply support for all MarketDataOperations.
53. MarketDataProviderCapabilities declares fine-grained supported operations.
54. Empty Market Data operation support is valid.
55. OpenBB does not automatically claim canonical Market Data operations merely because it supports the Market Data domain.
56. Stage 33 introduces strongly typed Market Data Provider Protocols.
57. Stage 33 does not create a generic execute(operation, dict) Market Data interface.
58. Market Data requests contain canonical business parameters only.
59. Market Data requests contain no Provider key.
60. Market Data requests contain no fallback configuration.
61. Market Data requests contain no credentials.
62. Market Data requests contain no user ID.
63. Quote requests use canonical instrument IDs.
64. Quote request batches are bounded.
65. Duplicate instrument IDs in a request are rejected.
66. Historical bars requests use explicit interval and adjustment.
67. Historical requests are bounded by time range and/or limit.
68. Order Book requests use bounded depth.
69. Typed responses always carry MarketDataOrigin.
70. Historical bars responses are chronologically ordered.
71. Duplicate bars in one canonical response are rejected.
72. Trades are chronologically ordered.
73. Stage 33 does not use dict[str, Any] for canonical Market Data payloads.
74. Stage 33 does not use DataFrame as a canonical API contract.
75. Stage 33 does not use Polars DataFrame as a canonical API contract.
76. Stage 33 does not expose OpenBB types in canonical models.
77. Stage 33 performs no Market Data network request.
78. Stage 33 introduces no public Market Data REST API.
79. Stage 33 introduces no application Market Data Capability Gateway operations.
80. Stage 33 introduces no PostgreSQL Market Data tables.
81. Stage 33 requires no Alembic migration.
82. Stage 37 remains responsible for ClickHouse deployment.
83. Stage 39 remains responsible for historical Market Data ingestion.
84. Stage 40 remains responsible for Market Data update workers.
85. Stage 41 remains responsible for live quote ingestion.
86. Stage 43 remains responsible for frontend WebSocket infrastructure.
87. Stage 44 remains responsible for Market Data freshness monitoring.
88. Stage 66 remains responsible for Charts V1.
89. Stage 69-70 remain responsible for technical indicators.
90. Stage 76 remains responsible for Watchlists V1.
91. Stage 94 remains responsible for Screeners V1.
92. Canonical model validation performs no database queries.
93. Canonical model validation performs no external network calls.
94. Entity existence validation belongs outside Pydantic record validation.
95. Provider selection belongs outside Market Data request models.
96. Provider routing belongs outside canonical Market Data models.
97. Provider Health belongs outside canonical Market Data models.
98. Provider credentials belong outside canonical Market Data models.
99. Stage 33 creates no fake production Provider.
100. Stage 34 remains responsible for canonical Fundamental Data models.
101. Canonical Fundamental Data models do not import database connections or perform network requests.
102. Canonical Fundamental Data models enforce precise canonical types (CanonicalDecimal) for value accuracy.
103. Stage 34 creates no calculated metrics or valuation ratios.
104. Stage 35 remains responsible for Economic models.
105. **ATLAS Owns Economic Schema**: ATLAS owns canonical Economic Data models.
106. **No Provider Leaks**: Provider-specific Economic objects must not leak above Provider adapters.
107. **Stage 20 Authoritative**: Stage 20 Economic Series remains the canonical series identity/metadata layer.
108. **No Replacement**: Stage 35 does not replace the Stage 20 Economic Series entity.
109. **Canonical References**: Economic Observations reference Stage 20 Economic Series UUIDs.
110. **External IDs**: FRED, World Bank, OECD, IMF codes are not canonical Economic Series identity. They remain Stage 21 identifiers.
111. **Decimal Precision**: Economic Observation values use Decimal. Binary float is not canonical.
112. **Finite Values**: Non-finite Decimal values are rejected.
113. **No Global Rounding**: Stage 35 does not globally round Economic Data.
114. **Valid Values**: Negative and zero Economic Observation values are valid and representable.
115. **Missing is Distinct**: Missing data is explicitly distinct from zero. Missing Provider markers are normalized before canonical model construction.
116. **No Rescaling**: Canonical Economic Data does not automatically rescale percentage values.
117. **Metadata Semantics**: Stage 20 series metadata defines value semantics (frequency, seasonal adjustment, value representation).
118. **Reference Date Required**: Economic Observation Period contains a required reference date. Precise period start/end boundaries are optional and never fabricated.
119. **Boundary Rules**: Period start and end are both present or both absent.
120. **Availability Status**: Economic Observation Availability explicitly distinguishes available from missing. Available requires value; missing requires no value.
121. **Revision Status**: Economic Revision Status supports preliminary, revised, final and unknown. Historical observations are not automatically assumed final.
122. **Revision Policies**: Economic Revision Policy supports latest_available, as_of, and all_vintages semantics.
123. **As-Of Rules**: As-of policy requires an as-of date. Provider-specific vintage query parameter names do not leak into canonical requests.
124. **Origin Semantics**: EconomicDataOrigin captures Provider/runtime lineage but does not replace Stage 24 Provenance. Contains no credentials.
125. **Observation Cleanliness**: EconomicObservation contains no Provider series code, duplicated metadata, or derived metrics (YoY, MoM, surprise).
126. **Timestamp Meanings**: released_at, retrieved_at, and vintage_date all have distinct meanings and are not substituted for each other. Stage 35 does not invent vintage dates.
127. **No Analytics**: Stage 35 does not interpolate, forward-fill, resample, rebase, or seasonally adjust data.
128. **Provider Capabilities**: EconomicDataOperation and EconomicProviderCapabilities declare actually implemented canonical operations and revision policies. Empty capabilities are valid.
129. **OpenBB Capabilities**: OpenBB does not automatically claim Economic operations merely because it supports the ECONOMICS Provider family.
130. **Typed Protocols**: Stage 35 introduces typed operation-specific Economic Provider Protocols (no generic execute executor).
131. **Request Hygiene**: Economic requests use canonical Economic Series UUIDs and do not contain Provider series codes, Provider keys, routing configuration, credentials, or user IDs.
132. **Bounded Requests**: Economic observation requests are bounded by date range or limit. Latest Economic Observation requests are batch-bounded. Duplicate Series IDs are rejected.
133. **Response Ordering**: EconomicObservationsResponse is chronological oldest-to-newest. Legitimate vintages are not deduplicated under all_vintages, but exact duplicates are rejected.
134. **No Fabrication**: Missing latest data is representable as None without fabricating observation periods.
135. **Offline Models**: Canonical Economic model validation requires no DB, network, identifier resolution, or Provider calls.
136. **No Live Requests**: Stage 35 performs no external Economic Data request (OpenBB, FRED, World Bank, OECD, IMF).
137. **No UI or APIs**: Stage 35 introduces no public Economic Data REST API, executable Economic Capability, Economic Observation persistence table, or UI/Dashboard.
138. **No Release System**: Stage 35 does not build the Economic Calendar, forecasting models, consensus models, or surprise calculations.

## Stage 36: Canonical News and Research Models

139. **Decoupled Architecture**: Established `atlas.news` and `atlas.research` canonical models (e.g. `NewsArticle`, `ResearchMetadata`) strictly separate from persistent entity models (`NewsEvent`, `ResearchDocument`), but conceptually aligned.
140. **Shared Pattern**: Reused the `DataOrigin` pattern (`NewsDataOrigin`, `ResearchDataOrigin`) for lightweight runtime extraction provenance.
141. **No Backend Persistence**: Stage 36 models are offline, frozen, Pydantic V2 definitions with no database dependency, network fetches, or FastAPI coupling.
142. **No Text Ingestion**: Stage 36 models handle metadata, ignoring binary/blob/full-text ingestion pipelines for Research papers.
143. **Provider Extensibility**: OpenBB adapter extended with `news_capabilities`, `research_capabilities`, and `ProviderDomain.RESEARCH`.

## Stage 37: Deploy ClickHouse

144. **Target Architecture**: ClickHouse is ATLAS's analytical/high-volume datastore. PostgreSQL remains ATLAS's transactional source of truth.
145. **No Replacements**: ClickHouse does not replace PostgreSQL.
146. **Infrastructure Only**: Stage 37 deploys infrastructure only, creating no Market Data, Economic, News, or Research business tables, and performing no data ingestion or PostgreSQL mirroring.
147. **Single Node Deployment**: ClickHouse runs as a single node initially without Keeper, replication, sharding, or distributed tables.
148. **Pinned Version**: ClickHouse server version is explicitly pinned (e.g. `24.3.2.74`). `latest` tags are forbidden.
149. **Storage**: Local ClickHouse data uses a persistent volume.
150. **Application User**: ATLAS uses a dedicated ClickHouse database (`atlas`) and a non-default application database user (`atlas_app`).
151. **Secret Management**: Passwords are not committed to Git, are not empty, and are excluded from logs and representations. They are backend-only; browsers never connect directly.
152. **Networking**: Port `8123` binds to loopback locally. Production environments mandate private networking. TLS is fully supported.
153. **Timezone**: Server and session timezone default to `UTC`.
154. **Security**: Privileged containers are avoided. Default user is restricted. Settings fail validation if misconfigured.
155. **Client Configuration**: ClickHouse integration uses `clickhouse-connect`, with lazy, lifecycle-managed clients separate from import-time execution.
156. **Health Boundary**: Infrastructure health uses a read-only lightweight ping (`SELECT 1`). It is disconnected from Provider Health tables and Provider routing.
157. **No Arbitrary SQL**: Stage 37 exposes no arbitrary SQL capabilities, no Terminal mode, and no Agent/MCP tools for ClickHouse.
158. **Migration Foundation**: Stage 37 outlines a separate directory convention for future ClickHouse schemas, keeping Alembic strictly for PostgreSQL.

## Stage 38: Deploy Redis / Valkey

159. **Target Architecture**: ATLAS uses one Redis-compatible infrastructure server (`valkey` preferred, `redis` acceptable) for ALL ephemeral state across the monorepo to avoid sprawling cache silos.
160. **PostgreSQL Authoritative**: PostgreSQL remains the authoritative transactional source of truth (Stage 11). Redis / Valkey is strictly non-authoritative.
161. **ClickHouse Analytical**: ClickHouse remains the analytical/high-volume datastore (Stage 37).
162. **Infrastructure Only**: Stage 38 deploys infrastructure only. It creates no production cache, session state, lock, or pub/sub capabilities yet.
163. **Namespace**: All Redis / Valkey keys must be namespaced using a defined prefix (e.g., `atlas:dev:`).
164. **Logical Database**: ATLAS restricts application usage to a single logical database (DB 0).
165. **No Pickle**: `pickle` deserialization is strictly forbidden due to arbitrary code execution risks.
166. **ACL Required**: The Redis / Valkey application user MUST have an explicit ACL.
167. **Security Disabled**: Security-sensitive and dangerous commands (CONFIG, FLUSHALL, MODULE, SHUTDOWN, DEBUG) MUST be explicitly disabled.

## Stage 39: Build Historical Market Data Ingestion

168. **Architecture Validation**: Stage 39 strictly implements the architecture designed in Stage 33 Market Data. Canonical representations are used for storage.
169. **Provider Isolation**: Provider-specific response objects NEVER hit ClickHouse. The path is Provider -> Canonical Model -> Storage Mapper -> ClickHouse.
170. **Versioning & Idempotency**: ClickHouse uses `ReplacingMergeTree` for canonical Historical Bars to ensure idempotency and logically deduplicate identical fetches.
171. **No Resampling**: The ingestion service strictly persists the interval fetched; it does not fabricate, interpolate, or resample Market Data.
172. **Operational Metadata**: PostgreSQL stores metadata about each historical data ingestion run (`historical_market_data_ingestion_runs`) to track execution, bars ingested, and provider routing details.
173. **Range Planning**: The `RangePlanner` uses the PostgreSQL run metadata to identify previously fetched data limits and avoid redundant external calls.
174. **No Scheduler**: Stage 39 is manually or internally triggerable via CLI or synchronous APIs. It is not an autonomous cron job.
175. **No Valkey**: Stage 39 introduces no dependencies on Redis/Valkey for market data ingestion state.

## Stage 42: Build Initial Live Event Pipeline

176. Stage 42 builds ATLAS's initial backend live-event transport.
177. Stage 42 live events are transport events, not Stage 135 Universal Events.
178. Stage 42 initially publishes only \market.quote.updated\.
179. Stage 42 does not build news/economic/intelligence event models.
180. Stage 42 integrates with Stage 41 routed latest Quote state.
181. Stage 42 events are emitted only when routed Quote state accepts a newer Quote.
182. Provider-specific cache updates alone do not necessarily emit a live event.
183. Older routed Quote candidates do not emit events.
184. Identical duplicate Quotes do not emit new events by default.
185. Newer fallback Provider Quotes may emit events.
186. Fallback Provider origin remains preserved.
187. Stage 42 reuses Stage 41 Quote ordering semantics.
188. Stage 42 does not create a second Quote ordering algorithm.
189. Routed-state transition and event append are atomic.
190. Independent routed SET followed by XADD is forbidden.
191. Stage 42 reuses Stage 41's Lua or WATCH/MULTI/EXEC concurrency strategy where possible.
192. User-controlled Lua is forbidden.
193. Stage 42 event transport uses Redis-compatible Streams.
194. Stage 42 does not use Redis Pub/Sub.
195. Stage 42 does not use Redis consumer groups.
196. Stage 42 uses cursor-based XREAD.
197. Stage 42 does not use Kafka, Redpanda, RabbitMQ, or NATS.
198. Stage 42 does not deploy a new broker service or event daemon.
199. Stage 42 uses the Stage 38 Redis / Valkey instance and client.
200. Stage 42 live event Stream is non-authoritative and may be trimmed or lost.
201. Stream loss does not destroy authoritative ATLAS state.
202. Stage 42 does not archive events in ClickHouse or PostgreSQL.
203. Stage 42 creates a schema-versioned event envelope with UUIDs.
204. Event ID is distinct from Redis Stream ID.
205. \emitted_at\ is ATLAS transport time, not Provider market time.
206. Event payload preserves true Provider origin without credentials or user IDs.
207. Generic \dict[str, Any]\ is not the canonical event payload.
208. JSON is the initial safe transport encoding.
209. Decimal values do not become binary floats. NaN and Infinity are rejected.
210. Event payload size is bounded; oversized events are rejected.
211. Stage 42 uses one initial Market live-event Stream with the Stage 38 environment key prefix.
212. Stream retention is bounded by maximum entry count with approximate MAXLEN.
213. Stage 42 uses explicit Redis Stream cursors parsed numerically.
214. Stage 42 provides bounded event reads and bounded blocking reads without exposing infinite BLOCK 0.
215. Stage 42 provides at-least-once-friendly replay semantics.
216. Stage 42 supports future snapshot-plus-cursor synchronization for Stage 43.
217. Stage 42 adds only the Redis Stream ACL permissions actually required (XADD, XREAD, XINFO).

## Stage 45 Decisions - Global Search

1. Stage 45 builds Global Search for ATLAS.
2. Stage 45 searches ATLAS Universal Entity metadata only.
3. Stage 45 does not search the public web.
4. Stage 45 does not call OpenBB.
5. Stage 45 does not call Provider APIs.
6. Stage 45 does not query ClickHouse.
7. Stage 45 does not use Redis as a search engine or cache.
8. Stage 45 does not deploy Elasticsearch.
9. Stage 45 does not deploy OpenSearch.
10. Stage 45 does not deploy Meilisearch.
11. Stage 45 does not deploy Typesense.
12. Stage 45 does not deploy Algolia.
13. Stage 45 does not use embeddings.
14. Stage 45 does not use pgvector search.
15. Stage 45 does not use LLM reranking.
16. PostgreSQL is the initial Global Search engine.
17. `pg_trgm` is used for fuzzy name/alias search.
18. Stage 45 searches canonical names.
19. Stage 45 searches display names.
20. Stage 45 searches current aliases.
21. Stage 45 searches current supported identifiers.
22. Entity UUID (`entity_id`) remains canonical Search identity.
23. Ticker is not canonical Search identity.
24. Company name is not canonical Search identity.
25. Provider ID is not canonical Search identity.
26. Searching a ticker returns Security/Instrument identity.
27. Search does not automatically convert Security into issuer Company.
28. Searching a Company name returns the Company Entity.
29. Ambiguous tickers return multiple Securities.
30. Identifier scope is preserved where relevant.
31. Stage 45 reuses Stage 22 Entity text normalization.
32. Stage 45 reuses Stage 21 identifier normalization.
33. Stage 45 does not create a second normalization system.
34. Stage 45 preserves meaningful punctuation.
35. Stage 45 supports exact matching.
36. Stage 45 supports prefix matching.
37. Stage 45 supports fuzzy matching for names/aliases.
38. Stage 45 does not fuzzy-match identifiers.
39. Very short queries (<3 chars) do not use trigram fuzzy matching.
40. One-character queries remain bounded and support valid short tickers.
41. SQL LIKE wildcards are escaped.
42. Search SQL is parameterized.
43. Stage 45 does not expose raw SQL controls.
44. Stage 45 does not expose user-defined sort expressions.
45. Stage 45 result count is bounded (default 20, max 50).
46. Stage 45 search query length is bounded (max 256 characters).
47. Stage 45 does not create unbounded pagination.
48. Stage 45 returns ranked candidate Entities.
49. Stage 22 Resolution remains separate from Global Search.
50. Global Search does not replace EntityResolutionService.
51. Search result ranking is deterministic.
52. Search ranking does not use fake confidence percentages.
53. Trigram similarity is an internal ranking signal, not confidence.
54. One Entity appears once using its best match.
55. Current aliases/identifiers are searched by default.
56. Historical aliases/identifiers are excluded by default.
57. Stage 45 does not personalize ranking.
58. Stage 45 does not boost Portfolio holdings.
59. Stage 45 does not boost Watchlist membership.
60. Stage 45 does not boost search popularity.
61. Stage 45 does not rank by market cap.
62. Stage 45 does not rank by volume.
63. Stage 45 does not rank using an LLM.
64. Search result payloads remain lightweight.
65. Search does not fetch all identifiers.
66. Search does not fetch all aliases.
67. Search does not fetch Relationships.
68. Search does not fetch Provenance.
69. Stage 45 does not search research-paper full text.
70. Stage 45 does not search PDF content.
71. Stage 45 does not search News article bodies.
72. Stage 45 does not search financial statement rows.
73. Stage 45 does not traverse Relationship Graph.
74. Stage 45 does not implement semantic search.
75. Stage 45 does not implement advanced query syntax.
76. Stage 45 does not implement Boolean search.
77. Stage 45 does not implement regex search.
78. Stage 45 does not implement wildcard query language.
79. Stage 45 does not implement module navigation search.
80. Stage 46 remains responsible for Command Palette.
81. Stage 47 remains responsible for command parsing.
82. Stage 48 remains responsible for natural-language command interpretation.
83. Search route requires authentication.
84. Search route requires `atlas.access`.
85. Global Search stores no search history by default.
86. Global Search stores no recent searches by default.
87. Global Search does not store raw queries in Redis.
88. Global Search does not store raw queries in PostgreSQL.
89. Raw search queries are not logged at INFO.
90. Search queries are treated as potentially private text.
91. Search UI uses the existing top-bar search location.
92. Stage 45 does not create a second global search surface.
93. Search UI is dense and consistent with ATLAS.
94. Search UI does not add fake metrics.
95. Search UI does not add AI decoration.
96. Search UI uses debounced requests (200ms).
97. Search UI cancels/ignores stale requests via AbortController.
98. Old HTTP responses cannot replace newer query results.
99. Search results are keyboard accessible.
100. Search uses combobox/listbox accessibility semantics.
101. Search result selection updates Stage 25 Selected Entity context.
102. Search selection stores only Entity UUID as global authoritative selection.
103. Search selection does not automatically navigate.
104. Search query is not put into Stage 26 Global Application Context.
105. Search query is not persisted in localStorage.
106. Search results are not persisted in localStorage.
107. Stage 45 does not create recent-search UI.
108. Stage 45 does not create user search preferences.
109. Stage 45 does not expose Provider external IDs by default.
110. Stage 45 does not generate backend HTML highlights.
111. Search highlighting uses safe text rendering.
112. `dangerouslySetInnerHTML` is not required.
113. Search uses existing database pool.
114. Stage 45 does not deploy a Search microservice.
115. Stage 45 does not deploy a background Search indexing worker.
116. Stage 45 does not deploy Kafka/Redpanda indexing.
117. Stage 45 does not create CDC indexing.
118. Stage 45 does not create a denormalized Search table by default.
119. Stage 45 adds only required PostgreSQL indexes/extensions.
120. Stage 46 remains the next stage.

## Stage 46 Decisions - Command Palette

1. Stage 46 builds the ATLAS Command Palette.
2. Stage 46 does not build the ATLAS command parser (Stage 47).
3. Stage 46 does not build natural-language command interpretation (Stage 48).
4. Stage 45 remains responsible for Entity Search.
5. Stage 46 commands are explicitly registered.
6. Stage 46 does not dynamically generate commands from arbitrary user text.
7. Stage 46 uses stable machine-readable command IDs.
8. Command IDs are not user command syntax.
9. Stage 46 initially focuses on safe frontend navigation and shell actions.
10. The exact 20 ATLAS module routes receive navigation commands.
11. Global Settings remains outside the 20 numbered modules.
12. Command Palette may open Global Search via "Search Entities" command.
13. Entity Search results are not converted into Command definitions.
14. Stage 46 does not create Entity-specific commands.
15. Stage 46 does not create trade commands.
16. Stage 46 does not create portfolio-analysis commands.
17. Stage 46 does not create Agent execution commands.
18. Stage 46 does not create Workflow commands.
19. Stage 46 does not create Terminal commands.
20. Stage 46 does not call Providers.
21. Stage 46 does not call OpenBB.
22. Stage 46 does not call the public web.
23. Stage 46 does not call an LLM (0 LLM calls).
24. Stage 46 does not use embeddings.
25. Stage 46 does not use vector search.
26. Stage 46 command filtering is local to the browser.
27. Stage 46 requires no PostgreSQL Search.
28. Stage 46 requires no Redis Search.
29. Stage 46 requires no ClickHouse.
30. Stage 46 uses a central typed Command Registry.
31. Command definitions are version-controlled application code.
32. Stage 46 does not create a Command database table.
33. Stage 46 does not create a Redis Command Registry.
34. Stage 46 does not load commands from a remote server.
35. Stage 46 does not allow user-created command code.
36. Stage 46 does not install plugin commands.
37. Stage 46 does not allow Agent-created commands.
38. Stage 46 command IDs must be unique.
39. Stage 46 commands use existing module metadata from Stage 4.
40. Stage 46 does not duplicate module route metadata.
41. Command availability is context-aware but fast and side-effect-free.
42. Command availability does not call databases.
43. Command availability does not call Providers.
44. Stage 46 respects existing module authorization.
45. Forbidden modules are hidden and not exposed through the palette.
46. Palette execution does not bypass route guards.
47. Command execution delegates to existing ATLAS actions.
48. The Command Executor does not become a second business-logic layer.
49. Stage 46 does not use eval.
50. Stage 46 does not use exec.
51. Stage 46 does not dynamically import code from user query.
52. Stage 46 does not execute shell commands.
53. Stage 46 does not navigate to arbitrary user-entered URLs.
54. Stage 46 command filtering is deterministic.
55. Stage 46 does not use AI ranking.
56. Stage 46 does not use personalized ranking.
57. Stage 46 does not record command usage history.
58. Stage 46 does not implement Recent Commands.
59. Stage 46 does not implement Favorite Commands.
60. Stage 46 does not show fake confidence percentages.
61. Stage 46 uses labels, aliases, keywords and descriptions for filtering.
62. Stage 46 aliases are palette metadata, not Stage 47 syntax.
63. Stage 46 does not implement Bloomberg shorthand.
64. Stage 46 does not parse slash commands.
65. Stage 46 does not parse `NVDA CHART`.
66. Stage 46 does not parse `PORT RISK`.
67. Stage 46 does not interpret natural language.
68. Matching a text query to a registered command is not command parsing.
69. User must explicitly select/execute a command.
70. Stage 46 does not auto-run the best result.
71. Cmd/Ctrl+K is the primary global shortcut.
72. Shortcut handling respects text-editing contexts.
73. Stage 46 uses the persistent authenticated AppShell.
74. Stage 46 does not create a second unrelated global search shell.
75. Global Search remains usable after Stage 46.
76. Command Palette state is ephemeral frontend state.
77. Palette query is not placed in Global Application Context.
78. Palette query is not stored in localStorage.
79. Palette query is not stored in the URL.
80. Palette query is not persisted in PostgreSQL.
81. Palette query is not persisted in Redis.
82. Raw palette query is not logged at INFO.
83. Stage 46 does not create command-history analytics.
84. Palette is keyboard accessible.
85. Palette restores focus after closing where practical.
86. Palette uses existing ATLAS design tokens.
87. Palette does not use purple gradients.
88. Palette does not use emoji UI icons.
89. Palette does not use heavy animation.
90. Palette does not use fake AI decoration.
91. Navigation uses internal router behavior (`router.push`).
92. Navigation does not force full-page reload.
93. Navigation does not clear Selected Entity.
94. `Clear Selected Entity` delegates to Stage 25 context.
95. `Search Entities` delegates to Stage 45 Global Search.
96. Stage 46 does not create a second Entity Search implementation.
97. Stage 46 requires no new backend API.
98. Stage 46 requires no PostgreSQL migration.
99. Stage 46 requires no Redis schema/business state.
100. Stage 46 requires no ClickHouse change.
101. Stage 46 adds 0 new npm packages.
102. Existing design system primitives are reused.
103. Stage 46 does not require `cmdk`.
104. Stage 46 does not create backend command Capabilities for simple frontend navigation.
105. Stage 46 does not modify Market Data systems.
106. Stage 46 does not modify Provider systems.
107. Stage 46 does not modify realtime Quote transport.
108. Stage 46 does not modify freshness monitoring.
109. Stage 47 remains responsible for ATLAS command parsing.
110. Stage 48 remains responsible for natural-language command interpretation.

## Stage 47 — Build ATLAS Command Parsing

1. Stage 47 builds ATLAS structured command parsing.
2. Stage 47 does not build natural-language interpretation.
3. Stage 48 remains responsible for natural-language commands.
4. ATLAS Command Language v1 is explicitly versioned (`command_language_version = 1`).
5. Stage 47 parsing is deterministic.
6. Stage 47 performs no LLM calls.
7. Stage 47 performs no embeddings.
8. Stage 47 performs no vector search.
9. Stage 47 performs no machine-learning intent classification.
10. Command processing is separated into lexing, parsing, binding, resolution and validation.
11. Lexer is side-effect free.
12. Syntactic parser is side-effect free.
13. Parser does not execute commands.
14. Parse API is read-only despite using POST.
15. Stage 47 reuses Stage 22 Entity Resolution.
16. Stage 47 does not create another Entity resolver.
17. Command target resolution is exact/deterministic.
18. Stage 47 does not fuzzy-correct target entities.
19. Global Search remains the fuzzy discovery mechanism.
20. Ticker resolves Security/Financial Instrument identity.
21. Ticker does not silently become Company.
22. Company-requiring commands reject Security targets unless explicitly supported later.
23. Ambiguous ticker targets are not guessed.
24. Ambiguous targets return bounded candidate summaries.
25. Historical identifiers/aliases are excluded by default.
26. Provider external IDs are excluded from normal commands.
27. Stage 47 supports slash command syntax.
28. Stage 47 supports curated Bloomberg-style shorthand.
29. Module names and aliases are explicit.
30. Action aliases are explicit.
31. Alias resolution is exact, not fuzzy.
32. Stage 47 supports quoted targets.
33. Stage 47 does not implement shell quoting semantics beyond its own limited grammar.
34. Stage 47 supports bounded long-form parameters.
35. Unknown parameters are rejected.
36. Duplicate parameters are rejected by default.
37. Stage 47 does not implement shell pipes.
38. Stage 47 does not implement redirection.
39. Stage 47 does not implement command chaining.
40. Stage 47 does not implement subshells.
41. Stage 47 does not implement environment expansion.
42. Stage 47 does not implement filesystem globbing.
43. Stage 47 does not execute shell commands.
44. Stage 47 does not use eval.
45. Stage 47 does not use exec.
46. Stage 47 does not dynamically import from user input.
47. Stage 47 does not generate SQL from command text.
48. Command input length is bounded (512 chars).
49. Token count is bounded (32 tokens).
50. Token length is bounded (256 chars).
51. Parameter count is bounded (16 parameters).
52. Stage 47 recognizes the canonical 20 modules.
53. Settings remains outside the 20 modules.
54. Stage 47 may map `/settings` to the existing Global Settings command.
55. Stage 47 may map `/search` to Stage 45 Global Search.
56. Stage 47 may map `/clear entity` to Stage 25 Selected Entity clearing.
57. Stage 47 entity-context commands use explicit typed Command IDs.
58. Stage 47 extends Stage 46 executor rather than creating a second executor.
59. Command execution uses typed arguments.
60. Raw command text is never executed.
61. AST is never directly executed.
62. User must explicitly execute READY parsed command.
63. Structured command text does not autoexecute.
64. Stage 47 may explicitly perform select-Entity + navigation.
65. Search selection continues to select Entity without navigation.
66. Command execution respects module authorization.
67. Command execution does not bypass route guards.
68. Forbidden module commands do not become READY.
69. `/markets` can map to Stage 46 Markets navigation.
70. `/charts NVDA` can map to selected Entity + Charts navigation.
71. `NVDA CHART` is recognized as deterministic shorthand.
72. `NVDA NEWS` is recognized as deterministic shorthand.
73. `NVDA RESEARCH` is recognized as deterministic shorthand.
74. `MAP TSMC` is recognized as deterministic shorthand.
75. `OPTIONS NVDA` may be recognized as deterministic shorthand.
76. Shorthand does not imply backend module functionality beyond navigation/context.
77. Stage 47 does not build Charts.
78. Stage 47 does not build News.
79. Stage 47 does not build Research.
80. Stage 47 does not build Maps.
81. Stage 47 does not build Options chains.
82. `NVDA FA` may be recognized as reserved/unavailable.
83. `PORT RISK` may be recognized as reserved/unavailable.
84. Stage 47 does not fake Fundamental Analysis.
85. Stage 47 does not fake Portfolio Risk.
86. Stage 47 does not implement BUY commands.
87. Stage 47 does not implement SELL commands.
88. Stage 47 does not call a broker.
89. Stage 47 does not create Trading actions.
90. Stage 47 uses stable machine-readable parse statuses.
91. READY means executable after validation.
92. AMBIGUOUS never autoexecutes.
93. INVALID never autoexecutes.
94. UNAVAILABLE never autoexecutes.
95. Stage 47 returns stable parser error codes.
96. Stage 47 parse endpoint requires authentication.
97. Stage 47 parse endpoint requires `atlas.access`.
98. Stage 47 parsing writes no PostgreSQL data.
99. Stage 47 parsing writes no Redis data.
100. Stage 47 parsing queries no ClickHouse.
101. Stage 47 parsing calls no Provider.
102. Stage 47 parsing calls no OpenBB.
103. Stage 47 parsing calls no external web service.
104. Stage 47 stores no command history.
105. Stage 47 stores no recent commands.
106. Stage 47 does not persist raw command text.
107. Raw command text is not logged at INFO.
108. Stage 46 local command matching remains available.
109. Stage 47 parser is not called for every arbitrary palette query.
110. Explicit slash syntax triggers structured parsing.
111. Recognized shorthand signatures may trigger structured parsing.
112. Natural-language text does not trigger Stage 48 behavior.
113. Parsed commands appear as preview before execution.
114. User must explicitly activate command preview.
115. Backend Command IDs must match frontend executor Command IDs.
116. Unknown backend Command IDs are rejected by frontend.
117. Typed command arguments are runtime-validated.
118. Stage 47 does not create a command database table.
119. Stage 47 does not create a Redis command registry.
120. Stage 47 does not create a command execution history table.
121. Stage 47 does not create a server-side parse session.
122. Stage 47 does not create a generic backend execute endpoint by default.
123. Stage 47 does not expose parser as an AI tool.
124. Stage 47 does not expose parser as an Agent tool.
125. Stage 47 does not expose parser as an MCP tool.
126. Stage 47 does not integrate with Terminal.
127. Stage 47 adds no PostgreSQL migration.
128. Stage 47 adds no ClickHouse schema.
129. Stage 47 adds no Redis business state.
130. Stage 48 remains the next stage.

---

## Stage 48 Decisions

1. Stage 48 builds natural-language command interpretation.
2. Stage 48 does not build the full AI Assistant.
3. Stage 48 is single-turn.
4. Stage 48 stores no chat history.
5. Stage 48 stores no command interpretation history.
6. Stage 48 uses Stage 47 as the deterministic command authority.
7. Natural-language model output is not executable by itself.
8. The model does not produce authoritative Entity IDs.
9. The model does not produce authoritative routes.
10. The model does not produce authoritative permissions.
11. The model does not directly execute Command IDs.
12. The model emits only a narrow structured intent enum.
13. Stage 48 compiles intent into Stage 47 syntax.
14. Compiled commands must successfully pass Stage 47 parsing/binding.
15. Stage 22 remains Entity identity authority.
16. Stage 14 remains authorization authority.
17. Stage 46 remains execution boundary.
18. Stage 48 does not bypass Stage 47.
19. Stage 48 does not bypass Stage 46.
20. Stage 48 does not bypass route guards.
21. Stage 48 does not infer Entity UUIDs from model knowledge.
22. Stage 48 does not infer tickers from Company names.
23. Stage 48 does not automatically convert Company to Security.
24. Stage 48 does not automatically convert Security to Company.
25. Stage 48 does not traverse issuer relationships implicitly.
26. Stage 48 does not fuzzy-correct Entity targets.
27. Stage 45 remains fuzzy Entity discovery.
28. Natural-language interpretation is conservative.
29. Informational questions return NOT_COMMAND.
30. Unsupported actions return UNSUPPORTED.
31. Ambiguous requests do not execute.
32. Stage 48 executes at most one command per interpretation.
33. Stage 48 does not implement command chaining.
34. Stage 48 does not implement multi-step planning.
35. Stage 48 does not implement autonomous planning.
36. Stage 48 does not implement tools.
37. Stage 48 gives the model zero tools.
38. Stage 48 does not use web search.
39. Stage 48 does not use OpenBB.
40. Stage 48 does not call Market Data Providers.
41. Stage 48 does not use RAG.
42. Stage 48 does not use embeddings.
43. Stage 48 does not use pgvector.
44. Stage 48 does not use Qdrant.
45. Stage 48 does not use Agent infrastructure.
46. Stage 48 does not use Workflow infrastructure.
47. Stage 48 does not use Terminal infrastructure.
48. Stage 48 does not execute Python.
49. Stage 48 does not execute shell commands.
50. Stage 48 does not execute JavaScript.
51. Stage 48 does not navigate arbitrary URLs.
52. Stage 48 does not perform trading actions.
53. Stage 48 does not execute BUY.
54. Stage 48 does not execute SELL.
55. Stage 48 does not call brokers.
56. Stage 48 does not optimize portfolios.
57. Stage 48 does not calculate portfolio risk.
58. Stage 48 does not run Agents.
59. Stage 48 does not run Workflows.
60. Stage 48 does not send external messages.
61. Model API credentials remain server-side.
62. Browser never calls the interpretation model directly.
63. Model endpoint is server-configured.
64. User cannot provide model endpoint URL.
65. User cannot provide model credentials.
66. Interpretation model calls are bounded.
67. Input length is bounded.
68. Output size is bounded.
69. One interpretation normally makes at most one model call.
70. Stage 48 does not use a model self-repair loop.
71. Stage 48 does not use a reasoning loop.
72. Stage 48 does not use unbounded retries.
73. Tool calling is disabled.
74. Model structured output is strictly validated.
75. Unknown model intent values are rejected.
76. Unknown module values are rejected.
77. Extra output fields are rejected.
78. Invalid model JSON fails closed.
79. Raw model output is not sent to frontend.
80. Raw model prompt is not sent to frontend.
81. Raw user text is not logged at INFO.
82. Raw model output is not logged at INFO.
83. Model API keys are never logged.
84. No prompt archive is created.
85. No model response archive is created.
86. No interpretation database table is created.
87. No interpretation Redis history is created.
88. Stage 48 adds no PostgreSQL migration.
89. Stage 48 adds no ClickHouse schema.
90. Stage 48 adds no Redis business state.
91. Stage 48 creates no interpretation cache by default.
92. Stage 46 local command matching remains model-free.
93. Stage 47 slash commands remain model-free.
94. Stage 47 shorthand remains model-free.
95. The model is called only after explicit natural-language interpretation request.
96. Opening Command Palette does not call the model.
97. Typing does not automatically call the model.
98. Stage 48 does not make one model request per keystroke.
99. READY interpretation still requires explicit user execution.
100. Model response never autoexecutes.
101. Stale interpretation results cannot execute after text changes.
102. Natural-language interpretation failure does not break local Command Palette commands.
103. Natural-language interpretation failure does not break structured commands.
104. Entity ambiguity remains resolved through deterministic Stage 47 flow.
105. The model does not rank ambiguous Entity candidates.
106. The model does not choose an Exchange for the user.
107. Stage 48 does not store Recent Commands.
108. Stage 48 does not create Favorite Commands.
109. Stage 48 does not create personalized command ranking.
110. Stage 48 does not create command usage history.
111. Stage 48 introduces only minimal command-specific model infrastructure.
112. Stage 48 does not build a general model marketplace.
113. Stage 48 does not build multi-model routing.
114. Stage 48 does not build model fallback chains.
115. Stage 48 does not build AI memory.
116. Stage 48 does not build AI tool orchestration.
117. Stage 48 does not build AI streaming.
118. Stage 48 does not build AI RAG.
119. Stage 124 remains responsible for ATLAS AI Assistant V1.
120. Stage 49 remains the next stage.

---

## Stage 49 - Build Persistent Notification Center

1. Stage 49 builds the Persistent Notification Center.
2. PostgreSQL is the durable Notification source of truth.
3. Notifications are user-scoped.
4. Every Notification belongs to one authenticated recipient.
5. Public Notification APIs never accept recipient user ID as ownership authority.
6. Notification IDs are UUIDs.
7. Notification content is plain text.
8. Stage 49 does not support executable HTML Notification bodies.
9. Stage 49 does not require Markdown rendering.
10. Notification title length is bounded (160 characters).
11. Notification message length is bounded (2000 characters).
12. Notifications have typed category metadata (`general`, `system`, `security`, `data`, `market`, `research`, `account`).
13. Notifications have typed severity metadata (`info`, `success`, `warning`, `error`).
14. Stage 49 does not create fake urgency/confidence scores.
15. Notifications record a producer key (`[a-z][a-z0-9._-]{0,127}`).
16. Notification producer key is not user-editable.
17. Notifications may include an optional producer dedupe key.
18. Dedupe uniqueness is scoped to recipient + producer + dedupe key.
19. Dedupe retries do not create duplicate rows.
20. Dedupe payload conflicts fail safely (`NotificationDedupeConflictError`).
21. Notification content is append-oriented after creation.
22. User state is represented through read/archive timestamps.
23. UNREAD means `read_at IS NULL AND archived_at IS NULL`.
24. READ means `read_at IS NOT NULL AND archived_at IS NULL`.
25. ARCHIVED means `archived_at IS NOT NULL`.
26. Archiving an unread Notification marks it read (`read_at = now, archived_at = now`).
27. Stage 49 does not hard-delete Notifications through user API.
28. Stage 49 does not implement archive restoration.
29. Stage 49 does not implement retention cleanup.
30. Stage 49 does not implement Notification expiration.
31. Notification actions are optional.
32. Notification actions may navigate only to safe internal ATLAS routes.
33. Stage 49 does not allow external Notification URLs.
34. Stage 49 does not allow `javascript:` Notification actions.
35. Stage 49 does not allow Notification actions to execute commands.
36. Stage 49 does not allow Notification actions to execute trades.
37. Stage 49 does not allow Notification actions to execute Agents.
38. Stage 49 does not allow Notification actions to execute Workflows.
39. ENTITY_ROUTE may select an existing Entity and navigate internally.
40. Notification Entity IDs must reference real Universal Entities.
41. Entity/module authorization remains enforced when following Notification actions.
42. Stage 49 introduces a `NotificationService`.
43. Stage 49 introduces a `NotificationRepository`.
44. `NotificationService` can be called by future backend subsystems.
45. Notification creation is not exposed as a normal public user API.
46. Stage 49 does not create an admin broadcast API.
47. Stage 49 does not create bulk Notification fanout.
48. Stage 49 APIs require authentication.
49. Stage 49 APIs require `atlas.access`.
50. Notification list/mutations are recipient-scoped.
51. Cross-user Notification IDs do not reveal another user's data (return HTTP 404).
52. Notification list uses deterministic keyset pagination.
53. Notification list is bounded (default 25, max 100).
54. Unread count has a dedicated lightweight endpoint.
55. Mark-read is idempotent.
56. Mark-unread is supported for non-archived Notifications.
57. Mark-all-read affects only the current authenticated user's non-archived unread rows.
58. Archive is idempotent.
59. Stage 49 adds a top-bar Notification Center.
60. Stage 49 reuses the existing AppShell.
61. Stage 49 does not create a separate Notifications page by default.
62. Stage 49 displays a real unread badge.
63. Stage 49 does not display fake Notification counts.
64. Stage 49 uses existing ATLAS design-system icons (`lucide-react`).
65. Stage 49 does not use emoji UI icons.
66. Stage 49 does not use pill-heavy styling.
67. Notification unread state is not communicated by color alone.
68. Notification rows are keyboard accessible.
69. Notification message content is rendered as text.
70. Stage 49 does not require `dangerouslySetInnerHTML`.
71. Notification list is paginated.
72. Stage 49 does not load the entire Notification history at once.
73. Frontend Notification state uses dedicated context/hook data layer.
74. Notification content is not persisted to `localStorage`.
75. Notification content is not persisted to `sessionStorage`.
76. Notification query caches are cleared when authenticated principal changes.
77. Stage 49 uses bounded unread-count polling (30 seconds).
78. Stage 49 does not poll the full Notification list continuously while closed.
79. Notification Center refetches when opened.
80. Unread count refetches on window focus.
81. Stage 49 does not create a Notification WebSocket protocol.
82. Stage 49 does not modify the Stage 42 Market Event Stream.
83. Stage 49 does not use Redis Pub/Sub.
84. Stage 49 does not create a Redis Notification Stream.
85. Stage 49 does not require Redis for Notification persistence.
86. Stage 49 adds no ClickHouse Notification storage.
87. Stage 49 does not create browser push notifications.
88. Stage 49 does not request browser Notification API permission.
89. Stage 49 does not send email.
90. Stage 49 does not send SMS.
91. Stage 49 does not send Telegram messages.
92. Stage 49 does not send WhatsApp messages.
93. Stage 49 does not send mobile push.
94. Stage 49 does not play Notification sounds.
95. Stage 49 does not toast every Notification.
96. Stage 49 does not create user Notification-preference settings.
97. Stage 49 does not create quiet hours.
98. Stage 49 does not create a Do Not Disturb system.
99. Stage 49 does not build Market alert rules.
100. Stage 49 does not build Watchlist alerts.
101. Stage 49 does not build Portfolio alerts.
102. Stage 49 does not build Risk alerts.
103. Stage 49 does not build Economic release alerts.
104. Stage 49 does not build News alerts.
105. Stage 49 does not build Agent alerts.
106. Stage 49 does not build Workflow alerts.
107. Stage 49 does not build approval actions.
108. Stage 49 does not cause Stage 44 stale Quotes to create Notifications.
109. Stage 49 Notification Center may legitimately be empty until a producer exists.
110. Stage 49 uses optimistic frontend mutations where safe.
111. Optimistic failures roll back.
112. Unread count never becomes negative in client state.
113. Stage 49 does not recursively create Notifications about Notification failures.
114. Notification API responses do not expose dedupe keys.
115. Notification API responses do not expose recipient user IDs unnecessarily.
116. Stage 49 does not expose arbitrary producer internals in the UI.
117. Notification messages are treated as potentially sensitive.
118. Notification titles/messages are not INFO-logged by default.
119. Notification responses use private authenticated cache semantics (`Cache-Control: private, no-store`).
120. Stage 50 remains responsible for the Bottom Taskbar Shell.

## Stage 50: Build Persistent Bottom Taskbar Shell

1. Stage 50 builds the persistent Bottom Taskbar Shell.
2. The taskbar is part of the authenticated AppShell.
3. The taskbar is not the 21st ATLAS module.
4. The canonical 20-module navigation remains unchanged.
5. The taskbar persists across client-side module navigation.
6. Stage 50 uses the existing shell/layout architecture.
7. Stage 50 does not introduce another AppShell.
8. Stage 50 does not introduce another state-management framework.
9. Stage 50 uses a typed panel registry.
10. Panel IDs are stable.
11. Panel registration is static/version-controlled.
12. Stage 50 does not support runtime-installed panels.
13. Stage 50 does not support plugin-installed panels.
14. Stage 50 does not support Agent-installed panels.
15. Stage 50 supports one active bottom panel at a time.
16. The taskbar remains visible while the panel is closed.
17. Clicking an inactive item opens that panel.
18. Clicking another item switches content.
19. Clicking the active item may close the panel.
20. Bottom panel state is frontend presentation state.
21. Bottom panel state does not contain domain records.
22. Bottom panel state is independent of selectedEntityId.
23. Stage 50 reuses Stage 6 layout persistence when available.
24. Stage 50 does not introduce duplicate localStorage persistence.
25. Stage 50 introduces no new database schema.
26. Stage 50 introduces no new backend service.
27. Stage 50 introduces no new Redis business keys.
28. Stage 50 introduces no ClickHouse changes.
29. Stage 50 does not modify the Market Event pipeline.
30. Stage 50 does not modify the Market WebSocket protocol.
31. Stage 50 does not create a new message broker.
32. Stage 50 does not create a frontend event bus.
33. Stage 50 uses ATLAS design tokens.
34. Stage 50 does not use purple gradients.
35. Stage 50 does not use emoji icons.
36. Stage 50 does not use fake metrics.
37. Stage 50 does not use fake task records.
38. Stage 50 does not use fake Agent records.
39. Stage 50 does not use fake Job records.
40. Stage 50 does not use fake Alerts.
41. Stage 50 does not use fake Downloads.
42. Stage 50 does not invent System Health values.
43. Unknown is distinct from zero.
44. Reserved is distinct from loading.
45. Loading is distinct from empty.
46. Error is distinct from empty.
47. Tasks panel is initially an integration shell.
48. Stage 50 does not create a Task engine.
49. Stage 50 does not create a Task database.
50. Stage 50 does not create approvals.
51. Agents panel is initially an integration shell.
52. Agents panel is distinct from the persistent right Agent Dock.
53. Stage 50 does not create Agent runtime services.
54. Stage 50 does not execute Agents.
55. Jobs panel is initially an integration shell.
56. Stage 50 does not create a Job queue.
57. Stage 50 does not create a Job scheduler.
58. Stage 50 does not create Job cancellation/retry execution.
59. Alerts panel is initially an integration shell.
60. Alerts are distinct from Stage 49 Notifications.
61. Stage 50 does not duplicate Notification Center.
62. Stage 50 does not create Alert rules.
63. Stage 50 does not create Price alerts.
64. Stage 50 does not create Portfolio alerts.
65. Downloads panel is initially an integration shell.
66. Stage 50 does not create a Download backend.
67. Stage 50 does not intercept browser downloads.
68. System Health panel may reuse existing real read-only health information.
69. System Health must not fabricate healthy state.
70. Stage 50 does not build new infrastructure health monitoring.
71. Terminal is visually distinguished at the trailing edge.
72. Stage 50 Terminal is a launcher/reserved panel only.
73. Stage 50 does not build a Terminal command input.
74. Stage 50 does not install xterm.js.
75. Stage 50 does not execute shell commands.
76. Stage 50 does not execute Python.
77. Stage 50 does not execute SQL.
78. Stage 50 does not create Terminal sessions.
79. Stage 122 remains responsible for Terminal Shell.
80. Stage 123 remains responsible for sandboxed Terminal execution.
81. Panel height is bounded.
82. Panel height respects viewport constraints.
83. Stage 50 reuses existing resize infrastructure.
84. Stage 50 does not create another docking layout engine.
85. Panel resizing does not make backend requests.
86. Panel resizing does not reconnect WebSockets.
87. Main workspace adapts to open panel height.
88. Main workspace remains scrollable.
89. Bottom panel remains independently scrollable.
90. Taskbar remains responsive.
91. Narrow screens retain access to all items.
92. Overflow menus are keyboard accessible.
93. Taskbar controls use accessible buttons.
94. Active state is not communicated by color alone.
95. Resize controls are keyboard accessible where supported.
96. Escape handling respects active overlays.
97. Stage 50 does not hijack Command Palette keyboard shortcuts.
98. Stage 50 does not assign a working Terminal shortcut.
99. Stage 50 does not require Ctrl+J.
100. Notification Center remains in the top bar.
101. Global Search remains in the top bar.
102. Command Palette remains functional.
103. Stage 47 structured parsing remains functional.
104. Stage 48 natural-language interpretation remains functional.
105. Stage 25 Selected Entity context remains authoritative.
106. Taskbar panel switching does not mutate selected Entity.
107. AppShell routing does not remount the taskbar.
108. Stage 43 Market WebSocket is unaffected by taskbar interaction.
109. Auth principal changes isolate/reset taskbar-related user state.
110. No sensitive domain records are persisted by the taskbar.
111. Stage 50 does not create browser push notifications.
112. Stage 50 does not send email.
113. Stage 50 does not send Telegram messages.
114. Stage 50 does not send WhatsApp messages.
115. Stage 50 does not implement Trading actions.
116. Stage 50 does not implement Portfolio actions.
117. Stage 50 does not implement Workflow execution.
118. Stage 50 does not create MCP tools.
119. Stage 50 does not create Agent tools.
120. Stage 50 does not add command execution Capabilities.
121. Stage 50 does not create a public API.
122. Stage 50 does not create an Alembic migration.
123. Stage 50 does not create background workers.
124. Stage 50 does not create scheduler infrastructure.
125. Stage 50 does not create a full Workspace docking framework.
126. Stage 50 does not allow panels to detach.
127. Stage 50 does not allow panel drag reordering.
128. Stage 50 does not create per-user pinned panels.
129. Stage 50 does not create taskbar usage history.
130. Stage 50 does not create taskbar analytics storage.
131. Stage 50 follows existing Next.js client/server boundaries.
132. Stage 50 must not introduce hydration errors.
133. Stage 50 must clean up resize listeners.
134. Stage 50 must avoid AppShell-wide unnecessary rerenders.
135. Stage 50 must be extendable by later domain stages.
136. Stage 51 remains responsible for Home V1.



