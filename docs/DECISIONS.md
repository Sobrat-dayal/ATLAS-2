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

## Stage 51 Decisions — Build HOME V1: The ATLAS Operational Command Center

1. Stage 51 builds ATLAS Home V1.
2. Home is the default operational dashboard, not a marketing landing page.
3. Home remains the first canonical module.
4. Home route is `/home`.
5. Stage 51 does not introduce `/dashboard`.
6. The twenty-module sidebar remains unchanged.
7. Home uses the existing authenticated AppShell.
8. Home does not create another top bar.
9. Home does not create another sidebar.
10. Home does not create another Agent Dock.
11. Home does not create another Bottom Taskbar.
12. Home does not create another Notification Center.
13. Home does not create another Global Search implementation.
14. Home does not create another Command Palette.
15. Home uses the ATLAS design system.
16. Home honors existing appearance settings.
17. Home honors existing background/watermark settings.
18. Home supports responsive layouts.
19. Home works with Agent Dock open.
20. Home works with Bottom Taskbar panel open.
21. Home prioritizes useful first-screen actions.
22. Home includes a compact operational heading.
23. Home includes working Quick Actions.
24. Quick Actions delegate to existing shell controls.
25. Home includes a Selected Entity context view.
26. Selected Entity identity remains UUID-based.
27. Stage 25 remains the selection authority.
28. Home does not maintain a second selected Entity store.
29. Home reuses canonical Entity fetching.
30. Home does not duplicate Entity API clients.
31. Home does not automatically convert Company into Security.
32. Home does not automatically convert Security into Company.
33. Home does not automatically traverse issuer relationships.
34. Home module navigation does not clear selectedEntityId.
35. Home includes Quick Launch.
36. Quick Launch uses Stage 4 route metadata.
37. Quick Launch respects existing authorization.
38. Quick Launch does not bypass route guards.
39. Quick Launch does not promise unfinished module functionality.
40. Home creates a reusable dashboard widget/layout foundation.
41. Stage 51 does not build a widget marketplace.
42. Stage 51 does not build remote widgets.
43. Stage 51 does not build plugin widgets.
44. Stage 51 does not build Agent-generated widgets.
45. Stage 51 does not build arbitrary executable widgets.
46. Stage 51 does not build drag-and-drop widget customization.
47. Stage 51 does not build persistent custom dashboard layouts.
48. Stage 51 does not create Home layout database tables.
49. Stage 51 does not create a Home content-management system.
50. Stage 51 does not create Home user preferences.
51. Home widget data states distinguish reserved, loading, empty, error and unavailable.
52. Reserved features are not represented as permanently loading.
53. Home contains no fake stock prices.
54. Home contains no fake market performance.
55. Home contains no fake portfolio value.
56. Home contains no fake Agent execution.
57. Home contains no fake task approvals.
58. Home contains no fake intelligence feed.
59. Home contains no fake news headlines.
60. Home contains no fake research papers.
61. Home contains no fake map incidents.
62. Home contains no fake operational health percentages.
63. Stage 52 owns Home Market Summary.
64. Stage 53 owns Home Personalized Activity.
65. Stage 54 owns Home Tasks/Approvals.
66. Stage 55 owns Home Intelligence Feed Placeholder.
67. Stage 51 does not implement Home Market Summary.
68. Stage 51 does not implement recent activity.
69. Stage 51 does not implement task feeds.
70. Stage 51 does not implement approval actions.
71. Stage 51 does not implement intelligence scoring.
72. Stage 51 does not implement Home live market data.
73. Stage 51 does not implement portfolio calculations.
74. Stage 51 does not implement map visualizations.
75. Stage 51 does not implement Agent activity feeds.
76. Stage 51 does not perform AI summarization.
77. Stage 51 does not call an LLM on page load.
78. Stage 51 does not use model-generated Home content.
79. Stage 51 does not create Search history.
80. Stage 51 does not create recent-Entity history.
81. Stage 51 does not create user activity tracking.
82. Stage 51 does not create recommendation ranking.
83. Stage 51 does not create new backend services.
84. Stage 51 does not create new public APIs.
85. Stage 51 does not create PostgreSQL tables.
86. Stage 51 does not create ClickHouse tables.
87. Stage 51 does not create Redis business state.
88. Stage 51 does not introduce new WebSocket topics.
89. Stage 51 does not modify Stage 42 Market Event transport.
90. Stage 51 does not introduce background workers.
91. Stage 51 does not introduce a scheduler.
92. Stage 51 does not introduce a new state-management library.
93. Stage 51 does not introduce a separate dashboard grid dependency by default.
94. Home uses existing routing and authentication.
95. Home does not force full-page reloads.
96. Home does not remount the authenticated AppShell unnecessarily.
97. Home does not reconnect the Market Data WebSocket unnecessarily.
98. Home remains usable if selected-Entity query fails.
99. Home renders safe empty states for absent context.
100. Home renders safe error states for failed requests.
101. Home does not expose internal Provider credentials.
102. Home does not expose authentication tokens.
103. Home does not bypass authorization.
104. Home does not allow arbitrary external URL navigation through Quick Launch.
105. Home does not execute arbitrary code.
106. Home does not require `dangerouslySetInnerHTML`.
107. Home does not execute shell commands.
108. Home does not execute trades.
109. Home does not run Agents.
110. Home does not run Workflows.
111. Home does not expose MCP tools.
112. Home respects authenticated-user cache isolation.
113. Home supports keyboard navigation.
114. Home supports screen-reader semantics.
115. Home supports reduced-motion preferences.
116. Home remains readable under custom backgrounds.
117. Home does not add unnecessary heavy JavaScript dependencies.
118. Home is extendable by later Home stages.
119. Stage 50 Bottom Taskbar remains globally mounted.
120. Stage 52 is the next canonical implementation stage.

## Stage 52 Decisions — Build Home Market Summary: Real-Time Market Overview and Financial Data Integration

1. Stage 52 builds the Home Market Summary.
2. Stage 52 reuses Stage 51 Home.
3. Stage 52 does not build the full Markets module.
4. Stage 52 does not modify canonical module ordering.
5. Stage 52 uses canonical Financial Instrument UUID identity.
6. Ticker remains display/identifier metadata.
7. Stage 52 does not create a new Entity resolver.
8. Stage 52 does not create a new Quote domain model.
9. Stage 52 uses existing latest Quote state.
10. Stage 52 does not call Providers on Home load.
11. Stage 52 does not create live targets on Home load.
12. Stage 52 does not trigger historical ingestion.
13. Stage 52 does not create a new Provider stream.
14. Stage 52 does not create a second Redis quote cache.
15. Stage 52 uses bounded curated instrument definitions.
16. Configured instruments must resolve to real canonical Entities.
17. Stage 52 does not commit invented Entity UUIDs.
18. Unresolved identifiers are not guessed.
19. Index and ETF identity remain distinct.
20. ETF proxy values are not labeled as index values.
21. Stage 52 does not fabricate index levels.
22. Latest price comes from defined canonical Quote semantics.
23. Stage 52 does not silently substitute bid/ask midpoint as last trade.
24. Stage 52 preserves Decimal precision.
25. Stage 52 does not perform authoritative financial calculations in JavaScript.
26. Monetary values retain correct currency.
27. Index values retain correct units.
28. FX values retain quote direction.
29. Crypto values retain source/venue context where applicable.
30. Commodity values retain supported contract/unit metadata.
31. Absolute change requires a valid reference.
32. Percentage change requires a valid nonzero reference where meaningful.
33. Previous close must come from qualified canonical data.
34. Previous close is not automatically yesterday's bar.
35. Current incomplete-session bars cannot be used as prior completed-session close.
36. Exchange holidays/weekends cannot be ignored.
37. Stage 52 does not build a trading-calendar engine.
38. Incompatible quote/reference adjustment bases are not compared.
39. Incompatible units/currencies are not compared.
40. Incompatible series/provider semantics are not silently mixed.
41. Missing reference close results in unavailable change.
42. Missing change does not invalidate an otherwise valid latest price.
43. Missing price is not rendered as zero.
44. Missing percentage is not rendered as 0%.
45. Stage 52 uses Stage 44 freshness.
46. Stage 52 does not introduce another freshness model.
47. Redis TTL is not considered freshness.
48. A recently received delayed quote is not automatically realtime.
49. Source timestamp and received timestamp remain distinct.
50. Market-open labels require valid session authority.
51. Stage 52 does not guess exchange open/closed state.
52. Stale Quote values are labeled appropriately.
53. Stage 52 exposes safe Provider provenance.
54. Provider credentials remain server-side.
55. Raw Redis keys are not exposed to browser.
56. Stage 52 creates a bounded authenticated read-only API.
57. The default API is `GET /api/v1/home/market-summary`.
58. The API does not accept unrestricted user-supplied Provider symbols.
59. The API uses bounded configured instrument count.
60. The API uses batched queries where practical.
61. The API does not produce market-data writes.
62. The API does not enqueue ingestion jobs.
63. The API does not create notifications.
64. The API does not create alerts.
65. The API does not execute trades.
66. The API respects authentication.
67. The API respects authorization/entitlements.
68. Stage 52 does not create a new Quote ingestion service.
69. Stage 52 does not create a new Redis client pool.
70. Stage 52 does not create a new ClickHouse client pool.
71. Stage 52 does not create a new market-data Provider.
72. Stage 52 reuses Stage 43 WebSockets when suitable.
73. Stage 52 does not create a second global WebSocket.
74. Stage 52 does not create a new WebSocket protocol.
75. Stage 52 does not create new Redis Streams.
76. Stage 52 does not create Kafka topics.
77. Stage 52 does not create a generic event bus.
78. Stage 52 handles snapshot/live-event ordering.
79. Older snapshots must not overwrite newer accepted Quote state.
80. Stage 52 handles WebSocket reconnects safely.
81. WebSocket connection state is not freshness authority.
82. Stage 52 avoids unnecessary realtime rerenders.
83. Stage 52 uses existing frontend query infrastructure.
84. Stage 52 does not create a new QueryClient.
85. Stage 52 does not persist prices to localStorage.
86. Stage 52 does not persist prices to IndexedDB.
87. Stage 52 Home UI supports missing data.
88. Stage 52 Home UI supports partial data.
89. Stage 52 Home UI supports stale data.
90. Stage 52 Home UI supports delayed data.
91. Stage 52 Home UI supports unknown freshness.
92. Stage 52 Home UI supports errors and retry.
93. Stage 52 Home remains usable if Market Summary fails.
94. Stage 52 uses existing ATLAS design tokens.
95. Stage 52 does not use purple gradients.
96. Stage 52 does not use emoji UI icons.
97. Stage 52 does not display fake quotes.
98. Stage 52 does not display fake percentages.
99. Stage 52 does not display fake market health.
100. Stage 52 does not display fake sparklines.
101. Stage 52 does not build Market Movers.
102. Stage 52 does not build Market Heatmaps.
103. Stage 52 does not build Cross-Asset Analytics.
104. Stage 52 does not build a Chart engine.
105. Stage 52 does not build technical indicators.
106. Stage 52 does not build financial recommendations.
107. Stage 52 does not build sentiment scoring.
108. Stage 52 does not build Watchlists.
109. Stage 52 does not build alert rules.
110. Stage 52 does not build Portfolio summaries.
111. Stage 52 does not build Risk summaries.
112. Stage 52 does not build Economic Calendar.
113. Stage 52 does not build News feeds.
114. Stage 52 does not build Research feeds.
115. Stage 52 does not build Agent activity.
116. Stage 52 does not invoke AI models.
117. Stage 52 does not invoke MCP tools.
118. Stage 52 does not execute Agents or Workflows.
119. Stage 52 does not modify Stage 49 Notification Center.
120. Stage 52 does not modify Stage 50 Bottom Taskbar.
121. Stage 52 preserves Stage 25 Entity selection semantics.
122. Card navigation uses canonical Entity UUID.
123. Card navigation uses canonical internal routes.
124. Card navigation cannot execute trades.
125. Stage 52 does not introduce per-user instrument personalization.
126. Stage 53 remains responsible for Home Personalized Activity.
127. Stage 54 remains responsible for Home Tasks/Approvals.
128. Stage 55 remains responsible for Home Intelligence Feed.
129. Stage 56 remains responsible for full Markets Overview.
130. Stage 52 must be supported by actual tests and documentation.

## Stage 53 Decisions — Home Personalized Activity

1. Stage 53 builds Home Personalized Activity.
2. Activity exists to support workspace continuity.
3. Stage 53 does not build a clickstream analytics platform.
4. Stage 53 does not build user surveillance.
5. Stage 53 does not build an audit-log system.
6. Stage 53 does not build task history.
7. Stage 53 does not build Agent history.
8. Stage 53 does not build Notification history.
9. Activity history is user-scoped.
10. PostgreSQL is the durable activity source of truth.
11. Stage 53 reuses Stage 13 user identity.
12. Stage 53 reuses Stage 14 authorization.
13. Stage 53 reuses Stage 15 preferences for consent.
14. Recording is disabled by default.
15. Existing users are not silently opted in.
16. Activity collection requires explicit opt-in.
17. Consent applies prospectively.
18. No historical activity is fabricated.
19. No unrecorded behavior is backfilled.
20. Disabled collection produces no new events.
21. Backend rechecks consent on every write.
22. Frontend avoids requests while disabled.
23. Disabling clears Stage 53 history under the chosen policy.
24. Consent disable and clearing are transactionally coordinated.
25. Users can clear recorded activity.
26. Clear History does not delete unrelated data.
27. Stage 53 supports MODULE_OPENED events.
28. Stage 53 supports ENTITY_SELECTED events.
29. No generic arbitrary event payloads exist.
30. Event type is strictly validated.
31. Activity event ID is a UUID.
32. Client event UUID supports idempotency.
33. Repeated event delivery does not create duplicate rows.
34. Conflicting idempotency payloads fail safely.
35. User ownership comes from authentication.
36. Client-provided user IDs are rejected.
37. Module IDs come from Stage 4.
38. Canonical module labels are not accepted from client as authority.
39. Entity references use Stage 16 UUIDs.
40. Ticker does not become activity identity.
41. Stage 53 does not use fuzzy Entity resolution.
42. Stage 53 does not convert Company to Security.
43. Stage 53 does not convert Security to Company.
44. Stage 53 does not infer issuer relationships.
45. Stage 53 does not store raw Search queries.
46. Stage 53 does not store Natural-Language commands.
47. Stage 53 does not store structured command text.
48. Stage 53 does not record every keystroke.
49. Stage 53 does not record mouse movements.
50. Stage 53 does not record scroll activity.
51. Stage 53 does not record passive component mounts.
52. Stage 53 does not treat route hydration as navigation.
53. Stage 53 does not automatically log browser refresh.
54. Stage 53 does not log background prefetches.
55. Stage 53 records supported explicit user actions.
56. Stage 53 does not claim complete browsing-history coverage.
57. Stage 53 events are convenience records, not audit proof.
58. Stage 53 does not use activity as security authority.
59. Stage 53 does not use activity as trading authority.
60. Stage 53 does not infer investment intent.
61. Stage 53 does not infer personal characteristics.
62. Stage 53 does not perform behavioral scoring.
63. Stage 53 does not call AI models.
64. Stage 53 does not generate embeddings.
65. Stage 53 does not implement RAG.
66. Stage 53 does not implement AI recommendations.
67. Stage 53 does not implement productivity scoring.
68. Stage 53 does not generate behavioral predictions.
69. Stage 53 does not build activity-based marketing.
70. Stage 53 does not send activity to external analytics SDKs.
71. Stage 53 does not store IP addresses in activity rows.
72. Stage 53 does not store User-Agent strings in activity rows.
73. Stage 53 does not fingerprint devices.
74. Stage 53 does not infer user geolocation.
75. Stage 53 does not store arbitrary metadata blobs.
76. Activity timestamps are server-authoritative.
77. Activity uses deterministic chronological ordering.
78. Activity has bounded per-user storage.
79. Activity has a documented retention period.
80. Expired records are excluded from reads.
81. Physical cleanup is implemented and its scheduling is disclosed.
82. Stage 53 does not create a new cleanup daemon by default.
83. Stage 53 does not create a Redis Activity Stream.
84. Stage 53 does not create Redis Pub/Sub.
85. Stage 53 does not create a new message broker.
86. Stage 53 does not create a ClickHouse activity warehouse.
87. Stage 53 does not create a new frontend event bus.
88. Stage 53 uses a narrow activity recorder.
89. Activity logging is best-effort.
90. Activity logging does not block navigation.
91. Activity logging does not block Entity selection.
92. Failed activity writes do not create an offline backlog.
93. Failed activity writes do not create recursive notifications.
94. Stage 53 does not retry recording indefinitely.
95. Stage 53 does not produce events from market quote updates.
96. Stage 53 does not produce events from background WebSocket activity.
97. Stage 53 does not produce events from AI interpretation alone.
98. Stage 53 does not record failed commands as successful actions.
99. Stage 53 does not record denied module navigation as successful opening.
100. Stage 53 reuses existing navigation handlers.
101. Stage 53 reuses existing Entity-selection handlers.
102. Stage 53 does not duplicate the module registry.
103. Stage 53 does not duplicate selected Entity state.
104. Stage 25 remains selection authority.
105. Activity read permissions are reevaluated.
106. Activity resume permissions are reevaluated.
107. Past activity does not grant present access.
108. Activity items use current authorized display metadata.
109. Deleted/inaccessible Entities are handled safely.
110. Activity may resume internal modules.
111. Activity may select a canonical Entity.
112. Activity cannot execute trades.
113. Activity cannot execute Agents.
114. Activity cannot execute Workflows.
115. Activity cannot execute shell commands.
116. Activity cannot open arbitrary external URLs.
117. Stage 53 uses authenticated APIs.
118. Stage 53 enforces `atlas.access`.
119. Stage 53 list queries are user-scoped.
120. Stage 53 clear operations are user-scoped.
121. Stage 53 supports keyset pagination.
122. Stage 53 enforces page-size bounds.
123. Stage 53 uses frontend query cache isolation.
124. Activity is not persisted in browser localStorage.
125. Activity is not persisted in browser IndexedDB.
126. Activity responses are not publicly cacheable.
127. Stage 53 does not add excessive activity polling.
128. Stage 53 does not create activity WebSockets.
129. Stage 53 does not modify Stage 42 Market Event transport.
130. Stage 53 does not modify Stage 43 WebSockets.
131. Stage 53 does not modify Stage 41 Quote state.
132. Stage 53 does not modify Stage 49 Notification Center.
133. Stage 53 does not modify Stage 50 Bottom Taskbar architecture.
134. Stage 53 integrates through Stage 51 Home widgets.
135. Stage 53 preserves Stage 52 Market Summary.
136. Stage 53 uses ATLAS design tokens.
137. Stage 53 does not use fake activity.
138. Stage 53 does not use emoji UI icons.
139. Stage 53 does not use purple gradients.
140. Stage 53 does not build a separate activity application.
141. Stage 53 does not build a full activity search page.
142. Stage 53 does not create an organization activity dashboard.
143. Stage 53 does not create public activity profiles.
144. Stage 53 does not create activity sharing.
145. Stage 53 does not build a recommendation engine.
146. Stage 53 does not build Watchlists.
147. Stage 53 does not build Saved Objects.
148. Stage 53 does not build Workspaces V1.
149. Stage 53 does not build Tasks and Approvals.
150. Stage 54 remains the next canonical stage.

## Stage 54 Decisions - Home Tasks and Approvals

1. Stage 54 builds Home Tasks and Approvals.
2. Personal Tasks and Approval Requests are separate domains.
3. Stage 54 does not build an autonomous execution engine.
4. Stage 54 does not implement a generic workflow engine.
5. Stage 54 does not implement a task scheduler.
6. Stage 54 does not implement Agent orchestration.
7. Stage 54 does not implement Trading execution.
8. PostgreSQL is the authoritative store.
9. Stage 54 reuses canonical user identity.
10. Stage 54 reuses canonical Entity identity.
11. Stage 54 reuses canonical module metadata.
12. Stage 54 uses existing authorization.
13. Personal Tasks are owned by one authenticated user.
14. Public clients cannot choose arbitrary task owners.
15. Task IDs are UUIDs.
16. Task titles and descriptions are plain text.
17. Task statuses are typed (OPEN, COMPLETED, CANCELLED).
18. Task transitions are validated.
19. Task completion is explicit.
20. Task reopening is explicit.
21. Task cancellation is explicit.
22. Task due dates do not trigger automatic actions.
23. Overdue is derived, not a competing persisted status.
24. Task context is optional.
25. Task Entity context uses UUID identity.
26. Task module context uses canonical module IDs.
27. Task navigation cannot execute commands.
28. Task creation supports safe idempotency.
29. Task mutations use concurrency safeguards (optimistic versioning).
30. Task API queries are owner-scoped.
31. Task API responses are bounded.
32. Task lists use deterministic keyset pagination.
33. No fake tasks are created.
34. No automatic task producers are added.
35. Market Data ingestion jobs are not Personal Tasks.
36. Approval Requests originate only from trusted backend subsystems.
37. Ordinary users cannot create trusted approval requests.
38. Approval producer identity is server-validated.
39. Approval action types are allowlisted.
40. Approval requests bind to immutable proposals.
41. Approval requests preserve proposal identity/digest.
42. Approval summaries exclude secrets.
43. Approval requests have finite expiration.
44. Approval requests are assigned to an authorized human.
45. Approval request IDs are UUIDs.
46. Approval decisions are explicit.
47. Approval decisions are user-scoped.
48. Approval decisions are race-safe.
49. Approval decisions are idempotent.
50. Approval decisions have immutable audit records.
51. Expiration eligibility is checked with server/database time.
52. Expired requests cannot be approved.
53. Rejected requests cannot be subsequently approved.
54. Approved requests cannot be subsequently rejected.
55. Cancelled requests cannot be decided.
56. Only one final decision is permitted.
57. Approval requests are not general authorization grants.
58. Approval does not bypass Stage 14.
59. Approval does not execute the proposed action.
60. Approval does not place trades.
61. Approval does not start Agents.
62. Approval does not run Workflows.
63. Approval does not execute shell commands.
64. Approval does not execute structured ATLAS commands.
65. Approval does not send external messages.
66. Approval does not invoke arbitrary callbacks.
67. Approval does not dispatch WebSocket execution events.
68. No automatic approve-all feature exists.
69. No AI-based approval decision exists.
70. No timeout auto-approval exists.
71. No implicit admin override exists.
72. Approval decisions are not reusable standing permissions.
73. Future execution must revalidate proposal, approval and current authorization.
74. Stage 54 does not implement approval consumption/execution.
75. Stage 47/48 confirmations remain unchanged.
76. Stage 54 does not migrate ephemeral command confirmations automatically.
77. No fictional production approval requests are seeded.
78. An empty Approval Inbox is valid.
79. Home uses the Stage 51 widget framework.
80. Stage 52 Market Summary remains intact.
81. Stage 53 Personalized Activity remains intact.
82. Stage 50 Bottom Tasks panel may reuse Stage 54 task services.
83. Stage 49 Notification Center remains separate.
84. Stage 54 adds no new Redis Streams.
85. Stage 54 adds no Redis Pub/Sub.
86. Stage 54 adds no ClickHouse schema.
87. Stage 54 adds no new WebSocket protocol.
88. Stage 54 adds no new Provider connections.
89. Stage 54 adds no new broker integration.
90. Stage 54 adds no new background Agent workers.
91. Stage 54 adds no generic callback engine.
92. Stage 54 adds no dynamic code execution.
93. Stage 54 does not track user behavioral history.
94. Stage 54 does not add Activity event types.
95. Stage 54 task/approval text is treated as private.
96. Stage 54 does not persist private content to localStorage.
97. Stage 54 user caches clear on principal changes.
98. Stage 54 supports responsive layouts.
99. Stage 54 supports keyboard and screen-reader access.
100. Stage 54 reports only verified functional capability.
101. Stage 55 is responsible for Home Intelligence Feed.
102. Stage 54 stops before Stage 55.

## Stage 55 Decisions - Home Intelligence Feed Placeholder

1. Stage 55 builds Home Intelligence Feed Placeholder.
2. Stage 55 does not build Intelligence V1.
3. Stage 55 integrates into the existing Home dashboard.
4. Stage 55 does not replace Home V1.
5. Stage 55 preserves Home Market Summary.
6. Stage 55 preserves Personalized Activity.
7. Stage 55 preserves Tasks and Approvals.
8. Stage 55 uses the existing AppShell.
9. Stage 55 uses the Stage 51 widget framework.
10. Stage 55 does not create another widget registry.
11. Stage 55 does not create another sidebar.
12. Stage 55 does not create another top bar.
13. Stage 55 does not create another Agent Dock.
14. Stage 55 does not create another Bottom Taskbar.
15. Stage 55 does not create another Notification Center.
16. Stage 55 does not create another Search system.
17. Stage 55 does not create another command system.
18. The widget title is Intelligence Feed.
19. The initial Intelligence Feed state is Reserved.
20. Reserved means the service is not connected.
21. Reserved does not mean the service returned zero items.
22. Reserved does not mean the service is loading.
23. Reserved does not mean a backend error occurred.
24. Mounted UI does not imply operational intelligence.
25. Stage 55 does not display fake intelligence records.
26. Stage 55 does not display invented market-impact claims.
27. Stage 55 does not display fake geopolitical reports.
28. Stage 55 does not display fake supply-chain disruptions.
29. Stage 55 does not display fake cyber incidents.
30. Stage 55 does not display fabricated news.
31. Stage 55 does not display fabricated research.
32. Stage 55 does not invent source citations.
33. Stage 55 does not invent source counts.
34. Stage 55 does not invent timestamps.
35. Stage 55 does not invent affected Entities.
36. Stage 55 does not invent risk scores.
37. Stage 55 does not invent confidence scores.
38. Stage 55 does not invent probability estimates.
39. Stage 55 does not invent severity classifications.
40. Stage 55 does not invent sentiment classifications.
41. Stage 55 does not invent financial-return predictions.
42. Stage 55 does not invent causal relationships.
43. Stage 55 does not create a Universal Event domain model.
44. Stage 135 remains responsible for Universal Events.
45. Stage 136 remains responsible for Event–Entity relationships.
46. Stage 137 remains responsible for exposure calculations.
47. Stage 138 remains responsible for Intelligence V1.
48. Stage 139 remains responsible for Intelligence Scoring.
49. Stage 140 remains responsible for God's Eye Intelligence.
50. Stage 42 Market Quote events are not Universal Intelligence Events.
51. Stage 55 does not convert Quote updates into Intelligence Events.
52. Stage 55 does not convert News records into verified intelligence.
53. Stage 55 does not convert research papers into intelligence findings.
54. Stage 55 does not convert Notifications into intelligence.
55. Stage 55 does not convert user activity into intelligence.
56. Stage 55 does not convert tasks into intelligence.
57. Stage 55 does not convert approvals into intelligence.
58. Stage 55 does not create a new backend intelligence service.
59. Stage 55 does not create an Intelligence Feed API.
60. Stage 55 does not create PostgreSQL tables.
61. Stage 55 does not create ClickHouse tables.
62. Stage 55 does not create Redis keys.
63. Stage 55 does not create Redis Streams.
64. Stage 55 does not create Redis Pub/Sub.
65. Stage 55 does not create a new broker.
66. Stage 55 does not create a new WebSocket topic.
67. Stage 55 does not create background workers.
68. Stage 55 does not create scheduled research.
69. Stage 55 does not trigger Provider calls.
70. Stage 55 does not trigger OpenBB calls.
71. Stage 55 does not trigger AI model calls.
72. Stage 55 does not generate embeddings.
73. Stage 55 does not implement RAG.
74. Stage 55 does not implement sentiment analysis.
75. Stage 55 does not implement OSINT ingestion.
76. Stage 55 does not scrape news websites.
77. Stage 55 does not monitor social-media feeds.
78. Stage 55 does not ingest satellite data.
79. Stage 55 does not build event clustering.
80. Stage 55 does not build event deduplication.
81. Stage 55 does not build supply-chain propagation.
82. Stage 55 does not build economic exposure analysis.
83. Stage 55 does not build Intelligence alert rules.
84. Stage 55 does not send intelligence notifications.
85. Stage 55 does not send Telegram or WhatsApp messages.
86. Stage 55 does not execute Agents.
87. Stage 55 does not execute Workflows.
88. Stage 55 does not execute shell commands.
89. Stage 55 does not execute Trading actions.
90. Stage 55 does not create MCP tools.
91. Stage 55 does not create Intelligence plugins.
92. Stage 55 does not add a widget marketplace.
93. Stage 55 does not add draggable intelligence dashboards.
94. Stage 55 does not add custom intelligence filters.
95. Stage 55 does not add fake pagination.
96. Stage 55 does not add fake sorting.
97. Stage 55 does not add fake loading.
98. Stage 55 does not add fake realtime badges.
99. Stage 55 does not add animated monitoring graphics.
100. Stage 55 uses a minimal typed presentation contract.
101. Presentation types are not authoritative Event models.
102. Future feed items must preserve provenance.
103. Future Entity references must use canonical UUIDs.
104. Future navigation must respect permissions.
105. Stage 25 remains selected-Entity authority.
106. Stage 14 remains authorization authority.
107. Stage 24 remains provenance authority.
108. Source content is untrusted data.
109. Stage 55 does not add arbitrary external URLs.
110. Stage 55 does not render unsafe HTML.
111. Stage 55 does not execute content.
112. Stage 55 uses ATLAS design tokens.
113. Stage 55 does not use purple gradients.
114. Stage 55 does not use emoji UI icons.
115. Stage 55 does not use oversized placeholder cards.
116. Stage 55 does not use fabricated system health values.
117. Stage 55 keeps the Intelligence region compact.
118. Stage 55 supports desktop, tablet and mobile.
119. Stage 55 supports the Agent Dock.
120. Stage 55 supports the Bottom Taskbar.
121. Stage 55 supports dark and light appearance.
122. Stage 55 supports custom background contrast.
123. Stage 55 supports accessible keyboard navigation.
124. Stage 55 supports screen-reader semantics.
125. Stage 55 respects reduced motion.
126. The Open Intelligence action uses `/intelligence`.
127. The action uses canonical Stage 4 navigation.
128. The action does not bypass authorization.
129. The action does not automatically select an Entity.
130. The action does not start an Agent.
131. The action does not start a workflow.
132. The action does not trigger intelligence processing.
133. The widget makes no new backend requests.
134. The widget does not poll.
135. The widget does not open a WebSocket.
136. The widget does not change Market Data transport.
137. The widget does not persist user behavior.
138. Stage 53 consent continues to govern supported navigation activity.
139. Stage 55 does not add Activity event types.
140. Stage 55 does not modify Stage 54 approval semantics.
141. Stage 55 does not add user intelligence preferences.
142. Stage 55 does not add an admin dashboard.
143. Stage 55 does not add a Provider configuration screen.
144. Stage 55 adds no dependencies unless genuinely justified.
145. Stage 55 remains lightweight.
146. Stage 55 must be supported by actual component tests.
147. Stage 55 must pass relevant AppShell regressions.
148. Stage 55 documentation must describe the real reserved state.
149. Stage 55 must report unimplemented future functionality accurately.
150. Stage 56 is the next canonical implementation stage.

## Stage 56: Markets Overview V1
1. Stage 56 builds Markets Overview V1.
2. The route remains `/markets`.
3. Markets remains canonical module 2.
4. Markets reuses the authenticated AppShell.
5. Markets does not create another sidebar.
6. Markets does not create another top bar.
7. Markets does not create another Agent Dock.
8. Markets does not create another Bottom Taskbar.
9. Markets uses the existing ATLAS design system.
10. Markets uses canonical Financial Instrument UUIDs.
11. Ticker remains identifier/display metadata.
12. Ambiguous tickers are not guessed.
13. Index and ETF identities remain distinct.
14. No proxy is mislabeled as its benchmark.
15. The overview uses a bounded configured instrument universe.
16. The overview does not claim comprehensive global coverage.
17. Stage 52 shared market read logic is reused.
18. Stage 33 canonical Quote semantics remain authoritative.
19. Stage 41 latest Quote state is reused.
20. Stage 39 historical data is reused for qualified references.
21. Stage 44 remains freshness authority.
22. Stage 43 remains WebSocket infrastructure authority.
23. Stage 42 remains Market Event transport authority.
24. Markets does not create a second Quote model.
25. Markets does not create a new Entity resolver.
26. Markets does not create a second Provider router.
27. Markets does not create a new Redis Quote cache.
28. Markets does not create new Provider ingestion workers.
29. Markets does not create live targets on page load.
30. Markets does not trigger backfills on page load.
31. Markets does not fetch Providers directly on page load.
32. Backend financial calculations preserve Decimal precision.
33. Currency and instrument units are respected.
34. Last price is not silently replaced by midpoint.
35. Missing price is not zero.
36. Missing change is not zero change.
37. Change requires qualified reference data.
38. Previous close is not blindly yesterday's calendar bar.
39. Adjustment compatibility is enforced.
40. Unit/currency compatibility is enforced.
41. Zero denominators are handled safely.
42. Stale observations remain labeled stale.
43. Delayed observations remain labeled delayed.
44. Source and receive timestamps are distinct.
45. Redis TTL is not freshness.
46. WebSocket connectivity is not freshness.
47. No unverified market-open labels are shown.
48. No fake global market health metrics are shown.
49. Markets Overview API is authenticated.
50. API respects financial-data entitlements.
51. API is read-only.
52. API responses are bounded.
53. API supports validated grouping.
54. API uses deterministic pagination where needed.
55. API exposes the universe's actual scope.
56. Coverage counts are scoped accurately.
57. Markets uses batch retrieval.
58. Markets avoids unbounded ClickHouse scans.
59. Markets avoids N+1 metadata queries.
60. Markets preserves safe Provider provenance.
61. No Provider secrets reach frontend.
62. Markets initial state comes from an HTTP snapshot.
63. Realtime updates reuse Stage 43.
64. No second global WebSocket is created.
65. No new realtime event type is introduced.
66. Older snapshots cannot overwrite newer state incorrectly.
67. Duplicate events are handled.
68. Reconnect triggers safe reconciliation.
69. Realtime refetches are bounded.
70. Markets uses a professional dense table.
71. Markets uses a compact featured instrument region.
72. Featured entries are genuinely configured.
73. Market groups use canonical classifications.
74. Missing groups are not populated with fake data.
75. Stage 57 remains responsible for dedicated Equities.
76. Stage 58 remains responsible for ETFs/Funds.
77. Stage 59 remains responsible for FX.
78. Stage 60 remains responsible for Cryptocurrency.
79. Stage 61 remains responsible for Bonds.
80. Stage 62 remains responsible for Futures/Commodities.
81. Stage 63 remains responsible for Market Movers.
82. Stage 64 remains responsible for Heatmaps.
83. Stage 65 remains responsible for Cross-Asset Analytics.
84. Stage 66 remains responsible for Charts V1.
85. Stage 56 does not build a charting engine.
86. Stage 56 does not build technical indicators.
87. Stage 56 does not create Watchlists.
88. Stage 56 does not create Screeners.
89. Stage 56 does not create price alerts.
90. Stage 56 does not create Portfolio analytics.
91. Stage 56 does not create Risk analytics.
92. Stage 56 does not create AI market commentary.
93. Stage 56 does not run Agents.
94. Stage 56 does not execute Workflows.
95. Stage 56 does not place trades.
96. Stage 56 does not connect brokers.
97. Stage 56 does not produce intelligence events.
98. Stage 56 does not create Notifications from Quote updates.
99. Stage 56 does not expand Personalized Activity collection.
100. Stage 56 uses canonical internal navigation.
101. Stage 25 remains selected-Entity authority.
102. Markets does not automatically select its first instrument.
103. Market-data errors do not crash AppShell.
104. Markets supports honest partial data.
105. Markets supports empty configurations.
106. Markets supports unavailable prices.
107. Markets supports unknown freshness.
108. Markets supports backend error and retry states.
109. Markets uses accessible table semantics.
110. Markets supports keyboard navigation.
111. Markets supports reduced motion.
112. Markets supports desktop, tablet and mobile.
113. Markets supports Agent Dock open.
114. Markets supports Bottom Taskbar open.
115. Markets does not add heavy chart or map libraries.
116. Markets does not add unnecessary state-management libraries.
117. Markets does not persist private Quotes to localStorage.
118. Markets avoids cross-user cache leakage.
119. Markets does not use fake production data.
120. Markets does not use purple gradients.
121. Markets does not use emoji icons.
122. Markets does not use fake performance rankings.
123. Markets does not use fake chart sparklines.
124. Markets does not use fake market-cap statistics.
125. Markets does not use fake volume.
126. Markets does not use fake source labels.
127. Markets does not use fake quote timestamps.
128. Markets must pass financial-data integrity tests.
129. Markets must pass authorization tests.
130. Markets must pass relevant previous-stage regressions.
131. Markets documentation must match implementation.
132. Stage 57 is the next canonical implementation stage.

## Stage 57: Equities Markets V1
1. Stage 57 builds Equities Markets V1.
2. Equities remains within canonical Markets module 2.
3. Stage 56 Markets Overview remains functional at `/markets`.
4. Equities uses the existing AppShell.
5. Equities does not add a global sidebar module.
6. Equities reuses the Stage 56 Markets visual architecture.
7. The chosen Equities route is `/markets/equities`.
8. Equity identity uses canonical Financial Instrument UUIDs.
9. Company identity remains distinct from Security identity.
10. Listing identity remains distinct where the canonical model supports it.
11. Multiple share classes are not merged.
12. Depositary receipts are not automatically treated as ordinary shares.
13. Preferred shares are not automatically common shares.
14. Rights and warrants are not silently classified as ordinary equities.
15. Tickers are not primary keys.
16. Symbol resolution remains exchange-scoped.
17. Ambiguous symbols are not guessed.
18. Exchange MICs are not invented.
19. Currency is taken from authoritative listing/Quote metadata.
20. Same-symbol securities across exchanges remain separate.
21. Cross-listed Quote series are not mixed.
22. Alias/history semantics reuse Stage 21–22.
23. Issuer relationships reuse Stage 23.
24. Issuer identity is not inferred from display names.
25. Company navigation requires a verified relationship.
26. Selecting an Equity Security does not automatically select its Company.
27. Stage 25 remains selected-Entity authority.
28. Directory source is the canonical equity instrument catalog.
29. Stage 57 is not limited solely to Stage 56 featured instruments.
30. Stage 57 does not claim complete global equity coverage.
31. Stage 57 does not bulk-import unverified exchange listings.
32. Stage 57 does not scrape random symbol lists.
33. Stage 57 does not create new Entities on search.
34. Stage 57 does not auto-backfill market data.
35. Stage 57 does not create live Quote targets on page load.
36. Stage 57 directory discovery is read-only.
37. Basic country filtering is based on listing-market semantics.
38. Exchange filtering uses canonical venue identity.
39. Equity subtype filtering uses canonical classification.
40. Listing status is not inferred from Quote availability.
41. Missing Quote does not imply delisting.
42. Directory search is bounded and typed.
43. Stage 45 Global Search is not duplicated.
44. Stage 57 is not Stage 94 Screeners.
45. Stage 57 does not implement fundamental screening.
46. Stage 57 does not implement technical screening.
47. Stage 57 does not implement saved screening formulas.
48. Stage 57 reuses Stage 52/56 financial read logic.
49. Stage 33 canonical Quote remains authoritative.
50. Stage 41 latest Quote state remains authoritative.
51. Stage 39 historical references are reused where qualified.
52. Stage 44 freshness remains authoritative.
53. Stage 42 event transport remains authoritative.
54. Stage 43 WebSockets remain authoritative.
55. Stage 57 does not create a second Quote model.
56. Stage 57 does not create a second Redis Quote cache.
57. Stage 57 does not create a second Provider router.
58. Stage 57 does not create new Market Data ingestion workers.
59. Stage 57 does not create another WebSocket transport.
60. Stage 57 does not invent a new live event type.
61. Last price semantics are preserved.
62. Bid/Ask data is not silently substituted for last trade.
63. Decimal precision is preserved.
64. Currency and units are preserved.
65. Qualified previous close is required for returns.
66. Adjustment compatibility is enforced.
67. Venue/series compatibility is enforced.
68. Missing reference close yields unavailable change.
69. Missing price is not rendered as zero.
70. Missing change is not rendered as zero.
71. Zero denominator is handled.
72. Stale Quotes remain labeled stale.
73. Delayed Quotes remain labeled delayed.
74. Unknown freshness is not called realtime.
75. Source timestamp and received timestamp are distinct.
76. Redis TTL does not determine freshness.
77. WebSocket connectivity does not determine freshness.
78. No unsupported market-session state is displayed.
79. Provider provenance is preserved safely.
80. Provider credentials remain server-side.
81. Equity directory APIs require authentication.
82. Equity directory APIs enforce authorization.
83. Market-data entitlements remain enforced.
84. API pagination is bounded.
85. Search parameters are validated.
86. Filter combinations have documented semantics.
87. Listing metadata queries are batched.
88. Quote reads are batched where possible.
89. Historical reference queries remain bounded.
90. Equity APIs do not execute writes.
91. Equity APIs do not invoke Providers directly.
92. Equity APIs do not create ingestion jobs.
93. Equity APIs do not create notifications.
94. Equity APIs do not create tasks.
95. Equity APIs do not place trades.
96. Equity APIs do not invoke Agents.
97. Equity APIs do not invoke Workflows.
98. Stage 57 provides an Equity Directory Table.
99. Stage 57 provides basic Equity filtering.
100. Stage 57 provides an Equity Inspector.
101. Inspector fields come from authoritative existing data.
102. Inspector does not implement full Company analytics.
103. Stage 58 remains responsible for ETFs/Funds.
104. Stage 59 remains responsible for FX.
105. Stage 60 remains responsible for Crypto.
106. Stage 61 remains responsible for Bonds.
107. Stage 62 remains responsible for Futures/Commodities.
108. Stage 63 remains responsible for Market Movers.
109. Stage 64 remains responsible for Heatmaps.
110. Stage 65 remains responsible for Cross-Asset Analytics.
111. Stage 66 remains responsible for Charts.
112. Stage 76 remains responsible for Watchlists.
113. Stage 80 remains responsible for Alerts.
114. Stage 81 remains responsible for Companies V1.
115. Stage 82 remains responsible for Statements.
116. Stage 83 remains responsible for Financial Ratios.
117. Stage 84 remains responsible for Earnings.
118. Stage 85 remains responsible for Ownership.
119. Stage 86 remains responsible for Filings.
120. Stage 87 remains responsible for Peers.
121. Stage 88 remains responsible for Supply Chains.
122. Stage 94–98 remain responsible for Screeners.
123. Stage 57 does not display fabricated volume.
124. Stage 57 does not fabricate market capitalization.
125. Stage 57 does not fabricate P/E.
126. Stage 57 does not fabricate dividend yield.
127. Stage 57 does not fabricate 52-week ranges.
128. Stage 57 does not fabricate shares outstanding.
129. Stage 57 does not provide trading recommendations.
130. Stage 57 does not implement broker actions.
131. Stage 57 does not build an order book.
132. Stage 57 does not implement AI equity analysis.
133. Stage 57 does not call LLMs on page load.
134. Stage 57 does not implement Agent execution.
135. Stage 57 does not expand Stage 53 behavioral tracking.
136. Stage 57 does not change Stage 54 approval semantics.
137. Stage 57 preserves the global Bottom Taskbar.
138. Stage 57 preserves the global Agent Dock.
139. Stage 57 preserves the global Search.
140. Stage 57 preserves the Command Palette.
141. Stage 57 preserves the Notification Center.
142. Stage 57 uses ATLAS design tokens.
143. Stage 57 does not use purple gradients.
144. Stage 57 does not use emoji icons.
145. Stage 57 does not display fabricated equity records.
146. Stage 57 does not display fabricated prices.
147. Stage 57 does not claim unsupported exchange coverage.
148. Stage 57 supports honest partial-data states.
149. Stage 57 supports responsive layouts.
150. Stage 57 supports accessible controls.
151. Stage 57 prevents unauthorized instrument data leakage.
152. Stage 57 does not persist private Quotes in browser storage.
153. Stage 57 uses only necessary new dependencies.
154. Stage 57 must pass actual identity and financial-math tests.
155. Stage 57 must pass permission and security tests.
156. Stage 57 must pass prior-stage regression tests.
157. Stage 57 documentation must match actual implementation.
158. Stage 58 is the next canonical stage.

## Stage 58 Decisions — ETFs & Funds Markets V1

1. Stage 58 implements ETFs & Funds Markets V1.
2. ETFs & Funds remains inside canonical Markets module 2 (`/markets/funds`).
3. The existing global sidebar is preserved.
4. The existing AppShell is preserved.
5. Stage 56 Markets Overview remains functional (`/markets`).
6. Stage 57 Equities remains functional (`/markets/equities`).
7. The chosen Funds route is canonical and documented as `/markets/funds`.
8. Stage 58 does not create a separate financial-data platform.
9. Fund identity uses canonical Financial Instrument UUIDs (`instrument_entity_id`).
10. Fund product and fund share class are distinct where represented.
11. Share classes are not merged by display name.
12. Exchange listings are not merged by ticker.
13. Ticker is not a primary key.
14. ISIN/FIGI/provider identifiers reuse Stage 21.
15. Symbol ambiguity reuses Stage 22.
16. Fund relationships reuse Stage 23.
17. Provenance reuses Stage 24.
18. Selected Entity reuses Stage 25 (`useSelectedEntity`).
19. ETF and ordinary corporate equity remain different classifications.
20. ETF and ETN remain distinct (ETNs are debt notes, not equity funds).
21. Mutual funds without exchange Quotes are valid and represent official close NAV.
22. Closed-end funds can have both traded price and NAV.
23. ETF market price and official NAV are separate measures.
24. NAV is not stored in a market Quote field.
25. NAV is not synthesized from market price.
26. Market price is not synthesized from NAV.
27. iNAV is not assumed equal to official NAV.
28. NAV valuation date is preserved and explicit.
29. NAV publication timestamp is distinct from valuation date.
30. NAV currency is explicit.
31. NAV is not automatically realtime.
32. NAV share-class identity is preserved.
33. NAV change is not the same as market-price change.
34. NAV change is not automatically total return.
35. Distribution effects are not ignored.
36. Incompatible NAV observations are not compared.
37. ETF market-price changes reuse Stage 52/56 logic.
38. Decimal precision remains authoritative.
39. Missing financial values are not zeros.
40. Unknown fund data is not invented.
41. Share-class currencies are distinct from trading currency.
42. Fund domicile is distinct from listing market.
43. Fund manager is distinct from sponsor and issuer.
44. Benchmark identity is not inferred from names.
45. An index is not replaced by an ETF proxy.
46. Expense ratio metric types remain explicit.
47. Gross expense ratio and net expense ratio are not conflated.
48. TER, OCF and management fee are not silently interchangeable.
49. Fee values preserve units and effective dates.
50. Fee values preserve share-class scope.
51. Missing expense ratio is not zero.
52. AUM preserves currency.
53. AUM preserves as-of date.
54. AUM preserves fund/share-class scope.
55. AUM is not fabricated from unverified units.
56. AUM changes are not fund flows.
57. Fund inception is not inferred from earliest Quote history.
58. Accumulating/distributing classification requires verified metadata.
59. Fund strategy descriptions are not AI-generated.
60. Stage 58 does not create a full holdings ingestion engine.
61. Optional holdings previews require genuine dated source data.
62. Stage 58 does not calculate fund look-through risk.
63. Stage 58 does not implement fund-flow analytics.
64. Stage 58 does not implement advanced ETF arbitrage.
65. Stage 58 does not implement tracking-error analytics.
66. Stage 58 does not implement portfolio overlap.
67. Stage 58 does not implement backtesting.
68. Stage 58 does not implement a full fund screener.
69. Fund directory source is canonical Financial Instrument data.
70. Stage 58 does not import unverified ticker lists.
71. Stage 58 does not create Entities on search.
72. Stage 58 does not call Providers on page load.
73. Stage 58 does not create upstream live-target subscriptions.
74. Stage 58 does not trigger historical backfill on read.
75. Stage 58 does not fabricate global fund coverage.
76. Directory search is bounded.
77. Directory filters are typed and validated.
78. Country semantics are explicit.
79. Currency filter semantics are explicit.
80. Fund type classification is canonical.
81. Exchange metadata is authoritative.
82. Fund pagination is deterministic.
83. Result counts are correctly scoped.
84. Stage 41 remains latest Quote authority.
85. Stage 42 remains Market Event authority.
86. Stage 43 remains WebSocket authority.
87. Stage 44 remains Quote freshness authority.
88. Stage 58 does not introduce a new WebSocket transport.
89. Stage 58 does not introduce a new Quote event type.
90. ETF Quote updates do not update official NAV.
91. Mutual funds do not receive synthetic realtime Quotes.
92. Stage 58 preserves source timestamps.
93. Stage 58 preserves NAV valuation dates.
94. Stage 58 preserves Provider provenance.
95. Stage 58 distinguishes unavailable from not applicable.
96. Stage 58 APIs are authenticated.
97. Stage 58 APIs enforce authorization.
98. Stage 58 APIs enforce financial-data entitlements.
99. Stage 58 directory reads are read-only.
100. Stage 58 uses bounded backend queries.
101. Stage 58 avoids N+1 reads.
102. Stage 58 uses shared Markets UI primitives.
103. Stage 58 uses ATLAS design tokens.
104. Stage 58 does not use purple gradients.
105. Stage 58 does not use emoji icons.
106. Stage 58 does not use fake fund ratings.
107. Stage 58 does not use fake NAV values.
108. Stage 58 does not use fake expense ratios.
109. Stage 58 does not use fake AUM values.
110. Stage 58 does not use fake holdings.
111. Stage 58 does not use fake fund returns.
112. Stage 58 does not use fake source labels.
113. Stage 58 does not create a new Agent panel.
114. Stage 58 does not create a new Bottom Taskbar.
115. Stage 58 does not create a new Search system.
116. Stage 58 does not create a new Command Palette.
117. Stage 58 does not create Watchlists.
118. Stage 58 does not create Alerts.
119. Stage 58 does not create Portfolios.
120. Stage 58 does not execute Trading.
121. Stage 58 does not execute Agents.
122. Stage 58 does not execute Workflows.
123. Stage 58 does not call LLMs on page load.
124. Stage 58 does not generate AI fund recommendations.
125. Stage 58 does not provide financial advice.
126. Stage 58 does not create another Provider credential store.
127. Stage 58 does not create unnecessary Redis keys.
128. Stage 58 does not create unnecessary ClickHouse tables.
129. Stage 58 does not create unnecessary workers.
130. Stage 58 uses minimal migrations only if genuinely required.
131. Stage 58 does not seed fake financial data.
132. Stage 58 supports partial-data states.
133. Stage 58 supports truthful missing-data states.
134. Stage 58 supports desktop, tablet and mobile.
135. Stage 58 supports Agent Dock open.
136. Stage 58 supports Bottom Taskbar open.
137. Stage 58 supports accessible tables and controls.
138. Stage 58 preserves cross-user data isolation.
139. Stage 58 must pass fund identity tests.
140. Stage 58 must pass Quote/NAV separation tests.
141. Stage 58 must pass currency tests.
142. Stage 58 must pass fee/AUM scope tests.
143. Stage 58 must pass authorization tests.
144. Stage 58 must pass relevant previous-stage regressions.
145. Stage 58 documentation must match actual implementation.
146. Stage 59 is the next canonical development stage.

## Stage 59: FX Markets V1 Architecture & Implementation

1. Stage 59 builds FX Markets V1.
2. FX remains within canonical Markets module 2.
3. The canonical route is `/markets/fx` integrated alongside Overview, Equities, and ETFs & Funds.
4. Markets Overview remains functional.
5. Equities remains functional.
6. ETFs & Funds remains functional.
7. The global AppShell remains unchanged.
8. FX uses canonical Financial Instrument UUIDs (`instrument_entity_id`).
9. Ticker text is not primary identity.
10. Base and Quote currency are explicit.
11. BASE/QUOTE means QUOTE units per BASE unit.
12. Pair orientation is never guessed.
13. Reverse conversion is a mathematical derivation, not necessarily a new Provider observation.
14. Currency identifiers use validated ISO 4217 reference metadata.
15. Fiat FX remains distinct from Cryptocurrency.
16. Precious-metal crosses are not silently ordinary fiat FX.
17. Spot FX remains distinct from forwards and derivatives.
18. Provider aliases are resolved through existing identifier infrastructure.
19. FX observations preserve Provider and series identity.
20. FX Provider observations are not a universal consolidated market price.
21. Reference fixings are distinct from spot bid/ask.
22. Indicative rates are distinct from executable rates.
23. Last-trade semantics are validated before use.
24. Bid and Ask remain separate.
25. Bid and Ask must be compatible.
26. Cross-Provider bid/ask mixing is prohibited.
27. Crossed bid/ask observations are not silently repaired.
28. Midpoint is explicitly derived.
29. Spread uses Decimal.
30. Spread calculation requires valid compatible bid/ask.
31. Spread basis points differ from pips.
32. Pip convention is not universally hardcoded.
33. FX quotation precision differs from ISO currency minor units.
34. Rate currencies and units are explicit.
35. Missing Quote is not zero.
36. Missing spread is not zero spread.
37. Missing change is not zero change.
38. FX percentage changes require qualified comparable references.
39. Equity previous-close rules are not blindly applied to FX.
40. Weekend and holiday semantics are respected where supported.
41. Reference rates are not mislabeled realtime.
42. Stage 44 remains freshness authority.
43. Source time remains distinct from receive time.
44. Data delay remains distinct from freshness.
45. WebSocket connection remains distinct from observation freshness.
46. Redis TTL does not establish freshness.
47. FX Directory uses canonical configured instruments.
48. Stage 59 does not claim full global FX coverage.
49. Stage 59 does not scrape pair lists.
50. Stage 59 does not create instruments on search.
51. Stage 59 does not invent Provider rate data.
52. Base currency filtering is canonical.
53. Quote currency filtering is canonical.
54. FX search is bounded.
55. FX pagination is deterministic.
56. Coverage counts are scoped.
57. Stage 59 reuses shared Markets read services.
58. Stage 59 reuses Stage 41 latest Quote state.
59. Stage 59 reuses Stage 39 historical data where compatible.
60. Stage 59 reuses Stage 42 Market Events.
61. Stage 59 reuses Stage 43 WebSockets.
62. Stage 59 does not create a second Quote cache.
63. Stage 59 does not create a second WebSocket client.
64. Stage 59 does not create another realtime event bus.
65. Stage 59 does not start upstream Provider streams on page load.
66. Stage 59 does not create ingestion targets on page load.
67. Stage 59 does not create historical jobs on page load.
68. Stage 59 does not query external Providers on every read.
69. Stage 59 includes a read-only indicative converter.
70. Conversion uses canonical existing observations.
71. Conversion arithmetic uses Decimal.
72. Base-to-quote conversion respects direction.
73. Quote-to-base conversion respects direction.
74. Bid/ask conversion direction is explicit.
75. Converter rate kind is explicit.
76. Converter Provider is explicit.
77. Converter timestamp is explicit.
78. Converter freshness/delay is explicit.
79. Converter amounts are validated.
80. Converter output rounding is documented.
81. Conversion is not a guaranteed executable offer.
82. Conversion does not include unverified bank fees.
83. Conversion does not place orders.
84. Conversion does not transfer money.
85. Conversion does not mutate Portfolios.
86. Conversion does not perform settlement.
87. Conversion does not infer tax-accounting rates.
88. Same-currency conversion is arithmetic identity.
89. Conversion does not silently triangulate.
90. Conversion does not create synthetic pair Entities.
91. Reverse conversion does not overwrite canonical Quote state.
92. Unsupported direct pair conversion returns unavailable.
93. FX APIs are authenticated.
94. FX APIs enforce authorization.
95. FX APIs enforce financial-data entitlements.
96. Conversion cannot bypass entitlements.
97. FX API pagination is bounded.
98. FX API inputs are strictly validated.
99. FX API reads cause no writes.
100. FX API reads cause no Provider fanout.
101. FX APIs do not place trades.
102. FX APIs do not invoke Agents.
103. FX APIs do not invoke Workflows.
104. FX APIs do not invoke LLMs.
105. FX uses the existing Markets table/filter primitives.
106. FX uses ATLAS design tokens.
107. FX does not use purple gradients.
108. FX does not use emoji icons.
109. FX does not use fabricated price charts.
110. FX does not use fake spreads.
111. FX does not use fake return percentages.
112. FX does not use fake liquidity.
113. FX does not use fake market-open status.
114. FX does not use fake trading volume.
115. FX does not use fake AI commentary.
116. FX preserves selected Entity context.
117. FX does not automatically select an arbitrary default pair.
118. FX uses canonical internal navigation.
119. FX does not add a global sidebar module.
120. FX preserves the Agent Dock.
121. FX preserves the Bottom Taskbar.
122. FX preserves Search.
123. FX preserves the Command Palette.
124. FX preserves Notification Center.
125. FX does not expand Personalized Activity tracking.
126. FX does not create Stage 54 tasks/approvals.
127. FX does not generate Stage 55 intelligence items.
128. Stage 60 remains responsible for Cryptocurrency.
129. Stage 61 remains responsible for Bonds.
130. Stage 62 remains responsible for Futures/Commodities.
131. Stage 63 remains responsible for Market Movers.
132. Stage 64 remains responsible for Heatmaps.
133. Stage 65 remains responsible for Cross-Asset Analytics.
134. Stage 66 remains responsible for Charts.
135. Stage 76 remains responsible for Watchlists.
136. Stage 80 remains responsible for Alerts.
137. Stage 94–98 remain responsible for Screeners.
138. Stage 110+ remains responsible for Portfolio analytics.
139. Stage 115+ remains responsible for Risk analytics.
140. Stage 141+ remains responsible for advanced quant functionality.
141. Stage 144+ remains responsible for Trading execution.
142. Stage 146+ remains responsible for Agents.
143. Stage 59 does not implement FX forwards.
144. Stage 59 does not implement FX swaps.
145. Stage 59 does not implement FX options.
146. Stage 59 does not implement carry-trade analytics.
147. Stage 59 does not implement cross-currency basis.
148. Stage 59 does not implement triangular arbitrage.
149. Stage 59 does not implement FX hedging execution.
150. Stage 59 does not implement leverage/margin management.
151. Stage 59 does not implement broker connectivity.
152. Stage 59 does not implement financial recommendations.
153. Stage 59 does not persist private rates in browser storage.
154. Stage 59 prevents cross-user entitlement leakage.
155. Stage 59 supports honest unavailable states.
156. Stage 59 supports partial-data states.
157. Stage 59 supports desktop, tablet and mobile.
158. Stage 59 supports Agent Dock and Bottom Taskbar layouts.
159. Stage 59 supports keyboard and screen-reader access.
160. Stage 59 uses only justified database changes.
161. Stage 59 does not seed fake data.
162. Stage 59 must pass FX direction tests.
163. Stage 59 must pass spread precision tests.
164. Stage 59 must pass conversion tests.
165. Stage 59 must pass authorization tests.
166. Stage 59 must pass previous-stage regressions.
167. Stage 59 documentation must match implementation.
168. Stage 60 is the next canonical development stage.

## Stage 60: Cryptocurrency Markets V1
1. Stage 60 builds Cryptocurrency Markets V1.
2. Cryptocurrency remains within Markets module 2.
3. The canonical route is `/markets/crypto` unless repository conventions require an equivalent.
4. Existing Markets routes remain functional.
5. The authenticated AppShell is reused.
6. No new global sidebar module is created.
7. Cryptocurrency uses canonical Entity UUIDs.
8. Asset identity is distinct from trading-pair identity.
9. Token contract identity is distinct from display symbol.
10. Blockchain network identity is explicit where applicable.
11. Contract addresses are network-scoped.
12. Native cryptocurrency does not require a token contract.
13. Wrapped assets remain distinct where modeled.
14. Bridged assets remain distinct where modeled.
15. Stablecoins remain distinct from fiat currency.
16. Stablecoin parity is not guaranteed or hardcoded.
17. Crypto symbols are not globally unique.
18. Symbol resolution reuses Stage 22.
19. Identifier infrastructure reuses Stage 21.
20. Existing Entity relationships remain authoritative.
21. Stage 60 does not auto-create assets from symbols.
22. Stage 60 does not auto-create tokens from arbitrary contracts.
23. Spot trading markets remain distinct from perpetuals.
24. Spot trading markets remain distinct from futures.
25. Spot trading markets remain distinct from options.
26. Crypto remains distinct from Stage 59 fiat FX.
27. Precious-metal instruments remain outside ordinary crypto spot classification.
28. Trading-pair base and quote are explicit.
29. BASE/QUOTE means QUOTE units per BASE.
30. BTC/USD and BTC/USDT remain distinct.
31. Reverse pairs are not automatically equivalent market listings.
32. No automatic synthetic pair inversion is stored.
33. No automatic cross-pair triangulation is implemented.
34. Venue identity is explicit.
35. Provider identity is explicit.
36. Different venue Quotes are not silently merged.
37. Provider aliases are venue-scoped.
38. Composite data is labeled explicitly.
39. Bid/ask data is not mixed across incompatible observations.
40. Crossed bid/ask observations are handled as inconsistent.
41. Latest trade price remains distinct from bid/ask/midpoint.
42. Stage 33 remains canonical Quote authority.
43. Stage 41 remains latest Quote state authority.
44. Stage 39 remains historical OHLCV authority.
45. Stage 42 remains Market Event transport authority.
46. Stage 43 remains WebSocket authority.
47. Stage 44 remains freshness authority.
48. Redis TTL is not observation freshness.
49. Socket connectivity is not observation freshness.
50. Source time remains distinct from received time.
51. Data delay remains distinct from freshness.
52. Quote units remain explicit.
53. Crypto price precision is not universally two decimals.
54. Tick size is not inferred from display decimals alone.
55. Quantity precision is distinct from price precision.
56. Backend financial arithmetic uses Decimal.
57. Frontend API preserves Decimal values safely.
58. Missing price is not zero.
59. Missing spread is not zero spread.
60. Missing 24h change is not zero movement.
61. Rolling 24h change is distinct from UTC-day change.
62. 24h change requires a qualified same-series reference.
63. 24h change does not mix quote assets.
64. 24h change does not mix venues without a defined methodology.
65. No fabricated 24h performance is displayed.
66. Base volume and quote volume remain distinct.
67. Volume units are explicit.
68. Rolling volume is distinct from calendar-day volume.
69. No false global venue-volume aggregation is performed.
70. Last price times base volume is not treated as authoritative quote volume.
71. No fabricated trade count is displayed.
72. Market cap is not derived without qualified circulating supply.
73. Circulating supply, total supply and max supply remain distinct.
74. FDV remains distinct from circulating market cap.
75. No fabricated global crypto ranking is displayed.
76. No fabricated total crypto market cap is displayed.
77. No fabricated BTC dominance is displayed.
78. Stablecoin prices are not normalized to a fixed peg.
79. No stablecoin issuer-risk engine is introduced.
80. No token-security verification is implied.
81. Stage 60 uses the canonical digital-asset catalog.
82. Stage 60 does not import unverified coin lists.
83. Stage 60 uses the canonical spot-market catalog.
84. Stage 60 does not claim complete global crypto coverage.
85. Search is bounded.
86. Token symbol ambiguity is handled explicitly.
87. Venue filtering is canonical.
88. Base-asset filtering is canonical.
89. Quote-asset filtering is canonical.
90. Crypto/fiat quote types are not conflated.
91. Pagination is deterministic.
92. Coverage counts are accurately scoped.
93. Stage 60 APIs require authentication.
94. Stage 60 APIs enforce authorization.
95. Stage 60 APIs enforce financial-data entitlements.
96. Stage 60 APIs do not invoke arbitrary Providers.
97. Stage 60 read APIs do not create Entities.
98. Stage 60 read APIs do not write Quotes.
99. Stage 60 read APIs do not create live targets.
100. Stage 60 read APIs do not create ingestion jobs.
101. Stage 60 read APIs do not execute trading.
102. Stage 60 read APIs do not invoke Agents.
103. Stage 60 read APIs do not invoke Workflows.
104. Stage 60 does not create a second Provider router.
105. Stage 60 does not create a second Quote cache.
106. Stage 60 does not create a second Market Event bus.
107. Stage 60 does not create a second global WebSocket client.
108. Stage 60 does not open upstream Provider sessions on page load.
109. Stage 60 does not build a new historical database.
110. Stage 60 avoids unnecessary database migrations.
111. Stage 60 does not seed fictional crypto market data.
112. Stage 60 may add minimal canonical asset/venue metadata only when justified.
113. Stage 60 UI uses the existing Markets architecture.
114. Stage 60 UI uses the existing ATLAS design system.
115. Stage 60 does not use purple gradients.
116. Stage 60 does not use emoji icons.
117. Stage 60 does not use fabricated candlestick charts.
118. Stage 60 does not use fake market-volume statistics.
119. Stage 60 does not use fake market-cap rankings.
120. Stage 60 does not use fake Provider health.
121. Stage 60 does not use fake live status.
122. Stage 60 does not use fake risk scores.
123. Stage 60 does not use AI investment recommendations.
124. Stage 60 does not implement wallet connection.
125. Stage 60 does not request private keys or seed phrases.
126. Stage 60 does not sign blockchain transactions.
127. Stage 60 does not connect exchange trading accounts.
128. Stage 60 does not execute orders.
129. Stage 60 does not perform token swaps.
130. Stage 60 does not provide leverage/margin management.
131. Stage 60 does not build derivatives trading.
132. Stage 60 does not build an order-book engine.
133. Stage 60 does not build an on-chain indexing engine.
134. Stage 60 does not build DeFi analytics.
135. Stage 60 does not build staking-yield analytics.
136. Stage 60 does not build wallet tracking.
137. Stage 60 does not build blockchain explorer functionality.
138. Stage 60 does not build autonomous trading bots.
139. Stage 60 does not build a full crypto screener.
140. Stage 60 does not create Watchlists.
141. Stage 60 does not create Alerts.
142. Stage 60 does not create Portfolios.
143. Stage 60 does not create Risk analytics.
144. Stage 60 does not create AI financial actions.
145. Stage 60 does not execute LLM inference on page load.
146. Stage 60 preserves Stage 25 selected Entity.
147. Stage 60 preserves the global Search.
148. Stage 60 preserves the Command Palette.
149. Stage 60 preserves the Agent Dock.
150. Stage 60 preserves the Bottom Taskbar.
151. Stage 60 preserves the Notification Center.
152. Stage 60 does not expand Personalized Activity collection.
153. Stage 60 does not generate tasks/approvals.
154. Stage 60 does not generate unsupported Intelligence events.
155. Stage 60 supports truthful unavailable states.
156. Stage 60 supports partial market-data coverage.
157. Stage 60 supports desktop, tablet and mobile.
158. Stage 60 supports accessible controls.
159. Stage 60 prevents cross-user entitlement leakage.
160. Stage 60 does not persist private Quote data in browser storage.
161. Stage 60 must pass crypto identity tests.
162. Stage 60 must pass spot-vs-derivative tests.
163. Stage 60 must pass venue-scoping tests.
164. Stage 60 must pass stablecoin distinction tests.
165. Stage 60 must pass Decimal precision tests.
166. Stage 60 must pass 24h change tests.
167. Stage 60 must pass volume semantics tests.
168. Stage 60 must pass authorization tests.
169. Stage 60 must pass relevant prior-stage regressions.
170. Stage 60 documentation must match actual implementation.
171. Stage 61 is the next canonical development stage.

## Stage 61: Bonds & Fixed-Income Markets V1
1. Stage 61 builds Bonds & Fixed-Income Markets V1.
2. Bonds remains within Markets module 2.
3. The preferred route is `/markets/bonds`.
4. Previous Markets sections remain functional.
5. Existing AppShell remains authoritative.
6. Bond identity uses canonical Financial Instrument UUID.
7. Issuer identity remains distinct from Bond Security identity.
8. Legal issuer remains distinct from guarantor.
9. Tranches are not merged.
10. Identifiers reuse Stage 21.
11. Resolution reuses Stage 22.
12. Issuer relationships reuse Stage 23.
13. Provenance reuses Stage 24.
14. Selection reuses Stage 25.
15. Bond ticker is not a primary key.
16. ISIN is validated where supported.
17. CUSIP licensing constraints are respected.
18. Bond classification uses canonical types.
19. Treasury bills are not assumed coupon-bearing.
20. Missing coupon is not zero coupon.
21. Fixed and floating coupons remain distinct.
22. Perpetual securities do not receive invented maturities.
23. Maturity date is not duration.
24. Past maturity is not automatically default.
25. Bond currency remains explicit.
26. Principal currency and quote currency are not silently conflated.
27. Face value and minimum denomination remain distinct.
28. Price basis is explicit.
29. Clean price remains distinct from dirty price.
30. Accrued interest remains distinct from market price.
31. Price quote units are explicit.
32. Price per 100 face is not an absolute security cost.
33. Clean/dirty arithmetic requires compatible units.
34. Accrued-interest settlement date is explicit.
35. Day-count conventions are not guessed.
36. Coupon schedules are not fabricated.
37. Ex-coupon rules are not ignored when calculating accrued interest.
38. Floating-reset assumptions are not invented.
39. Amortizing principal is not assumed constant.
40. Price kind is preserved.
41. Trade price remains distinct from evaluated price.
42. Evaluated price is not mislabeled an executed trade.
43. OTC market coverage is not presented as consolidated exchange coverage.
44. A bond may not have continuous realtime observations.
45. Stage 33 canonical Market Data is reused where semantically compatible.
46. Stage 41 latest Quote is reused where applicable.
47. Stage 39 historical references are reused where compatible.
48. Stage 44 remains freshness authority.
49. Stage 42 remains Market Event authority.
50. Stage 43 remains WebSocket authority.
51. No synthetic bond streaming is introduced.
52. No second Quote cache is created.
53. No second event transport is created.
54. No second global WebSocket is created.
55. Quote compatibility includes bond price basis.
56. Bid/ask compatibility includes units and Provider series.
57. Different price bases are not mixed.
58. Bond prices are Decimal-safe.
59. Coupon rate remains distinct from yield.
60. Source yield types are explicit.
61. YTM is not inferred from generic yield labels.
62. YTW remains distinct from YTM.
63. YTC remains distinct from YTM.
64. Discount yield remains distinct from conventional coupon-bond yield.
65. Negative yield values are supported where valid.
66. Zero yield remains distinct from missing yield.
67. Missing yield is not replaced by coupon.
68. Yield-scale conventions are explicit.
69. Yield basis-point changes are distinct from price percentage changes.
70. No generalized YTM solver is introduced.
71. No generalized bond pricing engine is introduced.
72. No general coupon cash-flow engine is introduced.
73. No yield-curve bootstrapping is introduced.
74. No duration engine is introduced.
75. No convexity engine is introduced.
76. No DV01/PV01 engine is introduced.
77. No credit-risk model is introduced.
78. No bond portfolio optimization is introduced.
79. No bond trading system is introduced.
80. No dealer RFQ engine is introduced.
81. No settlement instruction engine is introduced.
82. Stage 61 directory uses canonical Security data.
83. Stage 61 does not scrape unverified bond lists.
84. Stage 61 does not create Securities on search.
85. Issuer type filters use canonical classification.
86. Currency filters use verified denomination data.
87. Coupon type filters use verified contractual metadata.
88. Maturity filters use actual dates.
89. Perpetuals are not assigned artificial maturity.
90. Directory pagination is bounded.
91. Result ordering is deterministic.
92. Coverage counts are scoped.
93. Price observations preserve source timestamps.
94. Evaluated prices preserve valuation dates.
95. Receive timestamps remain distinct.
96. Redis TTL is not freshness.
97. WebSocket connectivity is not freshness.
98. Bond observation freshness may differ from equities.
99. Unknown freshness is not labeled realtime.
100. Unknown Provider delay is not invented.
101. Provider provenance is preserved.
102. Licensed data entitlements are enforced.
103. Bond APIs require authentication.
104. Bond APIs require authorization.
105. Read APIs do not write financial data.
106. Read APIs do not trigger Provider fanout.
107. Read APIs do not create ingestion targets.
108. Read APIs do not create background jobs.
109. Read APIs do not execute trading.
110. Read APIs do not run Agents.
111. Read APIs do not run Workflows.
112. Read APIs do not call LLMs.
113. Bond Inspector uses actual canonical data.
114. Issuer navigation requires a verified relationship.
115. The Markets design system is reused.
116. No new global sidebar module is created.
117. Global Search is reused.
118. Command Palette is preserved.
119. Agent Dock is preserved.
120. Bottom Taskbar is preserved.
121. Notification Center is preserved.
122. Selected Entity Context remains authoritative.
123. No purple gradients are introduced.
124. No emoji icons are introduced.
125. No fake yield curves are displayed.
126. No fabricated bond prices are displayed.
127. No fabricated yields are displayed.
128. No fabricated credit ratings are displayed.
129. No fabricated coupon schedules are displayed.
130. No fabricated accrued interest is displayed.
131. No fabricated liquidity metrics are displayed.
132. Missing financial data is not displayed as zero.
133. Partial-data states are supported.
134. Authentication cache isolation is preserved.
135. No private licensed pricing is persisted in browser storage.
136. Stage 62 remains responsible for Futures/Commodities.
137. Stage 63 remains responsible for Market Movers.
138. Stage 64 remains responsible for Heatmaps.
139. Stage 65 remains responsible for Cross-Asset.
140. Stage 66 remains responsible for Charts V1.
141. Stage 76 remains responsible for Watchlists.
142. Stage 80 remains responsible for Alerts.
143. Stage 94–98 remain responsible for Screeners.
144. Stage 110+ remains responsible for Portfolios.
145. Stage 115+ remains responsible for Risk.
146. Stage 118 remains responsible for advanced fixed-income risk.
147. Stage 141+ remains responsible for Options/Quant.
148. Stage 142 will introduce QuantLib.
149. Stage 144+ remains responsible for Trading.
150. Stage 146+ remains responsible for Agents.
151. No unnecessary database migration is created.
152. No fake bond records are seeded.
153. Stage 61 supports desktop, tablet and mobile.
154. Stage 61 supports keyboard accessibility.
155. Stage 61 supports screen readers.
156. Stage 61 supports Agent Dock open.
157. Stage 61 supports Bottom Taskbar open.
158. Stage 61 must pass Security identity tests.
159. Stage 61 must pass coupon/maturity tests.
160. Stage 61 must pass clean/dirty price tests.
161. Stage 61 must pass yield-type tests.
162. Stage 61 must pass accrued-interest safeguards.
163. Stage 61 must pass authorization tests.
164. Stage 61 must pass relevant prior-stage regressions.
165. Stage 61 documentation must match implementation.
166. Stage 62 is the next canonical stage.

## Stage 62 — Futures & Commodities Markets V1 Decisions

1. Stage 62 builds Futures & Commodities Markets V1.
2. Futures remains within Markets module 2.
3. The preferred route is `/markets/futures`.
4. Existing Markets sections (Stages 56–61) remain functional.
5. Existing AppShell remains authoritative.
6. Commodity Underlying identity is distinct from Futures Product.
7. Futures Product identity is distinct from individual Futures Contract.
8. Spot Benchmark identity is distinct from Futures price.
9. Individual contracts use canonical UUIDs.
10. Underlying relationships reuse Stage 23.
11. Identifiers reuse Stage 21.
12. Alias resolution reuses Stage 22.
13. Provenance reuses Stage 24.
14. Selected Entity reuse follows Stage 25.
15. Futures symbols are not primary keys.
16. Product roots are venue-scoped.
17. Contract month includes full year.
18. Single-digit year ambiguity is not guessed.
19. Month-code parsing does not create canonical contracts.
20. Contract month is distinct from expiration.
21. Last trading day is distinct from expiration.
22. Notice dates are separate.
23. Delivery dates are separate.
24. Final settlement date is separate.
25. Expired contract identity is preserved.
26. Expiration does not trigger automatic rollover.
27. Continuous Futures are not constructed.
28. Historical prices remain contract-specific.
29. Commodity grades are distinct where material.
30. Delivery/assessment locations are preserved.
31. Spot benchmarks are not inferred from Futures.
32. No universal physical commodity price is invented.
33. Exchanges and Providers are distinct.
34. MIC data is validated.
35. Exchange-specific contract specs are preserved.
36. Contract size is explicit.
37. Contract unit is explicit.
38. Price quotation unit is explicit.
39. Quotation currency is explicit.
40. Tick size is not inferred from decimals.
41. Tick value requires compatible units.
42. Contract multipliers are validated.
43. Physical settlement is distinct from cash settlement.
44. Unknown settlement type remains Unknown.
45. Exchange specifications may be effective-dated.
46. Last Trade is distinct from Settlement.
47. Preliminary Settlement is distinct from Final Settlement.
48. Settlement trade date is preserved.
49. Settlement publication time is preserved where available.
50. Bid/Ask observations remain separate.
51. Incompatible bid/ask values are not mixed.
52. Futures prices may legitimately be negative.
53. Zero Futures prices are not automatically missing.
54. Negative price support does not weaken other asset-class validation.
55. Percentage change is suppressed for invalid/nonpositive references unless a validated policy exists.
56. Absolute price change preserves quotation units.
57. Tick-based change requires verified tick size.
58. No automatic account P&L is calculated.
59. No Futures roll return is calculated.
60. Same-contract reference is required.
61. Previous settlement is used only when methodologically valid.
62. Different contract months are not compared as one series.
63. Volume counts contracts under verified source definitions.
64. Volume windows are explicit.
65. Open interest is distinct from volume.
66. Open interest as-of date is preserved.
67. Open interest is not automatically realtime.
68. Missing volume is not zero.
69. Missing open interest is not zero.
70. No global liquidity ranking is fabricated.
71. Stage 33 canonical Market Data is reused.
72. Stage 39 historical data is reused.
73. Stage 40 update workers are reused.
74. Stage 41 latest Quote state is reused.
75. Stage 42 event transport is reused.
76. Stage 43 WebSocket infrastructure is reused.
77. Stage 44 freshness remains authoritative.
78. No new global WebSocket is created.
79. No new Quote cache is created.
80. No new event bus is created.
81. No new historical database is created.
82. No uncontrolled Provider polling is added.
83. Provider capabilities are verified.
84. Provider aliases remain source-scoped.
85. Frontend page views do not create upstream sessions.
86. Contract directory is canonical and read-only.
87. Search does not create contracts.
88. Filters are validated.
89. Pagination is bounded.
90. Ordering is deterministic.
91. Coverage counts are scoped.
92. Contract specifications are sourced.
93. Missing specs are not invented.
94. Market observations preserve Provider provenance.
95. Source timestamps are distinct from receive times.
96. Settlement dates are distinct from Quote timestamps.
97. Redis TTL does not imply freshness.
98. WebSocket connectivity does not imply freshness.
99. Unknown freshness is not labeled Live.
100. Exchange sessions are not guessed.
101. APIs require authentication.
102. APIs enforce authorization.
103. APIs enforce exchange/Provider entitlements.
104. APIs do not perform arbitrary upstream fetches.
105. APIs do not write on read.
106. APIs do not create ingestion jobs on read.
107. APIs do not create live targets on read.
108. APIs do not execute trading.
109. APIs do not execute margin operations.
110. APIs do not execute physical delivery instructions.
111. APIs do not invoke Agents.
112. APIs do not invoke Workflows.
113. APIs do not call LLMs on page load.
114. Frontend reuses ATLAS design tokens.
115. No purple gradients are introduced.
116. No emoji icons are introduced.
117. No fabricated settlement values are displayed.
118. No fabricated contract volumes are displayed.
119. No fabricated open interest is displayed.
120. No fabricated market curves are displayed.
121. No fabricated trading opportunities are displayed.
122. No fabricated spot benchmarks are displayed.
123. No fake market-open status is displayed.
124. No fake global commodity statistics are displayed.
125. No Futures trading buttons are added.
126. No Futures Options analytics are introduced.
127. No margin engine is introduced.
128. No continuous Futures roll engine is introduced.
129. No contango/backwardation engine is introduced.
130. No cost-of-carry valuation engine is introduced.
131. No Futures portfolio accounting is introduced.
132. No physical supply analytics is introduced.
133. No warehouse inventory tracking is introduced.
134. No shipping logistics system is introduced.
135. Stage 63 remains responsible for Market Movers.
136. Stage 64 remains responsible for Heatmaps.
137. Stage 65 remains responsible for Cross-Asset.
138. Stage 66 remains responsible for Charts.
139. Stage 76 remains responsible for Watchlists.
140. Stage 80 remains responsible for Alerts.
141. Stage 94–98 remain responsible for Screeners.
142. Stage 110+ remains responsible for Portfolios.
143. Stage 115+ remains responsible for Risk.
144. Stage 141+ remains responsible for Options.
145. Stage 142 remains responsible for QuantLib.
146. Stage 143 remains responsible for Backtesting.
147. Stage 144 remains responsible for Paper Trading.
148. Stage 145 remains responsible for Broker Sandbox.
149. Stage 146+ remains responsible for Agents.
150. Stage 62 uses minimal justified migrations.
151. Stage 62 does not seed fake market records.
152. Stage 62 supports truthful unavailable states.
153. Stage 62 supports partial-data states.
154. Stage 62 supports desktop, tablet and mobile.
155. Stage 62 supports accessible table and Inspector controls.
156. Stage 62 preserves Agent Dock and Bottom Taskbar.
157. Stage 62 preserves global Search and Command Palette.
158. Stage 62 preserves authentication cache isolation.
159. Stage 62 does not persist private Quotes in browser storage.
160. Stage 62 must pass contract identity tests.
161. Stage 62 must pass quotation-unit tests.
162. Stage 62 must pass tick-value tests.
163. Stage 62 must pass negative Futures price tests.
164. Stage 62 must pass settlement distinction tests.
165. Stage 62 must pass volume/open-interest tests.
166. Stage 62 must pass authorization tests.
167. Stage 62 must pass relevant prior-stage regressions.
168. Stage 62 documentation must match implementation.
169. Stage 63 is the next canonical development stage.

---

# STAGE 63 — MARKET MOVERS V1 DECISIONS

### Product and Architecture
1. Stage 63 builds Market Movers V1.
2. Market Movers remains within Markets module 2.
3. Canonical route is `/markets/movers`.
4. Previous Markets modules remain functional (`/markets`, `/markets/equities`, `/markets/funds`, `/markets/fx`, `/markets/crypto`, `/markets/bonds`, `/markets/futures`).
5. Existing AppShell is reused.
6. Existing Sidebar is preserved.
7. Existing Agent Dock is preserved.
8. Existing Bottom Taskbar is preserved.
9. Existing Global Search is reused.
10. Existing Selected Entity Context is reused.
11. Market Movers introduces no new canonical financial instrument identity.
12. Universe membership uses canonical IDs.
13. Ranking grain is explicit (listing / venue-scoped market series).
14. Exchange/venue scope is explicit.
15. Ranking universe is explicitly defined.

### Ranking Integrity
16. Every ranking requires a qualified metric.
17. Every ranking requires a qualified period.
18. Every ranking requires a defined universe.
19. Rankings are computed after eligibility validation.
20. Rankings are not created by sorting one arbitrary directory page.
21. Rankings do not claim worldwide coverage without evidence.
22. Incomplete coverage is disclosed.
23. Candidate truncation is disclosed.
24. Qualified counts are reported.
25. Exclusion reasons are reported.
26. Ranking snapshot time is explicit.
27. Ranking source time remains distinct.
28. Ranking methods are versioned where necessary.
29. Ranking order is deterministic.
30. Tie-breaking uses canonical identity.
31. Full Decimal precision is used before sorting.
32. Pagination preserves snapshot consistency.

### Top Gainers and Losers
33. Gainers require qualified positive returns.
34. Losers require qualified negative returns.
35. Zero returns are not automatically classified as gainers or losers.
36. Reference denominator must be valid.
37. Current/reference observations must be compatible.
38. Source/series identity must be compatible.
39. Observation units must be compatible.
40. Comparison windows must be compatible.
41. Corporate-action mismatches are not ignored.
42. Missing reference is not zero change.
43. Missing current Quote is not zero change.
44. Invalid returns are excluded.
45. NaN and Infinity are prohibited.
46. Large genuine returns are not arbitrarily capped.

### Most Active
47. Most Active requires a typed activity metric.
48. Shares are not contracts.
49. Base volume is not quote volume.
50. Stablecoin volume is not automatically USD volume.
51. Volume intervals are explicit.
52. Volume units are explicit.
53. Missing volume is not zero.
54. Open interest is not trading volume.
55. Last price multiplied by volume is not automatically authoritative turnover.
56. Cross-asset volume metrics are not silently ranked together.
57. Invalid activity combinations are disabled.

### Asset Class Policies
58. Equity moves reuse qualified previous-session references.
59. Equity session definitions follow existing shared services.
60. Equity corporate-action adjustment bases must be compatible.
61. ETF moves use exchange prices rather than NAV.
62. Mutual-fund NAV changes are not mixed into live ETF/equity rankings.
63. FX movers preserve pair orientation.
64. FX movers preserve rate kind.
65. FX Most Active is unavailable without actual compatible activity data.
66. Cryptocurrency movers use qualified rolling 24-hour data where available.
67. Cryptocurrency venue identity is preserved.
68. BTC/USD and BTC/USDT remain distinct.
69. Stablecoin parity is not assumed.
70. Cryptocurrency volumes require compatible units.
71. Bond yields are not stock-style percentage price changes.
72. Bond clean and dirty prices are not mixed.
73. Evaluated and trade prices are not assumed equivalent.
74. Futures rankings preserve individual expirations.
75. Futures do not auto-roll contracts.
76. Nonpositive Futures reference prices are handled conservatively.
77. Futures activity uses actual contract-volume semantics.
78. Spot benchmarks are not mixed with Futures contract prices.

### Data Infrastructure
79. Existing Stage 33 Market Data is reused.
80. Existing Stage 39 historical data is reused.
81. Existing Stage 41 latest Quote state is reused.
82. Existing Stage 42 Market Event pipeline is reused.
83. Existing Stage 43 WebSocket infrastructure is reused.
84. Stage 44 remains data freshness authority.
85. Existing Provider routing is reused.
86. Existing Provenance is reused.
87. No duplicate Quote cache is created.
88. No new market event bus is created.
89. No new historical market database is created.
90. No uncontrolled Provider polling is introduced.
91. Ranking computation does not use unbounded Redis key scans.
92. Ranking computation uses bounded batch reads.
93. Ranking cache is derived and non-authoritative.
94. Ranking cache TTL is not market-data freshness.
95. Full ranking is not recalculated on every UI Quote event without controls.
96. Large universes use documented bounded/scalable calculation strategies.
97. Expired ranking snapshots are handled explicitly.
98. Snapshot cursors are validated.

### Authorization and Security
99. Movers APIs require authentication.
100. Movers APIs enforce authorization.
101. Movers APIs enforce market-data entitlements.
102. Derived return values cannot bypass data entitlements.
103. Ranking caches cannot leak cross-user information.
104. Read APIs do not mutate canonical Quotes.
105. Read APIs do not create market instruments.
106. Read APIs do not trigger new ingestion jobs.
107. Read APIs do not create live targets.
108. Read APIs do not execute trading.
109. Read APIs do not run Agents.
110. Read APIs do not run Workflows.
111. Read APIs do not call LLMs.
112. No arbitrary Provider calls are exposed.
113. No arbitrary SQL is accepted.
114. No unsafe HTML rendering is permitted.
115. No licensed data is persisted insecurely in browser storage.

### UI
116. ATLAS design tokens are reused.
117. No purple gradients are introduced.
118. No emoji icons are introduced.
119. No fake financial statistics are shown.
120. No fake worldwide rankings are shown.
121. No fake real-time indicators are shown.
122. No fake trading signals are shown.
123. No animated speculative counters are shown.
124. Ranking universe is visible.
125. Metric window is visible.
126. Coverage is visible.
127. Ranking calculation time is visible.
128. Provider provenance is accessible.
129. Data delay is visible.
130. Partial ranking status is visible.
131. Unsupported metric combinations are explained.
132. Canonical Entity selection is preserved.
133. Accessible keyboard navigation is required.
134. Responsive layouts are required.
135. Live updates must not constantly disrupt navigation.

### Roadmap Boundaries
136. Stage 64 owns Heatmaps.
137. Stage 65 owns Cross-Asset Analytics.
138. Stage 66 owns Charts.
139. Stage 76 owns Watchlists.
140. Stage 80 owns Alerts.
141. Stage 94–98 own Screeners.
142. Stage 110+ owns Portfolios.
143. Stage 115+ owns Risk.
144. Stage 143 owns Backtesting.
145. Stage 144 owns Paper Trading.
146. Stage 145 owns Broker Sandbox.
147. Stage 146+ owns Agents.
148. Stage 63 does not implement investment recommendations.
149. Stage 63 does not implement momentum-trading strategies.
150. Stage 63 does not implement alert notifications.
151. Stage 63 does not implement a heatmap engine.
152. Stage 63 does not implement multi-factor Screeners.
153. Stage 63 does not implement a cross-asset composite score.
154. Stage 63 does not implement automatic portfolio actions.
155. Stage 63 does not introduce unnecessary schema migrations.
156. Stage 63 does not seed fabricated ranking results.
157. Stage 63 tests must verify ranking correctness.
158. Stage 63 tests must verify coverage truthfulness.
159. Stage 63 tests must verify data entitlements.
160. Stage 63 documentation must match actual implementation.
161. Stage 64 is the next canonical stage.

## Stage 64 Decisions - Market Heatmaps V1

### Product and Navigation
1. Stage 64 builds Market Heatmaps V1.
2. Heatmaps remains within Markets module 2.
3. Canonical route is `/markets/heatmaps`.
4. All previous Markets routes remain functional.
5. Existing AppShell is reused.
6. No new global module is added.
7. Selected Entity Context is reused.
8. Global Search is reused.
9. Agent Dock is preserved.
10. Bottom Taskbar is preserved.

### Data and Universe
11. Heatmaps use canonical Financial Instrument identities.
12. Universe membership is explicit.
13. Ranking grain is explicit.
14. Exchange/venue scope is explicit.
15. Stage 63 universe and metric qualification are reused.
16. Stage 63 Top N results are not treated as a full market universe.
17. Incomplete coverage is disclosed.
18. Candidate truncation is disclosed.
19. Authorized scope is enforced.
20. Source provenance is preserved.
21. Comparison windows are explicit.
22. Missing performance is not zero performance.
23. Stale/unknown data is conservatively handled.
24. Data delays remain visible.
25. Heatmap calculation time is distinct from Quote time.

### Visualization Modes
26. Equal-size heatmap is the baseline.
27. Equal-size tile area has no financial-size meaning.
28. Weighted treemap is conditional on verified weights.
29. Market Cap Weighted means verified market capitalization.
30. Arbitrary weights are prohibited.
31. Unsupported weighting does not silently fall back while retaining the label.
32. Color and area represent separate quantities.
33. Weight normalization is deterministic.
34. Weight units are explicit.
35. Weight as-of dates are preserved.
36. Weight currency compatibility is required.
37. Cross-currency normalization is not guessed.
38. Float-adjusted and full market cap remain distinct.
39. Multi-listed capitalization is not double-counted without methodology.
40. ETF AUM is not equity market cap.
41. Crypto FDV is not circulating market cap.
42. Futures open interest is not market cap.
43. Bond principal is not market cap.
44. Missing weight is not assigned an arbitrary positive value.
45. Invalid weights are rejected.
46. Weight coverage is disclosed.
47. Unknown weighted completeness remains unknown.

### Color and Performance
48. Tile color uses qualified metric values.
49. Positive values use appropriate positive colors.
50. Negative values use appropriate negative colors.
51. Zero is distinct from unavailable.
52. Missing values use an explicit unavailable treatment.
53. Color domains are documented.
54. Saturation does not alter actual numeric returns.
55. Color scales remain stable under ordinary realtime changes.
56. Color meaning is accessible without hue.
57. Financial calculations use Decimal.
58. Display rounding does not alter qualification or grouping.
59. Asset-class comparison periods are not mixed.
60. Bond yield changes are not relabeled price returns.
61. Futures negative references are handled safely.
62. FX pair orientation is preserved.
63. Crypto venue/quote-asset identity is preserved.
64. Mutual fund NAV changes are not treated as intraday exchange prices.

### Sector and Industry
65. Sector grouping requires authoritative classification.
66. Industry grouping requires authoritative classification.
67. GICS and ICB are not silently merged.
68. Classification codes are stable identifiers.
69. Effective-dated taxonomy is respected where supported.
70. Missing sector is not guessed.
71. Unclassified members are disclosed.
72. Equal-size grouped area represents member count, not market cap.
73. Weighted group area represents qualified sum of member weights.
74. Sector performance is explicitly method-labeled.
75. Equal-weight mean is not cap-weighted return.
76. Cap-weighted return requires verified compatible weights.
77. Group aggregation is not called an official market index.
78. Insufficient constituent coverage produces partial/unavailable status.

### Layout and Interaction
79. Layout is deterministic for a fixed snapshot and viewport.
80. Area proportions respect qualified weights.
81. No overlapping rectangles are permitted.
82. Tiny tiles do not show unreadable labels.
83. Instrument access is retained despite tiny tile size.
84. Tile selection uses canonical UUID.
85. Group drilldown uses actual hierarchy.
86. Breadcrumbs are required for drilldown.
87. Hover/focus details preserve provenance.
88. Keyboard interaction is required.
89. A nonvisual accessible table is required.
90. Geometry is not recomputed for color-only changes.
91. No decorative 3D heatmap is introduced.
92. Visualization dependencies must be justified.

### Snapshot and Realtime
93. A heatmap uses a coherent snapshot.
94. Snapshot IDs are stable.
95. Snapshot calculation time is explicit.
96. Source observation times are preserved.
97. Derived snapshots are non-authoritative.
98. Cache TTL does not imply Quote freshness.
99. Existing Stage 41 Quote state is reused.
100. Existing Stage 42 events are reused.
101. Existing Stage 43 WebSockets are reused.
102. Stage 44 remains freshness authority.
103. No second global socket is created.
104. No new Quote cache is created.
105. No independent event bus is created.
106. Realtime refresh is bounded.
107. Stale HTTP snapshots do not overwrite newer snapshots.
108. Bursty events are coalesced.
109. No full-universe browser subscriptions are opened without capacity controls.
110. Reconnect uses authoritative snapshot refresh.

### Security
111. APIs require authentication.
112. Authorization is enforced.
113. Financial-data entitlements are enforced.
114. Derived colors do not bypass price entitlements.
115. Derived area weights do not bypass fundamental-data entitlements.
116. Cache isolation prevents cross-user leakage.
117. No arbitrary Provider calls are exposed.
118. No arbitrary SQL is accepted.
119. No unsafe HTML rendering is permitted.
120. No Provider credentials are exposed.
121. No canonical financial-data writes occur on read.
122. No ingestion jobs are created on page view.
123. No live targets are created on page view.
124. No Trading occurs.
125. No Agent execution occurs.
126. No Workflow execution occurs.
127. No LLM calls are required.

### UI
128. ATLAS design tokens are reused.
129. Dark/light modes are supported.
130. No purple gradients are introduced.
131. No emoji icons are introduced.
132. No fake market-cap statistics are introduced.
133. No fake sector classifications are introduced.
134. No fake price changes are introduced.
135. No fake global coverage claims are introduced.
136. No fake trading signals are introduced.
137. Legend is visible.
138. Scope is visible.
139. Coverage is visible.
140. Snapshot time is visible.
141. Data freshness/delay is visible.
142. Source metadata is accessible.
143. Keyboard and screen-reader alternatives exist.
144. Responsive behavior is required.

### Roadmap Scope
145. Stage 65 owns Cross-Asset Analytics.
146. Stage 66 owns Charts.
147. Stage 76 owns Watchlists.
148. Stage 80 owns Alerts.
149. Stage 94–98 own Screeners.
150. Stage 110+ owns Portfolios.
151. Stage 115+ owns Risk.
152. Stage 129+ owns geospatial Maps layers.
153. Stage 135+ owns Universal Event intelligence.
154. Stage 143 owns Backtesting.
155. Stage 144 owns Paper Trading.
156. Stage 145 owns Broker Sandbox.
157. Stage 146+ owns autonomous Agents.
158. No portfolio exposure heatmaps are introduced.
159. No geospatial choropleths are introduced.
160. No cross-asset correlation matrices are introduced.
161. No predictive AI ratings are introduced.
162. No trading strategies are introduced.
163. No unnecessary new database infrastructure is created.
164. No fabricated production data is seeded.
165. Stage 64 must pass financial visualization tests.
166. Stage 64 must pass weight integrity tests.
167. Stage 64 must pass coverage tests.
168. Stage 64 must pass authorization tests.
169. Stage 64 must pass prior-stage regressions.
170. Stage 64 documentation must match actual implementation.
171. Stage 65 is the next canonical stage.

## Stage 65 Decisions - Cross-Asset Markets V1

### Product and Navigation
1. Stage 65 builds Cross-Asset Markets V1.
2. Cross-Asset remains within Markets module 2.
3. Canonical route is `/markets/cross-asset`.
4. All previous Markets routes remain functional.
5. Existing AppShell is reused.
6. No new global module is created.
7. Existing Selected Entity Context is reused.
8. Global Search is reused.
9. Agent Dock is preserved.
10. Bottom Taskbar is preserved.

### Identity
11. Canonical Financial Instrument UUIDs remain authoritative.
12. Market-series identity is explicit.
13. Benchmark identity is distinct from proxy identity.
14. ETF proxies are not silently presented as underlying indexes.
15. Futures contracts are not interchangeable with spot benchmarks.
16. Crypto venue-specific spot pairs remain distinct.
17. FX pair orientation is preserved.
18. Bond Security remains distinct from issuer.
19. No ticker-based primary keys are introduced.
20. No fictional benchmark records are created.

### Analytical Modes
21. Native Overview and Aligned Price Performance are distinct modes.
22. Native metrics preserve their units.
23. Bond yield bps are not treated as price returns.
24. Futures settlement changes are not automatically investor ROI.
25. FX rate changes are not automatically currency investment total returns.
26. Crypto native rolling 24h returns are not automatically aligned with stock previous-session returns.
27. Mutual fund NAV observations are not mislabeled intraday market prices.
28. No arbitrary cross-asset scoring is introduced.
29. No unsupported global risk sentiment scores are introduced.

### Time Alignment
30. Strict aligned comparison uses explicit UTC start/end instants.
31. Requested times are distinct from effective observation times.
32. Alignment tolerance is explicit.
33. No look-ahead is permitted.
34. Market closures are not filled with invented prices.
35. Weekend differences are respected.
36. Exchange holidays are respected.
37. Futures trading-date conventions are preserved.
38. Bond valuation dates remain distinct.
39. Sparse observations may be excluded.
40. Last-known values are not automatically synchronized.
41. Alignment qualification happens before return calculation.
42. Alignment exclusions are reported.
43. Unsupported comparison windows are disabled.

### Financial Calculation
44. Aligned percentage price return uses compatible observations.
45. Financial arithmetic uses Decimal.
46. Same instrument/series identity is required.
47. Compatible quote units are required.
48. Compatible price types are required.
49. Compatible adjustment bases are required.
50. Corporate-action mismatches are not ignored.
51. Missing values are not zero.
52. Invalid denominators are rejected.
53. NaN/Infinity are prohibited.
54. Negative Futures reference prices are handled conservatively.
55. No synthetic Futures roll is created.
56. Price return is distinct from total return.
57. Local-currency price return is explicitly labeled.
58. Local-currency return is not automatically USD investor return.
59. Cross-currency conversion requires verified rates/timing/methodology.
60. No unsupported common-currency return is displayed.
61. Stablecoin parity is not assumed.
62. Bond yields are not mathematically transformed into price returns without actual compatible prices.
63. Benchmark proxies are explicitly labeled.

### Data Quality and Coverage
64. Stage 44 remains freshness authority.
65. Source timestamps are preserved.
66. Receive timestamps are distinct.
67. Valuation dates are distinct.
68. Snapshot calculation time is distinct.
69. Delayed data is disclosed.
70. Stale data is conservatively handled.
71. Unknown freshness is not labeled Live.
72. Provider outages are reported.
73. Incomplete comparisons are labeled partial.
74. Qualified member counts are truthful.
75. Exclusion reasons are typed.
76. No silent universe truncation occurs.
77. No unsupported global coverage claims occur.
78. Derived comparisons preserve Provider provenance.
79. Corrections trigger appropriate invalidation.

### Infrastructure
80. Stages 16–17 remain canonical identity authority.
81. Stages 21–22 remain identifier authority.
82. Stage 23 remains relationship authority.
83. Stage 24 remains provenance authority.
84. Stage 25 remains selection authority.
85. Stage 27 remains capability layer.
86. Stages 28–32 remain Provider infrastructure.
87. Stage 33 remains canonical Market Data authority.
88. Stage 39 remains historical-data authority.
89. Stage 41 remains latest Quote authority.
90. Stage 42 remains Market Event authority.
91. Stage 43 remains frontend WebSocket authority.
92. Stage 44 remains freshness authority.
93. Stage 63 metric qualification is reused.
94. Stage 64 visualizations are not duplicated.
95. No new Quote cache is introduced.
96. No new Market Event transport is introduced.
97. No duplicate global WebSocket is introduced.
98. No independent historical market database is introduced.
99. No uncontrolled Provider polling is introduced.
100. Batch reads are preferred over N+1 requests.
101. Derived snapshots are non-authoritative.
102. Cache TTL does not imply market freshness.

### APIs and Security
103. APIs require authentication.
104. APIs enforce authorization.
105. Data entitlements are enforced.
106. Derived returns cannot bypass price entitlements.
107. Cache isolation prevents cross-user leakage.
108. Input UUIDs and windows are validated.
109. No arbitrary Provider URLs are accepted.
110. No arbitrary SQL is accepted.
111. No unsafe HTML is rendered.
112. Read requests do not mutate canonical market data.
113. Read requests do not create live ingestion targets.
114. Read requests do not create market-data jobs.
115. Read requests do not execute trading.
116. Read requests do not modify Portfolios.
117. Read requests do not run Agents.
118. Read requests do not run Workflows.
119. Read requests do not require LLM calls.
120. Licensed market data is not persisted insecurely in browser storage.

### UI
121. Existing ATLAS design tokens are reused.
122. Native/Aligned methodology is visible.
123. Asset-class metric names are visible.
124. Units are explicit.
125. Comparison windows are visible.
126. Coverage status is visible.
127. Source observation time is visible.
128. Snapshot calculation time is visible.
129. Freshness/delay is visible.
130. No purple gradients are introduced.
131. No emoji icons are introduced.
132. No fake benchmark values are introduced.
133. No fake financial statistics are introduced.
134. No fake trading signals are introduced.
135. No invented global sentiment score is introduced.
136. Desktop/tablet/mobile are supported.
137. Keyboard accessibility is required.
138. Color is not the only information channel.

### Roadmap Boundaries
139. Stage 66 owns Charts V1.
140. Stage 67 owns live chart streaming.
141. Stage 68 owns chart intervals/types.
142. Stages 69–75 own indicators/drawings/multi-chart/replay.
143. Stage 76 owns Watchlists.
144. Stage 80 owns Alerts.
145. Stage 94–98 own Screeners.
146. Stage 110+ owns Portfolios.
147. Stage 115+ owns Risk.
148. Stage 118 owns advanced factor risk.
149. Stage 129+ owns geospatial Maps.
150. Stage 135+ owns Universal Event intelligence.
151. Stage 141–142 owns Options/QuantLib.
152. Stage 143 owns Backtesting.
153. Stage 144 owns Paper Trading.
154. Stage 145 owns Broker Sandbox.
155. Stage 146+ owns Agents.
156. No correlation/covariance engine is introduced.
157. No cross-asset predictive scoring is introduced.
158. No portfolio optimization is introduced.
159. No automated strategy execution is introduced.
160. No speculative economic regime classifier is introduced.
161. No full charting engine is introduced.
162. No unnecessary migrations are introduced.
163. No fabricated production market data is seeded.
164. Stage 65 must pass financial comparison tests.
165. Stage 65 must pass alignment tests.
166. Stage 65 must pass coverage tests.
167. Stage 65 must pass entitlement tests.
168. Stage 65 must pass prior-stage regressions.
169. Stage 65 documentation must match implementation.
170. Stage 66 is the next canonical development stage.

## Stage 66 — Charts V1: Institutional Financial Charting Workspace

### Product and Navigation
1. Stage 66 establishes Charts V1 as the foundational financial charting workspace.
2. Charts uses the existing global module route `/charts`.
3. Charts does not add a new sidebar module; it activates the existing navigation item.
4. Existing ATLAS AppShell remains authoritative.
5. Existing Agent Dock is preserved on the right side.
6. Existing Bottom Taskbar is preserved at the workspace footer.
7. Existing appearance preferences (dark/light mode tokens) are reused.
8. Existing Global Search is reused for instrument lookup.
9. Existing Selected Entity Context (Stage 25) is updated when a chart instrument is selected.
10. Cross-module chart navigation uses canonical instrument UUIDs.

### Canonical Data
11. Stage 33 OHLCV remains the canonical financial market data model.
12. Stage 39 remains the historical ingestion authority.
13. Stage 40 remains the historical update worker authority.
14. Stage 37 ClickHouse `historical_market_bars_versions FINAL` remains historical storage.
15. Stage 24 provenance remains authoritative for historical observations.
16. Provider routing is not duplicated.
17. Historical chart API is strictly read-only.
18. No Provider calls occur on ordinary chart reads.
19. Chart visits do not create ingestion jobs.
20. Chart visits do not enroll live Quote targets.
21. Chart reads do not mutate canonical OHLCV rows.

### Identity
22. Instrument UUID is authoritative for chart identity.
23. Market-series identity is preserved across venues and listings.
24. Listing venue is preserved and displayed.
25. Crypto base/quote and venue identity are strictly preserved (e.g. BTC/USDT vs BTC/USD).
26. FX pair orientation is preserved without silent inversion.
27. Futures contract month and expiration are preserved.
28. Bond clean/dirty price basis is preserved.
29. Raw and split-adjusted equity series remain distinct.
30. Ticker string is never used as the chart primary key.
31. Ambiguous symbols require explicit disambiguation.
32. Non-chartable Entities do not receive fabricated price series.

### Historical Data
33. Charts V1 uses one verified baseline interval: `1D` (daily bars).
34. Preferred interval is daily where supported by canonical historical ingestion.
35. Stage 68 owns expanded intervals (1m, 5m, 1h, 1W) and timeframe resampling.
36. Historical queries use bounded ranges with strict limit caps (default 250, max 2000).
37. Historical pagination is deterministic using chronological cursor timestamps.
38. Duplicate logical bars are resolved through canonical revision policy (`FINAL` + latest version).
39. A candle represents one coherent source observation.
40. No mixed-Provider OHLC candle is constructed.
41. Missing history is not interpolated.
42. Missing volume is not forced to zero.
43. No synthetic candles are created.
44. No fake historical coverage is reported.
45. Source timestamps are preserved in UTC.
46. Daily session dates are not shifted incorrectly across timezones.
47. Financial values preserve Decimal precision before serialization.
48. Invalid OHLC relationships (`high < open`, `low > close`, etc.) are strictly rejected.
49. Valid negative Futures prices are supported (e.g. WTI Crude oil).
50. Zero/negative price restrictions remain asset-class specific.
51. NaN, Infinity, and -Infinity are strictly prohibited.

### Chart Engine
52. One approved charting library is used: TradingView Lightweight Charts (`lightweight-charts@5.2.1`).
53. Library version is pinned in package.json.
54. Licensing and attribution requirements are reviewed (Apache 2.0).
55. SSR and client-only behavior is handled via Next.js `"use client"` and dynamic imports.
56. Renderer lifecycle is explicit with proper unmount cleanup.
57. Chart disposal (`chart.remove()`) is required to prevent memory leaks.
58. Responsive resize is supported via `ResizeObserver`.
59. Theme updates preserve data and viewport where practical.
60. Chart geometry does not alter underlying financial values.
61. Candlestick rendering uses genuine OHLC observations.
62. Basic Close Line uses canonical Close values from the same bars.
63. Advanced chart types (Heikin-Ashi, Renko, Kagi) belong to Stage 68.
64. No arbitrary smoothing is presented as genuine historical data.
65. Volume histogram appears only when genuine volume exists.
66. Price axis uses actual quote units and precision.
67. Price axis supports valid negative values.
68. Price precision is source- and instrument-aware.

### Time and Interaction
69. Time basis is explicit (UTC epoch seconds).
70. UTC canonical timestamps are preserved.
71. Exchange trading dates are respected.
72. Daylight saving time handling is timezone-aware.
73. Weekend and holiday gaps are not fabricated.
74. Crosshair uses actual bar timestamps.
75. Crosshair inspection uses actual OHLC values.
76. Keyboard-accessible inspection is provided.
77. Historical data table is provided for screen-reader accessibility.
78. Pan and zoom are supported.
79. Older-history backfill is bounded and triggered on horizontal scroll.
80. Duplicate backfill requests are prevented via refs and guards.
81. Backfill does not reset the viewport abruptly.
82. Empty pagination terminates correctly when `has_more` is false.
83. Instrument switching cancels stale in-flight requests via `AbortController`.
84. Chart rendering does not require LLM inference (0 LLM calls).

### Security
85. Charts APIs require authentication.
86. Authorization is enforced on all endpoints.
87. Historical-data entitlements are enforced.
88. Chart previews cannot bypass licensed-data restrictions.
89. No Provider secrets are exposed to the client.
90. No arbitrary Provider URLs are accepted.
91. No arbitrary SQL is accepted.
92. No unsafe HTML is rendered.
93. Authenticated query caches are isolated.
94. Restricted prices are not persisted insecurely in browser storage.
95. No Trading execution occurs from Charts V1.
96. No Portfolio changes occur from Charts V1.
97. No autonomous Agent runs occur from Charts V1.
98. No Workflow executions occur from Charts V1.
99. No LLM calls are required for charting.

### UI
100. Charts uses canonical ATLAS design tokens.
101. Dark and light modes are supported.
102. The chart occupies the main workspace viewport.
103. Toolbar remains compact and uncluttered.
104. Instrument identity is visible in the header.
105. Price units are visible.
106. Baseline interval is visible.
107. Source provenance is accessible in the status bar.
108. Adjustment basis is accessible in the status bar.
109. Historical coverage is visible.
110. Missing data is not disguised.
111. No fake Live badge is shown.
112. No purple gradients are introduced.
113. No emoji icons are introduced.
114. No fake candles are introduced.
115. No fake volumes are introduced.
116. No promotional hero graphics are introduced.
117. Responsive chart rendering is required across all device viewports.
118. Accessibility is required (WCAG 2.1 AA).
119. Color does not serve as the only indicator (text and labels accompany directional color).
120. Resource cleanup is required on unmount.

### Roadmap Boundaries
121. Stage 67 owns Live Chart Streaming.
122. Stage 68 owns expanded intervals and chart types.
123. Stage 69 owns Technical Indicator Infrastructure.
124. Stage 70 owns TA-Lib integration.
125. Stage 71 owns Drawing Tools.
126. Stage 72 owns Multi-Chart Layouts.
127. Stage 73 owns Chart Synchronization.
128. Stage 74 owns Saved Chart Layouts.
129. Stage 75 owns Chart Replay.
130. Stage 76 owns Watchlists.
131. Stage 80 owns Alerts.
132. Stage 94–98 own Screeners.
133. Stage 110+ owns Portfolios.
134. Stage 115+ owns Risk.
135. Stage 141–142 own Options/Quant.
136. Stage 143 owns Backtesting.
137. Stage 144 owns Paper Trading.
138. Stage 145 owns Broker Sandbox.
139. Stage 146+ owns Agents.
140. Stage 66 introduces no chart trading.
141. Stage 66 introduces no technical indicators.
142. Stage 66 introduces no user drawings.
143. Stage 66 introduces no multi-chart synchronization.
144. Stage 66 introduces no chart replay.
145. Stage 66 introduces no chart-layout persistence.
146. Stage 66 introduces no duplicate Quote/event infrastructure.
147. Stage 66 introduces no unnecessary database schema.
148. Stage 66 does not seed fake financial data.
149. Stage 66 tests verify OHLC correctness.
150. Stage 66 tests verify timestamp correctness.
151. Stage 66 tests verify pagination and revisions.
152. Stage 66 tests verify entitlements.
153. Stage 66 tests verify cleanup and responsiveness.
154. Stage 66 documentation matches implementation.
155. Stage 67 is the next canonical development stage.

## Stage 67 — Live Chart Streaming V1

### Product and Scope
1. Stage 67 implements Live Chart Streaming V1.
2. Charts continues using `/charts`.
3. No new global module is created.
4. Stage 66 historical chart remains functional.
5. Existing AppShell is preserved.
6. Existing Agent Dock is preserved.
7. Existing Bottom Taskbar is preserved.
8. Existing design tokens are reused.
9. Selected Entity remains canonical.
10. Stage 67 does not implement Stage 68 functionality.

### Historical and Live Separation
11. Stage 66 historical OHLCV remains authoritative.
12. Stage 39 remains historical ingestion authority.
13. Stage 41 remains latest Quote authority.
14. Stage 42 remains Market Event authority.
15. Stage 43 remains WebSocket authority.
16. Stage 44 remains freshness authority.
17. Live Quote state is separate from historical bars.
18. Latest Last-price overlay does not mutate stored OHLC.
19. No Quote-derived fake candles are created.
20. No client-side ClickHouse writes occur.
21. No direct Provider feed is opened by the browser.

### Quote Semantics
22. Quote snapshot is not a complete trade feed.
23. Bid is not Last.
24. Ask is not Last.
25. Midpoint is not executed Last.
26. Quote event count is not Volume.
27. Latest Last does not establish complete Open/High/Low.
28. Missing Last is not zero Last.
29. Source timestamps are preserved.
30. Receive timestamps remain distinct.
31. Provider metadata is preserved.
32. Venue metadata is preserved.
33. Decimal precision is preserved.
34. Negative Futures prices are supported.
35. Market-series identity is explicit.

### Event Processing
36. Stage 42 typed Quote events are reused (`market.quote.updated`).
37. Event schema validation is required.
38. Older events cannot overwrite newer accepted state.
39. Duplicate events are handled idempotently.
40. Transport event ID is not market event time.
41. At-least-once delivery is assumed.
42. No exactly-once claim is made.
43. Provider failover follows existing routing semantics.
44. Invalid events are rejected.
45. Unknown schema versions fail safely.
46. No raw Provider payload is directly rendered.

### Bootstrap
47. Initial live state is read from Stage 41.
48. WebSocket subscription is authorized.
49. Snapshot/event races are handled.
50. Bootstrap buffers are bounded (max 50 events).
51. Buffer overflow triggers reconciliation.
52. Stale HTTP snapshots cannot replace newer events.
53. Chart history and live state have separate lifecycles.
54. No new latest Quote cache is created.

### Live Candle Policy
55. Live bars require authoritative source OHLC or sufficiently complete trade data.
56. Snapshot-only Quotes do not authorize live OHLC construction.
57. Genuine trade quantity is required for trade-derived volume.
58. Complete period coverage must be established.
59. Missing trades invalidate claims of complete bar coverage.
60. Market-session boundaries must be verified.
61. Provisional bars remain distinct from finalized history.
62. Finalization is source/reconciliation-driven.
63. Browser clock alone does not finalize a bar.
64. Historical corrections remain authoritative.
65. Reconciliation must avoid duplicate bars.
66. No synthetic Futures continuous roll is introduced.
67. Optional typed bar events use existing Stage 42 transport.
68. No second event bus is introduced.
69. Unsupported live-candle capability is disclosed honestly.

### Subscription and Authorization
70. Existing global Stage 43 WebSocket is reused.
71. No second chart-specific global socket is created.
72. Subscriptions use canonical UUIDs (`instrument_entity_id`).
73. Market-series variants are preserved.
74. Authorization precedes subscription.
75. Realtime/delayed entitlements are enforced.
76. Subscription counts are bounded.
77. Reference-counted subscriptions are preserved where implemented.
78. Instrument switching releases obsolete subscriptions.
79. Unmount releases page-specific subscriptions.
80. Other modules' shared subscriptions are not disrupted.
81. Unauthorized streams cannot leak data.
82. No Provider secrets are exposed.

### Connection and Freshness
83. Transport connection is distinct from market freshness.
84. Connected does not automatically mean Live.
85. Delayed data is labeled Delayed.
86. Stale data is labeled Stale.
87. Unknown freshness remains Unknown.
88. Market Closed requires authoritative evidence.
89. Source times are displayed.
90. Last accepted observations are not silently represented as current.
91. Provider outages are reported.
92. Redis outages produce degraded states.

### Controls and UX
93. Live Updates control is functional.
94. Pause does not create an unbounded queue.
95. Resume triggers authoritative reconciliation.
96. Go to Latest changes viewport, not market data.
97. Manual historical navigation is respected.
98. Follow-live is disabled appropriately during manual panning.
99. Crosshair remains stable.
100. Historical bars remain visible during disconnects.
101. No random price animation is allowed.
102. No fake Live badge is allowed.
103. No purple gradients are introduced.
104. No emoji icons are introduced.
105. No nonfunctional trading buttons are added.
106. Price/unit formatting remains accurate.
107. Accessible status controls are required.
108. Responsive layouts remain supported.

### Reconnection and Performance
109. Reconnect uses Stage 43 infrastructure.
110. Resubscription is required where necessary.
111. Latest-state reconciliation follows reconnect.
112. Redis Stream replay is bounded.
113. Event gaps are not ignored.
114. Quote snapshot cannot reconstruct missing OHLC history.
115. Browser suspension triggers safe reconciliation.
116. Rendering updates are coalesced (100ms cadence).
117. Event buffers are bounded.
118. No unbounded full-history refetch occurs per event.
119. Historical pagination remains independent.
120. Chart renderer instances are reused.
121. Theme changes do not duplicate sockets.
122. Cleanup prevents listener/observer leaks.
123. Structured logging is reused.
124. High-cardinality metric labels are avoided.

### Security and Side Effects
125. Live-state reads require authentication.
126. Live-state reads enforce authorization.
127. Market-data entitlements are enforced.
128. No direct browser Provider credentials are used.
129. No arbitrary Provider URLs are accepted.
130. No arbitrary Redis commands are exposed.
131. No arbitrary SQL is accepted.
132. No unsafe HTML is rendered.
133. Private market data is not persisted insecurely.
134. Chart reads do not create ingestion jobs.
135. Chart reads do not create live targets.
136. Chart reads do not write OHLC history.
137. Chart reads do not append market events.
138. Chart display does not create trading orders.
139. Chart display does not modify Portfolios.
140. Chart display does not run Agents.
141. Chart display does not run Workflows.
142. Chart display does not require LLM calls.

### Roadmap Boundaries
143. Stage 68 owns expanded intervals/types.
144. Stage 69 owns Technical Indicator Infrastructure.
145. Stage 70 owns TA-Lib.
146. Stage 71 owns Drawing Tools.
147. Stage 72 owns Multi-Chart.
148. Stage 73 owns Chart Synchronization.
149. Stage 74 owns Saved Chart Layouts.
150. Stage 75 owns Chart Replay.
151. Stage 76 owns Watchlists.
152. Stage 80 owns Alerts.
153. Stage 94–98 own Screeners.
154. Stage 110+ owns Portfolios.
155. Stage 115+ owns Risk.
156. Stage 141–142 own Options/Quant.
157. Stage 143 owns Backtesting.
158. Stage 144 owns Paper Trading.
159. Stage 145 owns Broker Sandbox.
160. Stage 146+ owns Agents.
161. No indicator engine is introduced.
162. No advanced resampling engine is introduced.
163. No multi-chart synchronization is introduced.
164. No chart-layout persistence is introduced.
165. No replay system is introduced.
166. No trading automation is introduced.
167. No fake market data is seeded.
168. Stage 67 must pass quote/candle integrity tests.
169. Stage 67 must pass ordering and race tests.
170. Stage 67 must pass entitlements tests.
171. Stage 67 must pass reconnection tests.
172. Stage 67 must pass performance/cleanup tests.
173. Stage 67 must pass Stage 66 regressions.
174. Stage 67 documentation must match actual implementation.
175. Stage 68 is the next canonical development stage.

## Stage 68: Advanced Chart Intervals & Chart Types V1

### Architecture
1. Stage 68 extends the existing Charts module at `/charts`.
2. Canonical route remains `/charts`.
3. Stage 66 historical charting is reused without duplication.
4. Stage 67 live streaming is reused without duplication.
5. Stage 33 OHLCV remains canonical.
6. Stage 39 ingestion remains authoritative.
7. Stage 40 updates remain separate from reads.
8. ClickHouse remains historical storage.
9. No duplicate OHLCV database is introduced.
10. No new Provider routing layer is created.
11. No additional global WebSocket is created.
12. No new Quote cache is introduced.
13. No unnecessary microservice is introduced.

### Intervals
14. Intervals have stable typed IDs: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`, `1M`.
15. Interval and visible time range are distinct dimensions.
16. Interval availability is series-specific.
17. Availability must reflect genuine stored/source coverage.
18. Unsupported intervals are not advertised as functional.
19. Source-native (`AVAILABLE_NATIVE`) and derived (`AVAILABLE_DERIVED`) intervals are distinguished.
20. Daily intervals follow canonical trading/session dates.
21. Weekly intervals use validated calendar/session grouping (ISO weeks starting Monday).
22. Monthly intervals use validated calendar-month grouping (first of month).
23. DST is handled using timezone-aware calendar rules.
24. No arbitrary universal UTC-day policy is imposed.
25. No intraday data is manufactured from daily bars.
26. No Quote snapshots are converted into authoritative candles.
27. Historical interval requests are bounded.
28. Interval selection does not create ingestion jobs.
29. Interval selection does not trigger Provider fanout.

### Aggregation
30. Aggregation requires compatible canonical series.
31. Aggregation requires compatible Providers/source methodology.
32. Aggregation requires consistent price basis.
33. Aggregation requires consistent adjustment basis.
34. Aggregation requires consistent quotation units.
35. Aggregation uses high-precision Python Decimal.
36. Open uses first constituent bar Open.
37. High uses maximum constituent bar High.
38. Low uses minimum constituent bar Low.
39. Close uses last constituent bar Close.
40. Volume sums only genuine compatible quantities.
41. Missing Volume is not treated as zero; aggregate Volume is None.
42. Missing intervals are not silently synthesized.
43. Market closures are not fabricated as flat bars.
44. Unknown completeness prevents finalized aggregate claims.
45. Verified no-trade periods remain distinct from missing data.
46. Partial periods are explicitly handled and labeled provisional.
47. Current week/month is not automatically finalized.
48. Native target bars are preferred where available.
49. Derived bars preserve lineage (`source_interval`, `interval_source_kind`).
50. Derived cache responds to source corrections.
51. Provider observations are not arbitrarily stitched.
52. Futures contract expirations are never merged.
53. Bond clean/dirty/yield series are not merged.
54. Raw and adjusted equities are not merged.
55. Negative Futures price support remains intact (e.g. `CLZ26`).
56. Invalid OHLC/NaN/Infinity are rejected (`high < max(open, close)` or `high < low`).

### APIs and State
57. Existing history API `GET /api/v1/charts/history` is extended with `interval` parameter.
58. Available intervals are discoverable via `GET /api/v1/charts/intervals`.
59. Unsupported selections return explicit `HTTPException(400)`.
60. Pagination operates on target bars.
61. Cursor identity includes interval context.
62. Stale responses cannot overwrite newly selected intervals via request abort controllers.
63. Query caches are interval-aware.
64. Derived caches are non-authoritative.
65. Cache TTL is not market-data freshness.
66. Authorization applies to every interval.
67. Derived intervals cannot bypass source entitlements.
68. No canonical writes occur on history reads.

### Chart Types
69. Candlestick renderer is preserved (`candlestick`).
70. OHLC Bar renderer is added (`bar`).
71. Line renderer is preserved (`line`).
72. Area renderer is added (`area`).
73. Chart types share canonical source observations.
74. Area baseline semantics are documented and use adaptive scaling.
75. Line/Area do not invent intermediate financial values.
76. Unsupported renderers are disabled for incompatible data.
77. Chart-type switching avoids unnecessary Provider/API calls.
78. Price units and precision remain accurate.
79. Valid negative prices remain supported across all renderers.
80. Historical gaps remain visible/traceable without smoothing.
81. Theme compatibility is required across dark and light modes.
82. Viewport preservation is required where practical.

### Stage 67 Live Integration
83. Latest Last-price overlay remains separate from historical candles.
84. Interval switching does not duplicate Quote subscriptions.
85. Live bar updates require matching interval identity.
86. Only authoritative live bars or verified complete aggregation may update candles.
87. Incomplete lower-interval feeds cannot create finalized target bars.
88. Browser wall clock alone cannot finalize OHLC.
89. Historical corrections trigger derived-bar reconciliation.
90. Reconnection does not fabricate missed OHLC.
91. Quote freshness/delay metadata remains visible.

### UI and Security
92. Existing AppShell is preserved.
93. Existing Agent Dock is preserved.
94. Existing Bottom Taskbar is preserved.
95. Existing appearance/design tokens are reused.
96. No purple gradients are introduced.
97. No emoji icons are introduced.
98. No fake prices/candles/volume are introduced.
99. Interval availability is clearly communicated with status tags and tooltips.
100. Native/derived provenance is visible in status and inspector.
101. Accessible controls are required (ARIA, keyboard navigation, accessible table).
102. Responsive layouts are required (desktop, tablet, mobile).
103. Authentication is enforced.
104. Authorization is enforced.
105. Intraday market-data entitlements are enforced.
106. Provider credentials remain server-side.
107. No arbitrary SQL/aggregation expressions are accepted.
108. No Trading or Agent execution is introduced.
109. No LLM calls are required.

### Roadmap Boundaries
110. Stage 69 owns indicator infrastructure.
111. Stage 70 owns TA-Lib.
112. Stage 71 owns drawings.
113. Stage 72 owns multi-chart layouts.
114. Stage 73 owns synchronization.
115. Stage 74 owns saved chart layouts.
116. Stage 75 owns replay.
117. Stage 76 owns Watchlists.
118. Stage 80 owns Alerts.
119. Stage 94–98 own Screeners.
120. Stage 110+ owns Portfolios.
121. Stage 115+ owns Risk.
122. Stage 143 owns Backtesting.
123. Stage 144 owns Paper Trading.
124. Stage 145 owns Broker Sandbox.
125. Stage 146+ owns Agents.
126. No technical indicators are implemented prematurely.
127. No drawing tool infrastructure is implemented prematurely.
128. No replay system is implemented prematurely.
129. No trade execution is implemented.
130. Stage 68 tests must verify interval integrity.
131. Stage 68 tests must verify OHLC aggregation.
132. Stage 68 tests must verify session boundaries.
133. Stage 68 tests must verify live compatibility.
134. Stage 68 tests must verify entitlement isolation.
135. Stage 68 documentation must match implementation.
136. Stage 69 is the next canonical stage.

## Stage 69 — Technical Indicator Infrastructure V1

### Product & Scope
1. Stage 69 implements Technical Indicator Infrastructure V1 inside `/charts`.
2. Indicators remain strictly inside the existing Charts module (`/charts`); no new sidebar module is created.
3. No new global sidebar route or top-level navigation item is added.
4. Existing AppShell, Agent Dock, and Bottom Taskbar are preserved.
5. Stage 66 chart rendering engine is reused; no duplicate canvas engine is installed.
6. Stage 67 live streaming infrastructure and Last-price overlay are reused.
7. Stage 68 multi-timeframe interval framework and chart types are reused.
8. Stage 70 TA-Lib integration and broad indicator catalog are formally deferred.

### Registry & Indicator Identity
9. Indicator definitions have stable, namespaced identifiers (`atlas.sma`).
10. Indicator definitions are explicitly versioned (`version: 1`).
11. Indicator instances are strictly distinguished from indicator definitions.
12. Registry implementations are statically allowlisted on the backend.
13. Duplicate `(indicator_id, version)` registrations are rejected.
14. Unknown indicator IDs return typed `UNKNOWN_INDICATOR` validation errors.
15. Unsupported versions return typed `UNSUPPORTED_VERSION` validation errors.
16. No user-executable formulas, scripts, or arbitrary code (`eval`, `exec`) are permitted.
17. Registry design is forward-compatible with future Stage 70 TA-Lib adapters.

### Parameters
18. Indicator parameters are strictly typed (`INTEGER`, `DECIMAL`, `BOOLEAN`, `STRING`).
19. Parameters have validated bounds and schema definitions (`min_value`, `max_value`, `allowed_values`).
20. Default parameter values are defined authoritative by the backend registry.
21. Backend parameter validation is authoritative over client-side validation.
22. Invalid parameters reject calculation and never trigger execution.
23. Parameter changes invalidate previous calculation results atomically.
24. Instance identity is distinct from definition identity, allowing multiple instances of one indicator.

### Financial Data Inputs & Integrity
25. Canonical OHLCV observations from Stage 33 remain authoritative.
26. Indicator inputs preserve canonical financial instrument identity (UUID).
27. Market-series identity is strictly preserved.
28. Interval identity is strictly preserved (calculations are interval-aware).
29. Provider and venue semantics are strictly preserved.
30. Price basis is strictly preserved.
31. Adjustment basis (split/dividend adjusted vs unadjusted) is strictly preserved.
32. Source revisions are preserved using the logical-latest policy.
33. Incompatible market series or providers are never mixed.
34. Futures contract expirations are never silently joined.
35. Missing observations are never fabricated or silently interpolated.
36. Zero look-ahead is guaranteed: calculations at bar $T$ use only observations $\le T$.

### Deterministic Calculation Engine
37. Indicator calculations are deterministic mathematical transformations.
38. Reference SMA is implemented natively without third-party dependencies.
39. SMA uses qualified Close observations only.
40. SMA uses an efficient $O(N)$ rolling-sum accumulator window.
41. SMA warmup requires exactly $N$ real qualified observations.
42. Missing warmup points ($1 \dots N-1$) are explicitly represented as `None`/`null` (`WARMUP`), never 0.
43. Authoritative financial arithmetic uses Python `Decimal` to avoid floating-point drift.
44. Non-finite outputs (`NaN`, `Infinity`) are strictly prohibited and rejected.
45. Output timestamps align exactly to canonical bar timestamps without forward/backward shifts.
46. Output quotation units match the verified source quotation units.
47. Calculations enforce resource limits (max 5 instances, max 2,000 bars, max lookback).
48. Large lookback requests are strictly bounded (SMA period max 500).
49. Indicators are descriptive studies and never imply predictions or trading signals.

### Chart Overlays & Panes
50. Indicator overlays reuse the approved Lightweight Charts rendering adapter.
51. SMA is rendered as a clean price overlay on the compatible primary price scale.
52. Future oscillators are provided with a dedicated attached subpane container contract.
53. Subpane infrastructure does not create multi-chart layouts (Stage 72).
54. Crosshair inspection displays time-aligned numerical indicator values.
55. Toggling visibility does not mutate underlying source data or historical bars.
56. Removing one instance cleans up its series without removing other instances.
57. Indicator overlays do not modify or mutate underlying OHLCV candlesticks.
58. No fake or decorative indicator graphics are used.

### Historical & Live Integration
59. Historical backfill panning triggers safe lookback retrieval and recalculation.
60. Interval changes trigger requalification and interval-specific recalculation.
61. Instrument changes cleanly invalidate previous outputs and recalculate for the new series.
62. Source corrections invalidate and recompute affected rolling windows.
63. Latest Last-price Quotes do not create finalized indicator points.
64. Genuine finalized canonical bars update or append indicator outputs safely.
65. Provisional indicator values, if supported, must be visibly classified as provisional.
66. Duplicate or older live events cannot regress indicator output state.
67. No duplicate global WebSocket connection is created (reuses Stage 43).
68. No duplicate Quote cache is introduced (reuses Stage 41).
69. No duplicate market event bus is introduced (reuses Stage 42).

### Security & Governance
70. Catalog and calculation APIs require Stage 13 authentication.
71. Stage 14 authorization is enforced on all indicator requests.
72. Financial market-data entitlements are enforced.
73. Derived indicator studies cannot bypass source market-data entitlements.
74. No arbitrary Python execution is permitted.
75. No arbitrary JavaScript execution is permitted.
76. No arbitrary SQL execution is permitted.
77. No upstream Provider credentials or secrets are exposed.
78. Calculation resource limits (instances, bars, lookback) are enforced.
79. Cache isolation prevents cross-user or cross-instrument leakage.
80. Calculation requests have read-only semantics (0 writes to canonical database/ClickHouse).
81. No Trading, Agent, or Workflow action is executed.
82. No LLM calls are required.

### User Interface & Accessibility
83. ATLAS design tokens and color palettes are reused.
84. Indicator Picker shows actual registered definitions with categories and parameters.
85. Parameter controls are functional with inline validation and integer constraints.
86. Active indicator instances can be configured via a compact settings dialog.
87. Active indicator instances can be shown or hidden with an eye toggle.
88. Active indicator instances can be removed individually.
89. Multiple SMA instances (e.g., SMA 20 and SMA 50) are supported concurrently.
90. Insufficient-history and warmup states are clearly communicated.
91. Source interval, instrument, and provenance metadata are transparent.
92. Numerical indicator values are accessible via legend, inspector, and table.
93. Full dark and light theme compatibility is maintained.
94. Responsive layouts (desktop, tablet, mobile) are supported.
95. Strict UI ban: No purple gradients.
96. Strict UI ban: No emoji icons.
97. Strict UI ban: No fake technical analysis, fake oscillators, or artificial signals.

### Roadmap Boundaries
98. Stage 70 owns TA-Lib integration and expanded indicator catalog.
99. Stage 71 owns Drawing Tools.
100. Stage 72 owns Multi-Chart Layout.
101. Stage 73 owns Chart Synchronization.
102. Stage 74 owns Saved Chart Layouts.
103. Stage 75 owns Chart Replay.
104. Stage 76 owns Watchlists.
105. Stage 80 owns Alerts.
106. Stage 94–98 own Screeners.
107. Stage 110+ owns Portfolios.
108. Stage 115+ owns Risk.
109. Stage 141–142 own Options and Quant pricing.
110. Stage 143 owns Backtesting.
111. Stage 144 owns Paper Trading.
112. Stage 145 owns Broker Sandbox.
113. Stage 146+ owns Autonomous Agents.
114. No generalized indicator library is prematurely implemented before Stage 70.
115. No strategy engine is implemented.
116. No price prediction engine is implemented.
117. No chart-layout database is implemented.
118. No indicator replay is implemented.
119. No unnecessary new infrastructure is introduced.
120. Stage 69 must pass deterministic calculation tests.
121. Stage 69 must pass warmup and lookback tests.
122. Stage 69 must pass authorization and entitlement tests.
123. Stage 69 must pass overlay rendering tests.
124. Stage 69 must pass Stage 66–68 regressions.
125. Stage 69 documentation must match actual code.
126. Stage 70 is the next canonical stage.

## Stage 70 — Integrate TA-Lib & Build Production Technical Analysis Engine

### Library Integration
1. TA-Lib is the approved Stage 70 technical-analysis library.
2. The Python wrapper version is pinned (`ta-lib>=0.8.2`).
3. Native runtime compatibility is verified (`0.8.1`).
4. NumPy compatibility is verified (`numpy>=2.0.0`).
5. Production container installation is reproducible.
6. CI verifies installation.
7. Missing TA-Lib causes explicit capability failure (`TALIB_UNAVAILABLE`).
8. Stage 69 native reference SMA remains preserved.
9. TA-Lib functions are exposed through approved adapters (`TALibIndicatorCalculator`).
10. No arbitrary function dispatch is exposed.

### Registry
11. Stage 69 Indicator Registry remains authoritative.
12. Indicator IDs remain stable (`atlas.sma`, `atlas.ema`, `atlas.wma`, `atlas.rsi`, `atlas.macd`, `atlas.bbands`, `atlas.atr`, `atlas.stoch`, `atlas.adx`, `atlas.cci`, `atlas.roc`, `atlas.mom`, `atlas.obv`, `atlas.mfi`).
13. Indicator definitions remain versioned (`version: 1`).
14. Parameter schemas remain typed with bounds.
15. Backend validation remains authoritative.
16. TA-Lib parameter mappings are explicit.
17. Multi-output metadata is supported (`output_names`, `rendering_type`).
18. Actual capability availability is reported (`GET /charts/indicators/capabilities`).
19. Unsupported functions are not advertised as operational.
20. No arbitrary executable formulas are permitted.

### Financial Inputs
21. Canonical OHLCV remains authoritative.
22. Canonical Financial Instrument UUIDs are preserved.
23. Market-series identity is preserved.
24. Provider compatibility is enforced.
25. Venue compatibility is enforced.
26. Interval identity is preserved.
27. Price basis is preserved.
28. Adjustment basis is preserved.
29. Quote units are preserved.
30. Source revisions are respected.
31. Futures expirations are not mixed.
32. FX orientation is preserved.
33. Crypto quote-asset identity is preserved.
34. Bond price/yield semantics remain distinct.
35. Missing inputs are not fabricated.
36. Missing Volume is not zero.
37. Tick count is not automatically traded Volume.

### Numerical Correctness
38. Canonical Decimal inputs have an explicit TA-Lib conversion boundary (`extract_finite_float_series`).
39. TA-Lib calculations use the selected library's actual numeric conventions.
40. Float64 precision limitations are documented.
41. Nonfinite inputs (`NaN`, `Inf`) are rejected.
42. Expected warmup values are represented as unavailable (`null`, `WARMUP`).
43. Unexpected nonfinite outputs are treated as errors/data gaps.
44. No look-ahead is permitted.
45. Recursive lookback and seed history are respected.
46. TA-Lib global unstable-period configuration is not mutated per concurrent request.
47. Same inputs and versions produce reproducible results within documented tolerances.
48. Source corrections invalidate dependent outputs.
49. Unit formatting does not corrupt numerical values.

### Indicator Catalog
50. Trend indicators are implemented (SMA, EMA, WMA, ADX).
51. Momentum indicators are implemented (RSI, MACD, STOCH, CCI, ROC, MOM).
52. Volatility indicators are implemented (BBANDS, ATR).
53. Oscillator studies are implemented in independent subpanes.
54. Volume studies require genuine Volume.
55. EMA is based on actual TA-Lib semantics.
56. RSI uses correct lookback (14 bars lookback).
57. MACD produces three typed outputs (`macd_line`, `signal_line`, `histogram`).
58. Bollinger Bands produce three typed outputs (`upper_band`, `middle_band`, `lower_band`).
59. Stochastic produces two typed outputs (`slowk`, `slowd`).
60. ATR units remain price-distance units.
61. ADX is not represented as a trading forecast.
62. ROC and MOM remain distinct measures.
63. OBV and MFI do not fabricate Volume (`MISSING_VOLUME`).
64. No indicator is presented as guaranteed profitability.

### Rendering
65. Stage 66–68 charting library is reused (`lightweight-charts`).
66. Price overlays share compatible price scale.
67. Oscillator panes use their own scales with dedicated subpane canvases.
68. MACD histograms use correct sign/zero reference (green positive, red negative).
69. Bollinger Bands use accurate upper/middle/lower values.
70. Multi-output series are explicitly named.
71. Crosshair inspection uses source-aligned timestamps.
72. Warmup values are not plotted as zero.
73. Removing an indicator cleans up its series/pane.
74. Multiple instances are supported (up to 12 active instances).
75. UI remains responsive and accessible.
76. Dark/light themes are supported.
77. No purple gradients or emoji icons are introduced.
78. No fake indicator data is shown.

### History and Live
79. Stage 68 intervals remain authoritative.
80. Indicators are recalculated per selected interval.
81. Historical backfill is supported.
82. Source revisions are respected.
83. Stage 67 Last Quote remains separate from finalized OHLC.
84. Indicator output is updated from genuine finalized bars.
85. Provisional results are labeled if supported.
86. Duplicate and older events cannot regress output.
87. No additional global WebSocket is introduced.
88. No new market-data event bus is introduced.
89. No separate historical database is introduced.
90. No upstream Provider calls occur during ordinary calculation.

### Security and Performance
91. Catalog/calculation APIs require authentication.
92. Authorization is enforced.
93. Market-data entitlements are enforced.
94. Derived outputs cannot bypass source restrictions.
95. No arbitrary Python/JavaScript/SQL executes.
96. Input lengths are bounded (max 2,000 bars).
97. Parameter values are bounded.
98. Concurrent calculations are bounded.
99. Calculation time/memory use is controlled.
100. Failed indicators do not crash the chart.
101. Cache isolation prevents cross-user leakage.
102. Normal calculations do not modify canonical market data (0 writes).
103. No Trading orders are created.
104. No Portfolio changes are created.
105. No Agent/Workflow execution occurs.
106. No LLM calls are required.

### Roadmap Boundaries
107. Stage 71 owns Drawing Tools.
108. Stage 72 owns Multi-Chart Layout.
109. Stage 73 owns Synchronization.
110. Stage 74 owns Saved Chart Layouts.
111. Stage 75 owns Replay.
112. Stage 76 owns Watchlists.
113. Stage 80 owns Alerts.
114. Stage 94–98 own Screeners.
115. Stage 110+ own Portfolios.
116. Stage 115+ own Risk.
117. Stage 141–142 own Options/Quant pricing.
118. Stage 143 owns Backtesting.
119. Stage 144 owns Paper Trading.
120. Stage 145 owns Broker Sandbox.
121. Stage 146+ own Agents.
122. No drawing tools are implemented early.
123. No multi-chart synchronization is implemented early.
124. No saved layout persistence is implemented early.
125. No replay system is implemented early.
126. No automated strategy engine is implemented.
127. No predictive AI trading engine is implemented.
128. No fake financial data is seeded.
129. Stage 70 must pass TA-Lib dependency tests.
130. Stage 70 must pass numerical parity tests.
131. Stage 70 must pass warmup/gap tests.
132. Stage 70 must pass multi-output tests.
133. Stage 70 must pass authorization tests.
134. Stage 70 must pass previous chart regressions.
135. Documentation must reflect actual behavior.
136. Stage 71 is the next canonical stage.

## Stage 71 Decisions - Professional Chart Drawing Tools V1

### Product and Scope
1. Stage 71 implements interactive drawing tools in the ATLAS Charts module.
2. Drawings remain within `/charts`.
3. No new global Sidebar module is created.
4. Existing AppShell is preserved.
5. Existing Agent Dock is preserved.
6. Existing Bottom Taskbar is preserved.
7. Existing charting library (`lightweight-charts` v5.2.1) is reused.
8. Existing technical indicators remain functional and unobstructed.
9. No automated trading signals are introduced from user drawings.
10. No AI drawing generation or LLM predictions are introduced.

### Drawing Architecture
11. Drawings use typed, versioned object models (`DrawingObject`, version 1).
12. Every drawing has a stable, collision-resistant UUID identifier.
13. Drawing definitions are registered through approved application code in `DrawingToolRegistry`.
14. Drawing anchors use canonical financial coordinates `{ time, price }`.
15. Permanent drawing state never stores raw screen pixel positions.
16. Rendering geometry derives dynamically from active chart transforms.
17. Interaction logic is separated from rendering (`DrawingSessionStore` vs `DrawingLayer`).
18. Hit testing is separated from financial data access.
19. Snapping uses qualified canonical market observations from loaded bars.
20. Undo/Redo uses committed drawing actions as atomic transactions.
21. Session drawings are completely isolated from canonical market data.

### Financial Coordinates
22. Instrument entity ID remains authoritative.
23. Market-series identity is preserved.
24. Venue and quotation basis are preserved.
25. Adjustment basis is preserved.
26. Time anchors remain stable across zoom and pan.
27. Price anchors remain stable across resize and autoscale.
28. Chart logical index is not permanent drawing identity.
29. CSS pixels and device pixels are handled separately via SVG vectors.
30. Valid negative Futures prices are supported.
31. Unsupported price-scale modes fail safely without NaN geometry.
32. Unsupported future-time projection does not generate synthetic market candles.
33. Daily trading dates are not shifted incorrectly across timezones.
34. Existing anchors are not silently resnapped after interval changes.
35. Drawings from incompatible instruments or price bases are isolated.

### Tools
36. Trendlines are supported (2 anchors).
37. Horizontal lines are supported (1 anchor, full width).
38. Horizontal rays are supported (1 anchor, rightward projection).
39. Vertical lines are supported (1 anchor, full height).
40. Rectangles are supported (2 corner anchors, customizable fill opacity).
41. Price range measurement is supported (absolute $\Delta P$, percentage $\Delta P\%$, quotation units).
42. Time range measurement is supported (elapsed duration, canonical bar count).
43. Combined price/time measurement is supported.
44. Fibonacci retracements are supported (standard institutional ratios).
45. Every supported drawing has genuine creation, selection, and editing behavior.
46. User drawings are annotations, not market forecasts.

### Geometry and Editing
47. Pointer interaction uses an explicit controller state machine.
48. Drawing preview is transient and uncommitted.
49. Invalid partial drawings are never committed to session state.
50. Draw and Pan modes are distinguished through non-intrusive SVG pass-through.
51. Anchor handles are individually editable.
52. Whole drawings can be moved translating all anchors simultaneously.
53. Selected drawing hit tests are deterministic with priority on handles.
54. Overlapping drawings use stable z-index priority.
55. High-DPI coordinates are rendered sharply via SVG vector elements.
56. Drawing geometry is clipped to chart viewport bounds.
57. Pan/zoom redraws geometry without modifying stored financial anchors.
58. Drag cancellation restores previous committed geometry.
59. Locked drawings cannot be accidentally edited or dragged.
60. Hidden drawings remain in session state but are omitted from rendering.

### Fibonacci and Measurements
61. Fibonacci ratios use explicit directional formula $L(r) = P_0 + r(P_1 - P_0)$.
62. Anchor direction is preserved (high-to-low and low-to-high).
63. Fibonacci levels are geometric annotations, not guaranteed support/resistance.
64. Price difference preserves canonical quotation units.
65. Percentage change requires a strictly positive reference denominator.
66. Zero denominator does not produce a percentage (`N/A (base 0)`).
67. Negative denominator is handled conservatively (`N/A (negative base)`).
68. Elapsed time is distinct from qualified bar count.
69. Market holidays and weekend gaps do not create synthetic trading bars.
70. Price measurement is not investor total return or broker P/L.

### Snapping
71. Snapping is optional and configurable (`OFF`, `NEAREST_BAR`, `OHLC`).
72. Snapping candidates are genuine qualified canonical bars.
73. Missing bars cannot become snap targets.
74. Snapshot-only Last Quotes do not create OHLC snap targets.
75. Pixel snapping tolerance is bounded (15px).
76. Snapping respects active instrument, series, and interval.
77. Existing committed drawings are not automatically mutated by source corrections.
78. Snapping feedback displays target indicator without implying trade signals.

### Undo/Redo
79. Drawing edit actions are fully undoable and redoable.
80. One continuous pointer drag produces exactly one committed history command.
81. Redo history is invalidated immediately by new edits after Undo.
82. Undo history is bounded to 100 commands per context.
83. Clear All can be undone as a single atomic transaction.
84. Undo does not modify financial market data, quotes, or indicators.
85. Undo does not change Trading or Portfolio state.

### Session State and Persistence
86. Stage 71 drawing state is session-level in-memory state.
87. Drawings are scoped to canonical chart context `[instrument_entity_id : price_basis]`.
88. Drawings are restored when returning to a chart within the same active browser session.
89. Drawings are not guaranteed to survive full page reloads or logouts.
90. No drawing persistence database table is created.
91. No cloud-saved chart layout API is created.
92. No automatic localStorage persistence is claimed as saved layouts.
93. Stage 74 owns persistent chart layouts and cloud synchronization.
94. Drawing schema remains versioned for future Stage 74 compatibility.

### Chart Integration
95. Candlestick rendering remains functional.
96. OHLC Bar rendering remains functional.
97. Line rendering remains functional.
98. Area rendering remains functional.
99. Stage 67 live quote overlay remains functional.
100. Stage 70 TA-Lib indicators and subpanes remain functional.
101. Drawing operations do not trigger indicator recalculations.
102. Drawing operations do not refetch historical market data.
103. Drawing operations do not create live WebSocket subscriptions.
104. Chart resize does not corrupt drawings.
105. Chart theme changes do not corrupt drawings.
106. Source corrections do not silently rewrite manual anchors.

### Accessibility and UX
107. Keyboard tool selection is supported.
108. An accessible Drawing Manager drawer is provided.
109. Numerical coordinate editing is provided via `DrawingCoordinateEditor`.
110. Keyboard Delete, Backspace, Undo (Ctrl+Z), and Redo (Ctrl+Shift+Z) are supported.
111. Keyboard shortcuts respect focused form text inputs and textareas.
112. Pointer and touch placement are supported.
113. Selection does not rely only on color; anchor handles and bounding indicators are used.
114. Drawing labels use correct financial units and prices.
115. ATLAS design tokens (`zinc-950`, `zinc-900`, `zinc-800`, `cyan-400`, `emerald-400`) are reused.
116. No purple gradients are introduced.
117. No emoji icons are introduced.
118. No fake market observations are introduced.
119. No oversized decorative UI is introduced.
120. Responsive desktop, tablet, and mobile behavior is supported.

### Security and Performance
121. Drawing schemas are strictly validated.
122. Non-finite coordinate values (NaN, Infinity) are rejected.
123. User labels cannot execute arbitrary HTML, JavaScript, or scripts.
124. Drawing count is bounded (max 250 drawings per instrument context).
125. Undo history is bounded (100 commands).
126. Pointer and rendering work is bounded to animation frames and SVG transforms.
127. Cleanup prevents leaked observers, event listeners, or timers.
128. Drawing interaction does not mutate canonical financial data (0 writes).
129. Drawing interaction does not call external market Providers.
130. Drawing interaction does not create ingestion jobs.
131. Drawing interaction does not place orders or execute trades.
132. Drawing interaction does not modify Portfolios.
133. Drawing interaction does not execute autonomous Agents.
134. Drawing interaction does not execute Workflows.
135. Drawing interaction requires 0 LLM calls.

### Roadmap Boundaries
136. Stage 72 owns Multi-Chart Layouts.
137. Stage 73 owns Cross-Chart Synchronization.
138. Stage 74 owns Saved Chart Layouts.
139. Stage 75 owns Chart Replay.
140. Stage 76 owns Watchlists.
141. Stage 80 owns Alerts.
142. Stage 94–98 own Screeners.
143. Stage 110+ own Portfolios.
144. Stage 115+ own Risk.
145. Stage 143 owns Backtesting.
146. Stage 144 owns Paper Trading.
147. Stage 145 owns Broker Sandbox.
148. Stage 146+ own Autonomous Agents.
149. No multi-chart functionality is introduced prematurely.
150. No cross-chart synchronization is introduced prematurely.
151. No cloud drawing persistence is introduced prematurely.
152. No replay functionality is introduced prematurely.
153. No chart-triggered trade execution is introduced.
154. No drawing-triggered automated alerts are introduced.
155. Stage 71 must pass coordinate correctness tests.
156. Stage 71 must pass geometric hit-testing tests.
157. Stage 71 must pass editing and undo/redo tests.
158. Stage 71 must pass financial-unit tests.
159. Stage 71 must pass accessibility tests.
160. Stage 71 must pass Stage 66–70 regressions.
161. Documentation must match implementation.
162. Stage 72 is the next canonical stage.

## Stage 72: Multi-Chart Layouts V1

### Product
1. Stage 72 implements Multi-Chart Layouts V1.
2. The canonical route remains `/charts`.
3. No new global Sidebar module is created.
4. Existing AppShell remains authoritative.
5. Existing Agent Dock is preserved.
6. Existing Bottom Taskbar is preserved.
7. Existing design tokens are reused.
8. Multi-chart layouts are desktop-first and responsive.
9. No fake market data is introduced.
10. No Trading or Agent execution is introduced.

### Layouts
11. Single-chart layout is preserved.
12. Two-column layout is supported.
13. Two-row layout is supported.
14. Three-chart left-focus layout is supported.
15. Three-chart top-focus layout is supported.
16. Four-chart grid is supported.
17. Layout definitions are centralized in `CHART_LAYOUTS`.
18. Panel count is bounded (maximum 4 visible panels).
19. Layout changes preserve compatible panel state.
20. Layout resizing is functional with `AtlasSplit` / `react-resizable-panels`.
21. Minimum panel sizes are enforced (width >= 320px, height >= 220px).
22. Nested splitters remain within valid bounds.
23. Responsive presentation is separate from selected layout identity.
24. Mobile uses a usable reduced-visible-panel tabbed presentation.

### Panel Identity
25. Every chart panel has a stable ID (`panel-1`, `panel-2`, etc.).
26. Panel ID is distinct from instrument UUID.
27. React keys use stable panel identity.
28. Each panel owns its chart renderer instance.
29. Each panel owns its viewport.
30. Each panel owns its selected instrument and series.
31. Each panel owns interval and chart type.
32. Each panel owns its indicator instance state.
33. Each panel owns drawing interaction state.
34. Each panel owns its loading/error state.
35. No mutable global chart instance is reused by unrelated panels.

### Active Panel
36. One panel is designated active (`activePanelId`).
37. Active panel selection is explicit (clicking header/chart or keyboard focus).
38. Global Search targets the active panel under documented policy.
39. Inactive panels are not automatically overwritten.
40. Global Selected Entity integration avoids feedback loops.
41. Command Palette actions target the active panel.
42. Keyboard focus follows accessible active-panel semantics.

### Market Data
43. Stage 33 canonical Market Data remains authoritative.
44. Stage 39 historical ingestion remains authoritative.
45. Stage 41 latest Quote remains authoritative.
46. Stage 42 Market Events are reused.
47. Stage 43 global WebSocket is reused.
48. Stage 44 freshness remains authoritative.
49. Historical read APIs are reused.
50. No duplicate Provider router is introduced.
51. No duplicate historical database is introduced.
52. No duplicate Quote cache is introduced.
53. No duplicate event bus is introduced.
54. No Provider calls occur directly from chart layouts.
55. No ingestion jobs are created by layout changes.
56. No fake OHLCV is generated for empty panels.

### Caching
57. Historical data is shared through authorized immutable cache entries via `ChartQueryCache`.
58. Cache keys preserve instrument UUID / canonical symbol.
59. Cache keys preserve series/venue.
60. Cache keys preserve interval.
61. Cache keys preserve adjustment basis.
62. Cache keys preserve price basis.
63. Cache keys respect entitlements.
64. No mutable cross-panel bar contamination occurs (deep cloning / immutability).
65. Historical pagination remains panel-specific.
66. Identical authorized reads are deduplicated via in-flight request coalescing.

### Live Subscriptions
67. One existing global WebSocket infrastructure is used.
68. Subscription reference counting is managed by `SharedChartSubscriptionManager`.
69. Identical compatible series share one underlying subscription.
70. Different venues and expirations remain distinct.
71. Pausing one panel does not pause other consumers.
72. Closing one panel does not close shared transport.
73. Final consumer release cleanly disposes stream controllers.
74. Reconnect reconciles each active panel.
75. Duplicate/older events are rejected.
76. Quote snapshots do not fabricate candles.
77. Last-price and freshness semantics remain correct.
78. Live subscription quotas (max 10) are respected.

### Indicators
79. Stage 69 Indicator Registry remains shared.
80. Stage 70 TA-Lib calculation services remain shared.
81. Indicator instances are panel-specific.
82. Indicator visibility is panel-specific.
83. Indicator parameters are panel-specific.
84. Indicator panes belong to their owning primary chart.
85. Compatible immutable calculation results may be cached.
86. One panel's indicator settings do not mutate another's.

### Drawings
87. Stage 71 drawing engine is reused.
88. Drawing controllers are panel-specific via `DrawingSessionStore.getForPanel(panelId)`.
89. Financial anchors are preserved across resizes.
90. Drawing selection is panel-specific.
91. Undo/Redo is panel-specific.
92. Drawing state is not automatically copied between panels.
93. Panel resizing does not corrupt drawing anchors.
94. Session-only drawing storage is preserved.
95. No persistent drawing database is introduced.

### Resource Management
96. Maximum visible chart count is bounded (4 visible panels).
97. Mounted renderers are bounded (max 4).
98. Historical memory is bounded via LRU query cache.
99. Indicator workload is bounded (max 12 per panel).
100. Drawing workload is bounded (max 250 per panel).
101. Live subscriptions are bounded (max 10).
102. Visible panels are prioritized.
103. Hidden panels are suspended.
104. Suspended panels reconcile on resume.
105. No unbounded hidden event queue is maintained.
106. Layout resizing does not remount all charts unnecessarily.
107. Error isolation is enforced via `ChartPanelErrorBoundary`.
108. Cleanup prevents resource leaks.
109. Performance metrics avoid high-cardinality labels.

### Responsive and Accessibility
110. Desktop supports full grid layouts.
111. Tablet presentation remains usable.
112. Mobile avoids microscopic four-chart grids.
113. Panel tabs are supported on narrow viewports (<768px).
114. Layout resize handles are keyboard accessible.
115. Active panel state is accessible.
116. Focus management is explicit.
117. Chart controls remain accessible.
118. Agent Dock interactions are supported.
119. Bottom Taskbar interactions are supported.
120. Light/dark themes are supported.
121. No purple gradients are introduced.
122. No emoji icons are introduced.
123. No decorative fake charts are introduced.

### Security
124. Authentication is reused.
125. Authorization is reused.
126. Each panel enforces market-data entitlements.
127. Shared caches do not leak restricted data.
128. Provider credentials remain server-side.
129. Arbitrary Provider URLs are rejected.
130. No arbitrary SQL is executed.
131. No canonical financial-data writes occur from layout changes.
132. No Trading orders are placed.
133. No Portfolio modifications occur.
134. No Agents execute.
135. No Workflows execute.
136. No LLM calls are required.

### Roadmap Boundaries
137. Stage 73 owns cross-chart synchronization.
138. Stage 74 owns saved chart layouts.
139. Stage 75 owns chart replay.
140. Stage 76 owns Watchlists.
141. Stage 80 owns Alerts.
142. Stage 94–98 own Screeners.
143. Stage 110+ own Portfolios.
144. Stage 115+ own Risk.
145. Stage 143 owns Backtesting.
146. Stage 144 owns Paper Trading.
147. Stage 145 owns Broker Sandbox.
148. Stage 146+ own Autonomous Agents.
149. No linked crosshairs are implemented prematurely.
150. No linked chart intervals are implemented prematurely.
151. No synchronized pan/zoom is implemented prematurely.
152. No automatic drawing synchronization is implemented prematurely.
153. No cloud-saved chart layouts are implemented prematurely.
154. No replay engine is implemented prematurely.
155. No chart-triggered trading strategy is implemented.
156. No duplicated market-data infrastructure is introduced.
157. Stage 72 must pass panel isolation tests.
158. Stage 72 must pass shared subscription tests.
159. Stage 72 must pass resource lifecycle tests.
160. Stage 72 must pass layout-resize tests.
161. Stage 72 must pass responsive/accessibility tests.
162. Stage 72 must pass Stage 66–71 regressions.
163. Documentation must match actual implementation.
164. Stage 73 is the next canonical development stage.

## Stage 73 — Build Professional Chart Synchronization V1

### Product
1. Stage 73 implements Chart Synchronization V1.
2. Synchronization remains inside `/charts`.
3. No additional Sidebar module is created.
4. Existing AppShell remains unchanged.
5. Stage 72 multi-chart layouts are reused.
6. Synchronization is opt-in.
7. Independent chart behavior remains the default.
8. Session-level group configuration is used.
9. Persistent saved configurations are deferred.
10. No fake financial data is introduced.

### Synchronization Groups
11. Groups have stable unique IDs.
12. Group membership uses stable Stage 72 panel IDs.
13. Each panel belongs to at most one group in V1.
14. Group membership is bounded.
15. Group settings are typed.
16. Group properties are individually configurable.
17. Group creation does not automatically overwrite chart state.
18. Group deletion restores independent behavior.
19. Panel removal preserves local configuration.
20. Group revision invalidates stale events.
21. Hidden/disposed panels cannot receive invalid actions.

### Event Architecture
22. Synchronization uses local application events.
23. Stage 42 market-data events remain separate.
24. No new Redis Stream is introduced.
25. No new global WebSocket is introduced.
26. Events identify source panel.
27. Events identify group and property.
28. Events use ordering metadata.
29. Duplicate events are handled.
30. Stale events are rejected.
31. Sync-applied changes are not retransmitted.
32. Asynchronous callback feedback is suppressed correctly.
33. Target clamping does not propagate back to source.
34. High-frequency events are coalesced.
35. Pending event work is bounded.
36. Disposed panels release listeners.

### Crosshairs
37. Crosshair linking is time-based.
38. Raw screen X coordinates are not propagated.
39. Candle indices are not cross-panel identity.
40. Different intervals use verified temporal mapping.
41. Daily bars preserve trading-date semantics.
42. Different market calendars are handled.
43. Missing target candles are not fabricated.
44. Price-coordinate synchronization is not assumed across assets.
45. Ghost crosshair rendering uses supported APIs.
46. Crosshair leave clears stale guides.
47. High-frequency pointer updates are throttled.
48. Accessible timestamp readouts are provided.

### Time Ranges
49. Visible ranges are represented as valid financial time coordinates.
50. Horizontal pan may be linked.
51. Horizontal zoom may be linked.
52. Price-axis autoscale remains independent.
53. Historical coverage is respected.
54. Clamping does not cause feedback loops.
55. Different market sessions do not create synthetic bars.
56. Invalid ranges are rejected.
57. Unsupported mappings produce explicit status.

### Instruments
58. Instrument linking uses canonical UUIDs.
59. Market-series identity is preserved.
60. Venue identity is preserved.
61. Futures expiration is preserved.
62. Crypto pair quote asset is preserved.
63. FX orientation is preserved.
64. Bond price/yield basis remains distinct.
65. Group updates require compatibility checks.
66. Market-data entitlements remain enforced.
67. Unsupported targets do not silently substitute instruments.
68. Partial failures are explicitly reported.
69. Indicator outputs are recalculated for new instruments.
70. Drawings remain context-isolated.
71. Live subscriptions reuse Stage 43 reference counting.
72. Global Selected Entity feedback loops are prevented.

### Intervals and Types
73. Interval linking uses Stage 68 canonical interval IDs.
74. Series-specific availability remains authoritative.
75. Unsupported intervals are not fabricated.
76. Unsupported destination intervals remain unchanged.
77. Stage 68 owns resampling.
78. Indicators recalculate on valid interval change.
79. Drawings preserve financial anchors.
80. Chart-type linking uses existing supported types.
81. Unsupported chart types remain unchanged.
82. Chart-type changes do not mutate historical bars.
83. Indicators/drawings remain available where compatible.

### Drawings
84. Drawing synchronization is opt-in.
85. Drawing compatibility is checked against canonical financial context.
86. Incompatible price bases are not linked.
87. Drawing synchronization uses committed commands if supported.
88. No direct shared mutable drawing references are used.
89. Existing drawings are not silently mass-overwritten.
90. Stable drawing synchronization identities are required.
91. Unsupported drawing linking is reported honestly.

### Security and Performance
92. Stage 13 Authentication is reused.
93. Stage 14 Authorization is reused.
94. Market-data entitlements remain enforced.
95. No user-submitted scripts execute.
96. No arbitrary SQL is accepted.
97. No Provider credentials are exposed.
98. No canonical OHLCV writes occur.
99. No market-data ingestion is triggered by synchronization.
100. No new Provider router is introduced.
101. No new historical database is introduced.
102. No duplicate global WebSocket is introduced.
103. No unbounded event queues are created.
104. Chart indicators are not recalculated on crosshair motion.
105. Historical data is not refetched on crosshair motion.
106. Chart viewport updates are bounded.
107. Per-panel resource budgets remain enforced.
108. No Trading orders are created.
109. No Portfolio transactions occur.
110. No Agent/Workflow execution occurs.
111. No LLM calls are required.

### UI and Accessibility
112. Synchronization controls use existing ATLAS design tokens.
113. Groups and members are visible.
114. Per-property toggles are functional.
115. Independent mode is accessible.
116. Group status is not color-only.
117. Keyboard group management is supported.
118. Screen-reader labels are supported.
119. Responsive layouts are supported.
120. Mobile hidden panels do not receive unnecessary render work.
121. Agent Dock remains compatible.
122. Bottom Taskbar remains compatible.
123. No purple gradients are introduced.
124. No emoji icons are introduced.
125. No fake synchronized market data is introduced.

### Roadmap Boundaries
126. Stage 74 owns saved chart layouts.
127. Stage 74 owns persistent synchronization groups.
128. Stage 75 owns Chart Replay.
129. Stage 76 owns Watchlists.
130. Stage 80 owns Alerts.
131. Stage 94–98 own Screeners.
132. Stage 110+ own Portfolios.
133. Stage 115+ own Risk.
134. Stage 143 owns Backtesting.
135. Stage 144 owns Paper Trading.
136. Stage 145 owns Broker Sandbox.
137. Stage 146+ own Agents.
138. No persistent layout database is added.
139. No cross-browser synchronization is introduced.
140. No multi-user collaborative charts are introduced.
141. No replay synchronization is introduced.
142. No automated trading signals are introduced.
143. Stage 73 must pass default independence tests.
144. Stage 73 must pass loop-prevention tests.
145. Stage 73 must pass crosshair/time-range tests.
146. Stage 73 must pass instrument/interval compatibility tests.
147. Stage 73 must pass entitlement tests.
148. Stage 73 must pass Stage 66–72 regressions.
149. Documentation must match actual implementation.
150. Stage 74 is the next canonical development stage.

## Stage 74 — Build Saved Chart Layouts V1

### Product
1. Stage 74 implements Saved Chart Layouts V1.
2. The canonical route remains `/charts`.
3. No new global Sidebar module is introduced.
4. Existing AppShell remains authoritative.
5. Saved Layouts are distinct from arrangement presets.
6. Saved Layouts are distinct from the global Saved module.
7. Saved Layouts are distinct from broader Workspaces.
8. Chart layouts are user-owned.
9. Cross-device restoration is supported.
10. Persistent configuration is separate from runtime market data.

### Database
11. PostgreSQL is the authoritative layout store.
12. JSONB stores versioned configuration documents.
13. Ownership metadata remains relational (`owner_user_id`).
14. Layout IDs are canonical UUIDs.
15. Normalized names follow a case-insensitive uniqueness policy per owner.
16. Layout revisions are monotonic integers starting at 1.
17. Document schema versions are explicit (`document_schema_version = 1`).
18. Database migrations are versioned with Alembic (`stage74_chart_layouts`).
19. Indexes serve actual queries (owner lookup, updated_at ordering, default uniqueness).
20. No new MongoDB database is introduced.
21. No duplicate financial-data database is introduced.
22. Layout documents do not contain OHLCV arrays.

### Versioning
23. Layout record revision differs from document schema version.
24. Indicator version differs from layout version.
25. Drawing version differs from layout version.
26. Old supported documents are migrated explicitly via `migrate_layout_document`.
27. Unsupported future documents are not silently corrupted; rejected with clear error.
28. Unknown-field handling is strictly validated against schemas.
29. Normalization is deterministic.
30. Layout schema validation is authoritative on the backend.

### Saved Configuration
31. Layout arrangement preset is saved (`single`, `two-columns`, `two-rows`, `three-left-focus`, `three-top-focus`, `four-grid`).
32. Panel order is saved.
33. Stable logical panel IDs are saved.
34. Split ratios are saved.
35. Active panel preference is saved.
36. Canonical instruments are saved by UUID.
37. Market-series identity dimensions (venue, basis, quotation unit) are preserved.
38. Intervals are saved.
39. Chart types are saved (`candlestick`, `bar`, `line`, `area`).
40. Compatible price-scale settings are saved.
41. Meaningful viewport state is saved (timestamps, following latest).
42. Indicator definitions and parameters are saved.
43. Calculated indicator output arrays are not saved.
44. Drawing objects and financial coordinates are saved.
45. Raw drawing screen pixels are not saved.
46. Drawing Undo/Redo stacks are not saved.
47. Synchronization group settings are saved.
48. Pending sync events are not saved.
49. Active WebSocket state is not saved.
50. Provider credentials are not saved.
51. Authentication tokens are not saved.
52. Broker credentials are not saved.

### Financial Identity
53. Instrument UUID remains canonical.
54. Ticker text is not a primary key.
55. Exchange/venue identity is preserved.
56. FX pair orientation is preserved.
57. Cryptocurrency pair denomination is preserved.
58. Futures expiration is preserved.
59. Bond price/yield basis remains distinct.
60. Raw/adjusted equity price bases remain distinct.
61. Saved layouts do not establish live market-data availability.
62. Saved layouts do not bypass licensing restrictions.
63. Restricted series are not silently substituted.
64. Delisted and expired securities may retain historical configurations.
65. Missing data is never fabricated.

### Indicators
66. Stage 69 Registry remains authoritative.
67. Stage 70 TA-Lib remains authoritative.
68. Indicator instances preserve their configurations.
69. Indicator outputs are recalculated after restoration.
70. Missing indicator versions are reported.
71. Insufficient history is reported.
72. No artificial indicator values are created.

### Drawings
73. Stage 71 drawing model remains authoritative.
74. Drawing anchors remain financial coordinates (`timestamp`, `price`).
75. Drawing schema version is preserved.
76. Drawing contexts are validated.
77. Styles are persisted.
78. Lock/visibility states are persisted.
79. Unsupported drawings are not rendered unsafely.
80. Drawing undo command history is not persisted.
81. No hidden cross-instrument price conversion is performed.

### Synchronization
82. Stage 73 Sync Controller remains authoritative.
83. Sync group definitions are serialized.
84. Member panel references are validated.
85. Property settings are persisted.
86. Initial hydration does not trigger user-originated sync events.
87. No synchronization cascade overwrites saved individual panel state.
88. Unsupported sync capabilities are reported.
89. No live collaboration system is introduced.

### CRUD
90. Users can create layouts.
91. Users can list layouts.
92. Users can open layouts.
93. Users can update layouts.
94. Users can rename layouts.
95. Users can duplicate layouts.
96. Users can delete layouts.
97. Default layout selection is supported.
98. Layout quotas are enforced (max 50 per user).
99. Names are validated (max 100 chars, non-empty, NFKC normalized).
100. Payload sizes are bounded (max 512 KiB).
101. Server errors do not destroy unsaved work.

### Concurrency
102. Optimistic concurrency is required.
103. Updates use an expected revision via `If-Match` headers.
104. Database update checks are atomic compare-and-swap.
105. Stale updates cannot silently overwrite newer revisions (412 Precondition Failed).
106. Conflicts are reported clearly in the UI.
107. Users may preserve conflicts through Save As New.
108. No collaborative merge engine is required.
109. Deletion conflicts are handled safely.
110. Revision numbers are not document schema versions.

### Frontend
111. Working state is separate from saved state.
112. Dirty-state detection uses persistent configuration comparisons.
113. Latest Quote changes do not mark layouts dirty.
114. Crosshair movement does not mark layouts dirty.
115. Temporary drawing previews do not mark layouts dirty.
116. Save confirmation follows server success.
117. Failed saves preserve working state.
118. Opening another layout warns about unsaved changes.
119. Layout list contains actual user records only.
120. No fake saved layouts are created.
121. Light/dark themes remain supported.
122. Responsive behavior is preserved.
123. No purple gradients are introduced.
124. No emoji icons are introduced.
125. No oversized decorative UI is introduced.

### Restoration
126. Restoration validates before applying structural state.
127. Supported older document schemas are migrated.
128. Invalid documents are rejected.
129. Current authorization is rechecked.
130. Current entitlements are rechecked.
131. Historical data is reloaded from existing services.
132. Live subscriptions use existing shared infrastructure.
133. Indicators are recalculated.
134. Drawings are reconstructed from financial anchors.
135. Sync groups are installed without feedback loops.
136. Partial operational availability is reported.
137. Structural load failures preserve prior workspace where practical.
138. Restoring layouts does not create ingestion jobs.
139. Restoring layouts does not fabricate market data.
140. Device screen size does not overwrite the saved arrangement.

### Import/Export
141. Versioned JSON export is supported (`atlas_chart_layout` envelope).
142. Only allowlisted configuration is exported.
143. Credentials are excluded.
144. Market-data caches are excluded.
145. Import files are size-bounded (< 512 KiB).
146. Import schemas are validated.
147. Unknown future versions are rejected safely.
148. Imported layouts receive the current authenticated owner.
149. Import does not execute scripts.
150. Import does not fetch arbitrary external URLs.
151. Duplicate names do not cause silent overwrite.

### Security
152. Authentication is enforced.
153. Ownership is enforced at both service and database layers.
154. RLS is applied where appropriate.
155. Elevated backend database roles still enforce ownership.
156. Cross-user UUID guessing does not reveal layouts (404 Not Found).
157. SQL queries are parameterized.
158. Names and labels are rendered safely (HTML tags stripped).
159. JSON payloads are treated as untrusted.
160. Resource quotas prevent unbounded storage.
161. Provider credentials remain server-side.
162. Market-data entitlements are revalidated.
163. No Trading orders are executed.
164. No Portfolio holdings are modified.
165. No Agents execute.
166. No Workflows execute.
167. No LLM calls are required.

### Roadmap Boundaries
168. Stage 75 owns Chart Replay.
169. Stage 76 owns Watchlists.
170. Stage 80 owns Alerts.
171. Stage 94–98 own Screeners.
172. Stage 110+ own Portfolios.
173. Stage 115+ own Risk.
174. Stage 119 owns the broader Saved module.
175. Stage 120 owns broader Workspaces.
176. Stage 143 owns Backtesting.
177. Stage 144 owns Paper Trading.
178. Stage 145 owns Broker Sandbox.
179. Stage 146+ own Autonomous Agents.
180. No replay engine is implemented.
181. No generic Saved platform is rebuilt.
182. No global Workspaces platform is rebuilt.
183. No collaborative editing is implemented.
184. No public layout marketplace is implemented.
185. No strategy engine is introduced.
186. No duplicate historical-data storage is introduced.
187. No duplicate global WebSocket is introduced.
188. Stage 74 must pass serialization round-trip tests.
189. Stage 74 must pass owner-isolation tests.
190. Stage 74 must pass concurrency tests.
191. Stage 74 must pass drawing/indicator restoration tests.
192. Stage 74 must pass sync hydration tests.
193. Stage 74 must pass cross-device tests.
194. Stage 74 must pass Stage 66–73 regressions.
195. Documentation must reflect actual implementation.
196. Stage 75 is the next canonical development stage.

## Stage 75: Historical Chart Replay V1

### Product & Scope
1. Stage 75 implements Historical Chart Replay V1 inside the existing `/charts` module.
2. No 21st top-level navigation module or separate replay application is created.
3. Stages 66–74 chart rendering, indicator, drawing, and multi-chart infrastructure are reused.
4. Replay uses genuine qualified canonical OHLCV bars; no duplicate market data store is introduced.
5. Historical replay is strictly distinct from realtime market streaming, backtesting, paper trading, and broker sandboxes.
6. Replay does not generate AI trading predictions, buy/sell signals, or autonomous agent trades.
7. V1 replay targets one chart panel at a time (`panel_id`); other workspace panels remain normal.
8. Replay sessions are ephemeral; no permanent database tables or long-term replay checkpoints are introduced.
9. Session lifetime is bounded by a 60-minute inactivity TTL.
10. Session ownership is authenticated and strictly enforced.

### Historical Data Semantics & Transparency
11. Stage 33 canonical OHLCV and Stage 39 historical ingestion remain authoritative.
12. ClickHouse remains the sole historical analytical datastore.
13. Canonical instrument UUIDs and market-series identities are strictly preserved.
14. Finalized bars only: V1 replays actual completed historical bars; it does not fabricate intraday price paths from daily OHLC.
15. Legitimate trading calendar gaps (weekends, holidays, halts) are preserved; no artificial bars are created.
16. Missing volume remains unavailable (`null`), never filled with zero.
17. Historical playback uses the selected revised/adjusted dataset and explicitly discloses that it does not guarantee point-in-time information availability unless explicit vintage records exist.
18. Source revision fingerprints are tracked to prevent mixing differing historical revisions.

### Future-Data Isolation (No-Look-Ahead)
19. Replay chart strictly gates visible history to observations up to and including the replay cursor ($[0 \dots \text{cursor\_index}]$).
20. Future bars ($N+1 \dots$) are physically excluded from the data series; visual masking workarounds are strictly prohibited.
21. Future bars never influence visible price scaling, zoom, or $Y$-axis autoscale bounds.
22. Crosshair inspection and data inspector cannot query observations beyond the replay cursor.
23. Tooltips never fabricate price values for future empty time coordinates.
24. Preexisting drawings anchored to future historical prices are suppressed during replay.
25. Replay-created annotations are scoped to the replay session and respect visible history.

### Playback Controller & Scheduler
26. Play, Pause, Step Forward (+1), Step Backward (-1), Restart, Seek, and Speed adjustments are supported.
27. Speed is defined as monotonic bars-per-second (0.5x, 1x, 2x, 5x, 10x).
28. Playback scheduler suppresses overlapping in-flight step requests to prevent race conditions and timer drift.
29. Pausing halts scheduled advancement immediately without deleting revealed history.
30. Reaching the final available historical bar halts playback and transitions to `END_OF_DATA`.
31. Session cleanup on exit releases all timers, aborts pending requests, and disposes ephemeral state.

### Replay-Aware Technical Indicators
32. Stage 69 Indicator Registry and Stage 70 TA-Lib calculators are reused directly.
33. All indicator calculations are cursor-bounded; inputs terminate exactly at the replay cursor.
34. Indicator warmup uses qualified earlier historical bars only; future bars are never used.
35. Stepping backward removes future indicator outputs and restores valid cursor-specific state.
36. Indicator cache keys incorporate `replay_session_id` and `cursor_revision` to prevent sharing with normal mode.

### Live Separation & Multi-Chart Compatibility
37. Global market data WebSocket (Stage 43) is preserved and remains active for other panels.
38. Live quote overlays and current market ticks are suppressed on the replayed panel.
39. The replayed panel displays a prominent `REPLAY` badge and never displays `LIVE`.
40. Non-replayed panels in multi-chart workspaces continue normal live operations.
41. Stage 73 synchronization actions (instrument, interval) directed to the replayed panel are safely suppressed.
42. Crosshair sync events with timestamps beyond the replay cursor are dropped to prevent look-ahead leakage.
43. Removing the replayed panel terminates the replay session safely.

### Stage 74 Saved Layout Compatibility
44. Stage 74 persistent layout documents are preserved; replay state is never serialized into layouts.
45. Replay progression does not mark saved layouts dirty.
46. Switching or loading a saved layout safely exits replay mode.
47. Normal pre-replay workspace configuration is cleanly restored on replay exit.

### Security & Resource Governance
48. Replay APIs require Stage 13 authentication and Stage 14 authorization.
49. User quota: maximum 5 active replay sessions per user.
50. Read-only operation: zero canonical OHLCV writes, zero database migrations, zero trading orders, zero LLM calls.
51. Stage 76 is the next canonical development stage (Watchlists V1).

## Stage 76: Watchlists V1: Persistent Multi-Asset Watchlists

### Product
1. Stage 76 implements Watchlists V1.
2. The canonical route is `/watchlists`.
3. Watchlists are user-owned collections.
4. Watchlists are not Portfolios.
5. Watchlists are not Trading orders.
6. Watchlists are not Screeners.
7. Watchlists are not data Providers.
8. Watchlists support multiple asset classes.
9. Existing AppShell remains authoritative.
10. Existing design tokens are reused.

### Identity
11. Watchlist IDs are stable UUIDs.
12. Membership item IDs are stable UUIDs.
13. Instrument UUIDs remain canonical.
14. Ticker text is not a primary key.
15. Company and Financial Instrument identities remain distinct.
16. Listing/venue distinctions are preserved.
17. Share classes remain distinct.
18. Depositary receipts remain distinct where canonically defined.
19. FX orientation is preserved.
20. Crypto quote-asset denomination is preserved.
21. Futures expiration is preserved.
22. Bond price/yield semantics remain distinct.
23. Fund NAV and exchange-traded price remain distinct.
24. Missing/deactivated instruments are not silently replaced.

### Database
25. PostgreSQL stores watchlist definitions.
26. PostgreSQL stores membership and order.
27. Canonical instruments remain in existing tables.
28. No duplicate instrument catalog is created.
29. Watchlist name normalization is defined.
30. Per-user name uniqueness is enforced where selected.
31. Foreign keys are used where appropriate.
32. Membership uniqueness is enforced.
33. Ordered positions are stored explicitly.
34. Reorder updates are transactional.
35. Deleting a Watchlist does not delete Instruments.
36. Database migrations are versioned.
37. Ownership indexes support efficient reads.
38. No market-price values are duplicated into membership records.

### Ownership
39. Authentication is required for mutations.
40. Owner user ID is server-derived.
41. Ownership is checked on every read/mutation.
42. Membership access is scoped through parent ownership.
43. Cross-user Watchlist access is forbidden.
44. UUID guessing cannot leak Watchlist metadata.
45. RLS is applied where appropriate.
46. Privileged backend roles still enforce ownership in service code.
47. SQL queries are parameterized.

### Watchlist CRUD
48. Create is supported.
49. List is supported.
50. Read is supported.
51. Rename is supported.
52. Delete is supported.
53. Multiple Watchlists are supported.
54. Empty Watchlists are supported.
55. Quotas are enforced.
56. Names are validated.
57. Deletion requires confirmation.
58. Successful mutations are confirmed by the backend.

### Membership
59. Add Instrument is supported.
60. Remove Instrument is supported.
61. Canonical search is reused.
62. Duplicate entries are prevented according to canonical series identity.
63. One Instrument may belong to multiple Watchlists.
64. Selected listing/series identity is preserved.
65. Membership quotas are enforced.
66. Invalid instrument IDs are rejected.
67. Unsupported Quote coverage does not require fabricated data.
68. Membership changes are transactional.

### Ordering
69. Manual ordering is the V1 default.
70. Positions are explicit.
71. Drag-and-drop is supported.
72. Keyboard reorder is supported.
73. Reorder is persisted.
74. Invalid reorder payloads are rejected.
75. Revisions prevent stale overwrites.
76. Duplicate row positions are prevented.
77. Optimistic frontend updates roll back on failure.

### Market Data
78. Existing canonical latest Quote service is reused.
79. Market snapshots are read-only.
80. No Watchlist-specific realtime streaming is added in Stage 76.
81. No new Provider subscription is created merely by membership.
82. No market-data ingestion job is triggered.
83. No upstream per-row Provider fanout occurs.
84. Snapshot reads are bounded/batched.
85. Instrument/series identity is validated.
86. Quote basis is preserved.
87. Quote currency/units are preserved.
88. Freshness uses Stage 44.
89. Delayed Quotes are labeled accurately.
90. Stale observations are labeled accurately.
91. Missing Quotes are unavailable, not zero.
92. Valid negative Futures prices remain supported.
93. Change percentages require qualified reference observations.
94. Equity previous-close rules are not blindly applied across all assets.
95. Crypto rolling 24-hour changes are not UTC-day changes.
96. Bond price and yield changes are not interchangeable.
97. Mutual fund NAV is not a live traded Last price.
98. No synthetic price changes are created.

### UI
99. A compact Watchlist table is provided.
100. Baseline columns are fixed in V1.
101. Instrument names are genuine.
102. Venue context is visible where relevant.
103. Quote units are accurate.
104. Row actions are functional.
105. No-Watchlists empty state is supported.
106. Empty Watchlist state is supported.
107. Loading/error states are supported.
108. Search and Add are functional.
109. Create/Rename/Delete dialogs are functional.
110. Row reorder is accessible.
111. Desktop/tablet/mobile layouts are supported.
112. Agent Dock compatibility is preserved.
113. Bottom Taskbar compatibility is preserved.
114. Light/dark themes are supported.
115. No purple gradients are introduced.
116. No emoji icons are introduced.
117. No fake financial metrics are introduced.
118. No artificial financial table records are seeded.

### Navigation
119. Global Search is reused.
120. Charts navigation uses canonical instrument/series identity.
121. Markets navigation uses actual existing routes.
122. Company navigation requires verified relationships.
123. Symbol matching alone does not establish issuer identity.
124. Unsupported destinations are not invented.
125. Global Selected Entity behavior follows existing context policy.

### Performance and Security
126. Watchlist reads are paginated.
127. Instrument metadata is batched.
128. Latest Quote retrieval is batched.
129. Query cache remains entitlement-aware.
130. No cross-user state leakage occurs.
131. No new global WebSocket is created.
132. No duplicate Provider abstraction is introduced.
133. No new historical market-data database is created.
134. No arbitrary Provider URL is accepted.
135. No arbitrary SQL is executed.
136. Names/descriptions are rendered safely.
137. Resource quotas are enforced.
138. No Trading orders are placed.
139. No Portfolio changes occur.
140. No Agent execution occurs.
141. No Workflow execution occurs.
142. No LLM calls are required.

### Roadmap Boundaries
143. Stage 77 owns advanced Watchlist Columns.
144. Stage 78 owns Live Watchlist Updates.
145. Stage 79 owns Watchlist Enrichment.
146. Stage 80 owns Watchlist Alerts.
147. Stage 81–88 own Companies.
148. Stage 89–93 own Economics.
149. Stage 94–98 own Screeners.
150. Stage 99–103 own News.
151. Stage 104–109 own Research.
152. Stage 110–114 own Portfolios.
153. Stage 115–118 own Risk.
154. Stage 119 owns the broader Saved module.
155. Stage 120 owns broader Workspaces.
156. Stage 143 owns Backtesting.
157. Stage 144 owns Paper Trading.
158. Stage 145 owns Broker Sandbox.
159. Stage 146+ own Agents.
160. No configurable column engine is implemented.
161. No Watchlist streaming subscriber is implemented.
162. No fundamentals enrichment engine is implemented.
163. No technical indicator Watchlist columns are implemented.
164. No News/event enrichment is implemented.
165. No Watchlist alert scheduler is implemented.
166. No broker/order action is implemented.
167. No autonomous monitoring is implemented.
168. Stage 76 must pass ownership tests.
169. Stage 76 must pass canonical identity tests.
170. Stage 76 must pass CRUD/membership tests.
171. Stage 76 must pass ordering/concurrency tests.
172. Stage 76 must pass Quote semantics tests.
173. Stage 76 must pass accessibility/responsive tests.
174. Stage 76 must pass relevant previous-stage regressions.
175. Documentation must match implementation.
176. Stage 77 is the next canonical stage.

---

# STAGE 77 — ADVANCED WATCHLIST COLUMNS V1

### Product
1. Stage 77 implements Advanced Watchlist Columns.
2. The route remains `/watchlists`.
3. Stage 76 Watchlist membership remains authoritative.
4. Stage 76 row ordering remains authoritative.
5. Column ordering is separate from membership ordering.
6. Existing AppShell is preserved.
7. Existing design system is reused.
8. No new global Sidebar module is created.
9. No synthetic market data is introduced.
10. No Trading/Agent functionality is introduced.

### Column Registry
11. All columns have stable IDs.
12. Column definitions are typed.
13. Column definitions are versioned.
14. Column categories are explicit (`identity`, `market`, `quote`, `quality`).
15. Data-source capabilities are explicit.
16. Supported asset classes are explicit.
17. Formatting behavior is explicit.
18. Sorting policies are explicit.
19. Visibility policies are explicit.
20. Width constraints are explicit.
21. Pin capabilities are explicit.
22. Registry IDs are validated on backend.
23. Display labels are not column identities.
24. Arbitrary executable columns are rejected.
25. Unsupported future columns are not falsely advertised.

### Column Values
26. Values retain canonical types.
27. Display formatting is separate from source data.
28. Missing does not equal zero.
29. Valid negative values are preserved.
30. Currency units are explicit.
31. Quote kinds are preserved.
32. Source provenance is preserved.
33. Observation timestamps are preserved.
34. NAV valuation dates remain distinct from Last trades.
35. Bond price and yield remain distinct.
36. FX indicative Quotes are not exchange Last trades.
37. Crypto change windows remain explicit.
38. Unsupported assets show qualified unavailable states.
39. Entitlements are enforced independently of column visibility.
40. No fabricated numerical values are generated.

### Visibility and Ordering
41. Optional columns can be shown.
42. Optional columns can be hidden.
43. Instrument identity remains visible (`instrument.symbol` is mandatory).
44. Column order is configurable.
45. Drag-and-drop is supported.
46. Keyboard ordering is supported.
47. Unknown IDs are rejected.
48. Duplicate IDs are rejected.
49. Column ordering never changes Watchlist membership order.
50. Reset Defaults restores canonical configuration.

### Resizing and Pinning
51. Column resizing is supported.
52. Widths are bounded by `min_width` and `max_width`.
53. Widths are persisted.
54. Resize persistence occurs on commit/debounce.
55. Left pinning is supported.
56. Pinned offsets use actual cumulative widths.
57. Pinned columns do not overlap.
58. Excessive pinning is limited to 5 columns.
59. Keyboard pin/resize alternatives are available.
60. Responsive presentation does not corrupt saved widths.

### Sorting
61. Ascending sorting is supported for qualified columns.
62. Descending sorting is supported for qualified columns.
63. Manual row order remains the default.
64. Sorting does not modify membership positions.
65. Sorting uses stable tie breakers (manual position, then UUID item ID).
66. Missing values sort last on both ascending and descending.
67. Numeric values are not sorted as formatted strings.
68. Dates are sorted chronologically.
69. Financial sorts require compatible units.
70. Incompatible currencies are not blindly ranked.
71. Incompatible bond yield/price values are not ranked together.
72. Percentage comparisons require compatible methodologies.
73. Sorting scope matches the actual full authorized list (up to 250 items).
74. Partial-page sorting is not mislabeled as full-list sorting.
75. Mutable market snapshot sorting uses a coherent snapshot policy.
76. Unsupported sorts are disabled honestly.

### Persistence
77. Column preferences are saved per Watchlist.
78. PostgreSQL remains the authoritative preference store (`watchlist_column_preferences`).
79. JSONB stores versioned presentation configuration.
80. The schema includes version 1.
81. Preference revision protects updates independently of membership revisions.
82. Parent Watchlist ownership is enforced.
83. Deleting a Watchlist cascades and removes associated preferences.
84. Default configuration works without an explicit saved record.
85. Cross-device restoration is supported.
86. No localStorage-only persistence is claimed.
87. No market observations are persisted in preferences.
88. No Provider credentials are persisted.
89. No runtime DOM objects are persisted.

### Concurrency
90. Updates use an expected revision.
91. Atomic updates prevent lost writes.
92. Stale changes are rejected with 412/409.
93. Save failures preserve working state.
94. Conflicts are visible to users.
95. Preference revision is independent from membership revision.
96. Resizing does not create hundreds of writes per second (400ms debounce).

### Data Projection
97. Existing canonical metadata is reused.
98. Existing latest Quote service is reused.
99. Existing freshness service is reused.
100. Existing Provider routing remains authoritative.
101. Selected fields are projected through allowlisted definitions.
102. Source reads are batched.
103. Hidden columns do not cause unnecessary reads.
104. No per-cell Provider fanout occurs.
105. No new historical ingestion is triggered.
106. No new Watchlist live subscriptions are created.
107. Shared cache remains entitlement-aware.
108. Canonical market-data observations are not duplicated.

### UI and Accessibility
109. A Column Manager is provided.
110. Column descriptions are accessible.
111. Show/Hide controls function.
112. Header reorder functions.
113. Width resizing functions.
114. Pin/Unpin functions.
115. Sorting functions.
116. Reset Defaults functions.
117. Sticky headers are supported.
118. Horizontal scrolling is supported.
119. Numeric alignment follows financial conventions.
120. Tabular numerals are used where appropriate.
121. Keyboard configuration is supported.
122. Screen-reader labels and live announcements are supported.
123. Status is not color-only.
124. Mobile presentation remains usable with horizontal scroll.
125. Agent Dock compatibility is preserved.
126. Bottom Taskbar compatibility is preserved.
127. Light/dark themes are preserved.
128. No purple gradients are introduced.
129. No emoji icons are introduced.
130. No fake financial metrics are introduced.

### Security and Performance
131. Authentication is required.
132. Watchlist ownership is required.
133. Data entitlements are enforced.
134. Column IDs are allowlisted.
135. No arbitrary SQL expressions are executed.
136. No user-provided scripts are executed.
137. No arbitrary Provider URLs are fetched.
138. No Provider secrets are exposed.
139. No XSS is introduced.
140. Column limits are enforced (max 20 visible).
141. Width limits are enforced ([min, max]).
142. Request limits are enforced.
143. Table rendering is bounded.
144. Query caching is reused.
145. No new global WebSocket is created.
146. No Trading orders are placed.
147. No Portfolio changes occur.
148. No Agents execute.
149. No Workflows execute.
150. No LLM calls are required.

### Roadmap Boundaries
151. Stage 78 owns Live Watchlist Updates.
152. Stage 79 owns Watchlist Enrichment.
153. Stage 80 owns Watchlist Alerts.
154. Stage 81–88 own Companies.
155. Stage 89–93 own Economics.
156. Stage 94–98 own Screeners.
157. Stage 99–103 own News.
158. Stage 104–109 own Research.
159. Stage 110–114 own Portfolios.
160. Stage 115–118 own Risk.
161. Stage 119 owns the global Saved module.
162. Stage 120 owns broader Workspaces.
163. Stage 143 owns Backtesting.
164. Stage 144 owns Paper Trading.
165. Stage 145 owns Broker Sandbox.
166. Stage 146+ own Agents.
167. No realtime Watchlist streaming is implemented.
168. No Watchlist indicator calculation engine is implemented.
169. No fundamentals enrichment engine is implemented.
170. No News or event enrichment engine is implemented.
171. No alert scheduler is implemented.
172. No arbitrary formula engine is implemented.
173. No full Screener system is implemented.
174. No duplicate financial-data store is implemented.
175. No duplicate Provider router is implemented.
176. No duplicate WebSocket infrastructure is implemented.
177. Stage 77 must pass Column Registry tests.
178. Stage 77 must pass value-formatting tests.
179. Stage 77 must pass sort compatibility tests.
180. Stage 77 must pass preference persistence tests.
181. Stage 77 must pass concurrency tests.
182. Stage 77 must pass ownership/entitlement tests.
183. Stage 77 must pass Stage 76 regressions.
184. Documentation must match actual implementation.
185. Stage 78 is the next canonical development stage.

## Stage 78: Live Watchlist Updates V1

### Product
1. Stage 78 implements Live Watchlist Updates V1.
2. The route remains `/watchlists`.
3. Stage 76 membership remains authoritative.
4. Stage 77 Column Registry remains authoritative.
5. Existing AppShell is preserved.
6. Live data originates from verified ATLAS market-data services.
7. No synthetic production market data is introduced.
8. No new global Sidebar module is created.
9. Watchlists remain different from Portfolios.
10. Watchlist streaming does not imply trading.

### Streaming Architecture
11. Stage 41 Quote ingestion remains authoritative.
12. Stage 42 Market Event Pipeline remains authoritative.
13. Stage 43 shared WebSocket remains authoritative.
14. Stage 44 freshness remains authoritative.
15. No second frontend global WebSocket is created.
16. No per-row WebSocket is created.
17. No browser-to-Provider credential connection is created.
18. No second market event bus is created.
19. No duplicate latest Quote store is created.
20. No historical data store is introduced.

### Subscriptions
21. Subscriptions use canonical market-series identity.
22. Ticker text is not the subscription key.
23. Venue distinctions are preserved.
24. FX orientation is preserved.
25. Crypto quote-asset identity is preserved.
26. Futures expiration is preserved.
27. Financial measure basis is preserved.
28. Subscriptions use the shared registry.
29. Reference counting is preserved.
30. Multiple consumers share eligible subscriptions.
31. Unsubscribe does not affect remaining consumers.
32. Subscribe acknowledgments are validated.
33. Server-side entitlement checks are mandatory.
34. Subscription limits are enforced.
35. Unauthorized subscriptions are rejected.
36. Delayed-only entitlements remain delayed.
37. Active Watchlist visibility informs desired subscriptions.
38. Visible rows are prioritized.
39. Overscan is bounded.
40. Subscription churn is coalesced.
41. Background views release unnecessary references.
42. Charts consumers remain unaffected.

### Events
43. Existing event schemas are reused.
44. Event versions are validated.
45. Canonical instrument IDs are checked.
46. Market-series identity is checked.
47. Quote measures are checked.
48. Source identity is preserved.
49. Observation timestamps are preserved.
50. Receipt timestamps remain distinct.
51. Duplicate events are rejected.
52. Older events cannot overwrite newer valid state.
53. Sequence scope is source-specific.
54. No fictional global sequence is assumed.
55. Sequence gaps trigger appropriate reconciliation.
56. Source changes use canonical merge policy.
57. Malformed events are isolated.
58. Events for unsubscribed series are ignored appropriately.
59. No OHLC candles are derived from sparse Quote events.

### Financial Semantics
60. Last is distinct from Bid.
61. Last is distinct from Ask.
62. Mid is distinct from executed Last.
63. Fixing is distinct from live trade.
64. Futures settlement is distinct from Last.
65. Fund NAV is distinct from market price.
66. Bond price is distinct from yield.
67. Currency pairs retain orientation.
68. Crypto quote assets retain denomination.
69. Numerical precision is preserved.
70. Valid zero is not treated as missing.
71. Valid negative Futures prices remain supported.
72. Missing Volume is not fabricated.
73. Price changes require valid comparable references.
74. Tick-direction cues do not masquerade as official session changes.
75. No fake Volume/market cap data is generated.

### Reconciliation
76. Initial latest snapshots are qualified.
77. Startup snapshot/stream races are handled.
78. Older snapshots cannot revert newer state.
79. Buffer sizes are bounded.
80. Watermarks are used only where supported.
81. Missing event continuity is not fabricated.
82. Reconnect triggers valid subscription reconciliation.
83. Latest-state resync uses existing services.
84. Stale async responses are rejected.
85. Source revisions are handled through canonical policy.

### Freshness
86. WebSocket connection status differs from market-data freshness.
87. Realtime entitlement differs from delivery cadence.
88. Delayed observations are labeled.
89. Stale observations are labeled.
90. Duplicate delivery does not refresh observation time.
91. Provider outage is represented accurately.
92. Market closure is based on verified schedules.
93. Mixed-quality Watchlists are supported.
94. No false uniform realtime badge is shown.

### Frontend Rendering
95. Existing Stage 77 table is reused.
96. Stable Watchlist item IDs are preserved.
97. Stable Column IDs are preserved.
98. Only compatible cells update.
99. UI updates are batched.
100. High-frequency events do not rerender the whole AppShell.
101. Row layout remains stable.
102. Pinned columns remain functional.
103. Column visibility remains functional.
104. Manual membership order is preserved.
105. Sorting behavior follows Stage 77 policy.
106. No partial-page global ranking claims are introduced.
107. Update highlighting is restrained.
108. Color is not the only direction indicator.
109. Reduced-motion preferences are respected.
110. No market alert is created from a visual highlight.

### Security
111. Authentication is required.
112. Subscription authorization is server-side.
113. Entitlement revocation is enforced.
114. User/tenant data scope is preserved.
115. Arbitrary topic subscription is rejected.
116. Provider secrets remain server-side.
117. No arbitrary SQL is permitted.
118. Resource limits prevent subscription abuse.
119. No canonical market-data writes originate from table rendering.
120. No Trading orders are placed.
121. No Portfolio changes occur.
122. No Agents execute.
123. No Workflows execute.
124. No LLM calls are required.

### Performance
125. Visible-row subscription budgets are enforced.
126. Overscan is bounded.
127. Pending event buffers are bounded.
128. Event deduplication state is bounded.
129. UI rendering is coalesced.
130. Network subscriptions are reference counted.
131. Reconnect attempts use shared backoff.
132. Repeated fast scrolling does not create subscription storms.
133. Multiple Watchlists do not create unnecessary simultaneous subscriptions.
134. No per-cell Provider fanout occurs.
135. Existing caches are reused.
136. Observability is low-cardinality.
137. Performance tests measure actual behavior.

### UI and Accessibility
138. Live connection status is visible.
139. Data freshness is separate from connection status.
140. Delayed/stale states are visible.
141. Source details are accessible.
142. Actual observation timestamps are available.
143. Keyboard navigation is preserved.
144. Screen-reader announcements are rate-limited.
145. Reduced-motion settings are supported.
146. Mobile responsive behavior is preserved.
147. Agent Dock compatibility is preserved.
148. Bottom Taskbar compatibility is preserved.
149. Existing ATLAS design tokens are reused.
150. No purple gradients are introduced.
151. No emoji icons are introduced.
152. No fabricated market prices are displayed.

### Roadmap Boundaries
153. Stage 79 owns Watchlist Enrichment.
154. Stage 80 owns Watchlist Alerts.
155. Stage 81–88 own Companies.
156. Stage 89–93 own Economics.
157. Stage 94–98 own Screeners.
158. Stage 99–103 own News.
159. Stage 104–109 own Research.
160. Stage 110–114 own Portfolios.
161. Stage 115–118 own Risk.
162. Stage 119–120 own Saved/Workspaces.
163. Stage 121–128 own Terminal/AI.
164. Stage 129–140 own Maps/Intelligence.
165. Stage 141–142 own Options/Quant pricing.
166. Stage 143 owns Backtesting.
167. Stage 144 owns Paper Trading.
168. Stage 145 owns Broker Sandbox.
169. Stage 146+ own Agents.
170. No Watchlist fundamentals engine is introduced.
171. No Watchlist technical indicator engine is introduced.
172. No Watchlist News/event enrichment is introduced.
173. No market-alert evaluation worker is introduced.
174. No threshold notification scheduler is introduced.
175. No automated trading logic is introduced.
176. No duplicate streaming infrastructure is introduced.
177. Stage 78 must pass entitlement tests.
178. Stage 78 must pass subscription reference-counting tests.
179. Stage 78 must pass event-ordering tests.
180. Stage 78 must pass snapshot/reconciliation tests.
181. Stage 78 must pass freshness tests.
182. Stage 78 must pass rendering/performance tests.
183. Stage 78 must pass Stage 76–77 regressions.
184. Documentation must reflect the implementation.
185. Stage 79 is the next canonical development stage.

## Stage 79 Decisions — Build Advanced Watchlist Enrichment V1: Company Fundamentals, Financial Ratios, Technical Indicator Snapshots, Corporate Events, Earnings Information, Relevant News, Multi-Source Data Qualification, Provenance-Aware Column Registry Integration and High-Performance Financial Intelligence Tables

### Product
1. Stage 79 implements Watchlist Enrichment V1.
2. The module remains `/watchlists`.
3. The Stage 77 Column Registry is extended.
4. No separate twenty-first global module is created.
5. No automated trading, order generation, or portfolio mutations are executed.
6. Financial intelligence tables maintain dense institutional terminal styling.

### Roadmap Boundaries
7. Stage 80 owns Watchlist Alerts V1.
8. Stage 81 owns Companies V1.

---

## Stage 80 Decisions — Build Watchlist Alerts V1: Persistent Financial Monitoring Rules, Realtime Price Thresholds, Qualified Percentage-Change Conditions, Event-Driven Alert Evaluation, Durable Notification Delivery, Trigger History, Cooldowns, Deduplication, Entitlement Enforcement and Production-Grade Alert Lifecycle Management

### Product
1. Stage 80 implements Watchlist Alerts V1.
2. The module remains `/watchlists`.
3. Stage 49 Notification Center is reused.
4. Alerts are user-owned persistent rules.
5. Alerts are not orders.
6. Alerts are not Portfolios.
7. Alerts are not Trading strategies.
8. No new global navigation module is created.
9. The ATLAS design system is reused.
10. No fake financial conditions or notifications are generated.

### Identity
11. Alert IDs are UUIDs.
12. User ownership is explicit.
13. Watchlist/item relationships are validated.
14. Canonical Instrument identity is preserved.
15. Market-series identity is preserved.
16. Ticker is not an authoritative key.
17. Venue distinctions are preserved.
18. FX orientation is preserved.
19. Crypto quote denomination is preserved.
20. Futures expiration is preserved.
21. Bond measure basis is preserved.
22. Fund NAV and market price remain distinct.

### Conditions
23. Price-above is supported.
24. Price-below is supported.
25. Crossing-above is supported.
26. Crossing-below is supported.
27. Qualified percentage-change alerts are supported.
28. Above/below and crossing have separate semantics.
29. Crossing requires valid previous/current observations.
30. First snapshot does not imply crossing.
31. Equality behavior is defined.
32. Repeat crossings require re-arming.
33. Cooldowns do not replace re-arming.
34. Rule inputs are typed and validated.
35. Unsupported measures are rejected.
36. No arbitrary user scripts are executed.

### Financial Correctness
37. Source identity is validated.
38. Venue identity is validated.
39. Quote measure is validated.
40. Currency/units are validated.
41. Numerical comparisons use decimal-safe semantics.
42. Genuine zero is handled correctly.
43. Genuine negative Futures prices are supported.
44. Price and yield are distinct.
45. Indicative Quotes are not relabeled Last.
46. Percentage changes require compatible references.
47. Zero denominators are rejected.
48. Crypto rolling 24-hour reference is distinguished.
49. Session reference changes are handled.
50. No invented previous close is permitted.

### Freshness and Entitlements
51. Stage 44 freshness remains authoritative.
52. Delayed feeds remain labeled delayed.
53. Stale movement observations do not trigger.
54. Duplicate delivery does not create new observation time.
55. Market closure uses verified metadata.
56. Feed degradation is visible.
57. Creation checks entitlement.
58. Activation checks entitlement.
59. Evaluation checks entitlement.
60. Entitlement revocation stops unauthorized evaluation.

### Evaluation
61. Evaluation runs server-side.
62. Browser visibility is not required.
63. Stage 42 Market Events are reused.
64. Stage 41 latest Quote state is reused.
65. No per-alert upstream Provider connection is created.
66. No second global WebSocket is created.
67. Active-rule lookup is indexed.
68. Rule evaluation is bounded.
69. Event schema is validated.
70. Event IDs are deduplicated.
71. Source sequences are scoped correctly.
72. Out-of-order observations do not regress state.
73. Gaps cause safe uncertainty/rebaseline.
74. Reconnection does not invent missed crossings.
75. Provider changes do not silently create crossings.
76. Multiple workers coordinate safely.
77. Worker restart restores durable state.
78. Worker health is observable.
79. Backend deployment requirements are documented.

### Lifecycle
80. Create is supported.
81. Read is supported.
82. Update is supported.
83. Delete is supported.
84. Pause is supported.
85. Resume is supported.
86. One-shot is supported.
87. Recurring is supported.
88. Expiration is supported.
89. Cooldowns are supported.
90. Re-arming is supported.
91. Rule revisions protect concurrent updates.
92. Editing may reset evaluator baselines.
93. Removing a Watchlist item follows an explicit alert policy.
94. Deleting a Watchlist follows an explicit alert policy.
95. Trigger history retention is defined.

### Persistence
96. PostgreSQL stores alert rules.
97. PostgreSQL stores durable evaluation state.
98. PostgreSQL stores trigger history.
99. Versioned migrations are used.
100. Foreign keys and indexes are defined.
101. Owner-scoped queries are mandatory.
102. RLS is applied where appropriate.
103. Trigger deduplication is atomic.
104. No canonical Quote values are duplicated as a new financial-history store.
105. No arbitrary unbounded event history is retained.

### Notifications
106. Stage 49 is authoritative.
107. A trigger record is separate from delivery.
108. Durable notification handoff is used.
109. Outbox is transactional where applicable.
110. Delivery retries are bounded.
111. Notification records are deduplicated.
112. Failed delivery does not erase trigger history.
113. Market observation time is preserved.
114. Evaluation time is preserved.
115. Delayed-feed context is disclosed.
116. Deep links use canonical identity.
117. Notification ownership is enforced.
118. Exactly-once external delivery is not falsely guaranteed.

### Resource Protection
119. Alert quotas are enforced.
120. Per-series concentration is bounded.
121. Notification rates are bounded.
122. Concurrent evaluation is bounded.
123. Rule lookups are indexed.
124. Event buffers are bounded.
125. Feed consumption is shared.
126. No full-rule scan per tick is permitted.
127. Expired rules stop evaluating.
128. Inactive rules release unnecessary work.
129. Observability is low-cardinality.

### Security
130. Authentication is required.
131. Alert ownership is enforced.
132. Cross-user data is isolated.
133. Source licensing is enforced.
134. Subscription authorization is enforced.
135. No arbitrary SQL is allowed.
136. No executable custom scripts are allowed.
137. Provider credentials remain server-side.
138. External delivery channels require approval.
139. No Trading orders are placed.
140. No Portfolio changes occur.
141. No Broker actions occur.
142. No Agents execute.
143. No Workflows execute.
144. No LLM calls are required.

### UI and Accessibility
145. Create Alert is functional.
146. Edit Alert is functional.
147. Pause/Resume is functional.
148. Delete is functional.
149. Alert List is functional.
150. Trigger History is functional.
151. Source/freshness status is visible.
152. Realtime/delayed distinction is visible.
153. Alert evaluation health is visible.
154. Threshold units are displayed.
155. Keyboard navigation is supported.
156. Screen-reader status is supported.
157. Responsive layout is supported.
158. Agent Dock compatibility is preserved.
159. Bottom Taskbar compatibility is preserved.
160. No purple gradients are introduced.
161. No emoji icons are introduced.
162. No fake alert records are introduced.

### Roadmap Boundaries
163. Stage 81–88 own Companies.
164. Stage 89–93 own Economics.
165. Stage 94–98 own Screeners.
166. Stage 99–103 own News.
167. Stage 104–109 own Research.
168. Stage 110–114 own Portfolios.
169. Stage 115–118 own Risk.
170. Stage 119–120 own Saved/Workspaces.
171. Stage 121–128 own Terminal/AI.
172. Stage 129–140 own Maps/Intelligence.
173. Stage 141–142 own Options/Quant pricing.
174. Stage 143 owns Backtesting.
175. Stage 144 owns Paper Trading.
176. Stage 145 owns Broker Sandbox.
177. Stage 146+ own Agents.
178. No trading-order automation is implemented.
179. No full workflow engine is implemented.
180. No independent external communications platform is implemented.
181. No new market-data Provider router is implemented.
182. No duplicate market-data database is implemented.
183. Stage 80 must pass rule tests.
184. Stage 80 must pass crossing tests.
185. Stage 80 must pass deduplication tests.
186. Stage 80 must pass crash recovery tests.
187. Stage 80 must pass entitlement tests.
188. Stage 80 must pass notification tests.
189. Stage 80 must pass Stage 76–79 regressions.
190. Documentation must reflect actual behavior.
191. Stage 81 is the next canonical stage.

## Stage 81 — Build Companies V1

### Product
1. Stage 81 implements Companies V1.
2. The route remains `/companies`.
3. No new global Sidebar module is introduced.
4. The existing AppShell is preserved.
5. Company Overview is professional and data-driven.
6. No fictional Company profiles are seeded.
7. No duplicate Company master is created.
8. No new Provider ingestion system is introduced.
9. No trading action is introduced.
10. No AI-generated Company facts are introduced.

### Identity
11. Stage 18 Company Entities remain authoritative.
12. Stage 16 Universal Entity identity is reused.
13. Company UUIDs are stable.
14. Ticker text is not a Company primary key.
15. Legal name and display name are separate.
16. Company aliases use Stage 22.
17. Brand and legal corporation are distinct.
18. Parent and subsidiary are distinct.
19. Public and private companies are supported where canonically represented.
20. Inactive and dissolved entities retain lifecycle context.
21. Company mergers do not automatically merge historical identities.

### Identifiers
22. Stage 21 identifier infrastructure is reused.
23. LEI/CIK are scoped correctly.
24. Security ISINs are not treated as legal-company IDs.
25. Security FIGIs are not treated as Company IDs.
26. Identifier source and verification are preserved.
27. Missing identifiers are not fabricated.
28. Identifier conflicts are handled through canonical policy.

### Sector and Industry
29. Industry taxonomy identity is explicit.
30. Taxonomy version is preserved where available.
31. Sector and industry hierarchy are distinct.
32. Source provenance is preserved.
33. Missing classification remains unavailable.
34. No sector is inferred merely from a Company name.
35. Sector sharing does not automatically establish Peer relationships.

### Geography
36. Stage 19 Geographic Entities are reused.
37. Headquarters and incorporation are distinct.
38. Domicile and exchange country are distinct.
39. Company addresses are not guessed.
40. Location metadata has source/as-of context.
41. No facility-level geospatial system is built.

### Relationships
42. Stage 23 Relationship Graph remains authoritative.
43. Company and Financial Instrument identities are distinct.
44. Security and listing identities are distinct.
45. Multiple share classes are preserved.
46. Cross-listings are preserved.
47. Depositary receipts are distinct instruments where modeled.
48. Corporate bond issuers are verified.
49. Subsidiary/guarantor roles are not guessed.
50. ETF/fund manager relationships remain distinct.
51. Ticker matching alone is not a valid issuer join.
52. Relationship source and validity are preserved.
53. Missing verified relationships are not fabricated.

### Market Data
54. Stage 33 remains authoritative.
55. Stage 41 latest Quote state is reused.
56. Stage 44 freshness is reused.
57. Company market data is qualified through securities.
58. A Company is not assigned one universal Last price.
59. Venue and source are preserved.
60. Quotation currency is preserved.
61. Quote measures remain distinct.
62. Fund NAV and market price remain distinct.
63. Bond price and yield remain distinct.
64. Valid zero and negative prices are not incorrectly rejected.
65. Missing Quotes remain unavailable.
66. Market cap is not invented from incompatible share counts.
67. Duplicate cross-listings are not double-counted.
68. Opening a Company does not create Provider fanout.
69. No new market streaming subsystem is introduced.

### Financial Summary
70. Stage 34 Fundamentals remains authoritative.
71. Stage 81 displays only high-level verified summary metrics.
72. Reporting period is preserved.
73. Reporting currency is preserved.
74. Publication date is preserved.
75. Statement scope is preserved.
76. Restatement context is preserved.
77. Quarterly and annual data remain distinct.
78. TTM is not guessed.
79. Unsupported financial metrics remain unavailable.
80. No new detailed Statements engine is introduced.
81. No comprehensive Ratio engine is introduced.

### News and Documents
82. Stage 36 canonical references are reused.
83. News association must be verified.
84. Ticker text alone is insufficient.
85. Actual headlines and sources are displayed.
86. Publication timestamps are preserved.
87. Article/document licensing is enforced.
88. No new News crawler is introduced.
89. No News clustering or sentiment engine is introduced.
90. No full filing parser is introduced.

### APIs and Data
91. Company read APIs are typed.
92. Existing FastAPI architecture is reused.
93. Company UUID validation is enforced.
94. Related securities are paginated.
95. News/documents are paginated.
96. Section-level partial availability is supported.
97. Source qualification is preserved.
98. No canonical Company writes occur during profile reads.
99. No autonomous ingestion occurs on page load.
100. No duplicate financial datasets are persisted.

### Search and Navigation
101. Stage 45 Global Search is reused.
102. Legal names and aliases are supported according to actual search capabilities.
103. Company search results use canonical identity.
104. Ambiguous Company names remain distinguishable.
105. Unlisted companies may appear where authorized.
106. Global Selected Entity type remains correct.
107. Markets navigation uses actual Financial Instruments.
108. Charts navigation uses actual market-series identity.
109. Watchlist actions reuse Stage 76.
110. Company UUID is not submitted as a Watchlist Financial Instrument UUID.
111. Company News/Document links are verified.
112. Unsupported routes are not invented.

### UI
113. Companies uses professional high-density design.
114. Company search is functional.
115. Company selection is functional.
116. Company Header is functional.
117. Corporate Profile is functional.
118. Classification section is functional.
119. Geography section is functional.
120. Identifier section is functional.
121. Related Securities table is functional.
122. Market Context is qualified.
123. Financial Summary is qualified.
124. News/Document references are genuine.
125. Partial loading and errors are supported.
126. Dark/light mode is preserved.
127. Agent Dock compatibility is preserved.
128. Bottom Taskbar compatibility is preserved.
129. Responsive layouts are supported.
130. Keyboard accessibility is supported.
131. Screen-reader accessibility is supported.
132. No purple gradients are introduced.
133. No emoji icons are introduced.
134. No fake Company metrics are introduced.

### Security and Performance
135. Authentication is respected.
136. Source entitlements are enforced.
137. Restricted company records are protected.
138. SQL queries are parameterized.
139. External URLs are validated.
140. Provider credentials are never exposed.
141. Pagination is enforced.
142. Query budgets are enforced.
143. Cache isolation respects entitlements.
144. Related metadata is batched.
145. Market snapshots are batched.
146. No Provider fanout occurs per listing.
147. No market-data writes occur during Company reads.
148. No Trading orders are placed.
149. No Portfolio changes occur.
150. No Agents execute.
151. No Workflows execute.
152. No LLM calls are required.

### Roadmap Boundaries
153. Stage 82 owns Financial Statements.
154. Stage 83 owns Financial Ratios.
155. Stage 84 owns Earnings.
156. Stage 85 owns Ownership.
157. Stage 86 owns Filings.
158. Stage 87 owns Peers.
159. Stage 88 owns Supply Chains.
160. Stages 89–93 own Economics.
161. Stages 94–98 own Screeners.
162. Stages 99–103 own News.
163. Stages 104–109 own Research.
164. Stages 110–114 own Portfolios.
165. Stages 115–118 own Risk.
166. Stages 119–120 own Saved/Workspaces.
167. Stages 121–128 own Terminal/AI.
168. Stages 129–140 own Maps/Intelligence.
169. Stages 141–142 own Options/Quant pricing.
170. Stage 143 owns Backtesting.
171. Stage 144 owns Paper Trading.
172. Stage 145 owns Broker Sandbox.
173. Stages 146+ own Agents.
174. No full financial statement analysis is implemented.
175. No new ratio calculation platform is implemented.
176. No earnings forecast platform is implemented.
177. No ownership graph is implemented.
178. No filings ingestion/parser is implemented.
179. No automated peer-discovery engine is implemented.
180. No supply-chain graph is implemented.
181. No duplicated Company database is implemented.
182. No duplicated market-data pipeline is implemented.
183. Stage 81 must pass identity tests.
184. Stage 81 must pass relationship tests.
185. Stage 81 must pass financial-data qualification tests.
186. Stage 81 must pass provenance tests.
187. Stage 81 must pass entitlement tests.
188. Stage 81 must pass cross-navigation tests.
189. Stage 81 must pass responsive/accessibility tests.
190. Stage 81 must pass relevant previous-stage regressions.
191. Documentation must match the actual implementation.
192. Stage 82 is the next canonical stage.

## Stage 82: Institutional Company Financial Statements

### Product and Scope
1. Stage 82 implements Company Financial Statements.
2. The module remains `/companies`.
3. Stage 81 Company identity remains authoritative.
4. Stage 34 Fundamental Data remains authoritative.
5. Stage 82 is read-only with respect to canonical accounting facts.
6. The three statement types (Income Statement, Balance Sheet, Cash Flow Statement) are supported.
7. Annual and quarterly periods are supported.
8. TTM is supported only where valid.
9. No fabricated financial statements are permitted.
10. No duplicate fundamental-data warehouse is created.

### Statement Identity
11. Canonical Company UUID is preserved.
12. Reporting Entity identity is explicit.
13. Consolidated group and legal entity scope are distinct.
14. Statement type is explicit.
15. Fiscal period identity is explicit.
16. Reporting currency is explicit.
17. Accounting framework is explicit.
18. Source document identity is preserved.
19. Statement revision is preserved.
20. Company ticker text is not statement identity.

### Accounting Taxonomies
21. Original source concepts are preserved.
22. Normalized concepts use stable IDs.
23. Mapping versions are explicit.
24. Unsupported mappings remain unmapped.
25. US GAAP/IFRS/Ind AS differences are respected.
26. Source accounting dimensions are preserved.
27. Specialized financial institutions are handled appropriately.
28. Original fact values are not overwritten.
29. Hierarchical statement rows use stable concept IDs.
30. Reported totals and derived totals are distinguished.

### Period Semantics
31. Flow facts are distinct from instant facts.
32. Fiscal years are not assumed calendar years.
33. Quarterly standalone and YTD are distinct.
34. 52/53-week calendars are supported where represented.
35. YTD subtraction requires compatible periods.
36. Q4 derivation requires qualified FY and 9M observations.
37. Balance Sheets are never derived by subtracting periods.
38. EPS is not naively derived by subtracting per-share figures.
39. Missing periods remain unavailable.
40. Derived periods preserve source lineage.

### TTM
41. TTM requires compatible trailing flow periods.
42. TTM is not latest quarter times four.
43. TTM may use valid annual/YTD bridges.
44. TTM Balance Sheet summation is prohibited.
45. TTM EPS requires verified methodology.
46. TTM source facts and revisions are traceable.
47. Insufficient history results in unavailable state.

### Currency and Precision
48. Source reporting currency is preserved.
49. No silent FX conversion is performed.
50. Decimal-safe numerical representation is used.
51. Presentation scale does not modify source facts.
52. EPS/share counts use appropriate units.
53. Accounting sign conventions are explicit.
54. Genuine zero differs from missing.
55. Negative financial amounts are supported.
56. NaN/Infinity are never returned as facts.

### Scope and Consolidation
57. Consolidated/standalone values remain distinct.
58. Source scope is visible.
59. Comparisons enforce scope consistency.
60. Parent/subsidiary statements are not silently substituted.
61. Missing consolidation coverage is not fabricated.

### Restatements and Time
62. Original and revised facts are distinguished.
63. Source revision metadata is retained.
64. Publication dates are distinct from period ends.
65. Latest statements follow canonical source policy.
66. Point-in-time claims require actual historical vintages.
67. Later restatements do not leak into earlier as-known-at views.
68. Latest-only sources cannot claim historical reconstruction.
69. Derived values inherit qualified revision context.

### Comparisons
70. Annual YoY requires compatible annual periods.
71. Quarterly YoY requires compatible quarters.
72. QoQ requires qualified period definitions.
73. Stock and flow facts are compared appropriately.
74. Mixed currency comparisons are restricted.
75. Mixed consolidation comparisons are restricted.
76. Zero denominator is handled.
77. Negative base percentage comparisons use explicit policy.
78. Missing comparisons remain unavailable.
79. Common-size Income Statement uses qualified Revenue.
80. Common-size Balance Sheet uses qualified Total Assets.
81. Unsupported common-size calculations are disabled.

### Accounting Reconciliation
82. Balance Sheet equation is diagnostic.
83. Cash Flow reconciliation is accounting-aware.
84. Rounding tolerances are explicit.
85. Incomplete source facts do not imply false errors.
86. Diagnostics never mutate canonical facts.

### APIs and Performance
87. FastAPI contracts are typed.
88. Period catalog uses actual source coverage.
89. Statement history queries are bounded.
90. Fact retrieval is batched.
91. No per-cell Provider fanout is permitted.
92. Source entitlements are enforced.
93. Caches include statement identity and revision.
94. Restatements invalidate derived caches.
95. Stale responses do not override newer selections.
96. No external ingestion starts from table navigation.

### UI and Accessibility
97. Income Statement tab is functional.
98. Balance Sheet tab is functional.
99. Cash Flow tab is functional.
100. Annual/Quarterly selection is functional.
101. TTM selection is qualified.
102. Consolidation selection is accurate.
103. Scale selection changes display only.
104. Multi-period tables are supported.
105. Expand/collapse is functional.
106. Source detail is inspectable.
107. Restatement status is visible.
108. Missing values are explained.
109. Financial numerals are aligned.
110. Sticky headers and labels are supported.
111. Responsive layouts are supported.
112. Keyboard navigation is supported.
113. Screen-reader semantics are supported.
114. Dark/light mode is preserved.
115. Agent Dock compatibility is preserved.
116. Bottom Taskbar compatibility is preserved.
117. No purple gradients are introduced.
118. No emoji icons are introduced.
119. No fake figures are displayed.

### Security
120. Authentication policies are reused.
121. Financial data entitlements are enforced.
122. Historical revisions are access-controlled.
123. Derived outputs cannot reveal restricted facts.
124. Arbitrary SQL is rejected.
125. Arbitrary user formulas are rejected.
126. Unsafe external URLs are rejected.
127. Provider credentials remain server-side.
128. Resource limits are enforced.
129. No canonical fact writes occur during reads.
130. No Trading orders are placed.
131. No Portfolio changes occur.
132. No Agents execute.
133. No Workflows execute.
134. No LLM calls are required.

### Roadmap Boundaries
135. Stage 83 owns Financial Ratios.
136. Stage 84 owns Earnings.
137. Stage 85 owns Ownership.
138. Stage 86 owns Filings.
139. Stage 87 owns Peers.
140. Stage 88 owns Supply Chains.
141. Stages 89–93 own Economics.
142. Stages 94–98 own Screeners.
143. Stages 99–103 own News.
144. Stages 104–109 own Research.
145. Stages 110–114 own Portfolios.
146. Stages 115–118 own Risk.
147. Stages 119–120 own Saved/Workspaces.
148. Stages 121–128 own Terminal/AI.
149. Stages 129–140 own Maps/Intelligence.
150. Stages 141–142 own Options/Quant pricing.
151. Stage 143 owns Backtesting.
152. Stage 144 owns Paper Trading.
153. Stage 145 owns Broker Sandbox.
154. Stages 146+ own Agents.
155. No comprehensive valuation-ratio engine is implemented.
156. No earnings prediction engine is implemented.
157. No ownership analysis is implemented.
158. No filings ingestion/parser is implemented.
159. No peer comparison engine is implemented.
160. No supply-chain intelligence is implemented.
161. No duplicate accounting-data pipeline is implemented.
162. Stage 82 must pass statement identity tests.
163. Stage 82 must pass accounting taxonomy tests.
164. Stage 82 must pass period derivation tests.
165. Stage 82 must pass TTM tests.
166. Stage 82 must pass financial precision tests.
167. Stage 82 must pass restatement tests.
168. Stage 82 must pass point-in-time tests.
169. Stage 82 must pass entitlement tests.
170. Stage 82 must pass Stage 81 regressions.
171. Documentation must match implementation.
172. Stage 83 is the next canonical stage.

## Stage 83: Company Financial Ratios & Fundamental Analysis

### Product
1. Stage 83 implements Financial Ratios and institutional Fundamental Analysis.
2. Financial Ratios belongs strictly within the `/companies` module under a dedicated workspace tab.
3. Stage 81 canonical Company identity is reused without modification.
4. Stage 82 Financial Statements are reused as the primary authoritative accounting fact store.
5. Stage 34 canonical Fundamentals remain authoritative.
6. No duplicate accounting-data platform or fact store is introduced.
7. Ratios are read-only derived analytical observations.
8. No arbitrary investment recommendations (e.g. "Strong Buy") are generated.
9. No Trading or broker interactions are introduced.
10. No fabricated or simulated financial values are permitted.

### Formula Registry
11. Ratios have stable, canonical identifiers across all ATLAS modules.
12. Ratio definitions are explicitly versioned (v1.0.0 baseline).
13. Methodologies are explicit and documented.
14. Input dependencies are declared and validated before calculation.
15. Output units (PERCENT, MULTIPLE, DAYS, MONETARY) are explicit.
16. Entity and industry applicability rules are explicitly declared.
17. Denominator policies are explicit (e.g., non-zero, average balance).
18. Negative-value policies are explicit (e.g., negative equity returns NOT_MEANINGFUL).
19. Source fact lineage and provenance records are preserved.
20. Arbitrary user-authored formulas or code execution (eval, exec, arbitrary SQL) are prohibited.
21. Trusted formula functions are tested with comprehensive deterministic fixtures.
22. Existing Watchlist ratio logic is reused or consolidated where appropriate.

### Financial Inputs
23. Stage 82 canonical statement facts are used for input resolution.
24. Original source revisions and restatements are preserved in calculation lineage.
25. Consolidation scope (CONSOLIDATED vs STANDALONE) is validated.
26. Reporting currency is validated; cross-currency operations without qualified conversion are rejected.
27. Accounting framework (GAAP, IFRS) is tracked and qualified.
28. Fiscal periods are validated for temporal alignment.
29. Flow versus stock distinctions are respected via opening/closing balance sheet averages.
30. TTM is used only when qualified from verified quarterly statements.
31. Missing accounting facts are not fabricated or replaced with arbitrary zeroes.
32. Source/provider routing remains authoritative.
33. No unqualified taxonomy mapping is permitted.

### Profitability
34. Gross Margin is implemented using compatible Gross Profit and Revenue.
35. Operating Margin is implemented using Operating Income and Revenue.
36. EBITDA Margin has an explicit methodology (Operating Income + D&A).
37. Net Margin has explicit net income scope.
38. ROE uses qualified average stockholders' equity.
39. ROA uses qualified average total assets.
40. ROIC uses versioned NOPAT and invested capital definitions.
41. ROCE uses versioned capital employed definition (Assets - Current Liabilities).
42. Negative equity interpretation is qualified as NOT_MEANINGFUL (N/M).
43. Missing balance sheet periods do not result in guessed returns.

### Liquidity and Leverage
44. Current Ratio uses compatible current assets and current liabilities.
45. Quick Ratio methodology subtracts inventories from current assets.
46. Cash Ratio cash scope includes cash and cash equivalents.
47. OCF Ratio period alignment qualifies operating cash flow against current liabilities.
48. Total Debt is distinguished from Total Liabilities.
49. Debt/Equity is qualified with interest-bearing debt and equity.
50. Debt/Assets is qualified with total debt and total assets.
51. Debt/Capital is qualified with total debt and capital.
52. Net Debt definition is explicit (Total Debt - Cash & Equivalents).
53. Interest Coverage denominator is qualified; zero interest expense yields UNAVAILABLE rather than Infinity.
54. Zero interest expense does not create Infinity or NaN.
55. Debt/EBITDA source basis is explicit.
56. Negative EBITDA yields NOT_MEANINGFUL.
57. Bank/insurance applicability is constrained.

### Efficiency
58. Asset Turnover uses qualified average total assets.
59. Inventory Turnover uses COGS and average inventory.
60. Receivables Turnover uses qualified revenue and average receivables.
61. Payables Turnover uses COGS and average payables.
62. DSO methodology uses 365-day annual basis.
63. DIO methodology uses 365-day annual basis.
64. DPO methodology uses 365-day annual basis.
65. Cash Conversion Cycle uses compatible component days (DIO + DSO - DPO).
66. Period days are explicit and documented.
67. 52/53-week calendar differences are handled gracefully.

### Cash Flow
68. Free Cash Flow methodology is explicit (Operating Cash Flow - CapEx).
69. CapEx sign handling correctly normalizes positive spending or signed negative outflows.
70. FCF Margin is qualified against revenue.
71. OCF Margin is qualified against revenue.
72. Cash Conversion ratio is distinguished from Cash Conversion Cycle.
73. CapEx intensity is qualified as CapEx to Revenue.
74. Missing Cash Flow facts remain typed UNAVAILABLE.

### Valuation
75. Market-price identity is explicit and sourced from canonical market data.
76. Canonical security context is required for market multiples.
77. Multiple share classes are handled without double counting.
78. ADR conversion ratios are validated and not guessed.
79. Multiple listings of the same underlying instrument are excluded from duplicate summing.
80. Market capitalization is qualified and validated.
81. P/E numerator and denominator bases are compatible.
82. Forward P/E requires actual verified analyst consensus estimates (Stage 84 preview).
83. P/B is qualified against stockholders' equity.
84. P/S is qualified against revenue.
85. P/CF is qualified against operating cash flow.
86. P/FCF is qualified against free cash flow.
87. Enterprise Value component scope is explicit (Market Cap + Debt - Cash).
88. Incomplete EV is not mislabeled as complete EV.
89. EV/EBITDA is qualified against EBITDA.
90. EV/Revenue is qualified against revenue.
91. Dividend Yield methodology is explicit against dividends paid.
92. Earnings Yield is qualified against net income and market cap.
93. Negative denominators are qualified as NOT_MEANINGFUL.
94. Price timestamps remain distinct from financial reporting periods.

### Historical Integrity
95. Historical ratio series use qualified financial periods.
96. Quarterly and annual values remain distinguishable and unmixed.
97. TTM observations use verified TTM inputs from Stage 82.
98. Historical valuation prices use valid historical observation dates.
99. Current price is not reused to fake historical multiples.
100. Restatement basis is visible in input fact lineage.
101. Point-in-time claims require historical publication vintages.
102. Future financial publications do not leak backward.
103. Missing ratio observations remain missing gaps in history.
104. Methodology version consistency is preserved across series.

### Caching and Performance
105. Ratio inputs are batched in a single pass.
106. Shared statement dependencies are deduplicated.
107. Existing cache infrastructure is reused.
108. Cache keys include methodology version.
109. Cache keys include financial source revisions.
110. Cache keys include reporting consolidation scope.
111. Valuation cache keys include market context.
112. Entitlements scope derived caches.
113. Financial restatements invalidate affected caches.
114. Live market ticks do not recalculate all company ratios.
115. No per-ratio Provider fanout is permitted on read requests.
116. Resource limits on ratios and periods are enforced.
117. No redundant canonical financial store is introduced.

### API and UI
118. Ratio APIs are typed with Pydantic schemas.
119. Ratio catalog is discoverable via `/catalog`.
120. Formula details are inspectable via `/{ratio_id}/methodology`.
121. Source lineage is inspectable via `/{ratio_id}/lineage`.
122. Annual ratio views are supported.
123. Quarterly ratio views are supported.
124. TTM ratio views are supported where valid.
125. Historical charts use SVG rendering with interactive hover tooltips.
126. Company financial statement navigation is preserved.
127. Valuation security selection is explicit.
128. Missing-value explanations are visible in tooltips and badges.
129. Financial units are explicitly formatted (%, x, days, USD).
130. Responsive layouts are supported on desktop, tablet, and mobile.
131. Dark/light mode theme tokens are preserved.
132. Agent Dock compatibility is preserved.
133. Bottom Taskbar compatibility is preserved.
134. Keyboard accessibility is supported.
135. Screen-reader accessibility is supported.
136. No purple gradients are introduced.
137. No emoji icons are introduced.
138. No fake financial data or rankings are introduced.

### Security
139. Authentication is required (`PermissionCode.ATLAS_ACCESS`).
140. Source entitlements are enforced for all underlying statement facts.
141. Historical market data access is validated.
142. Derived ratios do not leak restricted financial facts.
143. Cache isolation is maintained across tenant contexts.
144. Arbitrary SQL injection is prevented through parameterized lookups.
145. Arbitrary user formulas or script execution are prohibited.
146. Provider credentials remain secure server-side.
147. Resource quotas on batch queries are enforced.
148. Canonical financial facts remain unmodified (read-only).
149. No Broker actions occur.
150. No Portfolio mutations occur.
151. No Agents execute during ratio calculations.
152. No Workflows execute during ratio calculations.
153. No LLM calls are required (zero LLM calls).

### Roadmap Boundaries
154. Stage 84 owns Earnings.
155. Stage 85 owns Ownership.
156. Stage 86 owns Filings.
157. Stage 87 owns Peers.
158. Stage 88 owns Supply Chains.
159. Stages 89–93 own Economics.
160. Stages 94–98 own Screeners.
161. Stages 99–103 own News.
162. Stages 104–109 own Research.
163. Stages 110–114 own Portfolios.
164. Stages 115–118 own Risk.
165. Stages 119–120 own Saved/Workspaces.
166. Stages 121–128 own Terminal/AI.
167. Stages 129–140 own Maps/Intelligence.
168. Stages 141–142 own Options/Quant pricing.
169. Stage 143 owns Backtesting.
170. Stage 144 owns Paper Trading.
171. Stage 145 owns Broker Sandbox.
172. Stages 146+ own Agents.
173. No Earnings estimates pipeline is implemented.
174. No Ownership analytics is implemented.
175. No new Filings parser is implemented.
176. No Peer ranking system is implemented.
177. No Supply Chain network is implemented.
178. No universe-wide Screener is implemented.
179. No trading strategy engine is implemented.
180. No duplicate Fundamental Data engine is implemented.
181. Stage 83 passes formula correctness tests.
182. Stage 83 passes financial period tests.
183. Stage 83 passes valuation identity tests.
184. Stage 83 passes historical point-in-time tests.
185. Stage 83 passes entitlement tests.
186. Stage 83 passes Stage 82 regressions.
187. Documentation matches actual code.
188. Stage 84 is the next canonical stage.

## Stage 84: Company Earnings Intelligence

### Product and Domain
1. Stage 84 implements Company Earnings V1.
2. Earnings belongs to `/companies`.
3. No global module is added.
4. Stage 81 Company identity is reused.
5. Stage 82 Financial Statements remain authoritative.
6. Stage 83 Financial Ratios remain authoritative.
7. Earnings events, actuals, estimates and guidance are distinct domains.
8. Earnings surprise is derived only from comparable actuals and consensus.
9. No fabricated financial expectations are created.
10. No trading recommendations are generated.

### Entity and Period Identity
11. Canonical Company UUID is preserved.
12. Reporting Entity scope is explicit.
13. Fiscal period identity is explicit.
14. Fiscal period end differs from announcement time.
15. Fiscal quarters are not assumed calendar quarters.
16. Non-calendar fiscal years are supported.
17. 52/53-week period conventions are respected.
18. Share-class context is explicit.
19. ADR per-share basis is qualified.
20. Parent/subsidiary results are not silently combined.

### Earnings Events
21. Canonical Corporate Events are reused.
22. Confirmed and estimated dates remain distinct.
23. Postponed events preserve revisions.
24. Cancelled events remain distinct.
25. Date-only events do not receive invented timestamps.
26. Timezones are preserved.
27. DST rules are respected.
28. Market-session classification requires valid source/session evidence.
29. Duplicate event records are safely reconciled.
30. No next earnings date is fabricated.

### Actual Results
31. EPS comes from genuine source facts.
32. Basic and diluted EPS are distinct.
33. GAAP and adjusted EPS are distinct.
34. Continuing-operations scope is preserved.
35. Revenue concept definitions are qualified.
36. Revenue currency is explicit.
37. YTD is distinct from standalone quarter.
38. Stage 82 derivations are reused.
39. Original release and later restatement are distinct.
40. Missing EPS/Revenue remain unavailable.

### Analyst Estimates
41. Consensus is not a reported financial fact.
42. Estimate source is explicit.
43. Consensus methodology is explicit.
44. Forecast horizon is explicit.
45. Analyst count is not fabricated.
46. Estimate basis is explicit.
47. Historical estimate observations require real vintages.
48. Latest-only consensus cannot produce historical revisions.
49. Source publication timestamps are preserved.
50. Missing consensus remains unavailable.

### Temporal Integrity
51. Earnings release time is distinct from period end.
52. Consensus snapshot time is distinct from ingestion time.
53. Historical surprise uses a pre-release eligible estimate.
54. Post-announcement estimate revisions are excluded.
55. Same-day date-only estimates are not assumed pre-release.
56. Historical as-known-at views require genuine vintages.
57. Later restatements do not leak into original-announcement comparisons.
58. Source corrections preserve lineage.
59. No fabricated historical estimate values are allowed.

### Surprise Calculations
60. Actual and estimate must have the same fiscal period.
61. Metric/accounting basis must be compatible.
62. Per-share basis must be compatible.
63. Currency must be compatible.
64. Consolidation/reporting scope must be compatible.
65. Absolute surprise formula is versioned.
66. Percentage surprise formula is versioned.
67. Zero estimates do not produce infinite percentages.
68. Negative estimates receive explicit interpretation.
69. Beat/miss/in-line policy is documented.
70. Missing estimates do not produce fabricated surprises.
71. No earnings beat automatically implies a Buy recommendation.
72. No earnings miss automatically implies a Sell recommendation.

### Guidance
73. Management guidance is distinct from analyst estimates.
74. Guidance period is explicit.
75. Guidance range and point values are distinct.
76. Guidance accounting basis is explicit.
77. Guidance currency is preserved.
78. Original guidance is preserved.
79. Revised guidance is distinguished.
80. Withdrawn guidance is distinguished.
81. No implied numerical guidance is generated from qualitative text.
82. Missing guidance remains unavailable.

### Calls and Documents
83. Earnings Call event references use verified sources.
84. Call time and timezone are explicit.
85. Webcast URLs are validated.
86. Transcripts use existing canonical Document Entities.
87. Transcript publication timestamps are preserved.
88. Transcript licensing is enforced.
89. No new transcription pipeline is introduced.
90. No fictional transcripts or LLM-generated call summaries are created.
91. Earnings-related News uses existing verified references.

### Data and APIs
92. Typed Earnings APIs are implemented.
93. Source provenance is preserved.
94. Derived surprise lineage is preserved.
95. Entitlements apply to estimates and actuals separately.
96. Restricted estimates cannot be leaked through derived surprises.
97. Source reads are bounded.
98. Historical periods are paginated/bounded.
99. Cache keys include event revisions.
100. Cache keys include consensus vintages.
101. Cache keys include calculation versions.
102. Restatements invalidate affected views.
103. No Provider fanout occurs on ordinary page load.
104. No duplicate fundamental-data store is created.
105. No new unrestricted News crawler is created.

### UI
106. Earnings Overview is functional.
107. Earnings History is functional.
108. Actual EPS and Revenue are qualified.
109. Consensus data is labeled.
110. Earnings surprise methodology is inspectable.
111. Verified next earnings status is visible.
112. Earnings event timezone is visible.
113. Guidance is source-backed.
114. Calls/transcript references are source-backed.
115. Historical charts use real observations.
116. Missing historical estimates remain missing.
117. Partial source failures do not break available actuals.
118. Companies navigation remains functional.
119. Financial Statements navigation remains functional.
120. Financial Ratios navigation remains functional.
121. Watchlist integration is preserved.
122. Responsive layouts are supported.
123. Keyboard accessibility is supported.
124. Screen-reader accessibility is supported.
125. Dark/light mode is preserved.
126. Agent Dock compatibility is preserved.
127. Bottom Taskbar compatibility is preserved.
128. No purple gradients are introduced.
129. No emoji icons are introduced.
130. No fake financial metrics are displayed.

### Security and Resource Use
131. Authentication is enforced.
132. Company/source authorization is enforced.
133. Analyst-estimate licensing is enforced.
134. Transcript licensing is enforced.
135. Restricted derived-data leakage is prohibited.
136. No arbitrary SQL is accepted.
137. No arbitrary formula execution is allowed.
138. Unsafe external URLs are rejected.
139. Provider credentials remain server-side.
140. Resource limits are enforced.
141. Normal Earnings reads do not mutate canonical facts.
142. No Trading orders occur.
143. No Portfolio changes occur.
144. No Broker calls occur.
145. No Agents execute.
146. No Workflows execute.
147. No LLM calls are required.

### Roadmap Boundaries
148. Stage 85 owns Ownership.
149. Stage 86 owns Filings.
150. Stage 87 owns Peers.
151. Stage 88 owns Supply Chains.
152. Stages 89–93 own Economics.
153. Stages 94–98 own Screeners.
154. Stages 99–103 own News.
155. Stages 104–109 own Research.
156. Stages 110–114 own Portfolios.
157. Stages 115–118 own Risk.
158. Stages 119–120 own Saved/Workspaces.
159. Stages 121–128 own Terminal/AI.
160. Stages 129–140 own Maps/Intelligence.
161. Stages 141–142 own Options/Quant pricing.
162. Stage 143 owns Backtesting.
163. Stage 144 owns Paper Trading.
164. Stage 145 owns Broker Sandbox.
165. Stages 146+ own Agents.
166. No Ownership analytics is implemented.
167. No Filings crawler/parser is introduced.
168. No peer company comparison engine is introduced.
169. No supply-chain analysis is introduced.
170. No full News sentiment pipeline is introduced.
171. No full Research RAG is introduced.
172. No trading strategy engine is introduced.
173. Stage 84 must pass earnings arithmetic tests.
174. Stage 84 must pass estimate-vintage tests.
175. Stage 84 must pass source entitlement tests.
176. Stage 84 must pass event/timezone tests.
177. Stage 84 must pass Stage 81–83 regressions.
178. Documentation must reflect actual source coverage.
179. Stage 85 is the next canonical stage.

## Stage 85: Company Ownership Intelligence

### Product
1. Stage 85 implements Company Ownership Intelligence.
2. Ownership remains inside `/companies`.
3. No new global module is created.
4. The existing AppShell is preserved.
5. Canonical source data is mandatory.
6. No fictional holders or holdings are created.
7. Reported positions are not treated as realtime.
8. Ownership does not imply trading recommendations.
9. No duplicate Company registry is introduced.
10. No new universal filing engine is created.

### Identity
11. Company Entity remains authoritative.
12. Financial Instrument Entity remains authoritative.
13. Holder Entity has a stable canonical identity.
14. Investment fund and manager are distinct.
15. Reporting party and holder are distinct.
16. Custodian and beneficial owner are distinct.
17. Parent and subsidiary are distinct.
18. Public insider identity is scoped appropriately.
19. Security share classes are preserved.
20. ADRs remain distinct from ordinary shares.
21. Ticker text is not a primary key.
22. Similar names do not cause automatic merging.

### Ownership Semantics
23. Ownership observation is source-qualified.
24. Holdings and transactions are distinct.
25. Direct and indirect ownership are distinct.
26. Economic and voting ownership are distinct.
27. Reported and derived percentages are distinct.
28. Source ownership dates are preserved.
29. Publication dates are preserved.
30. Revision dates are preserved.
31. Disclosure scope is explicit.
32. Positions do not automatically create controlling-parent relationships.

### Institutional Ownership
33. 13F data is not treated as complete beneficial ownership.
34. 13F data is not realtime.
35. Investment discretion is distinguished from economic benefit.
36. Put/Call positions are not ordinary shares.
37. Shorts are not inferred from absent 13F positions.
38. Manager/fund double counting is prevented.
39. Filing amendments are distinguished.
40. Institutional reporting jurisdiction is explicit.

### Insider Ownership
41. Insider roles are issuer-specific and time-aware.
42. Transactions are not total holdings.
43. Form 3/4/5 semantics are preserved where supported.
44. Direct/indirect positions are distinguished.
45. Derivative positions remain distinct.
46. Post-transaction holding is shown only when source-backed.
47. Missing current insider positions are not guessed.

### Beneficial Ownership
48. Beneficial ownership requires actual source claims.
49. Group disclosures are handled separately from members.
50. Sole/shared voting power is distinguished.
51. Sole/shared dispositive power is distinguished.
52. Economic ownership is not silently equated with control.
53. Absence of disclosure does not prove zero ownership.
54. Filing amendments and source periods are preserved.

### Jurisdictions
55. US ownership disclosures retain source-specific semantics.
56. Indian shareholding patterns retain their own classifications.
57. Promoter roles are source/jurisdiction-qualified.
58. Pledged shares are not treated as sold shares.
59. Different ownership taxonomies are not silently combined.
60. Unsupported jurisdictions remain unavailable.

### Percentages
61. Ownership percentage requires a compatible denominator.
62. Share-class identity is checked.
63. Outstanding vs issued shares are distinct.
64. Treasury-share treatment is documented.
65. Voting and economic denominators differ where relevant.
66. Historical percentage uses qualified historical context.
67. Source-reported percentages are preserved.
68. Derived percentages are separately labeled.
69. Missing denominator means unavailable percentage.
70. Exact decimal arithmetic is used.

### Historical Ownership
71. Historical holdings use actual reporting periods.
72. Publication date is distinct from reporting date.
73. Amendments do not silently overwrite history.
74. As-known-at requires genuine vintages.
75. No publication look-ahead is permitted.
76. Missing reporting periods are not fabricated.
77. Source coverage changes are visible.
78. Current holdings are not inferred from historical disclosures.

### Ownership Changes
79. Position changes require comparable securities.
80. Position changes require comparable holders.
81. Position changes require compatible source scopes.
82. Corporate actions are considered.
83. ADR conversion changes are considered.
84. Share issuance/buybacks may change percentages.
85. Newly reported is not synonymous with new investor.
86. Missing from dataset is not synonymous with full exit.
87. Snapshot changes are not trade history.
88. Change calculations preserve source lineage.

### Concentration
89. Concentration uses compatible nonduplicated records.
90. Top-holder metrics are scope-qualified.
91. Incomplete data does not imply complete institutional ownership.
92. Group/member duplicate counting is prohibited.
93. Pie-chart completeness must be proven.
94. Voting and economic concentration remain distinct.

### Market Context
95. Reported position values remain source-qualified.
96. Current indicative valuation is separately labeled.
97. Stale holdings are not treated as current positions.
98. Currency and share-price units are checked.
99. No portfolio accounting system is introduced.
100. No new market Quote store is created.

### Data and Performance
101. Existing canonical services are reused.
102. New ownership schema is narrow where needed.
103. Ownership source records are versioned.
104. Database indexes support issuer/holder/period queries.
105. Holder reads are batched.
106. Historical periods are bounded.
107. Graph traversals are bounded.
108. Source caches include revisions.
109. Entitlement scope is included in restricted cache keys.
110. Amended disclosures invalidate affected views.
111. No Provider fanout occurs on page load.
112. No regulatory crawler is triggered by UI reads.

### APIs and UI
113. Ownership APIs are typed.
114. Ownership Overview is functional.
115. Institutional Holders is functional where data exists.
116. Insider Holdings is functional where data exists.
117. Beneficial Ownership is functional where data exists.
118. Shareholding Patterns are supported where data exists.
119. Security selector is functional.
120. Reporting-period selector is functional.
121. Source inspector is functional.
122. Historical position analysis is qualified.
123. Source coverage is visible.
124. Missing values are explained.
125. Compact tables are used.
126. Existing Companies navigation is preserved.
127. Dark/light themes are preserved.
128. Responsive layouts are supported.
129. Agent Dock compatibility is preserved.
130. Bottom Taskbar compatibility is preserved.
131. Keyboard accessibility is supported.
132. Screen-reader accessibility is supported.
133. No purple gradients are introduced.
134. No emoji icons are introduced.
135. No fake shareholder data is introduced.

### Security and Privacy
136. Authentication is required.
137. Source entitlements are enforced.
138. Restricted derived holdings are protected.
139. Individual privacy is respected.
140. Home addresses are not exposed.
141. Private personal contact details are not exposed.
142. Arbitrary SQL is prohibited.
143. Unsafe arbitrary URLs are rejected.
144. Provider credentials remain server-side.
145. Resource limits are enforced.
146. Ownership reads do not mutate canonical facts.
147. No Trading orders occur.
148. No Broker calls occur.
149. No Portfolio mutations occur.
150. No Agents execute.
151. No Workflows execute.
152. No LLM calls are required.

### Roadmap Boundaries
153. Stage 86 owns Filings.
154. Stage 87 owns Peers.
155. Stage 88 owns Supply Chains.
156. Stages 89–93 own Economics.
157. Stages 94–98 own Screeners.
158. Stages 99–103 own News.
159. Stages 104–109 own Research.
160. Stages 110–114 own Portfolios.
161. Stages 115–118 own Risk.
162. Stages 119–120 own Saved/Workspaces.
163. Stages 121–128 own Terminal/AI.
164. Stages 129–140 own Maps/Intelligence.
165. Stages 141–142 own Options/Quant pricing.
166. Stage 143 owns Backtesting.
167. Stage 144 owns Paper Trading.
168. Stage 145 owns Broker Sandbox.
169. Stages 146+ own Agents.
170. No full Filings crawler/parser is implemented.
171. No peer benchmarking engine is implemented.
172. No supply-chain relationships are inferred.
173. No customer portfolio accounting is implemented.
174. No insider-trading strategy is implemented.
175. No duplicate Entity database is implemented.
176. No unrestricted personal-information collection is implemented.
177. Stage 85 must pass identity tests.
178. Stage 85 must pass percentage tests.
179. Stage 85 must pass disclosure scope tests.
180. Stage 85 must pass double-counting tests.
181. Stage 85 must pass history/temporal tests.
182. Stage 85 must pass entitlement/privacy tests.
183. Stage 85 must pass Stage 81–84 regressions.
184. Documentation must match implementation.
185. Stage 86 is the next canonical stage.

## Stage 86: Company Filings Intelligence

### Product and Scope
1. Stage 86 implements Company Filings Intelligence.
2. Filings remains inside `/companies`.
3. No new global module is created.
4. Stage 20 Document Entities are reused.
5. Stage 18 Company Entities are reused.
6. Stage 21 regulatory identifiers are reused.
7. Stage 24 provenance remains authoritative.
8. No fabricated filings are created.
9. No new broad Research platform is introduced.
10. No autonomous AI filing analysis is introduced.

### Source Identity
11. Regulatory source identity is explicit.
12. Official filing identifier is preserved.
13. Filer and issuer are distinct.
14. CIK is not derived from ticker formatting.
15. Filing type is source-defined.
16. Reporting period is distinct from filing date.
17. Publication time is distinct from ingestion time.
18. Filing amendment identity is preserved.
19. Original source documents remain immutable.
20. Parser revisions are distinct from official amendments.

### Regulator Adapters
21. SEC EDGAR is integrated only through permitted methods.
22. Regulator policies are verified before deployment.
23. Access identification requirements are configured.
24. Shared rate limits are enforced.
25. Backoff and retries are bounded.
26. Source permissions are respected.
27. Indian regulator integrations remain source-specific.
28. No protected source access is bypassed.
29. Unavailable adapters are not advertised as operational.
30. Source URLs use verified trusted domains.

### Filing Categories
31. Annual filing types are supported where available.
32. Quarterly filing types are supported where available.
33. Current-event filings are supported where available.
34. Ownership disclosures are supported where available.
35. Insider filings are supported where available.
36. Proxy/prospectus types are source-qualified.
37. Official form codes are preserved.
38. Amendments are not automatically equivalent to full replacement.
39. Unknown form types remain explicit.

### Ingestion
40. Ingestion uses background workers.
41. User page loads do not trigger unbounded crawls.
42. Jobs are idempotent.
43. Filing discovery has stable checkpoints.
44. Duplicate source records are prevented.
45. Partial failures are recoverable.
46. Source quotas are globally respected.
47. Parsing is bounded.
48. Ingestion states are explicit.
49. Parser errors do not destroy source metadata.
50. Source revisions trigger controlled updates.

### Storage and Security
51. Original document bytes are preserved where authorized.
52. Cryptographic hashes verify integrity.
53. Restricted documents require authorization.
54. Secure storage is reused.
55. HTML source is treated as untrusted.
56. JavaScript execution is prohibited in filing content.
57. XML external entities are disabled.
58. Archive decompression is bounded.
59. Unsafe URLs are rejected.
60. Path traversal is blocked.
61. PDF active content is not executed.
62. CSP and viewer isolation are enforced.
63. Parser CPU/memory limits are enforced.
64. Provider credentials remain server-side.

### XBRL
65. XBRL uses standards-aware parsing.
66. Original source facts are preserved.
67. Taxonomy namespaces are preserved.
68. Taxonomy versions are preserved.
69. Context identity is preserved.
70. Dimensions are preserved.
71. Instant and duration periods remain distinct.
72. Currency and share units remain distinct.
73. Decimals/precision are preserved.
74. Source sign semantics are respected.
75. Duplicate facts require complete context matching.
76. Custom extension concepts are not guessed.
77. Canonical mapping uses Stage 34/82.
78. Restated facts preserve source vintages.
79. No fabricated financial line items are created.
80. No duplicate Fundamental Data store is introduced.

### Search and Viewing
81. Search is based on genuine indexed text.
82. Search snippets are source-grounded.
83. Search entitlements apply.
84. Filing metadata filters are functional.
85. Search pagination is bounded.
86. Original source documents are verifiable.
87. HTML rendering is sanitized.
88. PDF viewers are access-controlled.
89. XBRL facts are inspectable.
90. Attachment lists use genuine source records.
91. Page/section references are not fabricated.
92. Citation controls identify official sources.

### Comparison
93. Original/amended comparison is supported where available.
94. Text differences use deterministic algorithms.
95. Structured financial facts require compatible contexts.
96. Comparison source IDs/hashes are preserved.
97. Extraction changes are distinct from filing amendments.
98. Missing extracted text does not imply deleted source text.
99. No unverified semantic materiality judgments are generated.

### Cross-Module Integration
100. Stage 82 Financial Statements remain authoritative.
101. Stage 83 Ratio Engine remains authoritative.
102. Stage 84 Earnings remains authoritative.
103. Stage 85 Ownership remains authoritative.
104. Filing-source references integrate with these modules.
105. Extracted accounting facts use existing canonical ingestion contracts.
106. Existing source revisions invalidate affected financial caches.
107. No separate Earnings or Ownership engine is created.
108. Global selected Company context is preserved.
109. Existing Markets and Charts navigation is preserved.

### Performance
110. Catalog queries are indexed.
111. Full-text search is bounded.
112. Document retrieval is size-limited.
113. Parsing is asynchronous.
114. Search indexing is asynchronous.
115. Cache keys include document hashes.
116. Cache keys include parser versions.
117. XBRL cache keys include taxonomy versions.
118. Comparison caches include both source documents.
119. Entitlements scope restricted caches.
120. No regulator fanout occurs on ordinary page loads.
121. No unbounded worker queues are permitted.

### UI and Accessibility
122. Filings Overview is functional.
123. Filing Catalog is functional.
124. Filing filters are functional.
125. Document search is functional.
126. Filing detail is functional.
127. Safe document viewing is functional.
128. Attachments are listed where available.
129. XBRL facts are inspectable where available.
130. Amendment history is visible.
131. Filing comparison is functional where supported.
132. Source provenance is visible.
133. Error/partial states are supported.
134. Dark/light modes are preserved.
135. Agent Dock compatibility is preserved.
136. Bottom Taskbar compatibility is preserved.
137. Responsive layouts are supported.
138. Keyboard navigation is supported.
139. Screen-reader accessibility is supported.
140. No purple gradients are introduced.
141. No emoji icons are introduced.
142. No fake filing records are displayed.

### Authorization
143. Authentication is enforced.
144. Filing metadata entitlements are enforced where applicable.
145. Full-text entitlements are enforced.
146. Download entitlements are enforced.
147. XBRL/extracted-data rights are enforced.
148. Search snippets do not leak restricted content.
149. Comparisons do not leak restricted content.
150. Arbitrary SQL is prohibited.
151. Unsafe arbitrary URL fetching is prohibited.
152. Sensitive personal data is minimized.
153. No Trading orders occur.
154. No Portfolio mutations occur.
155. No Broker calls occur.
156. No Agents execute.
157. No Workflows execute.
158. No LLM calls are required.

### Roadmap Boundaries
159. Stage 87 owns Peers.
160. Stage 88 owns Supply Chains.
161. Stages 89–93 own Economics.
162. Stages 94–98 own Screeners.
163. Stages 99–103 own News.
164. Stages 104–109 own Research.
165. Stages 110–114 own Portfolios.
166. Stages 115–118 own Risk.
167. Stages 119–120 own Saved/Workspaces.
168. Stages 121–128 own Terminal/AI.
169. Stages 129–140 own Maps/Intelligence.
170. Stages 141–142 own Options/Quant pricing.
171. Stage 143 owns Backtesting.
172. Stage 144 owns Paper Trading.
173. Stage 145 owns Broker Sandbox.
174. Stages 146+ own Agents.
175. No automated Peer discovery is implemented.
176. No supplier/customer graph is implemented.
177. No broad News sentiment pipeline is implemented.
178. No semantic Research RAG is implemented.
179. No investment recommendation engine is implemented.
180. No autonomous filing research Agent is implemented.
181. Stage 86 must pass filing identity tests.
182. Stage 86 must pass regulator adapter tests.
183. Stage 86 must pass ingestion tests.
184. Stage 86 must pass document security tests.
185. Stage 86 must pass XBRL tests.
186. Stage 86 must pass search tests.
187. Stage 86 must pass amendment comparison tests.
188. Stage 86 must pass temporal tests.
189. Stage 86 must pass authorization tests.
190. Stage 86 must pass Stage 81–85 regressions.
191. Documentation must match implementation.
192. Stage 87 is the next canonical stage.

## Stage 87: Company Peers & Comparable Company Analysis

### Product and Scope
1. Stage 87 implements Company Peers and Comparable Company Analysis.
2. Peers workspace remains inside `/companies`.
3. No new global sidebar module is created.
4. Stage 81 Company identity is reused.
5. Stage 82 Financial Statements are reused.
6. Stage 83 Financial Ratios are reused.
7. No duplicate Fundamental Data system is created.
8. No fake peer relationships are created.
9. Peer analysis is not a trading recommendation engine.
10. Stage 88 Supply Chains remains out of scope.

### Peer Semantics
11. Comparable candidates are distinguished from verified competitors.
12. User selections are distinguished from source assertions.
13. Source-defined peers retain provenance.
14. Comparable companies are not automatically business competitors.
15. User-selected peers do not create global relationship graph edges.
16. Subject Company identity is explicit.
17. Duplicate issuer entries are removed.
18. Ticker-only identity is prohibited.
19. Security identity remains separate from issuer identity.
20. Peer selection methodology is versioned.

### Industry Classification
21. Industry taxonomy identity is explicit.
22. Classification versions are preserved.
23. Different taxonomies are not silently merged.
24. Licensing is enforced.
25. Unknown classifications remain unknown.
26. Historical classifications are not fabricated.
27. Sector matching alone does not prove competition.
28. Business-model comparisons require real data.
29. Operating geography differs from headquarters.
30. Missing geographic exposure is not inferred.

### Candidate Selection
31. Candidate selection is deterministic unless using genuine verified source-defined peers.
32. Source relationships are distinguished from statistical similarity.
33. Size filters use real values.
34. Geography filters use verified attributes.
35. Candidate ranking methodology is explicit.
36. Missing factors are handled.
37. Arbitrary first-N Provider selection is prohibited.
38. Candidate lists are bounded.
39. Discovery reasons are inspectable.
40. No fake confidence percentages are generated.

### Peer Groups
41. User-defined groups use canonical Company IDs.
42. Group ownership is enforced.
43. Private groups are protected by authorization/RLS.
44. CRUD operations are functional.
45. Peer group size is limited to 25 companies.
46. Duplicate Companies are rejected.
47. The subject Company cannot be a peer of itself.
48. Changes use revision/concurrency protection.
49. User groups do not mutate canonical corporate relationships.
50. No premature global Saved/Workspaces platform is built.

### Financial Statements
51. Stage 82 remains authoritative.
52. Reporting Entity identity is verified.
53. Consolidation scope is validated.
54. Financial concepts are validated.
55. Accounting frameworks are qualified.
56. Fiscal periods are aligned.
57. Annual and quarterly values remain distinct.
58. TTM uses qualified Stage 82 inputs.
59. Source financial revisions are preserved.
60. Missing financial facts remain missing.

### Currency and Periods
61. Monetary metrics require compatible currencies.
62. FX conversion uses verified canonical rates only.
63. Conversion methodology is explicit.
64. Different FX treatment may apply to flows and stock values.
65. Missing FX prevents invalid comparison.
66. Ratios can be compared across reporting currencies when internally valid.
67. Non-calendar fiscal years are supported.
68. 52/53-week calendars are supported where represented.
69. Latest-available and common-period modes are distinguished.
70. No silent calendarization occurs.
71. No quarter-times-four TTM calculation occurs.

### Ratio Methodologies
72. Stage 83 Formula Registry remains authoritative.
73. Profitability ratios use registered methodologies.
74. Liquidity ratios use registered methodologies.
75. Leverage ratios use registered methodologies.
76. Efficiency ratios use registered methodologies.
77. FCF metrics use registered methodologies.
78. Formula versions are preserved.
79. Negative/zero denominator rules are reused.
80. Source lineage is preserved.
81. No independent duplicate ratio formulas are created.

### Valuation
82. Market Cap is issuer/security-qualified.
83. Share classes are respected.
84. ADR conversion is respected.
85. Cross-listings are not double-counted.
86. EV uses canonical Stage 83 methodology.
87. Missing EV components remain unavailable.
88. Market price measure is explicit.
89. Price observation time is explicit.
90. Different market sessions are handled.
91. Stale prices are flagged.
92. Historical valuation requires real historical prices.
93. Current prices do not fabricate historical P/E.
94. Negative P/E/EV multiples are handled appropriately.
95. Forward estimates are never fabricated.
96. Lower valuation multiples do not automatically imply Buy recommendations.

### Statistics
97. Peer median is computed from eligible observations.
98. Peer mean is computed from eligible observations.
99. Minimum/maximum use valid inputs.
100. Sample size is explicit.
101. Coverage is explicit.
102. Missing observations do not become zero.
103. Subject inclusion policy is explicit.
104. Percentile methodology is versioned.
105. Tie handling is documented.
106. Small samples are qualified.
107. Outliers are not silently excluded.
108. Percentage-point differences are labeled correctly.
109. Numeric rank is not automatically investment quality.

### Historical Integrity
110. Historical series use genuine observations.
111. Fiscal period identity is preserved.
112. Source restatements are visible.
113. Point-in-time claims require actual vintages.
114. Later filings do not leak into earlier historical views.
115. Historical valuation dates are qualified.
116. Current peer groups applied retrospectively are labeled.
117. Historical classification changes are handled where supported.
118. Survivorship-bias-free claims require appropriate historical universe data.
119. Missing historical periods remain missing.

### Performance and APIs
120. Peer APIs are typed.
121. Canonical financial facts are read in batches.
122. Source entitlements are enforced.
123. Group entitlements are enforced.
124. Restricted aggregates do not leak protected data.
125. Candidate queries are bounded.
126. Comparison queries are bounded.
127. Historical queries are bounded.
128. Cache keys include input revisions.
129. Cache keys include methodology versions.
130. Cache keys include market valuation context.
131. Group revisions invalidate caches.
132. No per-cell Provider fanout occurs.
133. No every-tick global recalculation occurs.
134. Derived comparison results do not mutate canonical facts.

### UI
135. Peer Overview is functional.
136. Candidate discovery is functional where data exists.
137. Candidate reasons are visible.
138. Manual peer selection is functional.
139. Peer-group CRUD is functional.
140. Financial comparison is functional.
141. Valuation comparison is functional.
142. Historical comparison is functional where data exists.
143. Peer statistics expose counts.
144. Missing/not-meaningful values are visible.
145. Source inspector is functional.
146. Formula inspector uses canonical methodologies.
147. Charts use genuine observations.
148. Company navigation is preserved.
149. Responsive layouts are supported.
150. Dark/light mode is preserved.
151. Agent Dock compatibility is preserved.
152. Bottom Taskbar compatibility is preserved.
153. Keyboard accessibility is supported.
154. Screen-reader accessibility is supported.
155. No purple gradients are introduced.
156. No emoji icons are introduced.
157. No fake financial data or peers are introduced.

### Security
158. Authentication is required.
159. User groups are access-controlled.
160. Financial data entitlements are enforced.
161. Industry classification licenses are enforced.
162. Restricted aggregation leakage is prevented.
163. Arbitrary SQL is prohibited.
164. Arbitrary formulas are prohibited.
165. Provider credentials remain server-side.
166. Resource limits are enforced.
167. No Trading orders occur.
168. No Broker calls occur.
169. No Portfolio mutations occur.
170. No Agents execute.
171. No Workflows execute.
172. No LLM calls are required.

### Roadmap Boundaries
173. Stage 88 owns Supply Chains.
174. Stages 89–93 own Economics.
175. Stages 94–98 own Screeners.
176. Stages 99–103 own News.
177. Stages 104–109 own Research.
178. Stages 110–114 own Portfolios.
179. Stages 115–118 own Risk.
180. Stages 119–120 own Saved/Workspaces.
181. Stages 121–128 own Terminal/AI.
182. Stages 129–140 own Maps/Intelligence.
183. Stages 141–142 own Options/Quant pricing.
184. Stage 143 owns Backtesting.
185. Stage 144 owns Paper Trading.
186. Stage 145 owns Broker Sandbox.
187. Stages 146+ own Agents.
188. No supplier/customer network is implemented.
189. No complete Screener engine is implemented.
190. No full Portfolio system is implemented.
191. No autonomous investment recommendation engine is implemented.
192. No duplicate Company database is implemented.
193. No duplicate Financial Ratio engine is implemented.
194. Stage 87 must pass identity tests.
195. Stage 87 must pass classification tests.
196. Stage 87 must pass peer-group authorization tests.
197. Stage 87 must pass financial compatibility tests.
198. Stage 87 must pass valuation tests.
199. Stage 87 must pass statistical tests.
200. Stage 87 must pass historical point-in-time tests.
201. Stage 87 must pass Stage 81–86 regressions.
202. Documentation must match actual code.
203. Stage 88 is the next canonical stage.

## Stage 88: Institutional Company Supply Chain Intelligence

### Product
1. Stage 88 implements Company Supply Chains.
2. Supply Chains remains inside `/companies`.
3. No global module is created.
4. Canonical Company identity is reused.
5. Canonical Relationship Graph is reused.
6. Source Provenance remains authoritative.
7. Existing Filings are reused.
8. No speculative relationship assertions are created.
9. No new full News/Research platform is created.
10. No Maps/Intelligence stages are implemented prematurely.

### Relationship Semantics
11. Supplier-to-customer direction is explicit.
12. Relationship type taxonomy is controlled.
13. Direct/indirect relations are distinguished.
14. Product/service context is qualified.
15. Commercial edges are distinct from ownership.
16. Commercial edges are distinct from peers.
17. Commercial edges are distinct from competitor relations.
18. Relationships may be multitype.
19. Relationship validity is time-aware.
20. No universal complete-network claim is made.

### Entity Resolution
21. All verified counterparties use canonical Entity IDs.
22. Public/private companies are supported.
23. Brands and legal entities are distinguished.
24. Parents and subsidiaries are distinguished.
25. Unresolved entities are not guessed.
26. Tickers are not authoritative relationship identifiers.
27. Entity alias changes are handled.
28. Group-level disclosures preserve scope.

### Evidence
29. Every asserted edge has actual evidence.
30. Filing source IDs are preserved.
31. Section/page references are genuine.
32. Official corporate reports can support relationships.
33. Authorized structured Provider data can support relationships.
34. News mentions alone do not prove supply.
35. Prospective agreements are distinct from completed supply.
36. Evidence review/qualification status is explicit.
37. Corroboration does not double-count syndicated copies.
38. Contradictory evidence is preserved.
39. Arbitrary confidence scores are prohibited.
40. LLM assertions are not authoritative source evidence.

### Historical Relationships
41. Publication time is preserved.
42. Reporting date is preserved.
43. Business validity time is qualified.
44. First publication is not automatically inception.
45. Missing recent evidence does not prove termination.
46. Confirmed termination requires evidence.
47. Historical as-known-at uses genuine source vintages.
48. Later filing amendments do not leak backward.
49. Historical gaps are not filled synthetically.
50. Relationship source revisions are preserved.

### Graph
51. Stage 23 remains canonical.
52. Directed traversal is implemented.
53. First-tier upstream is supported.
54. First-tier downstream is supported.
55. Bounded second-tier traversal is supported.
56. Deeper traversal is controlled.
57. Graph cycles are handled.
58. Expansion limits are enforced.
59. Paths retain edge-level evidence.
60. Indirect paths do not imply direct contracts.
61. Indirect paths do not imply a numerical economic exposure.
62. Source coverage is exposed.
63. The browser does not load the entire global graph.

### Concentration
64. Customer Revenue concentration is source-qualified.
65. Supplier procurement concentration is source-qualified.
66. Monetary scope is validated.
67. Fiscal periods are validated.
68. Currencies are validated.
69. Consolidation is validated.
70. Segment Revenue differs from consolidated Revenue.
71. Spend differs from Cost of Sales.
72. Contract value differs from recognized Revenue.
73. Reported and derived percentages are distinct.
74. Anonymous counterparties remain anonymous.
75. Missing denominators produce unavailable results.
76. Overlapping exposures are not summed.
77. No artificial other-customer remainder is fabricated.
78. No unsupported financial impact forecast is generated.

### Geography
79. Stage 19 Geographic Entities are reused.
80. Company location differs from factory location.
81. Facility references require verified identity.
82. Headquarters is not substituted for manufacturing facilities.
83. Facility coordinates are not invented.
84. Country/region filters use real metadata.
85. Maps/Cesium/H3 remain later stages.

### Source and Ingestion
86. Existing ingestion pipelines are reused.
87. Source Provider rights are enforced.
88. Structured relationship observations preserve Provider IDs.
89. Ambiguous filing mentions remain unverified.
90. UI reads do not launch new crawling.
91. Ingestion is idempotent.
92. Source revisions are preserved.
93. No broad scraper is introduced.
94. Normal operation requires no LLM calls.

### APIs and Performance
95. Supply-chain APIs are typed.
96. Graph limits are server-enforced.
97. Relationship lists are paginated.
98. Evidence lists are bounded.
99. Graph requests include source/revision context.
100. Cache keys include authorization scope.
101. Entity corrections invalidate affected caches.
102. Filing amendments invalidate impacted edges.
103. Financial fact revisions invalidate concentration.
104. No N×M Provider fanout occurs.
105. No unbounded traversal is permitted.
106. Browser graph rendering is bounded.
107. Graph cycles do not cause infinite loops.
108. Concurrent expansions are controlled.

### UI
109. Supply Chain Overview is functional.
110. Suppliers workspace is functional.
111. Customers workspace is functional.
112. Network Explorer is functional.
113. Source-backed edge details are functional.
114. Direct/indirect views are distinguished.
115. Concentration panels are qualified.
116. Historical views are source-backed.
117. Evidence inspector is functional.
118. Data coverage is visible.
119. Missing states are explicit.
120. Mobile table alternative is provided.
121. Dark/light mode is preserved.
122. Agent Dock compatibility is preserved.
123. Bottom Taskbar compatibility is preserved.
124. Keyboard accessibility is supported.
125. Screen-reader accessibility is supported.
126. No purple gradients are introduced.
127. No emoji icons are introduced.
128. No fake network nodes/edges are displayed.

### Security
129. Authentication is enforced.
130. Data entitlements are enforced.
131. Restricted source exposure is protected.
132. Derived aggregate leakage is prevented.
133. Arbitrary SQL is prohibited.
134. Unbounded graph queries are prohibited.
135. Unsafe URLs are rejected.
136. Provider credentials remain server-side.
137. Resource quotas are enforced.
138. Ordinary reads do not mutate source observations.
139. No Trading orders occur.
140. No Broker actions occur.
141. No Portfolio mutations occur.
142. No Agents execute.
143. No Workflows execute.
144. No LLM calls are required.

### Roadmap Boundaries
145. Stage 89 owns Economics V1.
146. Stage 90 owns Country Economics.
147. Stage 91 owns Central Banks.
148. Stage 92 owns Economic Calendar.
149. Stage 93 owns Macro Comparisons.
150. Stages 94–98 own Screeners.
151. Stages 99–103 own News.
152. Stages 104–109 own Research.
153. Stages 110–114 own Portfolios.
154. Stages 115–118 own Risk.
155. Stages 119–120 own Saved/Workspaces.
156. Stages 121–128 own Terminal/AI.
157. Stages 129–134 own Maps/geospatial capabilities.
158. Stages 135–140 own universal-event/intelligence capabilities.
159. Stages 141–142 own Options/Quant pricing.
160. Stage 143 owns Backtesting.
161. Stage 144 owns Paper Trading.
162. Stage 145 owns Broker Sandbox.
163. Stages 146+ own Agents.
164. No full Economics module is introduced.
165. No full Screener is introduced.
166. No full global Map is introduced.
167. No live shipment/physical telemetry system is introduced.
168. No worldwide disruption-prediction engine is introduced.
169. No agent-based supply-chain speculation is introduced.
170. No duplicate Relationship Graph is introduced.
171. Stage 88 must pass directionality tests.
172. Stage 88 must pass source evidence tests.
173. Stage 88 must pass identity tests.
174. Stage 88 must pass multi-tier traversal tests.
175. Stage 88 must pass concentration tests.
176. Stage 88 must pass historical temporal tests.
177. Stage 88 must pass entitlement tests.
178. Stage 88 must pass Stage 81–87 regressions.
179. Documentation must match the actual implementation.
180. Stage 89 is the next canonical stage.

## Stage 89 Decisions - Institutional-Grade Economics V1

### Product
1. Stage 89 implements Economics V1.
2. Economics is hosted at `/economics`.
3. No new global module is introduced.
4. The existing AppShell is preserved.
5. The global overview uses genuine statistical series.
6. The indicator explorer uses canonical data.
7. Historical charts use actual observations.
8. No fake global statistics are generated.
9. Stage 90–93 advanced features remain deferred.

### Canonical Identity
10. Economic Indicator identity is stable.
11. Source series identity is separate from canonical indicator identity.
12. Provider series codes are source-qualified.
13. Geographic Entity identity is reused.
14. Country and monetary area are distinct.
15. Official series definitions are preserved.
16. Source methodology versions are preserved.
17. Different indicator concepts are not silently merged.
18. Different provider statistical methodologies are not automatically interchangeable.

### Observations
19. Observation reference periods are explicit.
20. Publication time differs from reference period.
21. Ingestion time differs from publication time.
22. Values preserve original source units.
23. Frequency is explicit.
24. Seasonal adjustment is explicit.
25. Nominal/real basis is explicit.
26. Source status is explicit where known.
27. Missing values remain missing.
28. Latest-only sources do not imply historical vintages.
29. Genuine revisions are preserved where available.
30. No future information enters historical views.

### Statistical Units
31. Index levels differ from percentage changes.
32. Rates differ from rate changes.
33. Percentage points differ from percentages.
34. Basis points are handled explicitly.
35. GDP currency units retain scale.
36. Monetary and index units are not silently mixed.
37. Annualized and nonannualized growth remain distinct.
38. Conversion is allowed only under defined methodology.
39. Decimal-safe arithmetic is used.

### GDP
40. Real and nominal GDP are distinct.
41. Current and constant-price GDP are distinct.
42. PPP and FX-converted GDP are distinct.
43. Quarterly GDP growth uses valid periods.
44. Annualized GDP growth uses an explicit formula.
45. Source growth rates retain their definition.
46. National accounting methodology differences are preserved.
47. Historical revisions remain traceable.

### Inflation
48. CPI index levels are distinct from inflation rates.
49. YoY and MoM are distinct.
50. Index rebasing is handled explicitly.
51. Headline and core inflation are distinct.
52. Different CPI scopes are not silently merged.
53. Seasonal adjustment is preserved.
54. Missing reference periods prevent invalid derived growth.

### Labor
55. Unemployment uses source labor-force definitions.
56. Employment differs from unemployment.
57. Payroll changes differ from unemployment rates.
58. Survey methodology differences are preserved.
59. Labor series benchmark revisions are retained when available.

### Interest Rates
60. Policy rates differ from bond yields.
61. Policy targets differ from effective rates.
62. Policy rate ranges are supported where genuine.
63. Monetary area identity is explicit.
64. Central-bank institution research remains Stage 91.

### Providers
65. Stage 28–32 Provider architecture is reused.
66. Provider routing is concept-compatible.
67. Fallback cannot silently change statistical definition.
68. Provider health is reused.
69. Source licenses are enforced.
70. Official statistical sources are preferred where suitable.
71. Missing source data is not fabricated.
72. Source access policies are verified.
73. Normal page loads do not trigger upstream fanout.

### Transformations
74. Transformations use a versioned registry.
75. No arbitrary execution is allowed.
76. YoY requires compatible prior-year period.
77. MoM requires compatible prior-month period.
78. QoQ requires comparable quarters.
79. Annualization is methodology-specific.
80. Percentage point and basis point changes have distinct units.
81. Zero denominator produces an unavailable/nonmeaningful output where appropriate.
82. Derived values preserve source observation lineage.
83. Missing source observations are not interpolated.

### Overview
84. The global overview uses a curated supported economy set.
85. Curated economy data is not presented as a complete world aggregate.
86. Official global aggregates require actual source identities.
87. Each headline value retains its own period.
88. Mixed reporting frequencies are labeled.
89. Source freshness is visible.
90. No fake realtime status is displayed.
91. No unsupported macroeconomic interpretation is generated.

### Time Series
92. Historical charts use actual dates.
93. Units are displayed.
94. Negative values are supported.
95. Missing periods remain gaps.
96. Revisions are qualified.
97. Latest-revised vs vintage views remain distinct.
98. Existing chart adapters are reused.
99. No new universal chart engine is created.

### APIs and Storage
100. Typed Economics APIs are provided.
101. Authentication is enforced.
102. Source entitlements are enforced.
103. Series metadata is canonical.
104. Historical observations use existing storage.
105. New data warehouses are not introduced.
106. Queries are bounded.
107. Source revisions participate in cache keys.
108. Vintage context participates in cache keys.
109. Transformation versions participate in cache keys.
110. Entitlement scope participates in restricted cache keys.
111. Revision invalidation is supported.
112. No per-cell Provider requests are made.
113. Ordinary reads do not mutate canonical observations.

### UI
114. Economics Overview is functional.
115. Major Economies table is source-backed.
116. Indicator Explorer is functional.
117. Historical Series is functional.
118. Unit labels are visible.
119. Reporting periods are visible.
120. Source details are inspectable.
121. Revisions are visible where available.
122. Missing-data states are explicit.
123. Dark/light modes are preserved.
124. Agent Dock compatibility is preserved.
125. Bottom Taskbar compatibility is preserved.
126. Responsive layouts are supported.
127. Keyboard accessibility is supported.
128. Screen-reader accessibility is supported.
129. No purple gradients are introduced.
130. No emoji icons are introduced.
131. No fake economic values are displayed.

### Security
132. Authentication is reused.
133. Authorization is reused.
134. Source licensing is enforced.
135. Restricted derived data is protected.
136. Arbitrary SQL is prohibited.
137. Arbitrary formulas are prohibited.
138. Arbitrary URL fetching is prohibited.
139. Provider secrets remain server-side.
140. Resource limits are enforced.
141. No Trading orders occur.
142. No Portfolio mutations occur.
143. No Broker calls occur.
144. No Agents execute.
145. No Workflows execute.
146. No LLM calls are required.

### Roadmap Boundaries
147. Stage 90 owns Country Economics.
148. Stage 91 owns Central Banks.
149. Stage 92 owns Economic Calendar.
150. Stage 93 owns Macro Comparisons.
151. Stages 94–98 own Screeners.
152. Stages 99–103 own News.
153. Stages 104–109 own Research.
154. Stages 110–114 own Portfolios.
155. Stages 115–118 own Risk.
156. Stages 119–120 own Saved/Workspaces.
157. Stages 121–128 own Terminal/AI.
158. Stages 129–140 own Maps/Intelligence.
159. Stages 141–142 own Options/Quant pricing.
160. Stage 143 owns Backtesting.
161. Stage 144 owns Paper Trading.
162. Stage 145 owns Broker Sandbox.
163. Stages 146+ own Agents.
164. No full Country Economics module is built.
165. No comprehensive Central Banks module is built.
166. No Economic Calendar engine is built.
167. No global Macro Comparisons engine is built.
168. No autonomous macro forecast model is built.
169. No new full Screener is built.
170. No duplicate Economic Data store is created.
171. Stage 89 must pass indicator identity tests.
172. Stage 89 must pass unit tests.
173. Stage 89 must pass frequency tests.
174. Stage 89 must pass transformation tests.
175. Stage 89 must pass vintage and revision tests.
176. Stage 89 must pass point-in-time tests.
177. Stage 89 must pass geographic coverage tests.
178. Stage 89 must pass entitlement tests.
179. Stage 89 must pass relevant previous-stage regressions.
180. Documentation must match actual implementation.
181. Stage 90 is the next canonical stage.

## Stage 90: Country Economics Intelligence

### Product
1. Stage 90 implements Country Economics.
2. Country Economics belongs inside `/economics`.
3. Existing global navigation is preserved.
4. Stage 89 is reused.
5. No duplicate economic-data platform is introduced.
6. Country-specific statistics are source-backed.
7. Country coverage is represented honestly.
8. Missing statistics remain unavailable.
9. No macroeconomic forecasting engine is introduced.
10. Stage 91–93 features remain deferred.

### Country Identity
11. Geographic Entity identity is canonical.
12. Country identifiers are stable.
13. Countries and economic areas are distinct.
14. Historical geography changes are qualified.
15. Country currency identity is preserved.
16. Reporting-area scope is explicit.
17. No neighboring-country data substitution occurs.

### National Accounts
18. Nominal and real GDP are distinct.
19. Current and constant prices are distinct.
20. PPP and market-FX GDP are distinct.
21. GDP growth uses valid periods.
22. Annualization is explicit.
23. Per-capita GDP uses compatible population.
24. National accounts revisions are preserved.
25. Expenditure components are source-qualified.
26. Government consumption differs from total government spending.
27. Net exports use compatible national accounts values.
28. Chain-linked components are not forced to sum.
29. Statistical discrepancies are preserved.
30. Production value added is distinct from corporate Revenue.
31. Sectoral GVA differs from GDP.
32. Income-side GDP is supported only where data exists.
33. No unsupported component contributions are generated.

### Inflation
34. CPI index level differs from inflation.
35. Headline and core definitions are distinguished.
36. CPI food/energy weights use real source values.
37. Seasonal adjustment is explicit.
38. CPI rebasing is handled.
39. PPI/WPI differ from CPI.
40. No fictional inflation basket is created.
41. No inflation forecast is generated.

### Labor
42. Unemployment uses official labor-force definitions.
43. Employment rate differs from unemployment rate.
44. Payroll jobs differ from employed persons.
45. Labor-force participation is scope-qualified.
46. Youth age ranges are preserved.
47. Real and nominal wages are distinct.
48. Productivity uses compatible inputs.
49. Survey revisions are preserved.

### Industry and Consumption
50. Industrial production uses official source index methodology.
51. Retail sales retain real/nominal status.
52. Confidence surveys retain survey meaning.
53. PMI is displayed only when licensed.
54. Housing statistics retain source definitions.
55. No arbitrary conversion into GDP occurs.

### Monetary
56. Monetary aggregates are country-specific.
57. Credit stock differs from new lending.
58. Policy targets differ from effective rates.
59. Monetary-area scope is explicit.
60. Full Central Banks research remains Stage 91.

### Government Accounts
61. Central and general government are distinct.
62. Cash and accrual accounting are distinct.
63. Government consumption differs from total expenditure.
64. Fiscal periods are explicit.
65. Fiscal balance methodology is explicit.
66. Primary balance methodology is explicit.
67. Fiscal ratios require compatible denominators.
68. Gross and net debt are distinct.
69. Debt stock differs from GDP flow.
70. Debt-to-GDP timing is qualified.
71. No sovereign default forecast is generated.

### External Sector
72. Goods and services trade are distinct.
73. Trade balance uses compatible exports/imports.
74. Customs and national accounts trade definitions may differ.
75. Current account differs from trade balance.
76. BOP accounting sign conventions are preserved.
77. FDI flows differ from stocks.
78. Portfolio flows differ from FDI.
79. Gross and net reserves are distinct.
80. External debt scope is explicit.
81. No unsupported reserve-adequacy score is produced.
82. No corporate supply-chain relationships are inferred.

### Demographics
83. Population data uses official source observations.
84. Age groups use source boundaries.
85. Urbanization retains its definition.
86. GDP per capita uses aligned inputs.
87. Census revisions are preserved.
88. No fabricated high-frequency population data is introduced.
89. No unsupported structural growth forecast is generated.

### Temporal Integrity
90. Reference period differs from publication date.
91. Publication date differs from ingestion time.
92. Preliminary and revised observations are distinguished.
93. Actual source vintages are preserved.
94. Latest-revised history differs from as-known-at history.
95. Missing vintage capability is disclosed.
96. No historical look-ahead is permitted.
97. Missing periods are not interpolated.
98. Source methodological changes remain visible.

### APIs and Data
99. Stage 35 remains the canonical economic store.
100. Stage 89 indicator/series registries are reused.
101. Country APIs are typed.
102. Category reads are batched.
103. Historical queries are bounded.
104. Authentication is enforced.
105. Source entitlements are enforced.
106. Derived restricted values are protected.
107. Cache keys include source revisions.
108. Cache keys include geography.
109. Cache keys include statistical definitions.
110. Cache keys include vintage context.
111. Cache keys include entitlement scope.
112. Source revisions invalidate affected views.
113. Page loads do not trigger Provider fanout.
114. Ordinary reads do not mutate canonical observations.

### UI
115. Country selection is functional.
116. Country Overview is functional.
117. GDP workspace is functional.
118. Inflation workspace is functional.
119. Labor workspace is functional.
120. Industry workspace is functional where data exists.
121. Monetary workspace is functional where data exists.
122. Fiscal workspace is functional where data exists.
123. External workspace is functional where data exists.
124. Demographics workspace is functional where data exists.
125. Historical data is source-backed.
126. Source inspectors are functional.
127. Reporting periods are visible.
128. Units are visible.
129. Revisions are visible where supported.
130. Coverage limitations are visible.
131. Dark/light mode is preserved.
132. Agent Dock compatibility is preserved.
133. Bottom Taskbar compatibility is preserved.
134. Responsive layouts are supported.
135. Keyboard navigation is supported.
136. Screen-reader accessibility is supported.
137. No purple gradients are introduced.
138. No emoji icons are introduced.
139. No fabricated economic figures are displayed.

### Security
140. Authentication is reused.
141. Authorization is reused.
142. Provider licensing is enforced.
143. Derived-data leakage is prevented.
144. Arbitrary SQL is prohibited.
145. Arbitrary formulas are prohibited.
146. Arbitrary source URL fetching is prohibited.
147. Provider credentials remain server-side.
148. Resource limits are enforced.
149. No Trading orders occur.
150. No Portfolio mutations occur.
151. No Broker calls occur.
152. No Agents execute.
153. No Workflows execute.
154. No LLM calls are required.

### Roadmap Boundaries
155. Stage 91 owns Central Banks.
156. Stage 92 owns Economic Calendar.
157. Stage 93 owns Macro Comparisons.
158. Stages 94–98 own Screeners.
159. Stages 99–103 own News.
160. Stages 104–109 own Research.
161. Stages 110–114 own Portfolios.
162. Stages 115–118 own Risk.
163. Stages 119–120 own Saved/Workspaces.
164. Stages 121–128 own Terminal/AI.
165. Stages 129–140 own Maps/Intelligence.
166. Stages 141–142 own Options/Quant pricing.
167. Stage 143 owns Backtesting.
168. Stage 144 owns Paper Trading.
169. Stage 145 owns Broker Sandbox.
170. Stages 146+ own Agents.
171. No Central Banks research engine is implemented.
172. No upcoming Economic Calendar is implemented.
173. No full multi-country Macro Comparisons engine is implemented.
174. No economic forecasting system is implemented.
175. No geopolitical exposure engine is implemented.
176. No global Screener is implemented.
177. No duplicate economic warehouse is implemented.
178. Stage 90 must pass GDP reconciliation tests.
179. Stage 90 must pass inflation methodology tests.
180. Stage 90 must pass fiscal accounting tests.
181. Stage 90 must pass external-sector tests.
182. Stage 90 must pass historical vintage tests.
183. Stage 90 must pass Stage 89 regressions.
184. Documentation must match the implementation.
185. Stage 91 is the next canonical stage.

## Stage 91: Central Bank Intelligence

### Product and Scope
1. Stage 91 implements Central Bank Intelligence.
2. Central Banks belongs inside `/economics`.
3. No new global module is introduced.
4. Stage 89 Economic Data is reused.
5. Stage 90 Country Economics is preserved.
6. No duplicate canonical rate-history database is introduced.
7. No fake central-bank records are created.
8. No autonomous policy forecasting is implemented.
9. Stage 92 global calendar remains out of scope.
10. Stage 93 cross-country benchmarking remains out of scope.

### Institution Identity
11. Central Banks use canonical Entity UUIDs.
12. Institution aliases use Stage 22.
13. Monetary jurisdictions use Stage 19.
14. Currency authority is source-qualified.
15. Countries and monetary unions are distinguished.
16. Committee Entities are distinct from institutions.
17. Current institutional relationships are not retroactively applied.
18. Official institutional sources are retained.

### Policy Framework
19. Statutory mandates are distinct from operating strategies.
20. Inflation objectives use exact source definitions.
21. Point targets differ from target ranges.
22. Target bands differ from target centers.
23. Historical framework revisions are preserved.
24. Target effective periods are explicit.
25. No unsupported central-bank score is generated.

### Policy Instruments
26. Rate instruments have stable identities.
27. Target ranges are not collapsed into fake official point rates.
28. Administered rates differ from market effective rates.
29. Multiple official rates may coexist.
30. Negative rates are supported.
31. Historical instrument replacements are preserved.
32. Rate units are explicit.
33. Source series identity is preserved.

### Monetary Decisions
34. Decisions are distinct from rate observations.
35. Official decision identity is preserved.
36. Decisions may affect multiple instruments.
37. Scheduled and emergency decisions are distinct.
38. Announcement and effective timestamps are distinct.
39. Basis-point arithmetic uses compatible instruments.
40. Target range endpoints are calculated separately.
41. Holds require actual verified decisions.
42. Missing previous rates do not generate invented changes.
43. Source corrections preserve revision lineage.
44. No rate-series-only decision fabrication occurs.

### Meetings and Committees
45. Meeting identity is source-backed.
46. Multi-day meetings preserve date ranges.
47. Meeting outcome is distinct from meeting date.
48. Meeting minutes can publish later.
49. Emergency decisions need not be tied to ordinary meetings.
50. Committee membership is historical.
51. Voting status is explicit.
52. Individual votes are displayed only when published.
53. Dissent and abstention are source-qualified.
54. No artificial hawk/dove classifications are introduced.

### Official Documents
55. Stage 20 Document Entities are reused.
56. Document source identifiers are preserved.
57. Official source URLs are verified.
58. Publication dates are preserved.
59. Original content is protected.
60. HTML rendering is sanitized.
61. XML parsing is secure.
62. PDF active content is disabled.
63. Corrections preserve source revisions.
64. Search uses authorized genuine text.
65. No fake official publications are created.

### Forward Guidance
66. Forward guidance requires actual official communication.
67. Guidance wording is source-grounded.
68. Guidance types are explicit.
69. Conditional language is preserved.
70. Later revisions/supersessions are recorded.
71. Guidance is not transformed into an unsupported probability forecast.
72. LLM interpretations are not authoritative source records.

### Balance Sheets and Programs
73. Balance-sheet categories use canonical economic series.
74. Total assets differ from QE commitments.
75. Reserves liabilities differ from FX reserve assets.
76. Asset holdings differ from purchase flows.
77. Program authorizations differ from executed transactions.
78. Runoff may involve maturities and valuation.
79. QT cannot be inferred solely from any total-assets decline.
80. Reporting currency and unit scales are preserved.
81. Accounting classifications are source-defined.
82. Historical balance-sheet revisions are retained.
83. Missing categories are not fabricated.
84. Reconciliation is not forced without valid accounting coverage.

### Temporal Integrity
85. Meeting time differs from decision publication.
86. Announcement may differ from effective time.
87. Publication may differ from ingestion time.
88. Exact timestamps and date-only records are distinct.
89. Historical as-known-at requires source availability qualification.
90. Corrections do not leak backward.
91. Historical vintages are preserved where available.
92. No look-ahead is permitted.

### Providers and Ingestion
93. Stage 28–32 Provider architecture is reused.
94. Official source policies are respected.
95. Provider capability coverage is explicit.
96. Unavailable integrations are not advertised as operational.
97. Ingestion runs in existing background workers.
98. Idempotency is enforced.
99. Document duplicates are prevented.
100. Rate limits are shared across workers.
101. Retries and backoff are bounded.
102. Ingestion checkpoints are recoverable.
103. Page loads do not trigger uncontrolled external fetching.
104. Source conflicts are not silently overwritten.
105. Provider licensing is enforced.

### APIs and Performance
106. Central Bank APIs are typed.
107. Authentication is enforced.
108. Authorization is enforced.
109. Source entitlements are enforced.
110. Queries are bounded.
111. Historical reads are batched.
112. Cache keys include source revisions.
113. Cache keys include publication context.
114. Cache keys include instrument identity.
115. Cache keys include entitlement scope.
116. Document caches are access-controlled.
117. Corrections invalidate impacted views.
118. Normal reads do not mutate source records.
119. No every-tick external polling is introduced.

### UI
120. Central Banks Overview is functional.
121. Institution Explorer is functional.
122. Profile view is functional.
123. Policy instruments are inspectable.
124. Current rates are source-backed.
125. Rate history is functional.
126. Decision history is functional.
127. Meeting history is functional where source-backed.
128. Committee/vote views are qualified.
129. Publications are functional.
130. Speeches are functional where available.
131. Balance Sheet is functional where available.
132. Programs are source-backed.
133. Policy Timeline is functional.
134. Source Inspector is functional.
135. Missing-data states are explicit.
136. Dark/light modes are preserved.
137. Agent Dock compatibility is preserved.
138. Bottom Taskbar compatibility is preserved.
139. Responsive layouts are supported.
140. Keyboard accessibility is supported.
141. Screen-reader accessibility is supported.
142. No purple gradients are introduced.
143. No emoji icons are introduced.
144. No fabricated policy records are displayed.

### Security
145. Authentication is reused.
146. Authorization is reused.
147. Provider licensing is enforced.
148. Restricted source-text leakage is prevented.
149. Unsafe document execution is prohibited.
150. Arbitrary SQL is prohibited.
151. Arbitrary formulas are prohibited.
152. Arbitrary URL fetching is prohibited.
153. Provider secrets remain server-side.
154. Resource limits are enforced.
155. No Trading orders occur.
156. No Portfolio mutations occur.
157. No Broker actions occur.
158. No Agents execute.
159. No Workflows execute.
160. No LLM calls are required.

### Roadmap Boundaries
161. Stage 92 owns Economic Calendar.
162. Stage 93 owns Macro Comparisons.
163. Stages 94–98 own Screeners.
164. Stages 99–103 own News.
165. Stages 104–109 own Research.
166. Stages 110–114 own Portfolios.
167. Stages 115–118 own Risk.
168. Stages 119–120 own Saved/Workspaces.
169. Stages 121–128 own Terminal/AI.
170. Stages 129–140 own Maps/Intelligence.
171. Stages 141–142 own Options/Quant pricing.
172. Stage 143 owns Backtesting.
173. Stage 144 owns Paper Trading.
174. Stage 145 owns Broker Sandbox.
175. Stages 146+ own Agents.
176. No global Economic Calendar is built.
177. No economic surprise engine is built.
178. No market-implied meeting probabilities are built.
179. No full multi-country policy comparison engine is built.
180. No AI policy forecasting is built.
181. No duplicate Economics platform is built.
182. No duplicate Document Entity database is built.
183. Stage 91 must pass institution identity tests.
184. Stage 91 must pass instrument correctness tests.
185. Stage 91 must pass monetary decision tests.
186. Stage 91 must pass rate-change tests.
187. Stage 91 must pass meeting/voting tests.
188. Stage 91 must pass source-document security tests.
189. Stage 91 must pass historical point-in-time tests.
190. Stage 91 must pass balance-sheet/program tests.
191. Stage 91 must pass entitlement tests.
192. Stage 91 must pass Stage 89–90 regressions.
193. Documentation must match actual implementation.
194. Stage 92 is the next canonical stage.

## Stage 92: Global Economic Calendar

### Product
1. Stage 92 implements Global Economic Calendar.
2. Calendar belongs inside `/economics`.
3. No new global Sidebar module is created.
4. Stage 89 Economic Indicators are reused.
5. Stage 90 Country Economics is reused.
6. Stage 91 Central Banks is reused.
7. Stage 49 Notification Center is reused.
8. No duplicate global event-intelligence platform is created.
9. Stage 93 Macro Comparisons remains out of scope.

### Event Semantics
10. Calendar events are distinct from statistical observations.
11. Release families are explicit.
12. Official occurrences have stable identity.
13. One event may publish multiple observations.
14. Advance and revised releases may be distinct occurrences.
15. Event titles are not primary keys.
16. Source identifiers are preserved.
17. Provider duplicates are reconciled.
18. Schedule changes preserve event identity.
19. Cancelled events remain historically traceable.
20. Missing schedule data is not fabricated.

### Timezones
21. Exact instants use timezone-aware storage.
22. UTC is canonical for instants.
23. IANA source timezone is preserved.
24. User timezone is display context.
25. Date-only events are not assigned midnight.
26. Unknown release times remain unknown.
27. DST ambiguity is handled.
28. Local date boundaries are respected.
29. Today/Week views use selected timezone.
30. Source date and displayed user date can differ.

### Lifecycle
31. Scheduled does not equal released.
32. Passing scheduled time does not prove release.
33. Release verification requires evidence.
34. Official postponements require source support.
35. Official cancellations require source support.
36. Schedule revision history is preserved.
37. Publication corrections are preserved.
38. Provider outages do not generate fabricated release statuses.

### Actuals
39. Stage 35 remains authoritative for actual observations.
40. Calendar actuals reference canonical observation IDs.
41. Preliminary/revised/final stages remain distinct.
42. First release vintage is preserved where available.
43. Later revisions do not erase historical actuals.
44. Missing actuals remain missing.
45. Reference periods are explicit.
46. Publication time differs from ingestion time.

### Previous Values
47. Previous reporting periods are source-qualified.
48. Previous original and revised values are distinct.
49. Historical previous-value claims require genuine vintages.
50. Missing original previous values are not fabricated.

### Consensus
51. Consensus values require authorized source data.
52. Individual forecasts differ from consensus.
53. Forecast aggregation methodology is preserved.
54. Contributor count is displayed only when known.
55. Forecast snapshots are versioned.
56. Forecast publication timestamp is preserved.
57. Post-release snapshots cannot serve as pre-release forecasts.
58. Forecast licensing is enforced.
59. Missing consensus remains unavailable.
60. No model-generated consensus is created.

### Surprises
61. Surprise is actual minus compatible consensus.
62. Indicator identity must match.
63. Geography must match.
64. Reference period must match.
65. Adjustment policy must match.
66. Unit must match.
67. First-release vintage must be qualified.
68. Percentage-point differences are correct.
69. Basis-point differences are correct.
70. Employment units are preserved.
71. Zero denominators are handled.
72. Negative denominators are methodology-qualified.
73. Missing forecasts prevent calculation.
74. Surprise sign does not imply investment impact.
75. Calculation versions and lineage are preserved.

### Importance
76. Source-defined importance is distinguished from internal policy.
77. Internal ratings are deterministic and documented.
78. Importance is not market-impact probability.
79. Unknown ratings remain unclassified.
80. No fabricated probabilities appear.

### Central Banks
81. Stage 91 remains authoritative for Central Bank identities.
82. Meeting events reference verified institution records.
83. Decision announcements differ from meetings.
84. Rate holds differ from rate hikes/cuts.
85. Emergency meetings require official evidence.
86. No future decision outcomes are predicted.

### Providers and Ingestion
87. Stage 28–32 architecture is reused.
88. Official schedules are preferred where suitable.
89. Source licensing is verified.
90. Provider capability coverage is explicit.
91. Schedule and actual sources can differ.
92. Ingestion is shared across users.
93. Page loads do not trigger Provider fanout.
94. Jobs use checkpoints.
95. Retries are bounded.
96. Event ingestion is idempotent.
97. Source revisions are preserved.
98. Invalid Provider fallback is rejected.
99. No unrestricted external crawler is created.

### Realtime
100. Realtime event delivery is source-qualified.
101. Browser WebSocket receipt does not prove realtime source delivery.
102. Official publication time is distinct.
103. Provider delivery time is distinct.
104. ATLAS ingestion time is distinct.
105. Event updates have stable IDs/revisions.
106. Duplicate updates are idempotent.
107. Reconnect requires snapshot reconciliation.
108. No per-event WebSocket is created.
109. No guaranteed subsecond release delivery is claimed without evidence.

### Notifications
110. Stage 49 Notification Center is reused.
111. Alerts are user-owned.
112. Auth/RLS is enforced.
113. Reminders require valid schedule precision.
114. Release notifications require verified publication.
115. Rescheduled events update reminder logic.
116. Cancelled events stop normal reminders.
117. Notification intents are idempotent.
118. Durable delivery/outbox is used where appropriate.
119. Worker recovery is supported.
120. Concurrent workers do not create duplicate notification intents.
121. Quiet hours are respected.
122. User timezone is respected.
123. Entitlement changes are respected.
124. Notification quotas are enforced.
125. No external channel is claimed unless implemented.
126. No release-based trading action is created.

### Storage and Caching
127. Event records are distinct from canonical observations.
128. Event-to-indicator relationships are explicit.
129. Schedule revisions are preserved.
130. Forecast snapshots are preserved.
131. Event lists are indexed by date.
132. Queries are bounded.
133. Cache keys include schedule revision.
134. Cache keys include actual vintage.
135. Cache keys include forecast snapshot.
136. Cache keys include entitlement scope.
137. Schedule revisions invalidate affected views.
138. New actuals invalidate affected views.
139. Forecast revisions invalidate affected views.
140. Restricted consensus cannot leak through shared caches.

### UI
141. Calendar navigation is functional.
142. Today view is functional.
143. Tomorrow view is functional.
144. Week views are functional.
145. Custom range is functional.
146. Country filters are functional.
147. Category filters are functional.
148. Importance filters are functional.
149. Status filters are functional.
150. Source filters are functional.
151. Central Bank event filters are functional.
152. User timezone display is correct.
153. Date-only event display is correct.
154. Event details are functional.
155. Actual values are source-backed.
156. Forecasts are source-backed.
157. Previous/revised values are qualified.
158. Surprises use correct units.
159. Official source links are genuine.
160. User alert controls are functional.
161. Notification history is functional.
162. Missing-data states are explicit.
163. Dark/light themes are preserved.
164. Agent Dock compatibility is preserved.
165. Bottom Taskbar compatibility is preserved.
166. Responsive layouts are supported.
167. Keyboard accessibility is supported.
168. Screen-reader accessibility is supported.
169. No purple gradients are introduced.
170. No emoji icons are introduced.
171. No fake economic releases are displayed.

### Security
172. Authentication is enforced.
173. Authorization is enforced.
174. User alerts are private.
175. Forecast licensing is enforced.
176. Restricted surprise derivations are protected.
177. Arbitrary SQL is prohibited.
178. Arbitrary formulas are prohibited.
179. Arbitrary Provider URLs are prohibited.
180. Provider secrets remain server-side.
181. Alert resource quotas are enforced.
182. Safe source-document handling is preserved.
183. No Trading orders occur.
184. No Portfolio mutations occur.
185. No Broker actions occur.
186. No Agents execute.
187. No arbitrary Workflows execute.
188. No LLM calls are required.

### Roadmap Boundaries
189. Stage 93 owns Macro Comparisons.
190. Stages 94–98 own Screeners.
191. Stages 99–103 own News.
192. Stages 104–109 own Research.
193. Stages 110–114 own Portfolios.
194. Stages 115–118 own Risk.
195. Stages 119–120 own Saved/Workspaces.
196. Stages 121–128 own Terminal/AI.
197. Stages 129–140 own Maps/Intelligence.
198. Stages 141–142 own Options/Quant pricing.
199. Stage 143 owns Backtesting.
200. Stage 144 owns Paper Trading.
201. Stage 145 owns Broker Sandbox.
202. Stages 146+ own Agents.
203. No cross-country macro factor comparison engine is implemented.
204. No autonomous economic forecasting is implemented.
205. No research RAG engine is implemented.
206. No economic event trading engine is implemented.
207. No duplicate Economic Data warehouse is built.
208. Stage 92 must pass timezone/DST tests.
209. Stage 92 must pass release lifecycle tests.
210. Stage 92 must pass forecast vintage tests.
211. Stage 92 must pass economic surprise tests.
212. Stage 92 must pass alert recovery/idempotency tests.
213. Stage 92 must pass entitlement tests.
214. Stage 92 must pass Stage 89–91 regressions.
215. Documentation must match actual code.
216. Stage 93 is the next canonical stage.

## STAGE 93 — INSTITUTIONAL MACROECONOMIC COMPARISONS & BENCHMARKING ENGINE

### Product
1. Stage 93 implements Macro Comparisons.
2. It remains inside `/economics`.
3. No new global Sidebar module is introduced.
4. The Stage 89 indicator registry is reused.
5. Stage 90 Country Economics is reused.
6. Stage 91 Central Bank instrument identity is reused.
7. Stage 92 historical release/vintage context is reused.
8. No duplicate canonical economic database is introduced.
9. Country comparisons use source-backed observations.
10. Stage 94 Screeners remains out of scope.

### Geographic Identity
11. Country UUIDs are canonical.
12. Economic areas are distinct from countries.
13. Geographic cohorts are explicitly defined.
14. Historical cohort membership is qualified.
15. Geographic overlaps are identified.
16. Official aggregates differ from derived country sets.
17. Country names are not primary join keys.
18. No neighboring-country substitution occurs.

### Indicator Identity
19. Economic Indicator IDs are canonical.
20. Provider source series IDs are preserved.
21. Similar names do not imply identical concepts.
22. Harmonized and nonharmonized series are distinguished.
23. Methodology differences are disclosed.
24. Missing metadata does not prove compatibility.
25. Comparability states are explicit.
26. Invalid arithmetic is blocked.

### Units and Periods
27. Percent differs from percentage points.
28. Rates differ from rate changes.
29. Basis points are explicit.
30. Nominal vs real is preserved.
31. Stock vs flow is preserved.
32. Currency conversions require valid methods.
33. Reference periods are aligned.
34. Fiscal and calendar years are distinguished.
35. Latest-common differs from latest-per-country.
36. Missing periods are not fabricated.
37. Frequency transformations are controlled.

### GDP and PPP
38. Nominal GDP uses defined currency basis.
39. Real GDP uses source-specific price basis.
40. PPP GDP differs from market-FX GDP.
41. Historical GDP conversions are period-qualified.
42. GDP per capita uses compatible population.
43. GDP growth uses valid frequencies.
44. Annualized growth remains distinct.
45. Chain-linked component limitations are preserved.
46. No unsupported GDP aggregates are created.

### Inflation and Labor
47. CPI/HICP definitions remain distinct.
48. Headline/core inflation are distinct.
49. YoY/MoM inflation are distinct.
50. Index bases are qualified.
51. Inflation differences use percentage points.
52. Unemployment uses labor-force definitions.
53. Age-group populations are source-qualified.
54. Labor survey differences remain visible.
55. No false national labor-quality score is generated.

### Monetary
56. Central Bank instruments use Stage 91 identities.
57. Target ranges differ from point rates.
58. Effective rates differ from administered rates.
59. Monetary unions are handled correctly.
60. Basis-point differences use compatible instruments.
61. No carry-trade predictions are generated.

### Fiscal and External
62. Central/general government are distinct.
63. Gross/net debt are distinct.
64. Fiscal reporting years matter.
65. Debt-to-GDP uses qualified denominators.
66. Goods trade differs from total trade.
67. Trade balance differs from current account.
68. FDI stocks differ from flows.
69. Foreign reserves retain source definition.
70. No sovereign stability score is invented.

### Ranking
71. Rankings use eligible compatible observations.
72. Ranking direction is numeric and explicit.
73. Tie policy is documented.
74. Missing countries are disclosed.
75. Ranking population size is reported.
76. Historical rankings preserve cohort methodology.
77. No universal Best Economy score is introduced.

### Distributions
78. Means use eligible numeric samples.
79. Median/percentiles use documented conventions.
80. Standard deviation sample/population treatment is explicit.
81. Sample N is displayed.
82. Missing values are excluded honestly.
83. Outliers are not silently removed.
84. Weighted and unweighted statistics differ.
85. Missing weights are not guessed.

### Aggregates
86. Official source aggregates are distinguished.
87. Derived group aggregations require compatibility.
88. Geographic overlaps prevent naive sums.
89. GDP growth rates are not simply summed.
90. Arbitrary inflation rates are not averaged into World Inflation.
91. Group weights are period-qualified.
92. Source methodology is disclosed.

### Historical Analysis
93. Historical reference periods are aligned.
94. Actual missingness is preserved.
95. Latest-restated differs from as-known-at.
96. Source vintages are preserved.
97. Later revisions do not leak backward.
98. Historical differences use compatible series.
99. No artificial future trend is projected.

### Correlation
100. Correlation requires period-aligned observations.
101. Pearson and Spearman methods are distinct.
102. Sample N is displayed.
103. Zero variance produces undefined correlation.
104. Missing observations are handled.
105. Nonstationarity caveats are displayed.
106. Serial dependence is acknowledged.
107. Correlation is not causality.
108. Correlation is not a trading signal.
109. Arbitrary predictive lag optimization is not implemented.

### APIs and Performance
110. Comparison APIs are typed.
111. Queries are read-only.
112. Country counts are bounded.
113. Indicator counts are bounded.
114. Historical observation counts are bounded.
115. Correlation matrix sizes are bounded.
116. Queries batch canonical data reads.
117. Compatibility is evaluated server-side.
118. Calculation methodology is versioned.
119. Cache keys include source revisions.
120. Cache keys include vintage context.
121. Cache keys include country membership revision.
122. Cache keys include weighting policy.
123. Cache keys include entitlement scope.
124. Source revisions invalidate affected results.
125. No page-load Provider fanout occurs.

### UI
126. Country multi-select works.
127. Indicator selection works.
128. Period selection works.
129. Source selection works.
130. Comparison Matrix works.
131. Rankings work.
132. Historical Trends work.
133. Distributions work.
134. Divergence works.
135. Correlations work where valid.
136. Eligibility warnings are visible.
137. Source Methodology inspector works.
138. Sample sizes are visible.
139. Missing data is visible.
140. URL comparison state works.
141. Desktop layout is responsive.
142. Tablet layout is responsive.
143. Mobile layout is functional.
144. Dark/light is preserved.
145. Agent Dock compatibility is preserved.
146. Bottom Taskbar compatibility is preserved.
147. Keyboard accessibility is supported.
148. Screen-reader accessibility is supported.
149. No purple gradients are introduced.
150. No emoji icons are introduced.
151. No fictional economic values appear.

### Security
152. Authentication is enforced.
153. Authorization is enforced.
154. Source licensing is enforced.
155. Restricted derived results are protected.
156. Arbitrary SQL is prohibited.
157. Arbitrary user formulas are prohibited.
158. Arbitrary Provider URLs are prohibited.
159. Provider secrets remain server-side.
160. Resource limits are enforced.
161. No Trading occurs.
162. No Portfolio mutations occur.
163. No Broker actions occur.
164. No Agents execute.
165. No Workflows execute.
166. No LLM calls are required.

### Roadmap Boundaries
167. Stage 94 owns Screeners V1.
168. Stage 95–98 continue Screeners.
169. Stages 99–103 own News.
170. Stages 104–109 own Research.
171. Stages 110–114 own Portfolios.
172. Stages 115–118 own Risk.
173. Stages 119–120 own Saved and Workspaces.
174. Stages 121–128 own Terminal/AI.
175. Stages 129–140 own Maps/Intelligence.
176. Stages 141–142 own Options/Quant pricing.
177. Stage 143 owns Backtesting.
178. Stage 144 owns Paper Trading.
179. Stage 145 owns Broker Sandbox.
180. Stages 146+ own Agents.
181. No security/instrument Screener is created.
182. No economic forecasting engine is created.
183. No global Maps engine is created.
184. No duplicate Economic Data platform is created.
185. Stage 93 must pass compatibility tests.
186. Stage 93 must pass period alignment tests.
187. Stage 93 must pass PPP/currency tests.
188. Stage 93 must pass rankings/distributions tests.
189. Stage 93 must pass aggregation tests.
190. Stage 93 must pass correlation tests.
191. Stage 93 must pass point-in-time tests.
192. Stage 93 must pass source-entitlement tests.
193. Stage 93 must pass Stage 89–92 regressions.
194. Documentation must match actual code.
195. Stage 94 is the next canonical stage.

## Stage 94: Institutional-Grade Financial Screeners V1

### Product and Scope
196. Stage 94 implements Financial Screeners V1.
197. Screeners workspace is accessible at the canonical `/screeners` route.
198. Global navigation and AppShell structure remain strictly preserved.
199. Canonical Financial Instrument Entities (Stage 17) are reused.
200. Canonical Company Entities (Stage 18) are reused.
201. Canonical Market Data and Live Quotes (Stages 33, 41, 44) are reused.
202. Canonical Fundamental Statements and Ratios (Stages 34, 82, 83) are reused.
203. No separate or shadow source-of-truth warehouse is created.
204. Advanced recursive Boolean rule engines and automated alerts remain deferred to Stages 95–98.

### Financial Instrument Identity & Universes
205. Financial Instrument UUID is the primary canonical identifier authority.
206. Company Entity (issuer) and Financial Instrument Entity (security) identities are strictly distinct.
207. Exchange listing identity is explicit with venue-scoped Market Identifier Codes (MIC).
208. Ticker strings are not globally unique; exchange qualification prevents collisions.
209. Symbol renames do not create artificial new corporate or security entities.
210. Multiple share classes (e.g. Alphabet Class A GOOGL vs Class C GOOG, Berkshire Hathaway BRK.A vs BRK.B) are distinct instruments sharing the same issuer company.
211. Cross-listings (e.g. Infosys ADR on NYSE vs Infosys Common on NSE) maintain distinct instrument identities, trading currencies, and venue metadata.
212. Depositary receipts (ADRs/GDRs) retain foreign issuer domicile and conversion semantics.
213. ETFs and fund units are classified as funds and excluded from common equity screening by default.
214. Delisted and suspended securities are excluded from current active universes by default while preserved for historical survivorship-bias-free screening.
215. Screener row grain is explicitly canonical security listing.
216. Issuer and security counts are never conflated.

### Market Data, Fundamentals, and Valuation Ratios
217. Price metrics require trading currency, exchange session, and source timestamps.
218. Stale quotes are qualified and never deceptively labeled live.
219. Market capitalization represents institutional equity market cap and respects share-class scope.
220. Daily volume and 20-day average volume respect venue and session scope.
221. Fundamentals (Revenue, Net Income, Operating Income, Assets, Book Equity, EPS) belong to verified issuer companies and preserve fiscal period, reporting currency, and consolidation scope.
222. Conventional P/E on non-positive earnings is undefined / Not Meaningful (N/M), never 0 or negative.
223. Missing metrics are represented as unavailable/missing ("—") and never coerced to zero.
224. Missing metrics never satisfy relational comparisons (>, <, >=, <=, BETWEEN).

### Filter Engine & Query Execution
225. Filter definitions use stable, typed identifiers, explicit value types, and allowlisted operators.
226. Comparison operators include EQ, NE, GT, GTE, LT, LTE, BETWEEN, and IN.
227. Basic AND composition is supported; arbitrary user SQL or code execution is strictly prohibited.
228. Filter complexity is capped at 20 active conditions per query.
229. Screening executes entirely server-side; downloading the universe to the client is prohibited.
230. Server-side screening performs zero external provider RPC fanout on read.
231. Sorting is deterministic with primary field ordering (NULLS LAST) and a stable tie-breaker on (instrument_entity_id, listing_id).
232. Pagination is server-side bounded (default 50, maximum 100) with opaque cursor integrity.
233. Cell-level provenance, observation period, and freshness metadata are enriched on every response.
234. Stage 95 implements Visual Screener Filters.

## Stage 95: Institutional-Grade Visual Screener Filter Builder

### Product and Scope
235. Stage 95 implements the Visual Screener Filter Builder subsystem.
236. Stage 94 core screener engine remains the authoritative source of truth for filter semantics and query execution.
237. The feature lives strictly within the existing `/screeners` route; no new global navigation route is created.
238. Global navigation, sidebar, agent dock, and bottom taskbar integrations remain strictly preserved.
239. The Visual Builder is a presentation, validation, and typed query-construction interface.
240. No duplicate or parallel screener backend is created.
241. No new financial indicator calculations (e.g. RSI, MACD) are created; technical factors remain deferred to Stage 96.
242. No arbitrary SQL or executable formula query language is exposed to users.
243. Stage 96 (fundamental, technical, and multi-factor screening expansion) remains deferred.
244. Stage 97 (saved screens library, ranking formulas, exports) remains deferred.
245. Stage 98 (natural-language screener translation hooks) remains deferred.

### Filter Registry Integration
246. Filter definitions are source-backed by the canonical Stage 94 Filter Registry.
247. Stable, typed filter identifiers (`filter_id`) are preserved across all interactions.
248. Categorization is source-backed (Market Data, Fundamentals, Valuation, Profitability, Listing, Geography, Industry).
249. Operator eligibility is explicit per filter definition; invalid operators cannot be chosen.
250. Value types are explicit (CURRENCY, NUMERIC, PERCENTAGE, INTEGER, ENUM, BOOLEAN).
251. Measurement units are explicit (MONETARY, PERCENT, MULTIPLE, SHARES, CURRENCY_PER_SHARE, DIMENSIONLESS).
252. Metric applicability across security types and industries is explicit.
253. Source coverage summaries and provenance audit references are disclosed.
254. Entitlement states are enforced server-side; client cannot bypass licensing rules.
255. Disabled or unsupported filters are clearly labeled and cannot be executed.
256. No fabricated financial metrics or indicators appear in the catalog.

### Visual Condition Identity & Construction
257. Condition instances carry stable client-side identities (`conditionId`), strictly distinct from `filterId`.
258. Multiple conditions may refer to the same metric (e.g. price floor and price ceiling).
259. Adding a condition creates an editable draft with default operator without inventing false numeric values.
260. Editing condition metric, operator, value, currency, or magnitude is reactive and type-safe.
261. Removing a condition instantly updates draft query state.
262. Duplicating a condition safely creates a distinct condition instance with fresh client ID.
263. Visual reordering is supported for usability without altering Boolean semantics.
264. Visual category grouping organizes condition rows without secretly altering Boolean logic.
265. Query preview reflects actual serialized predicates deterministically.

### Typed Input Controls & Precision
266. Exact decimal text precision is preserved without IEEE 754 floating-point corruption.
267. Monetary inputs are currency-qualified (`USD`, `EUR`, `GBP`, `INR`, `JPY`) with explicit magnitude multipliers (`K`, `M`, `B`, `T`).
268. Percentage conventions are human-friendly (`15` = 15%) and clearly differentiated from valuation multiples (`20x`).
269. Financial ratios use canonical dimensionless multiple representations (`x`).
270. Numeric range controls enforce exact boundary validation (`min <= max`) with inclusive bounds.
271. Enumeration and multi-select filters use canonical registry identifiers rather than free-text names.
272. Empty input fields remain incomplete drafts and are never coerced to zero.
273. Non-finite values (`NaN`, `Infinity`, `-Infinity`) are rejected immediately.
274. Intermediate typing states (`-`, `12.`) are treated as incomplete drafts rather than fatal errors.
275. Magnitude factors normalize to canonical base values during query serialization.
276. Metric round-trips preserve numerical meaning without loss of precision.

### Dependency Management & Applicability
277. Universe selection changes re-evaluate all active draft conditions.
278. Incompatible filters are flagged with explanatory notices; conditions are never silently deleted.
279. Source availability directly influences metric eligibility.
280. Security type eligibility is enforced (e.g. ETF fundamentals excluded from operating equities).
281. Industry-specific ratio applicability is respected.
282. Reporting period policies (annual, quarterly, TTM) are explicitly labeled.
283. Currency conversion policies require explicit normalization.
284. Entitlements block unauthorized metric evaluation at the server level.

### Contradiction Detection
285. Provable numeric boundary contradictions are evaluated deterministically (`lower > upper`).
286. Strict inequality contradictions on matching boundaries (`> 100` AND `< 100`) are flagged.
287. Conflicting equality constraints on single-valued classifications (e.g. `sector == Tech` AND `sector == Healthcare`) are flagged.
288. Overlapping valid ranges are permitted and never falsely labeled impossible.
289. Missing data values are not treated as satisfying contradictory conditions.
290. Currency compatibility is checked prior to boundary comparison.
291. Scope and financial periods must match before asserting contradiction.
292. Valid empty-result queries are distinguished from mathematically contradictory predicates.

### State Management & Query Execution
293. Draft Query and Applied Query states are strictly separated.
294. Dirty state is explicitly indicated ("Changes not applied").
295. Apply Filters validates client state, executes server query, and updates results atomically.
296. Discard Changes restores the last successfully applied query state.
297. Clear All clears active draft conditions cleanly.
298. Results table retains association with the previously applied query while edits occur.
299. Failed execution preserves draft state and displays actionable error messages.
300. Rapid user edits and obsolete responses are rejected via query revision matching.
301. Active in-flight requests are cancelled using `AbortController` when superseded.
302. URL state synchronizes query parameters safely with schema versioning.
303. URL state reconstruction validates all filter IDs and operators against the registry.

### Security & Governance
304. Server-side validation remains mandatory and authoritative.
305. Filter IDs are strictly allowlisted against the approved registry.
306. Operators are strictly allowlisted per filter definition.
307. Enum identifiers are validated against canonical catalogs.
308. Active condition count is capped at 20 per query.
309. Input text, numbers, and query payload sizes are bounded.
310. SQL injection and arbitrary code execution vectors are completely eliminated.
311. Client-side state cannot bypass source licensing or user entitlements.
312. Restricted financial data cannot leak through filter discovery or metadata counts.
313. No provider secrets, credentials, or private keys are serialized in URL state.
314. No trading orders or broker interactions can be executed from screeners.
315. No portfolio mutations are triggered by screener edits.
316. No autonomous background monitoring or screening agents are dispatched.
317. Normal Stage 95 screener operations require exactly 0 LLM calls.

### Performance & Terminal Ergonomics
318. Local editing performs zero full-universe network requests on keystroke.
319. Filter catalog and enum option lists are memoized by registry revision.
320. Condition row updates isolate React re-renders using stable condition IDs.
321. Network validation is triggered on Apply, Review, or explicit user action.
322. Obsolete network requests are aborted immediately.
323. Server screening executes with zero external provider RPC fanout on read.
324. Large categorical lists (exchanges, countries) render efficiently.
325. Institutional dark UI surfaces, fine borders, and tabular numerals maintain Bloomberg terminal aesthetic.
326. Full keyboard navigation is supported (search shortcut, arrow traversal, Enter to add, Escape to close).
327. Screen-reader accessible input labels, error announcements, and focus restoration are enforced.
328. Responsive layouts operate seamlessly across desktop (1920px), tablet (768px), and mobile (320px).
329. Stage 95 satisfies all test requirements, passing 35 backend tests and 13 frontend tests.
330. Stage 96 is the canonical stage for fundamental, technical, and multi-factor screening expansion.

## Stage 96 — Fundamental, Technical and Multi-Factor Screening Engine

### Product & Architecture
331. Stage 96 implements institutional-grade fundamental, technical and multi-factor screening.
332. Stage 94 remains the canonical Screener Engine.
333. Stage 95 remains the Visual Filter Builder.
334. No new top-level Screener route is created; operations live at `/screeners`.
335. No duplicate security universe is introduced.
336. No duplicate market data store is introduced.
337. No duplicate financial statements store is introduced.
338. No alternate Screener query language is created.

### Fundamental Data & Accounting Integrity
339. Canonical financial statements from Stage 82 are authoritative.
340. Canonical financial ratios from Stage 83 are reused.
341. Financial reporting periods are explicit (FY2025/TTM).
342. Annual, quarterly, and TTM remain distinct concepts.
343. Consolidated and standalone scopes remain distinct.
344. Reporting currency is preserved and qualified.
345. Financial restatements are preserved and qualified.
346. Publication timestamp is respected for point-in-time integrity.
347. Missing data evaluates to strict NULL and never passes numerical filters.
348. Financial-sector applicability is enforced (Banking excluded from industrial COGS/FCF/Net Debt).
349. Negative denominator treatment in growth metrics is explicit.
350. No artificial EBITDA is created from arbitrary shortcuts.
351. No artificial earnings forecasts are created.

### Valuation & Multiples
352. Price-based ratios use valid completed prices.
353. Market cap uses valid security/issuer share-class scope.
354. Enterprise Value (EV) methodology is explicit.
355. Cash adjustments are source-qualified.
356. Negative earnings eligibility is respected (P/E evaluates to N/M).
357. Source-reported and derived ratios remain distinguishable.
358. No unsupported valuation scores are invented.

### Technical Indicator Engine & Mathematics
359. Canonical OHLCV data is authoritative.
360. Security and listing identity is preserved.
361. Trading calendar is respected (trading sessions != calendar days).
362. Completed bars are default (`LAST_COMPLETED`).
363. Incomplete bar values are strictly qualified if ever used.
364. Corporate-action adjustment (splits) is explicit.
365. Split-adjusted and total-return-adjusted series are distinct.
366. Missing bars are not synthesized.
367. Indicator lookback is validated with strict warm-up requirements.
368. Formula versions are stored (`1.0.0`).
369. Indicator warm-up is strictly enforced (returns None if bars < lookback).
370. Charts and Screeners use consistent formulas.
371. SMA implementation is documented and verified against TA-Lib.
372. EMA initialization uses seed SMA.
373. RSI smoothing uses Wilder's method with zero-loss edge case handling.
374. MACD parameter conventions are fast=12, slow=26, signal=9.
375. Bollinger Bands standard deviation uses sample convention.
376. ATR smoothing uses Wilder's method with ATR% normalized to close.
377. Momentum horizon is defined in eligible trading bars (5d, 20d, 60d, 252d).
378. Volatility annualization uses 252 trading sessions with log returns.
379. Relative Volume compares latest session volume to 20-session baseline.
380. Breakout windows exclude current observation from prior high/low threshold.
381. Crossovers use prior/current completed observations.
382. Technical indicators do not imply future market performance.

### Multi-Factor & Cross-Sectional Composition
383. Multi-factor screening combines approved factors in a single query.
384. Existing Boolean AND semantics remain authoritative.
385. Fundamental issuer and technical security grains are reconciled via canonical relationships.
386. Missing factor values do not pass numeric filters.
387. Factors use typed units (monetary, percent, multiple, shares, dimensionless).
388. Factor period eligibility is checked.
389. Factor entitlements are checked.
390. No arbitrary executable formulas or code injection allowed.
391. Cross-sectional transformations require defined eligible cohorts.
392. No arbitrary composite ranking product is created.
393. No ML alpha score or predictive return metric is introduced.

### Point-in-Time & Look-Ahead Prevention
394. Historical inputs respect knowledge-time eligibility.
395. Statement period end is not publication time.
396. Incomplete bars cannot be treated as completed.
397. Restatements cannot leak backward into historical vintages.
398. Source revisions are preserved.
399. Historical-as-known-at requires real source vintages.
400. Ordinary current screening does not imply historical backtesting.
401. No historical trading performance claims are created.

### Performance & Scaling
402. Zero external provider calls per security on screener query.
403. Screening is fully executed server-side.
404. Cheap universe predicates reduce candidate sets before expensive indicator checks.
405. Derived factors are batch-computed across eligible equities.
406. Common parameter sets (SMA 20/50/200, RSI 14, MACD 12/26/9) are materialized.
407. Uncommon parameter sets are bounded to integer periods between 2 and 500.
408. Derived projections are rebuildable from canonical history.
409. Source watermarks are recorded on derived indicators.
410. Formula versions participate in caching.
411. Corporate action revisions invalidate affected factors.
412. Financial restatements invalidate affected factors.
413. Entitlement changes invalidate restricted responses.
414. Query complexity is bounded to 20 active filters.
415. Database and computation timeouts are enforced.
416. Pagination occurs strictly after correct predicate evaluation.

### Visual Builder & UI Integration
417. Fundamental categories work seamlessly in Visual Builder.
418. Technical categories work seamlessly in Visual Builder.
419. Multi-factor composition works seamlessly with AND logic.
420. Parameterized technical inputs (period) operate dynamically.
421. Financial period controls display reporting policies.
422. Factor Inspector displays exact methodology and formula specs.
423. Source Inspector displays provenance, observation periods, and freshness.
424. Data quality and coverage indicators are visible.
425. Insufficient-history states are visible without errors.
426. No fake technical signals or stock recommendations are displayed.
427. Stage 94 results remain functional.
428. Stage 95 Visual Builder remains functional.
429. Dark/light themes are preserved.
430. Agent Dock remains compatible.
431. Bottom Taskbar remains compatible.
432. Desktop, tablet, and mobile layouts are fully responsive.
433. Keyboard and screen-reader accessibility are preserved.
434. No purple gradients or emoji icons are introduced.

### Security & Governance
435. Authentication is enforced.
436. Authorization is enforced.
437. Factor IDs are strictly allowlisted (70 canonical filters).
438. Parameters are bounded (periods between 2 and 500).
439. Source entitlements are enforced.
440. Derived-data licensing is respected.
441. Restricted filter counts do not leak values.
442. Cache isolation is enforced.
443. No arbitrary SQL or user code execution.
444. No executable user formulas.
445. No arbitrary provider URLs.
446. Provider secrets remain server-side.
447. No trading or financial order submission.
448. No portfolio mutation.
449. No broker execution.
450. No autonomous screening agents.
451. Exactly 0 LLM calls during screener operation.

### Roadmap Boundaries
452. Stage 97 owns Saved Screens.
453. Stage 97 owns advanced sorting and ranking leaderboards.
454. Stage 97 owns CSV/Excel exports.
455. Stage 98 owns natural-language translation hooks.
456. Stage 143 owns Backtesting.
457. Stage 144 owns Paper Trading.
458. Stage 145 owns Broker Sandbox.
459. Stage 96 passes fundamental correctness tests.
460. Stage 96 passes technical indicator numerical tests.
461. Stage 96 passes look-ahead and warm-up tests.
462. Stage 96 passes multi-factor combination tests.
463. Stage 96 passes Stage 94-95 regression tests (54 backend tests passed, 16 frontend tests passed).
464. Documentation matches actual code.
465. Stage 97 is the next canonical stage.

## Stage 97: Saved Screeners, Sorting, Ranking and Exports

### Product and Scope
466. Stage 97 owns Saved Screens, Multi-Column Sorting, Quantitative Factor Ranking and Professional Result Exports.
467. Stage 94 remains the canonical Screener Engine.
468. Stage 95 remains the canonical Visual Filter Builder.
469. Stage 96 remains the canonical Factor Registry.
470. Stage 97 remains strictly within `/screeners`.
471. No new global navigation module is created.
472. No duplicate Screener execution engine is introduced.
473. No general Saved module (Stage 119) is prematurely implemented.
474. Stage 98 natural-language translation hooks remain deferred.

### Saved Screens
475. Saved Screens are user-owned (`owner_user_id`) with strict tenant isolation.
476. Screen identity is a stable UUID primary key.
477. Screen names are display labels and not primary keys.
478. Query specifications are canonical and fully serialized.
479. Query schema versions are stored (`1.0.0`).
480. Filter Registry and Universe Registry compatibility is maintained.
481. Universe selection, exchange, and country scopes are persisted.
482. Filter parameters and conditions are persisted without loss.
483. Financial reporting policies (`period_policy`) are preserved.
484. Technical factor parameters (`rsi_14`, `sma_50`, etc.) are preserved.
485. Display column configurations are preserved.
486. Sort specifications are preserved.
487. Ranking specifications are preserved.
488. A saved query does not freeze matching securities; reruns evaluate current market data.
489. Saved queries are validated before execution.
490. Source entitlements are rechecked on open and run.
491. Duplication creates a new user-owned entity with a new UUID.
492. Deletion is authorized and applies soft-deletion.
493. Concurrent updates use optimistic revision checks (`expected_revision`).
494. Revision conflicts return HTTP 409 and do not silently overwrite changes.
495. Unsupported legacy filters are not silently dropped.
496. Query schema migrations are versioned and idempotent.

### Sorting
497. Sorting evaluates globally server-side across all matching securities before pagination.
498. Sort fields are strictly allowlisted from sortable columns.
499. Multi-column order is explicit with up to 5 sort keys.
500. Null ordering is explicit (`nulls_last` / `nulls_first`).
501. Stable unique tie-breakers `(instrument_entity_id, listing_id)` guarantee deterministic pagination.
502. Stable pagination prevents duplicate or missing rows across pages.
503. Sorting on restricted fields without source entitlement is blocked.
504. Currency compatibility is validated.
505. Financial period compatibility is enforced.
506. Technical factor parameters participate in sort field identity.
507. Sorting is never applied solely to the currently visible page.
508. Mutable market data changes are qualified with evaluation timestamps.

### Ranking
509. Ranking is distinct from sorting; it assigns relative ordinal positions or standardized scores.
510. Ranking evaluates within an explicit eligible cohort (`FILTER_MATCHED_SECURITIES` or `ALL_ELIGIBLE_UNIVERSE`).
511. Factor direction is explicit (`HIGHER_VALUE_FIRST` or `LOWER_VALUE_FIRST`).
512. Ties use documented policies (`DENSE_RANK` or `COMPETITION_RANK`).
513. Missing factor observations are excluded; zero imputation is strictly prohibited.
514. Sample size $N$, eligible count, and excluded count are disclosed.
515. Cross-sectional percentiles are bounded between $0.0\%$ and $100.0\%$.
516. Standardized Z-scores use sample statistics ($z = (x - \mu)/\sigma$).
517. Zero-variance cohorts ($\sigma = 0$) map deterministically to neutral $z = 0.0$.
518. Small samples display appropriate warnings.
519. Composite factor weights are explicit and normalized ($\sum w_j = 1.0$).
520. Weight validation rejects negative or non-finite weights.
521. Strict complete-case missingness excludes securities lacking any composite factor.
522. Financial period compatibility is enforced for fundamental rankings.
523. Technical bar eligibility is enforced for indicator rankings.
524. Ranking source vintages and calculation versions are preserved.
525. Ranking methodology versions are recorded (`1.0.0`).
526. Factor scores do not constitute investment recommendations.
527. No fabricated expected returns or alpha claims are generated.
528. Backtesting and trading strategy execution remain deferred.

### Exports
529. Export scope is explicit (`CURRENT_PAGE` or `ALL_MATCHING_RESULTS`).
530. CSV exports follow RFC 4180 with UTF-8 encoding.
531. XLSX exports generate professional multi-sheet workbooks (`Results`, `Methodology`, `Sources`, `Configuration`).
532. All-results export does not silently become a single-page export.
533. Exports bind to validated screener evaluations.
534. Source watermarks and evaluation timestamps are preserved.
535. Ranking exports preserve ranking methodology and factor weights.
536. Column identities and units are preserved.
537. Missing data is represented as blank/null, not zero.
538. Financial decimal precision is preserved.
539. Ticker symbols and leading-zero identifiers are preserved as text.
540. CSV formula injection is mitigated: untrusted text starting with `=, +, -, @, \t, \r` is prefixed with `'`.
541. Valid numeric values (including negative numbers) remain uncorrupted numeric cells.
542. Export metadata manifest is inspectable.
543. Export source licensing and field-level permissions are enforced.
544. Large exports (>1,000 rows up to 50,000 rows) use background jobs.
545. Export job statuses are durable (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `EXPIRED`).
546. Job creation supports client idempotency keys.
547. Job cancellation, worker crash recovery, and partial artifact cleanup are implemented.
548. Export files are stored in private protected storage.
549. Downloads require user authorization with 24-hour time-limited retention.
550. Export quotas (50,000 rows, max 2 concurrent jobs, max 5 pending) are enforced.

### Verification & Quality
551. Stage 97 passes saved-query persistence tests.
552. Stage 97 passes RLS ownership tests.
553. Stage 97 passes optimistic concurrency tests.
554. Stage 97 passes multi-column sorting correctness tests.
555. Stage 97 passes ranking mathematics tests (dense, competition, percentiles, Z-scores).
556. Stage 97 passes export correctness tests (CSV and openpyxl XLSX).
557. Stage 97 passes spreadsheet formula injection protection tests.
558. Stage 97 passes export job lifecycle and cancellation tests.
559. Stage 97 passes Stage 94-96 regression tests (66 backend pytest tests, 21 frontend vitest tests).
560. Stage 98 is the next canonical roadmap stage.

## Stage 98: Natural-Language Financial Screener Translation Engine

### Translation Engine & Architecture
561. Deterministic translation is the primary implementation: zero external LLM calls or API keys are required for normal operational parsing and validation.
562. Natural language query processing is strictly an input method; the Stage 94–97 screener schema and execution engine remain the sole authority for query execution.
563. Translation outputs a validated proposal (`NLTranslationProposalDTO`) containing structured conditions, universe selection, sorting criteria, explanation, and ambiguity resolutions.
564. Financial lexicon grounds across all 70 canonical catalog filters, covering fundamentals, valuation ratios, technical indicators, and classifications.
565. Numeric parsing resolves Indian numbering systems (`lakh`, `lakhs`, `crore`, `crores`, `lakh crore`) and international abbreviations (`k`, `m`, `million`, `bn`, `billion`, `tr`, `trillion`).
566. Currency units (`INR`, `USD`, `EUR`, `GBP`, `₹`, `$`, `€`, `£`) are resolved to ISO currency codes and bound to monetary thresholds.
567. Range expressions (`between X and Y`) are parsed prior to clause splitting to avoid breaking coordinate pairs.
568. Percentages and basis points are normalized deterministically (`15%` -> `15.0`, `100 bps` -> `1.0%`).

### Ambiguity Resolution & Guardrails
569. Ambiguity is treated as a first-class citizen: subjective terms (`cheap`, `profitable`, `oversold`, `large cap`) trigger structured clarification questions with selectable presets rather than silent guesses.
570. Clarification workflows (`/screeners/nl/clarify`) deterministically merge user selections with existing proposals.
571. Unsupported requirements are explicitly reported with status `UNSUPPORTED` and clear user explanations; unsupported filters are never silently dropped or substituted.
572. No metrics, indicators, or security match counts are fabricated.
573. Prompt-injection and instruction-override detection protects the translation pipeline against adversarial inputs and jailbreak attempts.
574. Query modification diffing provides granular transparency into added, modified, retained, and removed filters when editing existing screens via natural language.

### Verification & Hand-off
575. Stage 98 passes comprehensive backend tests (36 test cases in test_screener_nl_translation.py covering parsing, currencies, magnitudes, technicals, single-factor queries, boundary semantics, ambiguities, clarifications, draft modifications, security injections, and all 4 router endpoints).
576. Stage 98 passes full regression testing across Stages 94–98 (102 backend tests in apps/api passing cleanly, 0 ruff errors).
577. Stage 98 passes comprehensive frontend tests (27 unit and integration tests in apps/web covering types, requests, proposals, diffing, and condition conversion; tsc --noEmit passes with 0 errors; pnpm build passes with 0 errors).
578. Stage 98 completes the 5-stage Screener series (Stages 94, 95, 96, 97, 98).
579. Stage 99 (News module) is the next canonical roadmap stage; no Stage 99 implementation is started during Stage 98.

## Stage 99: Financial News Platform Foundation

### Domain Identity & Provenance
580. News module foundation operates at primary top-level route `/news`; all 20 canonical routes remain intact.
581. Canonical `NewsArticle` is distinct from Stage 20/36 `NewsEvent`; an article is an immutable media record, while an event is a real-world occurrence that may be reported by multiple articles.
582. Publisher identity (`NewsPublisher`) is strictly decoupled from distributor/provider identity (`NewsSource`); wire services and syndicating outlets maintain separate attribution.
583. Article identifier is a deterministic SHA-256 hash (`sha256(f"{source_provider_id}:{provider_article_id}")[:24]`); repeated ingestion is strictly idempotent.
584. Five distinct timestamp semantics are preserved: `published_at`, `source_updated_at`, `first_seen_at`, `ingested_at`, and `last_fetched_at`. Ingestion timestamps are never substituted for publication timestamps.
585. Canonical URL normalization strips tracking parameters (`utm_*`, `fbclid`, `gclid`, `ref`, `source`, `campaign`, `trk`) and fragments while preserving destination semantics.
586. SSRF defense rejects loopbacks, RFC 1918 private ranges, link-local addresses, AWS metadata endpoints (`169.254.169.254`), and dangerous schemes (`javascript:`, `data:`, `file:`, `ftp:`).
587. HTML sanitization strips `<script>`, `<style>`, and `<iframe>` blocks before removing residual tags, preventing script execution and formatting distortion.

### Entity Linking & Deduplication
588. Articles are linked to canonical Company Entities (Stage 18) and Financial Instrument Entities (Stage 17) via explicit mentions (`NewsEntityMention`).
589. Ticker collision guardrails reject short common English words (e.g. `IT`, `ON`, `CAN`, `ARE`, `FOR`, `ALL`) unless explicitly formatted as cashtags (`$TICKER`).
590. ADRs and multiple share classes (`GOOGL` vs `GOOG`, `INFY` ADR on NYSE vs `INFY.NSE`) are disambiguated by exchange and verified source identifiers.
591. Entity mention never implies market impact or investment recommendation; sentiment scores and predictive return percentages are strictly prohibited in Stage 99.
592. Deduplication identifies exact source duplicates while preserving separate records for independent publisher reports on the same event.
593. Syndication preserves original wire publisher attribution (`is_syndicated=True`, `original_wire_publisher_id="reuters"`).
594. Article corrections, revisions, and retractions are preserved in an immutable audit trail (`NewsArticleRevision`); withdrawn articles are marked `WITHDRAWN` and full excerpts suppressed.
595. Full-text scraping and paywall circumvention are prohibited; ATLAS stores and displays only source-licensed headlines and excerpts.

### Feeds, Caching & Workspace
596. News feeds use keyset cursor pagination (`published_at DESC, article_id DESC`) with base64 cursors; pages are strictly disjoint with zero skipped or duplicate records.
597. In-memory feed cache uses MD5 query hashing, TTL bounds, and immediate cache invalidation upon article ingestion or status revision.
598. Read-only news access causes zero mutations across securities, companies, fundamentals, economic indicators, portfolios, watchlists, or broker accounts. News ingestion never triggers trading or order routing.
599. The frontend delivers an institutional Bloomberg-style financial news workspace with high-density feed tables, split article previews, category tabs, source/publisher/geography filters, entity navigation chips, latency class indicators, keyboard navigation, and full accessibility.
600. Stage 99 establishes the foundational News data layer; advanced intelligence, AI summarization, market impact scoring, and automated event clustering are deferred to Stages 100–103. Stage 100 is the next canonical roadmap stage.

## Stage 100: Financial News Discovery, Search and Timeline System

### Scope, Roadmaps & Core Directives
601. Stage 100 builds the institutional-grade News Discovery, Search, and Timeline system on top of Stage 99's canonical news infrastructure at primary route `/news`.
602. The canonical frozen roadmap confirms Stages 99–103 belong to the News sequence; Stage 100 owns the discovery, multi-dimensional search, faceted counts, and chronological timelines layer.
603. Stage 100 strictly reuses Stage 99's canonical `NewsArticle` data and `NewsRepository` as the single authoritative read model; no second master news store or shadow database is introduced.
604. Advanced AI summarization, LLM article synthesis, sentiment classification, predictive market impact scores, automated news-driven trading, and autonomous monitoring agents remain strictly deferred to later stages.
605. All 20 canonical top-level routes (`/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, etc.) remain intact and untouched.

### Discovery Modes & Taxonomy
606. News Discovery operates across seven canonical modes: `ALL`, `MARKETS`, `COMPANIES`, `SECURITIES`, `TOPICS`, `INDUSTRIES`, and `WATCHLIST`.
607. Canonical Topic Taxonomy establishes 14 controlled topics (`EARNINGS_RELEASES`, `MERGERS_ACQUISITIONS`, `DIVIDENDS_DISTRIBUTIONS`, `SHARE_BUYBACKS`, `CAPITAL_RAISING`, `INTEREST_RATES_MONETARY_POLICY`, `INFLATION_PRICES`, `EMPLOYMENT_LABOR`, `FOREIGN_EXCHANGE_CURRENCIES`, `COMMODITIES_ENERGY`, `FINANCIAL_REGULATION_COMPLIANCE`, `CORPORATE_GOVERNANCE_BOARD`, `TECHNOLOGY_AI_INNOVATION`, `SUPPLY_CHAIN_LOGISTICS`).
608. Topic classification is deterministic, rule-backed, and grounded in article categories and source-reported metadata; arbitrary keyword hallucination is prohibited.
609. Industry sector associations use canonical GICS/ICB classification (`NewsIndustrySector`); company-derived sector associations are cleanly qualified and distinguishable from direct article industry tags.
610. Watchlist-scoped news aggregates eligible articles matching instruments in the user's authenticated watchlists; zero watchlist mutations or background alerts are created.

### Search, Relevance & Highlighting
611. Advanced search parses quoted exact phrases (`"..."`) and multi-token queries over source-licensed headlines and permitted excerpts; unauthorized full-text indexing is prohibited.
612. Search relevance scoring uses an explainable, deterministic term-weighting methodology (+100 headline exact match, +40 excerpt exact match, +50 quoted phrase in headline, +20 quoted phrase in excerpt, +15 token in headline, +5 token in excerpt, +30 all-token overlap bonus, +10 topic alignment).
613. Text search relevance is strictly decoupled from financial materiality; relevance scores are never represented to users as market impact scores or probability of price movement.
614. Search inputs are treated as untrusted text, sanitized against SQL injection, search DSL abuse, and XSS; search highlights use text escaping to prevent arbitrary script execution.
615. Search suggestions provide prefix autocomplete for companies, tickers, topics, publishers, and categories from verified system metadata with zero LLM inference cost.

### Faceted Search & Aggregation
616. Faceted search aggregates discrete counts for Sources, Publishers, Categories, Topics, Countries, and Article Types under active filters.
617. Facet counts strictly respect source licensing and user entitlement scopes; restricted articles are never leaked through aggregate counts.
618. Deduplication semantics ensure facet counts represent discrete canonical articles rather than raw fetch attempts or syndicated duplicates.

### Chronological Timelines & Timezones
619. News timelines group genuine canonical articles chronologically by `DAY`, `WEEK`, or `MONTH` intervals.
620. Timeline grouping explicitly converts publication timestamps to the requested IANA timezone (e.g. `UTC`, `America/New_York`, `Asia/Kolkata`, `Asia/Tokyo`) using timezone-aware arithmetic.
621. Publication time is strictly separated from first-seen and ingestion timestamps; missing or date-only timestamps are preserved without artificial precision fabrication.
622. Empty timeline periods remain honestly empty; no synthetic events or price-causality arrows are invented.

### Quality Gates, Performance & Hand-off
623. Keyset cursor pagination (`published_at DESC, article_id DESC` or `score DESC, published_at DESC, article_id DESC`) provides stable, disjoint page navigation.
624. Ordinary news discovery causes zero mutations across securities, companies, fundamentals, economic indicators, portfolios, watchlists, or broker accounts.
625. Stage 100 passes all automated test suites (58 backend tests across Stage 99 and 100 passing cleanly with 0 ruff errors; 40 frontend tests passing cleanly; TypeScript compile passing with 0 errors; Next.js production build passing with 0 errors). Stage 101 is the next canonical stage.

## Stage 101: Financial News Story Intelligence and Event Classification System

### Scope, Roadmaps & Core Directives
626. Stage 101 builds the institutional-grade Financial News Story Intelligence and Event Classification System on top of Stage 99 (Foundation) and Stage 100 (Discovery, Search & Timelines) at primary route `/news`.
627. The canonical frozen 150-stage roadmap confirms Stages 99–103 belong to the News sequence; Stage 101 owns canonical Story Threads (`story-*`) and Financial Event records (`fev-*`).
628. Stage 101 maintains strict conceptual separation across Article (source-specific published text), Story Thread (group of related coverage covering the same developing narrative), and Financial Event (evidence-backed assertion about an identifiable corporate, economic, or market occurrence).
629. Advanced generative research synthesis, multi-article narrative briefs, sentiment trading signals, predicted share-price impact, abnormal return forecasts, and autonomous research agents remain strictly deferred to later stages.
630. All 20 canonical top-level routes (`/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, etc.) remain intact and untouched.

### Story Threads & Conservative Clustering
631. Story Threads possess deterministic, stable identifiers (`story-<sha256(lead_article_id)[:16]>`) independent of variable headlines.
632. Candidate retrieval uses blocking on shared canonical company/instrument entities, verified event type, and temporal proximity windows (e.g. 7 days for earnings, 30 days for M&A).
633. Entity overlap alone is strictly insufficient to cluster articles; articles must share specific event context or narrative identity to prevent false merges of unrelated corporate news.
634. Syndicated wire republications (e.g., PR Newswire distributed to multiple outlets) are distinguished from independent newsroom reporting; `independent_publisher_count` tracks genuine independent publisher organizations rather than raw republished copies.
635. Administrative story merge and split operations preserve full audit trails, recording previous story IDs, timestamp, and administrative reason; split articles retain their verified relationships.
636. Story titles are source-grounded display labels derived from the lead representative article; synthetic, hallucinated narrative summaries are strictly prohibited.
637. Story operational lifecycle tracks `ACTIVE`, `QUIET`, `ARCHIVED`, `MERGED`, and `WITHDRAWN_FROM_DISPLAY` without confusing operational tracking with real-world event completion.

### Financial Event Taxonomy & Classification
638. Canonical Event Taxonomy establishes 20 versioned event types (`EARNINGS_RELEASE`, `EARNINGS_GUIDANCE`, `DIVIDEND_DECLARATION`, `SHARE_BUYBACK_AUTHORIZATION`, `MERGER_ACQUISITION_PROPOSAL`, `MERGER_ACQUISITION_AGREEMENT`, `MERGER_ACQUISITION_COMPLETION`, `MERGER_ACQUISITION_TERMINATION`, `EQUITY_FINANCING_ANNOUNCEMENT`, `DEBT_FINANCING_ANNOUNCEMENT`, `EXECUTIVE_APPOINTMENT`, `EXECUTIVE_DEPARTURE`, `REGULATORY_INVESTIGATION_ANNOUNCEMENT`, `REGULATORY_ENFORCEMENT_ACTION`, `LITIGATION_FILING`, `BANKRUPTCY_RESTRUCTURING_FILING`, `PRODUCT_LAUNCH_ANNOUNCEMENT`, `FACILITY_EXPANSION_ANNOUNCEMENT`, `CENTRAL_BANK_POLICY_DECISION`, `ECONOMIC_RELEASE_ANNOUNCEMENT`).
639. Event assertion status (`OFFICIALLY_REPORTED`, `THIRD_PARTY_REPORTED`, `ALLEGED`, `RUMORED`, `DENIED`, `DISPUTED`, `CORRECTED`, `UNRESOLVED`) is strictly separated from transaction lifecycle status (`PROPOSED`, `ANNOUNCED`, `PENDING`, `APPROVED`, `COMPLETED`, `CANCELLED`, `WITHDRAWN`, `UNKNOWN`).
640. Rumors, anonymous sources, and preliminary talks are never converted into confirmed announcements; an acquisition rumor remains `RUMORED` / `PROPOSED`.
641. Regulatory investigations are never classified as findings or proof of wrongdoing; an investigation remains `ANNOUNCED` or `PENDING` with assertion `OFFICIALLY_REPORTED` or `THIRD_PARTY_REPORTED`.
642. Event participants use canonical Entity IDs with verified roles (`PRIMARY_SUBJECT`, `ACQUIRER`, `TARGET`, `REGULATOR`, `ISSUER`, `LENDER`, `INVESTOR`, `UNDERWRITER`, `EXECUTIVE`, `COUNTERPARTY`).
643. Source-evidenced monetary amounts (`EventAmount`) preserve exact numeric values, currencies, units, and approximation flags (`EXACT`, `APPROXIMATE`, `RANGE_MIN`, `RANGE_MAX`, `ESTIMATED`); unverified valuations are never guessed.
644. Currency conversion is never performed implicitly without verified, time-aligned FX rates; original reported currencies and Indian numbering scales (`crore`, `lakh`) are preserved.

### Temporal Precision & Evidence Lineage
645. Multiple temporal dimensions are preserved without conflation: `event_date` (when the underlying event allegedly occurred), `announcement_time` (when officially disclosed), `published_at` (when the reporting article was published), and `first_seen_at` (when ATLAS ingested the evidence).
646. Point-in-time integrity is strictly enforced: historical-as-known-at queries do not leak future revisions, subsequent corrections, or post-dated announcements into earlier timelines.
647. Every financial event attribute is grounded in verifiable structured evidence (`NewsEventEvidence`) linking source provider, publisher, revision ID, and permitted quotation excerpts.
648. Article corrections or retractions propagate automatically: if a source article is withdrawn, its evidence link is revoked, and the event lifecycle status transitions to `WITHDRAWN` or is re-evaluated.
649. Event revisions maintain an immutable audit history (`NewsEventRevision`) recording previous statuses, new statuses, timestamps, and reason for change.

### API, Ingestion & User Experience
650. REST API provides dedicated, typed endpoints under `/api/v1/news`: `/stories`, `/stories/{id}`, `/stories/{id}/articles`, `/stories/{id}/events`, `/events`, `/events/{id}`, `/events/{id}/evidence`, `/events/types`, and `/entities/{id}/events`.
651. Ingestion-time classification hooks process articles idempotently (`sha256(article_id + extraction_version)`); duplicate ingestion jobs cause zero duplicate events or stories.
652. Story and event feeds use keyset pagination and cache invalidation upon article ingestion, story merge/split, or event revision.
653. The frontend delivers four integrated view modes: `[Headlines]` (Stage 99), `[Story Threads]` (Stage 101), `[Financial Events]` (Stage 101), and `[Timelines]` (Stage 100), sharing canonical entity filters and search state.
654. The UI adheres strictly to ATLAS institutional design tokens: zero purple gradients, zero emoji icons, zero fabricated confidence percentages, and full dark/light theme support.
655. Stage 101 completes successfully with 74 passing backend tests (test_news_story_intelligence_v1.py, test_news_discovery_v1.py, test_news_v1.py), 0 ruff errors, 46 passing web unit tests, 0 TypeScript errors (`tsc --noEmit`), and a successful Next.js production build. Stage 102 is the next canonical roadmap stage.

## Stage 102: Financial News Sentiment, Entity Relevance, and Market Reaction Analytics System

### Scope, Roadmaps & Core Directives
656. Stage 102 builds the institutional-grade Financial News Sentiment, Entity Relevance, and Market Reaction Analytics System inside the News module at primary route `/news`.
657. The authoritative 150-stage roadmap confirms Stages 99–103 belong to the News sequence; Stage 102 extends verified articles, story threads, and financial events into target-aware financial language analytics.
658. Sentiment is strictly analytical and descriptive: zero automated investment recommendations (Buy/Sell), zero predicted share-price changes, zero price-impact claims, and zero news-driven trading orders.
659. Strict noncausal attribution: market price movements are descriptive before/after measurements over defined exchange windows; correlation does not imply causation and news is never asserted to have caused price movements without validated causal event studies.
660. All 20 canonical top-level routes (`/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, etc.) remain intact and untouched; news sentiment integrates cleanly into `/news`.

### Sentiment Taxonomy & Target-Aware Semantics
661. Versioned 6-label sentiment taxonomy establishes `POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`, `INSUFFICIENT_EVIDENCE`, and `NOT_APPLICABLE`.
662. Neutral reporting of descriptive facts is strictly separated from Insufficient Evidence (e.g. short/missing text or ambiguous tone).
663. Financial aspect classification defines 14 versioned aspects: `EARNINGS_PERFORMANCE`, `EARNINGS_GUIDANCE`, `REVENUE_GROWTH`, `PROFITABILITY`, `CASH_FLOW`, `BALANCE_SHEET`, `DEBT_FINANCING`, `CORPORATE_GOVERNANCE`, `REGULATORY_EXPOSURE`, `PRODUCT_DEVELOPMENT`, `OPERATIONAL_PERFORMANCE`, `MANAGEMENT`, `CORPORATE_TRANSACTION`, and `GENERAL`.
664. Target-specific polarity isolation: multi-entity articles assign distinct, independent sentiment annotations per participating company (e.g. Company A winning a deal from Company B).

### Entity Relevance & Conservative Materiality
665. Conservative entity relevance stratification establishes `PRIMARY_SUBJECT` (1.00), `DIRECT_PARTICIPANT` (0.75), `VERIFIED_MENTION` (0.40), `VERIFIED_RELATED_ENTITY` (0.35), `CONTEXTUAL_MARKET_REFERENCE` (0.15), and `INSUFFICIENT_EVIDENCE` (0.00).
666. Zero invented materiality claims: relevance indicates textual association, never proven financial materiality, earnings impact, or legal determination.
667. Strict evidence grounding: every annotation cites verbatim source spans from headline or licensed excerpt with rationale code and evidence scope (`HEADLINE`, `LICENSED_EXCERPT`, `LICENSED_BODY`, `STRUCTURED_FILING`).
668. Source copyright and licensing protection: licensed excerpts and headlines only; unlicensed text redistribution or unauthorized third-party LLM transmission is strictly blocked.
669. Article revision binding: annotations link to exact `article_revision_id`; source corrections or retractions invalidate obsolete annotations.

### Aggregation, Syndication & Temporal Integrity
670. Syndication-aware aggregation: syndicated wire copies (e.g. PR Newswire distributed to 10 outlets) count as 1 independent newsroom voice, not 10 independent confirmations.
671. Net Sentiment metric: $[-1.0, +1.0]$ defined as $(N_{\text{pos}} - N_{\text{neg}}) / N_{\text{eligible}}$ with explicit sample size $N$, unique story count, and coverage completeness disclosure.
672. Chronological sentiment trajectory: publication timestamp-anchored grouping (`DAY`, `WEEK`) with zero look-ahead hindsight bias; missing days remain honestly empty.
673. Story-level and Event-level sentiment profiles: track polarity distributions across member articles and evidence without altering event assertion status.

### Descriptive Market Reaction Context
674. Descriptive market reaction context: supports exchange session alignment (`PREV_CLOSE_TO_NEXT_CLOSE`, `PUB_BAR_TO_NEXT_BAR`, etc.) with calendar, holiday, and weekend handling (Saturday/Sunday maps start to Friday close and end to Monday close).
675. Zero price fabrication: missing or unverified historical prices return typed unavailable states rather than interpolated estimates.
676. Benchmark context: optional relative return vs. benchmark (e.g. SPY) is descriptive and never claimed as alpha or abnormal return.
677. Negation and hedging detection: corporate denials (e.g. "Firm denies probe allegations") are neutralized to NEUTRAL with explicit explanation.

### Evaluation, Infrastructure & Quality Gates
678. Golden benchmark evaluation harness: built-in benchmark fixture evaluates 7 diverse scenarios, measuring precision, recall, and Macro-F1 = 1.0 across classes.
679. Typed REST APIs: dedicated endpoints under `/api/v1/news`: `/articles/{id}/sentiment`, `/entities/{id}/sentiment`, `/entities/{id}/sentiment/timeline`, `/stories/{id}/sentiment`, `/events/{id}/sentiment`, `/entities/{id}/relevance`, `/articles/{id}/relevance`, `/analytics/methodologies`, `/analytics/market-reaction`, and `/analytics/evaluation`.
680. Idempotent processing and cache invalidation: cache keys incorporate entity, window, and revision watermark.
681. Frontend News Workspace integration: adds `[Sentiment & Reactions]` tab seamlessly alongside `[Headlines]`, `[Story Threads]`, `[Financial Events]`, and `[Timelines]`.
682. Institutional UI design: zero purple gradients, zero emoji icons, zero fake confidence percentages, tabular numerals, accessible keyboard/screen-reader navigation.
683. Security and privacy controls: parameterized SQL, input sanitization, SSRF protection on URLs, strict RBAC entitlements.
684. Comprehensive automated verification: 94 passing backend tests (test_news_sentiment_analytics_v1.py, test_news_story_intelligence_v1.py, test_news_discovery_v1.py, test_news_v1.py), 0 ruff errors, 55 passing web unit tests, 0 TypeScript errors (`tsc --noEmit`), and clean Next.js production build.
685. Stage 102 is complete; Stage 103 is the next canonical roadmap stage.

## Stage 103: Personalized Financial News Monitoring, Custom Feeds, Rule-Based Alerts, and News Digests

### Monitoring Rules Architecture & Condition Typing
686. User-Owned Monitoring Rules: Rules are persistent, isolated to individual authenticated principals (`owner_user_id`), and enforce maximum quota constraints (50 rules per user).
687. Typed Rule Dimensions: Rules support typed criteria: `COMPANY` (tickers/entities), `INSTRUMENT` (asset classes), `WATCHLIST` (Stage 39 watchlist binding), `TOPIC` (Stage 100 discovery taxonomy), `PUBLISHER` (wire sources), `EVENT_TYPE` (Stage 101 event taxonomy), and `COMPOSITE` (multi-criteria conjunction).
688. Optimistic Concurrency Revisioning: Every update increments an integer `rule_revision`, preventing race conditions across multiple client tabs.
689. Target-Aware Sentiment Condition Integration: Optional rule condition binds to Stage 102 polarity isolation (`POSITIVE`, `NEGATIVE`, `NEUTRAL`, `MIXED`), minimum confidence score, and financial aspect (`EARNINGS_PERFORMANCE`, etc.).
690. Bounded Historical Rule Preview: Rule creation modal includes historical validation preview against bounded recent articles and events to estimate match frequency without retroactive alert floods.
691. Non-Retroactive Alert Guarantee: Historical rule preview and rule activation strictly evaluate forward-going events; retroactive alert flood dispatch is prohibited by design.

### Evaluation Engine, Deduplication & Suppression
692. Pure Deterministic Evaluation: The `NewsRuleMatcher` evaluates rules as pure functions of ingested article metadata, resolved entities, and verified events.
693. Evidence-Grounded Alert Records: Every alert match stores explicit human-readable condition evidence spans in `matched_conditions`.
694. Syndication-Aware Deduplication: Identical articles syndicated across multiple wires collapse under a unified SHA-256 deduplication key, recording duplicates as `SUPPRESSED_SYNDICATION`.
695. Rule Cooldown Policy: Rules enforce configurable cooldown periods (default: 30m, 5–1440m); matches within active cooldown are recorded as `SUPPRESSED_COOLDOWN`.
696. Quiet-Hours Suppression: Configurable UTC quiet hours suppress instant notification dispatch during off-hours (`SUPPRESSED_QUIET_HOURS`), holding items for scheduled morning digests.
697. Alert Severity Stratification: Explicit priority levels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) control routing channels and UI visual treatment.
698. Evaluation Latency Budget: The rule-matching engine evaluates rules within sub-5ms latency budgets per ingested item, tracked via real-time telemetry.

### Custom Feeds & Canonical Discovery Alignment
699. Persistent Custom Discovery Feeds: Users can save discovery search criteria (`q`, `category`, `topics`, `publishers`, `entities`) as persistent `CustomNewsFeed` objects (quota: 25 feeds/user).
700. Query Re-Compilation: Custom feeds compile dynamically into canonical Stage 100 `NewsFeedQuery` discovery executions, preventing divergent query syntax.
701. Custom Feed Alert Integration: Custom feeds can be flagged as `is_alert_enabled`, automatically evaluating inbound articles for new additions.

### Scheduled Digests & Durable Notification Integration
702. Scheduled News Digest Subscriptions: Users can configure `DAILY` or `WEEKLY` digests with local timezone and delivery schedule time.
703. Multi-Story Grouping & Topic Balancing: Digests group top stories by importance, balancing corporate actions, macro trends, and verified event highlights.
704. Idempotent Digest Execution: Every digest execution run generates a deterministic idempotency token (`idemp-digest-{digest_id}-{timestamp}`), guaranteeing exactly-once dispatch.
705. Stage 49 Durable Notification Integration: Real-time alert dispatch directly invokes `NotificationService.create_notification` via canonical action routes `/news`.
706. Email & Digest Channels: Multi-channel delivery supports in-app, durable notifications, email dispatch markers, and scheduled digest summaries.

### Telemetry, Health & Observability
707. Pipeline Telemetry Service: Real-time health endpoint `/api/v1/news/monitoring/status` reports active rules count, active custom feeds, active digests, 24h alert volume, 24h deduplicated volume, evaluation latency, and watermark timestamp.
708. Engine Version Pinning: The monitoring engine explicitly publishes its version (`v103.0-institutional`) in all telemetry payloads.

### User Experience & Institutional Design
709. Frontend News Workspace Sub-Tabs: The `/news` workspace integrates `[Monitoring & Alerts]` view mode, rendering sub-tabs for Rules, Custom Feeds, Alert History, Digests, and Health.
710. Real-Time Live Validation: The Rule Builder Modal validates rule syntax and detects broad/unbounded filters in real-time as the user types.
711. Interactive One-Click Feed Execution: The Custom Feeds panel allows one-click execution and browsing of matching articles in real-time.
712. Manual Digest Triggering: Users can test and trigger digest generation on-demand with instant run history logging.

### Security, Safety & Roadmap Boundaries
713. Strict Non-Trading Boundary: Zero automated order placement, zero buy/sell signals, zero portfolio mutations. The News module is an analytical research surface.
714. Comprehensive Automated Verification: 108 backend tests (Stages 99–103), 66 frontend unit tests, 0 ruff errors, 0 tsc errors, and clean Next.js production build.
715. Stage 103 concludes the 5-stage Financial News Intelligence sequence (Stages 99–103); Stage 104 begins the Research module sequence.

## Stage 104: Institutional-Grade Financial Research Platform Foundation

### Canonical Research Entities & Investigation Lifecycle
716. Canonical Research Investigations: Implemented `ResearchInvestigation` as the foundational research entity with typed investigation scopes (`COMPANY`, `INSTRUMENT`, `INDUSTRY`, `MACROECONOMIC`, `MARKET`, `FINANCIAL_EVENT`, `GENERAL_FINANCIAL`).
717. Explicit Lifecycle State Machine: Enforced strict lifecycle transitions across `DRAFT`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, and `ARCHIVED`, prohibiting modifications to archived investigations without explicit re-activation.
718. Optimistic Concurrency & Revision Control: Every mutable research entity (`ResearchInvestigation`, `ResearchNote`) tracks monotonically incrementing integer `revision` counters; updates must supply the matching revision or be rejected with a 409 Conflict.
719. Research Questions with Non-Automatic Truth: Formalized `ResearchQuestion` entity with explicit priority, status tracking (`UNANSWERED`, `IN_PROGRESS`, `ANSWERED`, `DEFERRED`, `ABANDONED`), and explicit analyst validation requirements.
720. Research Hypotheses Evaluation Framework: Hypotheses maintain explicit status (`UNTESTED`, `SUPPORTED`, `REFUTED`, `INCONCLUSIVE`, `ABANDONED`) and require tied evidence rather than automated confidence scoring.

### Structured Notes, Point-in-Time Revisions & Claim Categorization
721. Structured Note Typology: Formalized `ResearchNote` across canonical note types (`INVESTMENT_MEMO`, `EARNINGS_DEBRIEF`, `SECTOR_DEEP_DIVE`, `MANAGEMENT_INTERVIEW`, `VALUATION_MODEL_NOTES`, `CATALYST_TRACKER`, `GENERAL_THESIS`, `SCRATCHPAD`) and editorial statuses (`DRAFT`, `IN_REVIEW`, `PUBLISHED`, `DEPRECATED`).
722. Immutable Point-in-Time Note Revisions: Every note edit creates an immutable `ResearchNoteRevision` snapshot preserving author, timestamp, change summary, and markdown content history.
723. Separation of Fact vs. Interpretation in Claims: `ResearchClaim` enforces epistemic categorization: `SOURCE_REPORTED_FACT`, `ANALYST_INTERPRETATION`, `ASSUMPTION`, `HYPOTHESIS`, `ESTIMATE`, and `OPEN_QUESTION`, ensuring subjective projections cannot be conflated with verified facts.
724. Rich-Text & Markdown XSS Sanitization: All note content and analyst inputs undergo strict HTML sanitization via `bleach` allowing only safe formatting tags and whitelisting safe URI schemes.

### Verified Source Libraries, Evidence & Citations
725. Verified Canonical Source References: Integrated SEC Filings (Stage 86), Financial Facts (Stage 82), News Articles & Events (Stages 99–103), and Economic Data (Stages 89–93) into a unified `ResearchSourceReference` entity.
726. Deterministic Source Deduplication: Generated SHA-256 content hashes and canonical URI normalizers across verified financial documents to guarantee idempotency and provenance integrity.
727. Granular Evidence Excerpts: `ResearchEvidence` anchors source references to precise locations (`PAGE_NUMBER`, `PARAGRAPH`, `TABLE_CELL`, `TIME_OFFSET_SECONDS`, `SECTION_HEADING`, `URI_FRAGMENT`) with exact quote verification.
728. Broken & Withdrawn Citation Handling: Implemented citation tracking with `ResearchCitation` statuses (`VERIFIED`, `UNVERIFIED`, `DISPUTED`, `WITHDRAWN`, `UNREACHABLE`), ensuring citations remain visible with clear status flags if an underlying source is retracted or altered.
729. Bilateral Claim-Evidence Linkage: Claims can link multiple evidence items with typed relationships (`SUPPORTS`, `REFUTES`, `NEUTRAL`, `INCONCLUSIVE`), enabling auditable debate and thesis stress-testing.

### Security, Audit Logging & SSRF Mitigation
730. Comprehensive SSRF Mitigation: Enforced strict URL validation for external research links, blocking private, link-local, loopback, loopback-adjacent, cloud metadata endpoints, and non-standard ports.
731. Immutable Research Activity Audit Log: Every research action (create, update, status change, citation link, revision save) logs an append-only `ResearchActivity` record capturing actor, action, diff summary, and timestamp.
732. Role-Based Principal Identity: Standardized user identity extraction via `AuthPrincipal.sub` across all research endpoints, ensuring consistent actor attribution across multi-analyst environments.

### Institutional Analyst Workspace Architecture
733. Unified Route Preservation: Maintained `/research` as one of the 20 immutable top-level ATLAS routes, providing sub-views for Overview, Investigations Directory, 3-Pane Console, Source Library, and Activity Timeline.
734. Three-Pane Analyst Investigation Console: Engineered a responsive 3-pane layout featuring Scope & Question Navigator (Left), Markdown Note Editor & Hypothesis/Claim/Evidence Tabs (Center), and Context/Source Inspector (Right).
735. Keyboard Ergonomics & Auto-Save: Implemented keyboard shortcuts (`Ctrl+S`/`Cmd+S` for note saving, `Ctrl+Enter` for claim submission) and non-destructive conflict alerts.
736. Zero-Trading Scope Enforcement: Strictly isolated research entities from automated order routing, broker APIs, or portfolio mutations; all research notes and claims remain purely analytical assets.
737. Zero Hallucination Guarantee: Prohibited autonomous agent generation of synthetic analyst opinions, fictitious price targets, or falsified citation sources; all assertions require explicit human or verified source backing.
738. Production-Ready Verification: Backed by 18 comprehensive backend pytest integration tests, 5 frontend test suites (71 tests total), 0 ruff lint errors, and 0 TypeScript errors.
739. Roadmap Continuity: Stage 104 establishes the canonical research data model and institutional workspace, forming the robust foundation for downstream research modeling and analytics in Stage 105.

## Stage 105: Institutional-Grade Financial Research Source Discovery, Document Intelligence and Evidence Extraction Platform

### Multi-Facet Research Source Discovery & Search
740. **Multi-Facet Discovery Engine**: Implemented `POST /api/v1/research/sources/search` with facet filters across `entity_ids`, `filing_types`, `source_type_ids`, `publisher_ids`, `reporting_period_range`, `date_from`, `date_to`, and `search_mode` (`KEYWORD`, `EXACT_PHRASE`, `HYBRID`).
741. **Relevance Scoring & Snippet Extraction**: Search hits return normalized relevance scores (0.0 to 1.0) along with contextual matched snippets and matched span anchors.
742. **Canonical Document ID & Accession Number Resolution**: Search seamlessly supports resolution by canonical accession numbers (e.g., `0000320193-24-000106`) and internal source reference IDs (`src-filing-aapl-10k-2024`).
743. **Source Type Registry**: Implemented `GET /api/v1/research/source-types` to provide controlled taxonomic metadata, searchable flags, and rights classifications.

### Document Processing, Outline Structure & In-Document Search
744. **Hierarchical Document Outline Navigation**: Formalized `ResearchDocumentSection` and `ResearchDocumentOutline` (`GET /api/v1/research/documents/{document_id}/outline`), extracting section paths, heading levels, character offsets, and page numbers.
745. **Processing Status & Performance Audit**: `GET /api/v1/research/documents/{document_id}/processing-status` audits document parsing status (`COMPLETED`, `PROCESSING`, `PARTIAL`, `FAILED`, `RESTRICTED`), processor version, and section/table/span counts.
746. **High-Speed In-Document Search**: `POST /api/v1/research/documents/{document_id}/search` enables fast span search with character offset start/end anchors and parent section identifiers.
747. **Granular Section Content Retrieval**: `GET /api/v1/research/documents/{document_id}/sections/{section_id}` delivers isolated section text previews and offset bounds without requiring full document re-transmission.

### Structured Financial Table Extraction & Fact Links
748. **Tabular Matrix Representation**: Tables are structured into matrix columns, row labels, formatted text cells (`cells: string[][]`), and raw numeric representations (`raw_values: (number | null)[][]`).
749. **Unit Scales & Currencies**: All financial statements enforce explicit numeric unit scales (`EXACT`, `THOUSANDS`, `MILLIONS`, `BILLIONS`, `PERCENTAGE`, `PER_SHARE`) and ISO currency codes.
750. **Footnotes & Associated Fact IDs**: Extracted tables preserve footnote disclosures and XBRL fact link associations for complete provenance auditability.

### Evidence Candidate Discovery & One-Click Promotion
751. **Evidence Candidate Extraction**: `POST /api/v1/research/evidence/candidates` dynamically scans documents to extract high-confidence candidate disclosures with exact location references.
752. **Source Location Verification**: `POST /api/v1/research/evidence/resolve-location` verifies evidence location anchors (page, section, table, paragraph) against physical document spans before linking.
753. **One-Click Promotion to Canonical Evidence**: `POST /api/v1/research/evidence/convert-candidate` converts an unverified candidate into an immutable Stage 104 `ResearchEvidence` record tied to an investigation, recording an auditable `ResearchActivity`.

### Multi-Document Comparison & Financial Statement Fact Variance
754. **Two-Document Text Diffing Engine**: `POST /api/v1/research/documents/compare` aligns matching sections between two document revisions and generates standard unified diffs (`diff_unified`) with added/removed line metrics.
755. **Multi-Period Normalized Period Matching**: Normalizes reporting period strings by stripping whitespace and hyphens (e.g. `"FY 2023"` matches `"FY2023"`).
756. **Financial Fact Variance Calculation**: Computes absolute dollar variance ($\Delta$) and percentage delta ($\%\Delta$) across matching financial line items.
757. **Zero-Base Division Protection**: Mathematical variance handles zero or inverted base figures safely, returning `null` with explicit `N/A (Zero Base)` labeling rather than runtime NaN or infinite values.
758. **Restatement Indicators**: Identifies restated financial line items across comparative filing periods.

### Frontend Institutional Workspace Architecture
759. **Three New Professional Workspaces**: Added `Discovery`, `Document Viewer`, and `Comparison` sub-views in `/research`, updating navigation tabs and global state in `useResearchWorkspace`.
760. **Institutional Multi-Facet Search Interface**: `ResearchSourceDiscovery.tsx` renders query bars, facet selects, relevance bars, and direct actions ("View Document", "Compare", "Link to Investigation").
761. **Three-Pane Document Reader**: `ResearchDocumentViewer.tsx` implements Outline/In-Doc Search (Left), Section Reader / Financial Tables (Center), and Source Metadata / Evidence Candidate Inspector (Right).
762. **Side-by-Side Comparison Workspace**: `ResearchDocumentComparison.tsx` presents preset comparative pairs (e.g. Apple FY24 vs FY23 Form 10-K), unified diff syntax coloring, and dense variance tables.

### Security, Safety & Roadmap Boundaries
763. **Strict Non-Trading & Non-Execution Boundary**: Research discovery and document comparison are strictly analytical and evidentiary. Zero order routing, zero broker execution, zero portfolio mutation.
764. **Zero Fabrication Policy**: All filing text, section outlines, and financial statement matrices are grounded in real SEC EDGAR disclosures (e.g., Apple Form 10-K 2023/2024, Microsoft Form 10-K 2024, BLS CPI, Bloomberg FOMC rate report); synthetic opinions and fabricated metrics are prohibited.
765. **Stage 105 Roadmap Completion**: Stage 105 concludes the Source Discovery and Document Intelligence phase of the Research module.

## Stage 106: Institutional-Grade Financial Research Analysis, Hypothesis Evaluation, and Reproducible Analytical Workbenches

### Canonical Research Analysis Domain & Optimistic Concurrency
766. **Canonical Research Analysis Entity**: Engineered `ResearchAnalysis` entity with stable identifiers (`analysis_id`), user ownership (`owner_user_id`), investigation links (`investigation_id`), and optimistic concurrency versioning (`revision`).
767. **Controlled Analysis Type Registry**: Formalized 13 institutional analysis types (`COMPANY_FINANCIAL_TREND`, `COMPANY_RATIO_ANALYSIS`, `CASH_FLOW_ANALYSIS`, `CAPITAL_STRUCTURE_ANALYSIS`, `PEER_BENCHMARKING`, `INDUSTRY_COMPARISON`, `MACROECONOMIC_TIME_SERIES`, `MULTI_INDICATOR_COMPARISON`, `HISTORICAL_MARKET_CONTEXT`, `EVENT_DISCLOSURE_COMPARISON`, `HYPOTHESIS_EVALUATION`, `DESCRIPTIVE_STATISTICAL_ANALYSIS`, `ASSUMPTION_SENSITIVITY_ANALYSIS`).
768. **Typed Analysis Specifications**: Enforced strict validation of `ResearchAnalysisSpecification` with input metric identifiers, subjects, reporting period ranges, currency policies (`NATIVE_REPORTED`, `USD_NORMALIZED`), missing data policies (`EXCLUDE_INCOMPLETE`, `ERROR_ON_MISSING`, `FORWARD_FILL`), and data revision policies (`LATEST_AUTHORIZED_DATA`, `PINNED_SOURCE_VERSION`).
769. **Reproducible Analysis Runs & Immutable Results**: Implemented `ResearchAnalysisRun` with input specification hashes (`sha256`), execution lifecycle states (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `STALE`), execution duration tracking, and immutable result persistence.

### Rigorous Financial Mathematics & Safe AST Expressions
770. **Period-over-Period Variance & Growth**: Calculated absolute delta ($\Delta = X_t - X_{t-1}$) and percentage change ($\%\Delta = \frac{X_t - X_{t-1}}{X_{t-1}} \times 100$). Enforced zero-base guard (`null` when denominator is zero) and negative-base warnings to prevent misleading percentage growth for deficit or loss accounts.
771. **Compound Annual Growth Rate (CAGR)**: Implemented institutional CAGR formula $\text{CAGR} = (X_{\text{end}} / X_{\text{start}})^{1/n} - 1$ strictly enforcing positive endpoint constraints ($X_{\text{start}} > 0, X_{\text{end}} > 0, n > 0$). Returns `null` with explicit mathematical qualification for non-positive baselines.
772. **Safe AST Expression Evaluator**: Bounded formula engine (`SafeExpressionEvaluator`) rejecting `eval()`, `exec()`, arbitrary Python/SQL/shell, imports, attribute access, and nested function calls. Enforced recursion depth limit ($\le 10$) and AST node count limit ($\le 50$), with explicit zero-division guard.

### Cross-SectionAL Peer Benchmarking & Non-Parametric Statistics
773. **Verified Stage 87 Peer Group Integration**: Reused canonical peer group definitions without synthetic company fabrication.
774. **Cross-Sectional Summary Statistics**: Implemented non-parametric median, first quartile ($Q_1$), third quartile ($Q_3$), sample mean, and standard deviation. Explicitly report eligible sample size ($N$), excluded count, and comparability warnings (such as fiscal year-end or accounting standard divergences).
775. **No Fabricated Rankings**: Prohibited naive percentile ranks or fabricated "quality scores" for incomplete or unverified cohorts.

### Deterministic Hypothesis Testing & Evidence Grounding
776. **Deterministic Hypothesis Evaluation Engine**: Connected Stage 104 Hypotheses to empirical analysis runs via `ResearchHypothesisEvaluation`. Formulated explicit test criteria with metric concepts, relational operators (`GREATER_THAN`, `LESS_THAN_OR_EQUAL`, etc.), thresholds, and minimum required sample sizes.
777. **Evidence Separation**: Categorized evaluated observations into explicit supporting evidence (`supporting_evidence_ids`) and contradicting evidence (`contradicting_evidence_ids`).
778. **Qualified Outcomes Without Hyperbole**: Evaluation returns institutional states (`CRITERIA_MET`, `CRITERIA_NOT_MET`, `MIXED_RESULTS`, `INCONCLUSIVE`, `INSUFFICIENT_DATA`) rather than claiming universal scientific proof or infallible trading signals.

### Epistemic Research Findings Lifecycle
779. **Canonical Research Finding Domain**: Implemented `ResearchFinding` entities categorized into `OBSERVED_FACT`, `CALCULATED_RESULT`, `STATISTICAL_OBSERVATION`, `ANALYST_INTERPRETATION`, and `INCONCLUSIVE_RESULT`.
780. **Auditable Review Lifecycle**: Tracked finding review progression (`DRAFT`, `NEEDS_EVIDENCE`, `READY_FOR_REVIEW`, `REVIEWED`, `REVISED`, `ARCHIVED`) with required limitation disclosures.
781. **Stale Finding Invalidation**: Source revisions or re-runs automatically flag connected findings as potentially outdated without silently erasing historical analyst contributions.

### Controlled Sensitivity Analysis & Bounded Scenarios
782. **Analyst Assumption Management**: Formalized `ResearchAssumption` records clearly distinguishing `SOURCE_REPORTED`, `ANALYST_ASSUMED`, and `DERIVED` parameters.
783. **Deterministic What-If Scenario Matrix**: Generated bounded sensitivity tables (e.g. baseline, alternative A, alternative B) evaluating deterministic parameter adjustments.
784. **Mandatory Non-Predictive Disclaimers**: All scenario calculations strictly display institutional disclaimers stating that outputs are hypothetical illustrations and not forecast probabilities or investment recommendations.

### Cryptographic Analytical Provenance & SEC EDGAR Manifests
785. **Source Observation Watermark Manifest**: Every analysis run builds a comprehensive provenance manifest indexing exact SEC EDGAR Form 10-K accession numbers, reporting dates, fact IDs, and calculation formula versions.
786. **Zero Look-Ahead Violation Protection**: Enforced as-known-at publication cutoffs to prevent future restatements or subsequent disclosure leakage into historical analysis frames.

### Frontend Institutional Research Workbench
787. **Institutional Analysis Workspace**: Built `/research` sub-tab `"ANALYSIS"` featuring Split-pane layout with searchable analysis list, type filters, and interactive master studio (`ResearchAnalysisWorkspace.tsx`, `ResearchAnalysisStudio.tsx`).
788. **Interactive Financial Visualization**: Implemented `FinancialTrendChart` (time series bar chart with deltas and CAGR badge), `PeerBenchmarkChart` (cross-sectional horizontal bars with median reference line), and `EconomicResearchChart` (macro observation series with vintage flags).
789. **Deep Evidence & Provenance Inspectors**: Developed `AnalysisResultsTable` with financial delta indicators and accession links, `HypothesisEvaluationPanel` with live criteria execution, `FindingsWorkspace` with epistemic badges, `ScenarioSensitivityWorkspace` with interactive assumption sliders, and `AnalysisProvenanceInspector` with cryptographic audit trails.

### Security, Safety, and Scope Boundaries
790. **Multi-Tenant User Isolation & RLS**: All analysis CRUD, runs, findings, and assumptions enforce strict user-level ownership and authorization. Cross-user data access returns 403 Forbidden.
791. **Zero Trading / Broker Execution**: Strictly confined within analytical and epistemic boundaries. Prohibited all automated order placement, broker execution, portfolio rebalancing, or price target generation.
792. **Zero Fabrication Policy**: Prohibited creation of synthetic financial statement values, fake peer entities, or unverified macro numbers.
793. **Stage 106 Boundary & Continuity**: Completely delivered Stage 106. Preserved strict roadmap boundary stopping before Stage 107.

## Stage 107: Investment Research Thesis, Evidence-Based Research Synthesis & Professional Analyst Report Studio

### Structured Investment Thesis & Argument Architecture
794. **Canonical Thesis Domain Entity**: Formalized `ResearchInvestmentThesis` with central thesis statement, investment horizon (`time_horizon`), target entity identification (`primary_subject_id`), conviction scoring (`conviction_score`), and lifecycle status (`DRAFT`, `ACTIVE`, `UNDER_REVIEW`, `ACCEPTED`, `REVISED`, `INVALIDATED`, `ARCHIVED`).
795. **Taxonomy of Thesis Arguments**: Implemented `ResearchThesisArgument` categorizing thesis arguments into `BULL_CASE`, `BEAR_CASE`, `BASE_CASE`, `CATALYST`, `KEY_RISK`, `CORE_ASSUMPTION`, and `CONTRADICTING_EVIDENCE`.
796. **Epistemic Evidence Anchoring**: Each argument requires explicit linkages to verified Stage 104 investigation claims (`claim_ids`), verified filing evidence citations (`evidence_ids`), reproducible Stage 106 analysis runs (`analysis_run_ids`), and acknowledged analytical limitations (`limitations`).

### Institutional Report Governance & Section Composition
797. **Canonical Report Studio Domain**: Structured `ResearchReport` supporting institutional report types (`COMPANY_RESEARCH`, `EQUITY_INITIATION_DRAFT`, `COMPANY_UPDATE`, `EARNINGS_REVIEW`, `INDUSTRY_RESEARCH`, `MACROECONOMIC_RESEARCH`, `FINANCIAL_EVENT_NOTE`, `FUNDAMENTAL_ANALYSIS`, `PEER_BENCHMARKING`, `INVESTMENT_THESIS`, `RISK_RESEARCH_NOTE`, `GENERAL_RESEARCH_MEMORANDUM`).
798. **Structured Content Block Model**: Section content is modeled via `ResearchReportContentBlock` taxonomy supporting `HEADING_2`, `HEADING_3`, `PARAGRAPH`, `BULLET_LIST`, `NUMBERED_LIST`, `BLOCK_QUOTE`, `QUOTE`, `FINANCIAL_TABLE`, `ANALYSIS_TABLE`, and `CHART` embeds.
799. **Template-Driven Institutional Consistency**: Engineered built-in institutional templates (`tpl-company-research`, `tpl-equity-initiation`, `tpl-earnings-review`, `tpl-macro-research`, `tpl-investment-thesis`, `tpl-general-memo`) enforcing mandatory governance sections (Executive Summary, Financial Analysis, Valuation Framework, Risks, Methodology, and Disclaimers).

### Point-in-Time Research Snapshots & Immutability
800. **Strict Optimistic Concurrency Control**: All report mutations require `expected_revision` tracking to eliminate silent overwrite conflicts in multi-tab institutional analyst workflows.
801. **Auditable Revision History & Unified Diff Engine**: Every saved change increments revision, captures word counts and content hashes, and enables granular section-by-section diff comparisons via `compare_report_revisions`.
802. **Finalization Immutability**: Transitioning a report to `FINALIZED` or `PUBLISHED` locks the document tree, prohibiting further in-place edits and certifying the artifact as a point-in-time publication snapshot.

### Automated Claim-to-Evidence & Look-Ahead Verification Engine
803. **Multi-Vector Verification Engine**: Validates structural completeness of required sections, validates filing citations against Stage 104/105 source availability (flagging withdrawn or restricted sources), verifies reproducible Stage 106 analysis runs, and performs temporal cutoff analysis.
804. **Zero Look-Ahead Violation Protection**: Automatically scans all embedded data points, analysis run timestamps, and cited evidence against the report's `research_cutoff` date; any future data leaks generate blocking issues (`POINT_IN_TIME_CONFLICT`).
805. **Publication Gatekeeper**: Finalization and certified publication are strictly prohibited while blocking verification violations remain unresolved.

### Zero-External-Dependency Institutional Export
806. **Direct PDF-1.4 Binary Generation**: Engineered a self-contained PDF generator (`render_report_pdf`) using Python's standard library (`io.BytesIO`) that constructs standard PDF catalogs, pages, font dictionaries (`/Courier`, `/Helvetica-Bold`), text streams, line wraps, tabular financial data, and institutional disclaimers without requiring heavyweight external dependencies like ReportLab.
807. **Direct OpenXML DOCX Generation**: Built a self-contained DOCX renderer (`render_report_docx`) packaging standard OpenXML schemas (`word/document.xml`, `[Content_Types].xml`, `_rels/.rels`, `word/styles.xml`) via Python's built-in `zipfile` module.
808. **Mandatory Institutional Compliance Disclaimers**: All generated export documents systematically embed prominent regulatory notices clarifying informational nature, non-promissory risk disclosures, and source attribution.

### Frontend Institutional Report Studio
809. **Dedicated `/research` Sub-View**: Seamlessly expanded `/research` with top navigation switchers `"Reports & Theses"`, supporting split tabs between Institutional Analyst Reports and Structured Investment Theses.
810. **Professional 3-Pane Authoring Studio**: Developed `ResearchReportStudio.tsx` integrating `ResearchReportOutline` (drag-and-drop section hierarchy), `ResearchReportEditor` (rich content block authoring and embed controls), and tabbed right-hand inspector panels (`ResearchReportVerificationPanel`, `ResearchReportEvidencePanel`, `ResearchReportRevisionHistory`).
811. **Print-Ready Document Preview & Controlled Export**: Built `ResearchReportPreview.tsx` rendering high-fidelity executive document layouts with table of contents and compliance notices, and `ResearchReportExportDialog.tsx` triggering background jobs and binary downloads.

### Security, Safety, and Scope Boundaries
812. **Multi-Tenant Authorization & Cross-User Isolation**: All report, section, revision, verification, export, thesis, and argument operations enforce strict user-level ownership. Attempted access to other users' work returns HTTP 403 Forbidden.
813. **Zero Autonomous Trade Generation**: Preserved strict boundary prohibiting automated buy/sell recommendations, portfolio rebalancing, or direct market execution.
814. **Roadmap Boundary (Stage 107 of 150)**: Master engineering implementation completed for Stage 107. All Stage 108 implementation is strictly deferred.

## Stage 108: Institutional Research Collaboration, Analyst Review, Evidence Governance and Approval Workflow Platform

### Participant Governance & Granular Research Access Grants
815. **Participant Governance & Granular Research Access Grants**: Engineered `ResearchAccessGrant` domain model supporting resource targets (`INVESTIGATION`, `REPORT`, `THESIS`) and hierarchical roles: `OWNER` (full control, participant management, finalization), `EDITOR` (author revisions, edit content), `REVIEWER` (issue formal review decisions, request changes), `COMMENTER` (post anchored discussions), and `VIEWER` (read-only audit).
816. **Principal Polymorphism & Expiration Lifecycle**: Supported both individual users (`USER`) and institutional teams (`TEAM` / `GROUP`), with optional ISO 8601 expiration timestamps (`expires_at`) and audit-traceable revocations (`revoked_at`).
817. **Dynamic Role Resolution Engine**: Created `resolve_user_role` repository method unifying direct ownership check (user ID equals resource owner) and explicit access grants with role precedence to ensure deterministic privilege determination across all research actions.

### Institutional Research Review State Machine & Revision Pinning
818. **Canonical Research Review Request**: Formalized `ResearchReviewRequest` capturing target resource, revision number (`target_revision_number`), cryptographic SHA-256 fingerprint (`target_content_hash`), review scope (`FULL_REPORT`, `SECTION_SPECIFIC`, `FINANCIAL_ANALYSIS`, `THESIS_VALIDATION`, `EVIDENCE_INTEGRITY`), round index, and instructions.
819. **Strict Research Review State Machine**: Implemented deterministic transition graph: `DRAFT` -> `SUBMITTED` -> `IN_REVIEW` -> `CHANGES_REQUESTED` | `APPROVED` | `REJECTED`, alongside terminal transitions `CANCELED` and `SUPERSEDED`.
820. **Exact Revision Binding & Anti-Tampering Concurrency**: When a review request is submitted, it binds to the exact revision and content hash of the target report or thesis. If the author mutates the document creating a higher revision while review is pending, subsequent review decisions fail with `ResearchReviewRevisionMismatchError` (HTTP 400), preventing approvals of unreviewed content.

### Separation of Duties & Quality Gates
821. **Separation of Duties & Author Self-Approval Prohibition**: Implemented hard regulatory control forbidding report authors/owners from issuing an `APPROVE` decision on their own research submissions (`reviewer_user_id == target_resource.owner_user_id`), raising `ResearchReviewSelfApprovalForbiddenError` (HTTP 403).
822. **Formal Review Decisions with Auditable Rationale**: Captured `ResearchReviewDecision` containing decision type (`APPROVE`, `REQUEST_CHANGES`, `REJECT`), reviewer ID, revision number, content hash, decision comments, and timestamp.
823. **Synchronized Report Lifecycle Progression**: Recording an `APPROVE` decision automatically updates the report lifecycle to `REVIEWED`, while `REQUEST_CHANGES` sets review status to `CHANGES_REQUESTED` to prompt author iteration.
824. **Automated Governance Quality Gates Engine**: Engineered `run_quality_gate` performing multi-rule verification: minimum structural sections, zero unresolved blocking comments, all citations linked to active sources, absence of placeholder content, and formal review approval verification.
825. **Multi-Severity Quality Gate Diagnostics**: Classified findings into `BLOCKING` issues (preventing internal circulation and sign-off), `WARNING` items, and passed checklist criteria (`checks_passed`), returning `can_circulate` boolean flag.

### Anchored Discussions & Staleness Tracking
826. **Anchored Discussion Threads & Comment Model**: Built `ResearchCommentThread` enabling targeted commentary anchored to granular entities: `REPORT_SECTION`, `CONTENT_BLOCK`, `TEXT_RANGE`, `CITATION`, `ANALYSIS_RUN`, and `FINDING`.
827. **Revision Staleness Detection for Anchored Threads**: Threads track the `target_revision_number` at time of creation; when a newer report revision is generated, `is_stale` is automatically evaluated and surfaced in UI badges to warn reviewers that the underlying content has changed.
828. **Thread Resolution Lifecycle & Verification Audit**: Supported thread states `OPEN`, `RESOLVED`, and `REOPENED` with resolution metadata (`resolved_by`, `resolved_at`), enabling reviewers to verify whether all critique items have been addressed.

### Controlled Internal Circulation & Operations Audit Trail
829. **Controlled Internal Circulation & Sharing Platform**: Formalized `ResearchInternalCirculation` enabling restricted distribution of reviewed and approved reports to explicit internal recipients (`authorized_recipient_ids`, `authorized_team_ids`).
830. **Circulation Approval Prerequisite**: Circulating a report strictly requires verified `APPROVED` or `FINALIZED` status; attempting to circulate draft or unreviewed research raises `ResearchCirculationForbiddenError` (HTTP 400).
831. **Circulation Revocation & Distribution Audit**: Supported immediate circulation revocation (`revoke_internal_circulation`) with timestamp tracking, audit logging, and watermark restriction guidance (`WATERMARK_CONFIDENTIAL`).
832. **Comprehensive Research Operations Audit Trail**: Implemented `record_review_audit_event` and `list_review_audit_events` capturing immutable log entries across all operational events (`GRANT_CREATED`, `REVIEW_SUBMITTED`, `REVIEW_DECIDED`, `COMMENT_ADDED`, `COMMENT_RESOLVED`, `QUALITY_GATE_RUN`, `REPORT_CIRCULATED`, `CIRCULATION_REVOKED`).

### Frontend Research Reviews Workspace & Safety Boundaries
833. **Frontend Research Reviews Workspace**: Integrated `"Reviews & Governance"` tab into `/research` supporting three-pane workflow: `ResearchReviewQueue` (filterable by status, scope, priority), `ResearchReviewDetail` (target metadata, assigned reviewers, instructions, decision controls), and `ResearchCommentSidebar` (anchored discussions and replies).
834. **Interactive Collaboration Modals**: Developed `ResearchParticipantsModal` (manage collaborators, grant/change/revoke roles), `ResearchCirculationDialog` (distribute approved reports to internal recipients, inspect active circulations), and `NewReviewDialog` (submit reports for peer review).
835. **Cross-Tenant Isolation & Least Privilege Enforcement**: All collaboration, review, comment, quality gate, and circulation endpoints enforce authentication and tenant isolation, restricting resource mutations to authenticated users with requisite role entitlements.
836. **Roadmap Boundary (Stage 108 of 150)**: Master engineering implementation completed for Stage 108. All Stage 109 implementation is strictly deferred.

## Stage 109: Institutional-Grade Research Knowledge, Continuous Evidence Monitoring and Research Lifecycle Management Platform

### Knowledge Library & Indexing
837. **Institutional Research Knowledge Registry**: Implemented `ResearchKnowledgeEntry` unifying heterogeneous research assets across all 6 Research development stages (`INVESTIGATION`, `NOTE`, `QUESTION`, `HYPOTHESIS`, `CLAIM`, `EVIDENCE`, `ANALYSIS`, `FINDING`, `THESIS`, `REPORT`, `SOURCE_REFERENCE`).
838. **Cross-Tenant Knowledge Search & Isolation**: Search query engine verifies authenticated ownership and explicit collaboration access rights before returning knowledge entries, guaranteeing zero cross-tenant metadata leakage.
839. **Knowledge Availability & Lifecycle Tracking**: Classified entry statuses into `ACTIVE`, `ARCHIVED`, `DEPRECATED`, and `DRAFT`, coupled with source availability tags (`AVAILABLE`, `PENDING_VERIFICATION`, `RESTRICTED`, `UNAVAILABLE`).

### Dependency Lineage Graph
840. **Multi-Hop Research Dependency Graph**: Formalized `ResearchDependencyEdge` linking canonical sources, evidence snippets, quantitative calculations, empirical findings, investment theses, reports, and review decisions.
841. **Cycle-Safe Bounded Lineage Traversal**: Engineered depth-first traversal engine bounded to `max_depth=5` with deterministic cycle detection, preventing infinite recursion while flagging loop anomalies.
842. **Directed Lineage Nodes & Graph Visualization**: Provided frontend lineage graph visualizer rendering typed nodes and edge connections with source references and traversal limit badges.

### Continuous Source-Change Ingestion & Monitoring
843. **Canonical Source Change Event Model**: Built `ResearchSourceChangeEvent` capturing filing amendments (`DOCUMENT_AMENDED`), financial restatements (`FACT_RESTATED`), economic vintages (`VINTAGE_UPDATED`), news corrections (`NEWS_CORRECTED`), and entitlement changes (`ENTITLEMENT_REVOKED`).
844. **Idempotent Source Change Deduplication**: Enforced natural composite deduplication key `(source_type, canonical_source_id, old_revision_id, new_revision_id, change_type)` to eliminate duplicate alert spam.
845. **Multi-Field Change Tracking**: Captured specific amended items and footnotes (e.g. `Item 8 Note 3 Segment Revenue`) for granular impact mapping.

### Deterministic Impact Assessment
846. **Downstream Impact Propagation Engine**: Traverses dependency paths from modified sources down to dependent deliverables, generating `ResearchImpactAssessment` records.
847. **Stratified Impact Categorization**: Classified impacts into `DIRECT_SOURCE_REFERENCE_CHANGED`, `INTERMEDIATE_CALCULATION_IMPACTED`, `DOWNSTREAM_FINDING_REQUIRING_REVALIDATION`, and `REPORT_ASSERTION_AFFECTED`.
848. **Epistemic Humility & Non-Causal Guidance**: Avoided speculative or hallucinated causal certainty; impacts provide clear review recommendations rather than ungrounded conclusions.

### Automated Citation & Approval Revalidation
849. **Automated Reference & Citation Revalidation Engine**: Evaluates target reports, analyses, and findings against current source registries, detecting broken citation targets and upstream modifications.
850. **Approval Revision Freshness Verification**: Revalidation verifies whether the inspected revision holds active formal review approval, highlighting unreviewed or modified revisions.
851. **Granular Revalidation Issue Severity**: Categorized revalidation issues into `BLOCKING`, `WARNING`, and `INFORMATIONAL`, mapping to outcomes (`VALID_REFERENCES`, `VALID_WITH_WARNINGS`, `REQUIRES_HUMAN_REVIEW`, `INVALID_CITATIONS`, `APPROVAL_REVOCATION_RECOMMENDED`).

### Research Update Queue Lifecycle State Machine
852. **Analyst Update Queue State Machine**: Modeled `ResearchUpdateItem` with deterministic transitions: `OPEN` -> `ACKNOWLEDGED` -> `RESOLVED` / `DISMISSED` / `REOPENED`.
853. **Mandatory Resolution Rationale**: Transitioning an update item to `RESOLVED` strictly mandates analyst resolution notes detailing evidence verification or adjustments made.
854. **Cross-Tenant Update Task Isolation**: Update items enforce tenant ownership checks; unauthorized users cannot acknowledge or mutate another analyst's tasks.

### Point-in-Time Correctness & Platform Integration
855. **Historical Point-in-Time Immutability**: Source change detection and revalidation never silently mutate historic analysis run results, locked evidence records, or finalized reports.
856. **Unified Institutional Research Overview**: Implemented `get_institutional_overview_summary` exposing live counts across active investigations, notes, analyses, reports, theses, pending reviews, open updates, and critical updates.
857. **Frontend Knowledge & Updates Workspaces**: Integrated `"Knowledge Library"` and `"Updates & Monitoring"` workspaces with search, inspector, lineage graph, and revalidation modal.
858. **Full Research Sequence Closure (Stages 104–109)**: Successfully closed the complete 6-stage Research module development sequence within the primary route `/research`.
859. **Roadmap Boundary (Stage 109 of 150)**: Stage 109 implementation complete. Stage 110 (Portfolios) and subsequent stages are strictly deferred. Zero portfolio mutation, zero trade execution, zero autonomous AI trading agents.
## Stage 110: Build PORTFOLIOS V1 — Accounts, Transactions, Positions, Cash and Valuation

### Canonical Portfolio and Investment Account Domain
860. **Canonical Portfolio & Account Architecture**: Formalized `Portfolio` and `InvestmentAccount` entities with stable UUID identifiers, user-level tenant ownership (`owner_user_id`), portfolio types (`TAXABLE_INDIVIDUAL`, `JOINT_TENANTS`, `CORPORATE_TREASURY`, `INSTITUTIONAL_FUND`, `TRUST_FIDUCIARY`, `RETIREMENT_IRA`, `MODEL_BENCHMARK`), base reporting currencies (`base_currency`), and lifecycle states (`ACTIVE`, `RESTRICTED`, `CLOSED`, `ARCHIVED`).
861. **Multi-Account Container Hierarchy**: Implemented multi-account containment allowing each portfolio to manage multiple segregated accounts (`BROKERAGE_RECORD`, `INVESTMENT_ACCOUNT`, `CASH_ACCOUNT`, `MANUAL_PORTFOLIO_ACCOUNT`) with strict isolation and account-level settlement policies.
862. **Optimistic Concurrency & Audit Metadata**: Enforced integer revision counters (`revision`) across portfolios and accounts to detect and prevent mid-air collision overwrites during concurrent ledger postings.

### Immutable Transaction Ledger & Controlled Reversals
863. **Double-Entry-Inspired Transaction Journal**: Structured `PortfolioTransaction` supporting 12 canonical transaction types (`BUY`, `SELL`, `CASH_DEPOSIT`, `CASH_WITHDRAWAL`, `CASH_TRANSFER_IN`, `CASH_TRANSFER_OUT`, `CASH_DIVIDEND`, `CASH_INTEREST`, `ACCOUNT_FEE`, `WITHHOLDING_TAX`, `STOCK_SPLIT_ADJUSTMENT`, `CORRECTION_REVERSAL`). Every transaction captures trade date, settlement date, gross execution amount, fees, net cash impact, and transaction status (`PENDING`, `SETTLED`, `REVERSED`, `CORRECTED`, `CANCELED`).
864. **Interactive Transaction Preview Engine**: Built pure deterministic preview endpoint (`preview_transaction`) that calculates fee allocations, net cash impacts, FIFO lot consumption projections, and projected cash/position balances prior to committing changes to the ledger.
865. **Idempotency Protection & Duplicate Detection**: Enforced client-provided `idempotency_key` checking to eliminate duplicate transaction postings across network retries or double-click events.
866. **Audited Reversing Entries & Non-Destructive Corrections**: Prohibited raw physical deletion of posted transactions. Implemented `CORRECTION_REVERSAL` entries with mandatory audit reasons (`audit_reason`), maintaining unbroken journal provenance while reversing lot consumptions and cash movements.

### Multi-Currency Cash Management & Segregated Balances
867. **Multi-Currency Cash Balance Segregation**: Modeled cash balances per account and per currency code, separating `POSTED_CASH`, `SETTLED_CASH`, `UNSETTLED_RECEIVABLE`, `UNSETTLED_PAYABLE`, and `AVAILABLE_CASH`. Prohibited raw mathematical addition across differing currencies without explicit canonical FX rate conversion.
868. **Cash Ledger Audit Trail**: Maintained atomic `PortfolioCashLedgerEntry` journal recording directional cash inflows, outflows, transaction links, and resulting running balances for institutional audit verification.

### FIFO Tax-Lot Accounting Engine & Exact Part XXII Reference Fixture
869. **FIFO Cost-Basis Engine with Fee Capitalization**: Engineered deterministic First-In, First-Out (FIFO) tax-lot matching (`PortfolioSecurityLot`). Purchases capitalize transaction fees into acquisition cost basis ($\text{Unit Basis} = \frac{\text{Gross Amount} + \text{Fees}}{\text{Quantity}}$).
870. **Partial Lot Consumption & Realized P&L Calculation**: Sales consume open lots chronologically, generating immutable `PortfolioLotConsumption` records. Net proceeds deduct exit fees ($\text{Net Proceeds} = \text{Gross Amount} - \text{Fees}$), computing exact realized capital gains ($\text{Realized P&L} = \text{Net Proceeds} - \text{Cost Basis Disposed}$).
871. **Exact Part XXII Reference Fixture Verification**: Fully tested and mathematically verified the canonical benchmark fixture: $10,000 cash deposit, Buy 100 shares @ $50.00 + $10 fee, Sell 40 shares @ $60.00 - $8 fee $\rightarrow$ 60 remaining shares @ $50.10 unit basis, $2,004.00 cost basis disposed, $388.00 realized P&L, $3,006.00 remaining basis, $7,382.00 cash balance, $3,300.00 market value @ $55.00 mark, $10,682.00 total portfolio value, $294.00 unrealized P&L, and $682.00 net economic gain.
872. **Corporate Action Stock Split Adjustments**: Stock splits and reverse splits adjust open lot quantities while preserving total aggregate cost basis, reciprocally updating unit basis with zero cash movement.

### Position Projections & Event Stream Replay
873. **Deterministic Position Derivation**: Portfolio positions (`PortfolioPosition`) are projected dynamically from transaction event logs. Backdated transactions trigger ordered stream replay to ensure accurate historical lot states and prevent basis corruption.

### Canonical Market Data, FX Integration & Valuation Engine
874. **Canonical Quote Freshness & Completeness States**: Position valuation integrates canonical market quotes with explicit freshness tracking (`REAL_TIME`, `DELAYED_15MIN`, `END_OF_DAY`, `STALE_OVER_24H`). Portfolio valuations classify completeness states into `COMPLETE`, `PARTIAL_MISSING_PRICES`, `PARTIAL_MISSING_FX`, `PARTIAL_STALE_DATA`, and `UNAVAILABLE`.
875. **Multi-Currency Conversion with Directional FX Quotes**: Foreign asset and cash valuations are converted to portfolio base reporting currency using verified FX rates (e.g., ECB reference feeds), handling direct pairs and mathematical inversions with explicit timestamp capture.

### Continuous Ledger Reconciliation Engine
876. **Automated Balance & Lot Reconciliation**: Built automated audit verification comparing cash ledger entry sums against cash balance records, open lot share counts against position quantities, remaining lot basis against position cost basis, and total realized P&L against lot consumptions. Returns explicit reconciliation states (`RECONCILED`, `RECONCILIATION_WARNING`, `OUT_OF_BALANCE`).

### Professional Bloomberg-Style Frontend Workspaces
877. **Integrated `/portfolios` Workspaces**: Delivered comprehensive frontend at `/portfolios` featuring Portfolio Header with switcher, Overview with KPI metric cards, Holdings & Tax-Lots Table, Position Inspector, Transaction Journal with Live Preview, Transaction Reversal/Correction modals, Multi-Currency Cash Workspace, Valuation Workspace with FX rates and quote freshness inspectors, and Investment Account Management.

### Roadmap Boundaries & Strict Deferrals
878. **Stage 110 Roadmap Boundary (Portfolios V1)**: Stage 110 exclusively establishes core accounts, transaction ledgers, positions, FIFO tax lots, cash management, valuation, and reconciliation.
879. **Strict Deferral of Performance Analytics (Stage 111)**: Strictly prohibited conversion of accounting P&L into Time-Weighted Return (TWR), Money-Weighted Return (MWR), IRR, or XIRR (reserved for Stage 111).
880. **Strict Deferral of Allocation, Attribution, Risk, and Trading**: Strictly deferred Stage 112 (Allocation/Exposure), Stage 113 (Attribution), Stage 114 (Optimization), Stages 115–118 (Risk), Stage 143 (Backtesting), Stage 144 (Paper Trading), Stage 145 (Broker Sandbox), and Stages 146–149 (Autonomous Agents). Zero live broker order execution.


## STAGE 111 — INSTITUTIONAL-GRADE PORTFOLIO PERFORMANCE ANALYTICS ENGINE

### Canonical Performance Domain & Exact Subperiod TWR Engine
881. **Canonical Performance Domain Identity**: Established unified performance analytics module in `atlas.portfolios.performance` managing calculation runs, methodology registries, period type resolvers, and cryptographic execution snapshots.
882. **Exact Subperiod Time-Weighted Return (TWR) Methodology**: Implemented GIPS/CFA-aligned exact subperiod TWR segmentation ($R_{\text{twr}} = \prod (1 + R_i) - 1$). New subperiods are bounded strictly by external investor cash flows, eliminating external cash-flow distortions from compounding returns.
883. **Part XIII Exact Reference Fixture Verification**: Mathematically verified the canonical Part XIII reference fixture: Subperiod 1 ($100 \to 110$, $R_1 = 10\%$), $+\$50$ external contribution at $t_1$, Subperiod 2 ($160 \to 176$, $R_2 = 10\%$), yielding exact compound TWR of $(1.10 \times 1.10) - 1 = \mathbf{21.0\%}$, strictly rejecting the naive calculation of $(176 - 100) / 100 = 76.0\%$.
884. **Modified Dietz Approximate TWR Support**: Provided clear methodological distinction for Modified Dietz approximate TWR ($R_{\text{dietz}} = \frac{V_e - V_b - F}{V_b + \sum F_t \cdot W_t}$) with day-weighting for historical periods lacking interim valuation marks, tagging runs with explicit approximation warnings.

### Money-Weighted Returns (MWR / XIRR) & Bounded Root Solver
885. **Money-Weighted Return (MWR / XIRR) Formulation**: Implemented annualized internal rate of return ($\sum \frac{C_t}{(1 + r)^{\frac{d_t - d_0}{365}}} = 0$) under standard ACT/365 day-count convention.
886. **Bounded Newton-Raphson & Bisection Fallback Root Solver**: Engineered robust numerical root solver utilizing analytic first derivatives with search boundaries clamped to $[-0.9999, 50.0]$ and guaranteed bisection fallback to eliminate infinite loops and solver divergence.
887. **Investor-Perspective Cash Flow Sign Convention**: Standardized investor-perspective dated cash flow schedules where deposits/contributions are negative outflows ($-C_t$), withdrawals are positive inflows ($+C_t$), and terminal marked valuation is positive liquidation equivalent ($+V_e$).
888. **Descartes Sign Rule Analysis for Non-Unique Roots**: Implemented sign-change analysis on cumulative net flows to detect schedules with multiple mathematical roots, generating explicit diagnostic alerts when multiple IRR solutions exist.
889. **Part XIX Simple 1-Year Reference Fixture Verification**: Validated exact Part XIX fixture: $-\$1,000$ initial contribution at $t_0$, $+\$1,100$ terminal valuation at $t_0 + 365 \text{ days} \implies \mathbf{10.0\%}$ annualized XIRR.

### Cash Flow Classification & Scope Boundary Isolation
890. **Deterministic Cash Flow Classification Matrix**: Implemented strict classification rules categorizing transactions into `EXTERNAL_CONTRIBUTION`, `EXTERNAL_WITHDRAWAL`, `INTERNAL_SECURITY_TRADE`, `INTERNAL_INCOME`, `INTERNAL_FEE`, `INTERNAL_TRANSFER`, and `CORPORATE_ACTION_NONCASH`.
891. **Internal Trade & Reinvestment Isolation**: Strictly excluded buys, sells, dividend receipts, and interest payments from external flow status, ensuring portfolio internal operations do not distort investor-level return metrics.
892. **Inter-Account Transfer Scope Netting**: Handled cash transfers dynamically based on measurement scope: netted out as $0.00$ internal flow at `PORTFOLIO` scope, while classified as external contributions/withdrawals at `ACCOUNT` scope.
893. **Treatment of Dividends and Fees**: Retained cash dividends and interest within portfolio equity value (generating organic return), while deducting management and account fees as internal costs reducing net performance.

### Multi-Currency Return Engine & Canonical FX Integration
894. **Multi-Currency Flow-Date & Valuation-Date FX Conversion**: Converted cash flows at verified spot FX rates on the exact flow date and valuation points at spot FX rates on each valuation timestamp.
895. **Part XXXIV Multi-Currency Reference Fixture Verification**: Mathematically validated Part XXXIV fixture: native USD investment ($100 \to 110$, $R_{\text{USD}} = 10.0\%$) with historical FX moving from $80.0$ to $90.0$ USD/INR yields starting INR valuation of $8,000$, ending INR valuation of $9,900$, and base INR return of $\frac{9,900 - 8,000}{8,000} = \mathbf{23.75\%}$.

### Periodic Returns & Geometric Annualization
896. **Periodic Calendar Returns & Compounding Grid**: Engineered calendar monthly and annual returns table with geometric sub-interval compounding ($(1 + R_{\text{yr}}) = \prod (1 + R_{\text{mo}})$).
897. **Geometric Annualization (CAGR) & Sub-Year Guardrails**: Standardized annualization ($(1 + R)^{\frac{365.25}{D}} - 1$) for durations $\ge 365$ days, strictly suppressing annualization for periods under 1 year to prevent false volatility extrapolation.

### Canonical Benchmarks & Relative Performance Comparison
898. **Canonical Market Benchmark Registry**: Established built-in benchmarks including S&P 500 (`PRICE_RETURN`), SPDR S&P 500 ETF Trust (`TOTAL_RETURN`), NASDAQ 100 (`PRICE_RETURN`), and MSCI All Country World Index (`TOTAL_RETURN`).
899. **Arithmetic Relative Return & Rebased Growth Index**: Computed arithmetic excess return ($\Delta R = R_{\text{portfolio}} - R_{\text{benchmark}}$) and rebased both curves to $100.00$ at period start for visual tracking.
900. **Price Return vs Total Return Compliance Warnings**: Implemented automatic compliance notices alerting users whenever a total-return portfolio is compared against a price-return index benchmark.

### Cryptographic Provenance, Data Quality & Security
901. **Cryptographic Input Hashing (`sha256`)**: Generated SHA-256 digests over period bounds, transaction counts, ledger revision tags, and calculation parameters to ensure reproducible execution provenance.
902. **Data Completeness & Stale Mark Diagnostics**: Classified audit states into `COMPLETE`, `COMPLETE_WITH_STALE_MARKS`, `PARTIAL_MISSING_PRICES`, `PARTIAL_MISSING_VALUATION`, and `EMPTY`, explicitly logging counts of missing marks and FX rates.
903. **Immutable Performance Run Snapshots**: Maintained historical run snapshots with unique run IDs, execution timestamps, and parameter records for regulatory auditability.
904. **Typed Error Hierarchy**: Defined specific domain exceptions including `PortfolioPerformanceXirrNoSolutionError`, `PortfolioPerformanceXirrInvalidCashFlowsError`, and `PortfolioPerformancePeriodInvalidError`.
905. **FastAPI Performance Endpoints**: Exposed 9 endpoints under `/api/v1/portfolios` covering `/benchmarks`, `/{portfolio_id}/performance`, `/calculate`, `/runs`, `/series`, `/periodic`, `/cash-flows`, and `/data-quality`.
906. **Multi-Tenant Isolation & Ownership Verification**: Enforced strict tenant isolation, verifying portfolio ownership before computing or serving performance analytics and returning HTTP 403/404 on cross-tenant access.

### Bloomberg-Style Frontend Workspaces
907. **Integrated Performance Analytics Workspace**: Built comprehensive workspace at `/portfolios` under the "Performance Analytics" tab with period pills (`1D`, `WTD`, `MTD`, `QTD`, `YTD`, `1M`, `3M`, `1Y`, `3Y`, `5Y`, `INCEPTION`, `CUSTOM`), account filter, methodology toggle, and recalculation triggers.
908. **Interactive SVG Performance Charts**: Delivered high-precision Time-Weighted Growth of $100 chart with benchmark overlay and cash flow milestone markers, plus historical monetary valuation equity curve.
909. **Methodology & Formula Audit Inspector**: Designed slide-over inspector detailing exact mathematical equations, day-count conventions, SHA-256 provenance hash, and discrete subperiod audit tables.
910. **Strict Roadmap Boundaries**: Stage 111 exclusively delivers portfolio performance calculations. Strictly deferred Stage 112 (Allocation/Exposure), Stage 113 (Attribution), Stage 114 (Optimization), Stages 115–118 (Risk/VaR/Sharpe/Sortino), and Stages 143–149 (Backtesting/Paper Trading/Trading Execution). Zero live broker order placement.


## STAGE 112 — INSTITUTIONAL-GRADE PORTFOLIO ALLOCATION, EXPOSURE INTELLIGENCE AND CONCENTRATION ANALYTICS PLATFORM

### Mathematical Foundations & Partition Reconciliation Engine
911. **Canonical Exposure Domain Architecture**: Established unified exposure intelligence module in `atlas.portfolios.exposure` managing calculation runs, multi-dimensional classification engines, ETF look-through decomposition, concentration analytics, and cryptographic run snapshots.
912. **Exact Decimal Partition Weight Math**: Formulated all allocation and partition weights with exact Python `Decimal` arithmetic relative to verified Net Asset Value ($w_i = v_i / \text{NAV}$), strictly preventing floating-point drift.
913. **Non-Positive NAV Denominator Guardrail**: Enforced strict validation on denominator valuation ($V \le 0.00$), raising a typed `PortfolioExposureNavInvalidError` to prevent divide-by-zero or inverted relative proportions.
914. **Deterministic Partition Sum Reconciliation**: Implemented automated reconciliation verification requiring partition weights across exhaustive dimensions (asset classes, sectors, countries, currencies) to sum to exactly $1.000000$ within $10^{-4}$ tolerance, flagging `RECONCILIATION_WARNING` or `RECONCILIATION_FAILED` otherwise.
915. **Part X Allocation Fixture Verification**: Mathematically validated the Part X canonical reference fixture: $\$20,000.00$ Net Asset Value partitioned into $\$15,000.00$ Equity ($75.0\%$) and $\$5,000.00$ Cash ($25.0\%$) with $100.0\%$ partition reconciliation.

### Concentration Analytics, HHI & Effective Holdings ($N_{\text{eff}}$)
916. **Herfindahl-Hirschman Index (HHI) Engine**: Built exact HHI calculation ($\text{HHI} = \sum w_i^2$) and normalized conventional index scale ($\text{HHI}_{\text{idx}} = 10,000 \times \text{HHI}$) across both security-level and ultimate parent issuer-level scopes.
917. **Effective Number of Bets ($N_{\text{eff}}$)**: Engineered $N_{\text{eff}} = \frac{1}{\text{HHI}}$ indicator representing the equivalent number of equal-sized holdings providing the identical diversification profile.
918. **Quantile Concentration Ladders**: Computed Top 1, Top 3, Top 5, Top 10, and Top 20 cumulative concentration metrics with quantile rankings.
919. **Institutional Diversification Regimes**: Standardized concentration classification into `HIGHLY_DIVERSIFIED` ($\text{HHI} < 0.15$), `MODERATELY_CONCENTRATED` ($0.15 \le \text{HHI} < 0.25$), and `HIGHLY_CONCENTRATED` ($\text{HHI} \ge 0.25$).
920. **Part XXVIII Concentration Fixture Verification**: Mathematically validated Part XXVIII reference fixture ($50\%, 25\%, 25\%$ weights) yielding exact $\text{HHI} = 0.3750$ ($\text{HHI}_{\text{idx}} = 3,750$) and $N_{\text{eff}} = 2.67$.

### Issuer Aggregation & Security Roll-up
921. **Ultimate Parent Issuer Consolidation**: Engineered issuer aggregation grouping disparate instrument share classes (e.g. GOOG Class C and GOOGL Class A) and cross-border listings (e.g. INFY local equity and INFY ADR) under their canonical issuer entity, preventing hidden single-issuer concentration.
922. **Cross-Instrument Weight Aggregation**: Consolidated issuer weights by summing direct equity holdings, fixed-income instruments, and indirect fund look-through exposures associated with each issuer UUID.

### Fund & ETF Look-Through Decomposition & Cross-Fund Overlap
923. **Recursive ETF Look-Through Decomposition**: Engineered `FundLookThroughEngine` decomposing collective investment vehicles (SPY, QQQ) into their constituent securities proportional to the fund's portfolio weight ($w_{\text{effective}}(k) = W_F \cdot w_{k,F}$).
924. **Part XXXII ETF Look-Through Fixture Verification**: Mathematically validated Part XXXII reference fixture: $\$100,000$ NAV with $\$60,000$ direct AAPL ($60.0\%$) and $\$40,000$ SPY ($40.0\%$ containing $7.2\%$ AAPL) correctly calculates $2.88\%$ indirect AAPL look-through weight and $62.88\%$ total effective AAPL exposure.
925. **Look-Through Recursion Depth & Cycle Prevention**: Enforced strict recursion limit (default depth 3) and cycle detection graph tracking to prevent infinite loops in fund-of-funds structures (`PortfolioExposureLookThroughCycleError`).
926. **Explicit Residual Unmapped Constituent Bucket**: Created explicit `residual_unmapped` constituent row for non-disclosed or sub-threshold holdings to ensure $100\%$ fund reconciliation.
927. **Cross-Fund Overlap Engine**: Implemented pairwise constituent overlap matrix ($\sum \min(w_{k,A}, w_{k,B})$) and consolidated portfolio overlap tracking duplicated exposures across multiple ETF holdings.

### Multi-Dimensional Taxonomies & Geographic Policies
928. **Canonical Asset Class Registry**: Classified holdings across 7 mutually exclusive asset classes: Equity, Fixed Income, Cash Equivalent, Commodity, Real Estate, Alternative, Derivative.
929. **GICS 11 Sectors & 25 Industry Groups**: Integrated standard 11 GICS sectors and 25 industry groups with hierarchical roll-up and benchmark comparative deltas.
930. **Tri-Policy Geographic Engine**: Built geographic categorization supporting three distinct regulatory perspectives: Country of Legal Domicile, Country of Corporate Headquarters, and Primary Exchange Listing Country, with ISO 3166-1 alpha-2 resolution and regional aggregations.
931. **Denomination Currency Exposure**: Computed portfolio currency exposure isolating unhedged foreign denomination assets from base reporting currency.

### Historical Allocation & Allocation Drift Analytics
932. **Historical Time-Series Allocation Engine**: Extracted historical daily and period-end asset class, sector, and top holding allocations across custom time horizons.
933. **Date-to-Date Allocation Drift Engine**: Engineered date-to-date drift calculation measuring allocation change ($\Delta w_i = w_i(t_2) - w_i(t_1)$), basis point drift ($\Delta \text{bps}_i = 10,000 \cdot \Delta w_i$), and absolute valuation variance.

### Cryptographic Provenance, Quality Tiers & Security
934. **Cryptographic Input Hashing (`sha256`)**: Generated SHA-256 digests over valuation timestamps, position identifiers, taxonomy version tags, and look-through parameters for regulatory auditability and tamper detection.
935. **Data Completeness Tiers**: Classified mapping status into `COMPLETE`, `COMPLETE_WITH_FALLBACKS`, `PARTIAL_UNMAPPED`, and `INCOMPLETE`, logging unmapped security counts and missing price indicators.
936. **Comprehensive Typed Error Hierarchy**: Implemented domain exceptions including `PortfolioExposureNavInvalidError`, `PortfolioExposureLookThroughCycleError`, `PortfolioExposureReconciliationFailedError`, and `PortfolioExposureUnknownInstrumentError`.
937. **FastAPI REST Exposure Endpoints**: Exposed 17 high-performance REST endpoints under `/api/v1/portfolios/{portfolio_id}/exposures/...` with comprehensive filtering and Pydantic V2 DTOs.
938. **Multi-Tenant Isolation & Ownership Enforcement**: Enforced strict tenant isolation, verifying portfolio ownership before generating or serving exposure analytics and returning HTTP 403/404 on cross-tenant access.

### Bloomberg-Style Professional Frontend Workspaces
939. **Integrated `/portfolios` Allocation Workspace**: Built professional Bloomberg-style workspace under the "Allocation & Exposures" tab featuring KPI summary cards, interactive sector and asset-class panels, geographic policy switchers, currency exposure views, concentration quantile ladders, ETF look-through inspector, cross-fund overlap matrix, and date-to-date drift tables.
940. **Strict Roadmap Boundaries & Deferrals**: Stage 112 exclusively delivers portfolio allocation, exposure intelligence, concentration, look-through, and drift analytics. Strictly deferred Stage 113 (Portfolio Attribution / Brinson-Fachler), Stage 114 (Portfolio Optimization / Markowitz / Black-Litterman), Stages 115–118 (Risk / VaR / Stress Testing), and Stages 143–149 (Order Execution / Automated Trading). Zero live broker order execution.


## Stage 113: Portfolio Performance Attribution Architecture (Decisions 941–970)

### Attribution Foundations & Mathematical Models
941. **Brinson-Fachler Arithmetic Decomposition (1985)**: Adopted Brinson-Fachler arithmetic decomposition as the primary institutional attribution engine, subtracting the total benchmark return from sector returns to evaluate active allocation decisions ($A_k = (w_{P,k} - w_{B,k})(R_{B,k} - R_B)$) and penalize overweighting in underperforming sectors.
942. **Brinson-Hood-Beebower Baseline Support (1986)**: Implemented Brinson-Hood-Beebower ($A_k = (w_{P,k} - w_{B,k}) R_{B,k}$) alongside Brinson-Fachler to ensure historical comparability and reconciliation with legacy institutional custodial systems.
943. **Selection Effect Formulation**: Formulated selection effect as benchmark-weighted active segment return ($S_k = w_{B,k}(R_{P,k} - R_{B,k})$), measuring manager stock-picking skill isolated from weighting differences.
944. **Interaction Cross-Product Term**: Isolated the interaction effect ($I_k = (w_{P,k} - w_{B,k})(R_{P,k} - R_{B,k})$) as the non-linear cross-product between allocation decisions and security selection.
945. **Total Segment Effect Identity**: Guaranteed that the sum of allocation, selection, and interaction effects equals total segment effect ($E_k = A_k + S_k + I_k$), preserving segment-level additivity.
946. **Part XVII Brinson-Fachler Reference Fixture Verification**: Mathematically validated Part XVII two-sector reference fixture: Portfolio ($60\%$ Tech @ $12.0\%$, $40\%$ Fin @ $5.0\%$, $R_P = 9.20\%$) vs Benchmark ($50\%$ Tech @ $10.0\%$, $50\%$ Fin @ $4.0\%$, $R_B = 7.00\%$) yields exact Active Return $+2.20\%$, Allocation $+0.60\%$, Selection $+1.50\%$, Interaction $+0.10\%$, and Residual $0.00\%$.
947. **Part XVIII Brinson-Hood-Beebower Reference Fixture Verification**: Mathematically validated Part XVIII BHB reference fixture on the two-sector portfolio, confirming BHB allocation Tech $+1.00\%$ and Fin $-0.40\%$ yielding $+0.60\%$ total allocation.

### Benchmark Constituent Snapshots & Point-in-Time Alignment
948. **Point-in-Time Benchmark Snapshot Engine**: Engineered `BenchmarkCompositionEngine` fetching historical constituent weights and returns aligned to evaluation dates, supporting S&P 500, SPY ETF, NASDAQ-100, and MSCI ACWI.
949. **Missing Benchmark Constituent Guardrails**: Enforced strict validation: when benchmark constituent data is unavailable, ATLAS returns `BENCHMARK_CONSTITUENTS_MISSING` and retains simple Stage 111 benchmark comparison rather than synthesizing artificial holdings.
950. **Absent Category Handling ($w_P = 0$)**: Engineered absent portfolio category logic where benchmark sectors not held by the portfolio ($w_{P,k} = 0$) contribute purely to allocation effect ($A_k = -w_{B,k}(R_{B,k} - R_B)$) with zero selection and interaction.
951. **Off-Benchmark Categories & Cash Drag**: Engineered off-benchmark category logic ($w_{B,k} = 0$) where cash and unbenchmarked holdings generate zero allocation under Brinson-Fachler and allocate residual excess performance into the interaction term ($w_{P,k}(R_{P,k} - R_B)$), cleanly isolating cash drag without distorting core sectors.

### Security-Level Return Contributions & Rankings
952. **Absolute Return Contribution Engine**: Engineered `SecurityContributionEngine` decomposing total portfolio return into security-level contributions ($C_j = w_{P,j} \cdot R_{P,j}$), with total sum strictly reconciling to portfolio return ($\sum C_j \equiv R_P$).
953. **Part XXVII Security Contribution Fixture Verification**: Mathematically validated Part XXVII reference fixture: $50\%$ AAPL ($+10.0\%$) and $50\%$ JPM ($-4.0\%$) yields $+5.00\%$ AAPL contribution, $-2.00\%$ JPM contribution, and $+3.00\%$ total portfolio return.
954. **Top 5 Contributors & Detractors Spotlight**: Implemented automatic ranking isolating the top 5 alpha-generating holdings and top 5 alpha-detracting holdings for executive PM briefings.

### Multi-Currency Decomposition & International Attribution
955. **Three-Way Currency Decomposition Engine**: Implemented `CurrencyAttributionEngine` decomposing unhedged foreign holdings into local market return, currency rate movement, and compounding cross-product interaction ($R_{base} = R_{local} + R_{FX} + R_{local} \cdot R_{FX}$).
956. **Part XXXVI Currency Reference Fixture Verification**: Mathematically validated Part XXXVI reference fixture: Local $+10.00\%$ with FX appreciation $+12.50\%$ generates $+1.25\%$ cross-product and exact $+23.75\%$ base currency return ($1.10 \times 1.125 - 1 = 0.2375$).
957. **Multi-Currency Cash & Instrument Isolation**: Segmented portfolio weight by quotation and settlement currency, cleanly delineating foreign equity market returns from cash currency balances.

### Multi-Period Compounding (Carino Logarithmic Linking)
958. **Carino Logarithmic Linking Engine**: Built `MultiPeriodLinkingEngine` executing Carino (1999) logarithmic scaling to compound discrete sub-period arithmetic attributions into multi-period cumulative active returns.
959. **Limiting Case Domain Protection**: Engineered mathematical limiting case handling when $R_{P,t} \to R_{B,t}$, using Taylor series expansion ($c_t \to \frac{1}{1 + R_{B,t}} \frac{R_P - R_B}{\ln(1 + R_P) - \ln(1 + R_B)}$) to prevent division-by-zero singularities.
960. **Positive Gross Return Domain Guardrail**: Enforced domain bounds ($1 + R > 0$) preventing undefined logarithmic evaluations under catastrophic portfolio loss scenarios.
961. **Multi-Period Additivity Identity Verification**: Mathematically validated that sum of scaled period effects ($\sum c_t (A_t + S_t + I_t)$) matches cumulative active return ($R_P^{comp} - R_B^{comp}$) within $10^{-6}$ precision.

### Mathematical Reconciliation & Data Quality Guardrails
962. **Five-Point Independent Audit Engine**: Implemented `AttributionReconciliationEngine` verifying 5 simultaneous checks: portfolio return reconstruction, benchmark return reconstruction, active return additivity, security contribution consistency, and residual tolerance.
963. **Strict Residual Tolerance Threshold**: Established strict $1.0\text{ bps}$ ($10^{-4}$) maximum residual tolerance, flagging any run exceeding tolerance as `UNRECONCILED`.
964. **Cryptographic SHA-256 Provenance Hashing**: Computed deterministic SHA-256 digests across portfolio holdings, prices, tax-lots, and benchmark constituent tables for tamper-evident regulatory compliance.
965. **Data Completeness & Coverage Tiers**: Classified input quality into `FULL_COVERAGE`, `PARTIAL_COVERAGE`, `BENCHMARK_CONSTITUENTS_MISSING`, and `UNMAPPED_CATEGORIES`, tracking coverage ratios.

### Error Hierarchy, REST API & Tenant Isolation
966. **Typed Attribution Domain Exception Hierarchy**: Built comprehensive typed exception hierarchy (`PortfolioAttributionBenchmarkNotFoundError`, `PortfolioAttributionReconciliationFailedError`, `PortfolioAttributionAccessDeniedError`, etc.) mapped to HTTP status codes.
967. **14 High-Performance REST Endpoints**: Implemented complete REST router under `/api/v1/portfolios/{portfolio_id}/attribution/...` covering runs, effects, securities, sectors, industries, currencies, history, linked multi-period, reconciliation, and benchmarks.
968. **Strict Multi-Tenant Isolation Enforcement**: Enforced ownership verification across all attribution calculations and cached retrieval endpoints, returning HTTP 403/404 for unauthorized cross-tenant requests.

### Bloomberg-Style Professional Attribution Workspaces
969. **Bloomberg-Style Performance Attribution Workspace**: Built high-density frontend workspace under the `/portfolios` "Attribution Analytics" tab featuring summary KPI cards, interactive waterfall chart, sector attribution table with expandable sub-industries, security contribution ranking, Carino multi-period table, currency decomposition view, benchmark inspector, methodology formulas, and audit reconciliation panel.
970. **Strict Roadmap Boundaries & Deferrals**: Stage 113 exclusively delivers portfolio performance attribution, Brinson decomposition, security return contributions, and Carino multi-period linking. Strictly deferred Stage 114 (Portfolio Optimization / Markowitz / Black-Litterman), Stages 115–118 (Risk / VaR / Stress Testing), and Stages 143–149 (Order Execution / Automated Trading). Zero live broker trading.


## Stage 114: Portfolio Optimization & Quantitative Construction Platform (Decisions 971–1000)

### Mathematical Formulations & Optimization Solvers
971. **Convex Optimization Solver Foundation**: Standardized on SciPy `SLSQP` (Sequential Least Squares Programming) with analytical Jacobians for constrained quadratic portfolio optimization and `L-BFGS-B` for unconstrained risk-parity logarithmic barriers.
972. **Mean-Variance Quadratic Utility Formulation**: Formulated mean-variance utility as minimizing $\frac{1}{2} w^T \Sigma w - \lambda w^T \mu$, with analytical gradient $\nabla f(w) = \Sigma w - \lambda \mu$, providing smooth monotonic transitions across the risk-return spectrum as risk aversion parameter $\lambda$ varies.
973. **Analytical Minimum-Variance Portfolio**: Formulated minimum-variance optimization as minimizing $w^T \Sigma w$ subject to budget $\sum w_i = 1$ and non-negativity bounds $w_i \ge 0$, reproducing exact closed-form two-asset solutions ($w_1 = \frac{\sigma_2^2 - \sigma_{12}}{\sigma_1^2 + \sigma_2^2 - 2\sigma_{12}}$) within $< 10^{-6}$ precision.
974. **Part XXIX Analytical Fixture Verification**: Mathematically validated Part XXIX reference fixture of two uncorrelated assets with variances $0.04$ and $0.09$, confirming numerical solver converges to exact analytical weights $w_A = \frac{9}{13} \approx 69.23077\%$ and $w_B = \frac{4}{13} \approx 30.76923\%$ with portfolio variance $\sigma_p^2 = \frac{4.68}{169} \approx 0.0276923$.
975. **Maximum Sharpe Ratio Tangency Formulation**: Implemented tangency portfolio solver maximizing $\frac{w^T \mu - r_f}{\sqrt{w^T \Sigma w}}$ subject to budget and position constraints, isolating the optimal capital allocation line contact point.
976. **Target-Return Minimum Variance**: Implemented quadratic constrained formulation minimizing variance subject to an explicit expected return floor constraint $w^T \mu \ge R_{target}$.
977. **Maximum Return Formulation**: Implemented linear programming solver maximizing expected return $w^T \mu$ subject to risk, sector, and individual security concentration boundaries.
978. **Spinu Equal Risk Contribution (Risk Parity) Log-Barrier**: Adopted Florin Spinu's (2013) convex logarithmic barrier formulation $\min_{y > 0} \frac{1}{2} y^T \Sigma y - c \sum \ln(y_i)$ solved via `L-BFGS-B` with analytical gradient $\nabla f(y) = \Sigma y - \frac{c}{y}$, followed by normalization $w_i^* = \frac{y_i^*}{\sum y_j^*}$, ensuring unique global convergence and equal marginal risk contributions ($w_i (\Sigma w)_i = w_j (\Sigma w)_j$) within $< 10^{-6}$ discrepancy.
979. **Benchmark-Aware Tracking Error Optimization**: Engineered benchmark-relative active weight optimization minimizing active variance $(w - w_B)^T \Sigma (w - w_B)$ subject to active sector and stock bounds.

### Covariance & Expected Return Estimation
980. **Ledoit-Wolf Diagonal Shrinkage Covariance**: Implemented Ledoit-Wolf (2004) shrinkage estimator $\Sigma_{LW} = \delta F + (1 - \delta) S$ toward a constant correlation diagonal target, guaranteeing well-conditioned out-of-sample covariance matrices.
981. **Positive Semi-Definite (PSD) Verification**: Enforced mandatory eigenvalue inspection verifying $\lambda_{\min}(\Sigma) \ge 10^{-7}$, automatically injecting diagonal loading jitter ($10^{-6} \cdot I$) if numerical singularity or indefiniteness is detected.
982. **Condition Number Health Monitoring**: Tracked covariance condition numbers $\kappa(\Sigma) = \frac{\lambda_{\max}}{\lambda_{\min}}$ to detect multicollinearity across highly correlated holdings.
983. **Pluggable Expected Return Models**: Implemented historical arithmetic mean, explicit user assumptions, and shrinkage mean models, annualizing return projections deterministically with 252-day convention.

### Constraint Modeling & Feasibility Validation
984. **Pre-Check Feasibility Engine**: Engineered `ConstraintEngine.precheck_feasibility` validating budget compatibility before solver invocation, preventing avoidable solver timeouts and cryptic numerical failures.
985. **Part LXIV Infeasible Constraint Fixture Verification**: Mathematically validated Part LXIV reference fixture where 4 assets capped at $20\%$ each sum to a maximum total weight of $80\% < 100\%$, verifying instant detection and informative conflict reporting.
986. **Comprehensive Institutional Constraint Taxonomy**: Supported 15 typed constraints including `FULLY_INVESTED`, `LONG_ONLY`, `SECURITY_WEIGHT_BOUND`, `SECTOR_WEIGHT_BOUND`, `CASH_WEIGHT_BOUND`, `TURNOVER_LIMIT`, `VOLATILITY_LIMIT`, and `FROZEN_HOLDING`.
987. **KKT Slacks & Binding Constraint Evaluator**: Computed post-solve boundary slacks $s_j = \text{bound} - g_j(w^*)$, identifying active/binding constraints exerting non-zero shadow prices on the portfolio objective.

### Efficient Frontier & Rebalancing Proposals
988. **Pareto-Optimal Efficient Frontier Builder**: Engineered discrete frontier tracing across $M$ target returns with quadratic minimum-variance solving, strict dominated-point filtering ($\sigma_i < \sigma_j$ for $R_i \le R_j$), and Sharpe calculation per point.
989. **One-Way Portfolio Turnover Engine**: Computed rebalancing turnover as $\frac{1}{2} \sum |w_{i,\text{cand}} - w_{i,\text{curr}}|$, quantifying transaction volume required to rotate into target allocations.
990. **Self-Funding Verification & Cash Drag Prevention**: Enforced self-funding check where net rebalancing trade value $\sum \Delta V_i$ matches candidate cash weight shift, ensuring zero cash leakage.
991. **Proportional Transaction Cost Modeling**: Modeled rebalancing frictional costs ($10\text{ bps}$ default rate) applied to absolute trade values $|\Delta V_i|$.
992. **Line-Item Proposed Orders Generation**: Derived trade recommendations with trade direction (BUY/SELL/HOLD), current vs target weights, value deltas, and estimated fees.

### Parameter Sensitivity & Stress Testing
993. **Alpha Shock Sensitivity Scenario**: Evaluated portfolio weight stability under $+100\text{ bps}$ uniform expected return shocks, assessing target allocation drift.
994. **Risk Aversion Spectrum Testing**: Evaluated portfolio solutions across conservative ($\lambda = 4.0$) and aggressive ($\lambda = 1.0$) investor utility settings, tracking asset weight migrations.
995. **Deterministic Provenance Digesting**: Generated cryptographic SHA-256 digests across expected return vectors, covariance matrices, constraint sets, and baseline NAV, guaranteeing reproducible optimization audits.

### Domain Errors, REST API & Security
996. **Typed Optimization Domain Exception Hierarchy**: Built 15 typed domain exceptions (`PortfolioOptimizationInfeasibleError`, `PortfolioOptimizationConvergenceError`, `PortfolioOptimizationCovarianceSingularError`, etc.) mapped to HTTP status codes.
997. **15 Institutional REST Endpoints**: Implemented complete REST router under `/api/v1/portfolios/{id}/optimization/...` covering studies, runs, latest candidate, frontier, comparisons, diagnostics, universe, constraints validation, and methodologies.
998. **Strict Multi-Tenant Isolation Enforcement**: Enforced ownership verification across all optimization studies, runs, and validation checks, returning HTTP 403/404 for cross-tenant access.

### Bloomberg-Style Professional Optimization Workspaces
999. **Bloomberg-Style Optimization Workspace**: Built professional frontend workspace under `/portfolios` "Optimization & Frontier" tab featuring Summary KPI cards, Interactive SVG Efficient Frontier chart, Current vs Candidate comparative table, Sector & Security Allocation shift chart, Constraint Builder with instant Feasibility Checker, Feasibility & Slacks Panel, Hypothetical Trade Proposals table with prominent institutional non-execution disclaimer, Solver Diagnostics inspector, Sensitivity Scenarios grid, Methodology Inspector, and Study Manager.
1000. **Strict Roadmap Boundaries & Deferrals**: Stage 114 exclusively delivers portfolio optimization, quantitative asset allocation, efficient frontier modeling, and rebalancing proposals. Strictly deferred Stages 115–118 (Portfolio Risk / VaR / Stress Testing / Liquidity), Stage 143 (Backtesting), Stage 144 (Paper Trading), Stage 145 (Broker Sandbox), and Stages 146–149 (Autonomous Agents & Auto-Execution). Optimization candidates are analytical decision-support tools and never mutate the Stage 110 accounting ledger or place live market orders.


## Stage 115: Portfolio Risk Foundation and Core Market-Risk Analytics

### Canonical Risk Architecture & Subject Hierarchy
1001. **Universal Risk Subject Hierarchy**: Established standard `RiskSubject` model polymorphic across `PORTFOLIO`, `ACCOUNT`, `BENCHMARK`, and individual `SECURITY`, enabling unified risk calculation pipelines across single and aggregated holdings.
1002. **Decoupled Read-Only Decision Support**: Enforced strict architectural boundary ensuring risk engines operate purely as read-only analytical decision support, never mutating Stage 110 accounting transactions, positions, or cash balances, and never executing live orders.
1003. **Typed Risk Domain Exception Hierarchy**: Built 24 typed domain exceptions inheriting from `RiskError` (`RiskInsufficientObservationsError`, `RiskBenchmarkVarianceZeroError`, `RiskCovarianceNotPositiveSemiDefiniteError`, `RiskDataCoverageDegradedError`, etc.) mapped to HTTP status codes.
1004. **Central Metric & Model Registries**: Established formal metadata registries for 16 risk metrics and 7 risk model engines with mathematical formulations, annualization factors, allowed metrics, and explicit limitations.

### Volatility & Annualization Standards
1005. **Bessel-Corrected Sample Variance**: Enforced sample variance $s^2 = \frac{1}{T-1} \sum (R_t - \bar{R})^2$ using degrees of freedom $N-1$ (Bessel correction), strictly avoiding downward-biased population variance $N$ for finite sample series.
1006. **Square-Root-of-Time Annualization Convention**: Annualized volatility as $\sigma_{annual} = s \sqrt{K}$ with standard period constants ($K = 252$ for daily, $K = 52$ for weekly, $K = 12$ for monthly), with explicit methodology disclosure of i.i.d. assumptions.
1007. **Part XV Mathematical Reference Verification**: Validated reference fixture with 4 alternating returns $[+1\%, -1\%, +1\%, -1\%]$, yielding sample mean $0.0$, variance $\frac{0.0004}{3}$, period volatility $\approx 1.1547\%$, and annualized volatility ($K=252$) $\sigma_{annual} \approx 18.3303\%$.
1008. **No-Hindsight Rolling Volatility Engine**: Enforced rolling window calculations computed strictly on past observations with rolling window sizes (20D, 60D, 120D, 252D) and completeness checks.

### Drawdown & High Watermark Analytics
1009. **Cash-Flow-Neutral Wealth Index Foundation**: Reused Stage 111 cash-flow-adjusted wealth index $W_t$ to ensure capital additions and withdrawals do not artificially trigger or erase drawdowns.
1010. **Running Peak High Watermark Tracking**: Derived running peak $P_t = \max_{0 \le \tau \le t} W_\tau$ and continuous drawdown series $D_t = \frac{W_t}{P_t} - 1.0$.
1011. **Part XXI Drawdown Reference Verification**: Validated reference fixture with wealth index $[100, 120, 90, 99, 130]$, producing peak 120, trough 90, maximum drawdown $-25.0\%$, and empirical recovery at observation index 4 ($130 > 120$).
1012. **Drawdown Episode Extraction**: Engineered episode segmenter extracting discrete episodes with peak date/level, trough date/level, maximum drawdown, time to trough, recovery date, recovery duration, and recovery status (`RECOVERED` vs `ONGOING`).

### Benchmark Sensitivity & Systematic Risk
1013. **Timestamp-Aligned Covariance & Correlation**: Synchronized portfolio and benchmark return time series on exact matching observation dates, eliminating mismatched holiday and weekend artifacts.
1014. **Part XXVIII Benchmark Reference Verification**: Validated reference fixture with portfolio returns $R_P = 2 R_B$, confirming beta $\beta = \frac{Cov(P, B)}{Var(B)} = 2.0$ and Pearson correlation $\rho = 1.0$ within $< 10^{-6}$ precision.
1015. **Zero Benchmark Variance Exception Handling**: Detected degenerate constant or zero-variance benchmarks, raising `RiskBenchmarkVarianceZeroError` and gracefully surfacing `ZERO_VARIANCE` metric status.
1016. **Active Tracking Error Measurement**: Calculated annualized tracking error $TE = \sqrt{252} \cdot s_{P - B}$ quantifying active dispersion relative to the benchmark.

### Covariance Diagnostics & Euler Risk Decomposition
1017. **Positive Semi-Definite (PSD) Validation**: Enforced mandatory eigenvalue inspection verifying minimum eigenvalue $\lambda_{\min}(\Sigma) \ge 10^{-7}$, automatically injecting Ledoit-Wolf diagonal loading jitter if ill-conditioned.
1018. **Condition Number Health Monitoring**: Evaluated matrix condition number $\kappa(\Sigma) = \frac{\lambda_{\max}}{\lambda_{\min}}$ to alert on collinearity across portfolio constituents.
1019. **Euler Volatility Decomposition**: Implemented Euler's homogeneous theorem decomposing portfolio volatility $\sigma_P = \sqrt{w^T \Sigma w}$ into Marginal Contributions $MRC_i = \frac{(\Sigma w)_i}{\sigma_P}$ and Component Contributions $CRC_i = w_i \cdot MRC_i$.
1020. **Part XXXV & XL Euler Additivity Verification**: Validated reference fixture of 2 uncorrelated assets with $\Sigma = \text{diag}(0.04, 0.09)$ and weights $w=[0.5, 0.5]$, verifying portfolio variance $\sigma_P^2 = 0.0325$, volatility $\sigma_P \approx 18.0278\%$, percentage contributions $PCR = [30.7692\%, 69.2308\%]$, and strict Euler additivity $\sum CRC_i \equiv \sigma_P$ and $\sum PCR_i \equiv 1.0$.
1021. **Negative Risk Contribution Preservation**: Preserved signed negative contributions for short positions, inverse funds, and negatively correlated hedging assets, reflecting genuine risk-reducing properties.

### Multi-Currency & Data Quality Governance
1022. **Geometric Multi-Currency Return Compounding**: Compounded local and FX returns geometrically via $1 + R_{base} = (1 + R_{local})(1 + R_{FX})$, avoiding first-order linear approximation errors.
1023. **Observation Coverage & Gap Auditing**: Tracked required vs available vs matched observations, generating data coverage health badges (`FULL`, `ACCEPTABLE`, `DEGRADED`, `CRITICAL_GAPS`) and reporting missing intervals.
1024. **Reproducible Calculation Manifests**: Bound every risk calculation to an immutable `RiskInputManifest` containing valuation IDs, performance run IDs, benchmark IDs, parameters, and an audit hash.

### REST API & Frontend Risk Terminal
1025. **13 Production REST Endpoints**: Implemented complete REST router under `/api/v1/risk/...` covering metrics, models, calculations, input sources, portfolio summaries, historical volatility, drawdowns, benchmark sensitivity, contributions, data quality, and audit runs.
1026. **Strict Multi-Tenant Isolation**: Enforced ownership verification across all risk calculations and historical portfolio runs, returning HTTP 403/404 for unauthorized access.
1027. **Dedicated Route `/risk` & Integrated Portfolios Tab**: Rendered the institutional `<RiskTerminalWorkspace />` on the canonical global route `/risk` while also embedding it in `/portfolios` under the "Risk Management" tab.
1028. **Interactive SVG Visualizations**: Engineered high-density interactive charts for rolling volatility with window selection, underwater drawdown valley fills with peak/trough markers, and correlation heatmap matrix with hover inspection.
1029. **Strict Roadmap Scope Boundaries**: Stage 115 focuses strictly on market-risk foundations (volatility, drawdowns, benchmark sensitivity, covariance, Euler contributions). Strictly deferred Value at Risk (VaR) and Expected Shortfall to Stage 116, Stress Testing to Stage 117, Risk Limits and Escalations to Stage 118, and Autonomous Execution to Stages 143–149.

## Stage 116: Build Value at Risk, Expected Shortfall, and Financial Scenario Testing

### Architectural Positioning & Invariant Standards
1030. **Decoupled Read-Only Decision Support**: Tail risk and scenario engines operate purely as read-only analytical decision support, never mutating Stage 110 accounting transactions, positions, or cash balances, and never executing live broker orders.
1031. **Comprehensive Tail Exception Hierarchy**: Added 26 typed domain exceptions (`RiskVaRModelUnsupportedError`, `RiskVaRConfidenceInvalidError`, `RiskVaRHorizonInvalidError`, `RiskScenarioNotFoundError`, `RiskTailRunNotFoundError`, etc.) mapped to appropriate HTTP status codes.
1032. **Three Institutional Tail Risk Models**: Built Historical Simulation (non-parametric), Parametric Delta-Normal (Gaussian analytical), and Monte Carlo Simulation (Gaussian factor paths) with uniform `VaRResult` and `ExpectedShortfallResult` interfaces.

### Historical Simulation & Fractional Tail Integration
1033. **Continuous Empirical Quantile Step Integration**: Implemented exact fractional boundary weighting for empirical Expected Shortfall: ES_alpha = [1 / (1 - alpha)] * integral_{alpha}^1 Q(u) du, accurately scaling the marginal boundary observation k = ceil(alpha * N).
1034. **Part XVI Reference Fixture Verification**: Reconciled historical simulation fixture with 5 daily losses [-2.0%, -1.0%, +0.5%, +1.0%, +3.0%] at alpha = 0.80, verifying VaR = 1.0% (k=4) and ES = 3.0% (k=5).

### Parametric Normal & Closed-Form Gaussian ES
1035. **Closed-Form Gaussian Expected Shortfall**: Derived exact analytical Expected Shortfall under normality: ES_alpha = -mu_h + sigma_h * [phi(z_alpha) / (1 - alpha)], avoiding crude numerical approximations.
1036. **Part XX Reference Fixture Verification**: Reconciled parametric fixture with mu = 0.0, sigma = 0.02 at alpha = 0.95, verifying VaR = 3.2897% and closed-form ES = 4.1254% with leptokurtosis ratio ~1.254x.
1037. **Zero Volatility Degeneracy Protection**: Gracefully handled zero-volatility or single-observation portfolios without division-by-zero crashes.

### Monte Carlo Simulation & Covariance Factorization
1038. **Regularized Covariance Cholesky Decomposition**: Enforced PSD verification on constituent covariance matrix Sigma, applying eigenvalue floor clipping (min_eigenvalue >= 1e-8) before Cholesky factorization Sigma = A A^T.
1039. **Reproducible PRNG Seeding**: Integrated deterministic seed parameterization via numpy's `default_rng(seed)` ensuring identical, auditable Monte Carlo trajectories.

### Multi-Currency Compounding & Scenario Stress Testing
1040. **Multiplicative Multi-Currency Compounding**: Replaced naive linear addition with rigorous geometric compounding R_compound = (1 + s_price)(1 + s_fx) - 1, eliminating first-order approximation errors during severe currency devaluations.
1041. **Part XXXIV Reference Fixture Verification**: Reconciled fixture with -10% asset shock and -5% FX shock, confirming exact compound return of -14.50% (vs naive -15.00%).
1042. **Scenario Collision Precedence Hierarchy**: Enforced strict priority resolution: Security > Industry > Sector > Asset Class > Currency > Portfolio-Wide, allowing specific security stress targets to override broad macroeconomic shocks.
1043. **Exact Position-to-Portfolio Reconciliation**: Enforced mathematical equality: Sum(Delta V_i) === Delta V_P across all position revaluations, raising reconciliation warnings if numerical error exceeds 1e-4.
1044. **Part XLIII Reference Fixture Verification**: Reconciled scenario revaluation fixture with Asset A ($60k at -10% -> $54k, P&L = -$6k) and Asset B ($40k at +5% -> $42k, P&L = +$2k), confirming Shocked NAV = $96k, Portfolio P&L = -$4k, and exact reconciliation diff 0.0000.
1045. **Predefined Historical Episode Catalogue**: Packaged institutional scenario presets for COVID-19 (Feb-Mar 2020), Global Financial Crisis (Sep-Nov 2008), 2022 Tech Rate Hike De-rating, and 2011 US Sovereign Downgrade.

### Model Validation & Kupiec Backtesting
1046. **Kupiec POF Likelihood Ratio Test**: Implemented Kupiec Proportion of Failures test evaluating LR_UC = -2 ln [((1 - p_0)^(N-x) * p_0^x) / ((1 - p_hat)^(N-x) * p_hat^x)] ~ Chi^2(1) with 95% critical value 3.841459.
1047. **Three-Way Coverage Decision Engine**: Categorized backtest results into ACCEPT_UNCONDITIONAL_COVERAGE, REJECT_TOO_MANY_EXCEPTIONS (underestimates risk), and REJECT_TOO_FEW_EXCEPTIONS (overestimates risk), with sample size warnings for N < 30.
1048. **Point-in-Time Rolling Forecast Backtester**: Designed rolling backtester tracking historical 1-step-ahead VaR projections vs realized returns and recording breach margins.

### User Interface & Bloomberg-Style Risk Terminal
1049. **Interactive Tail Risk Sub-Tabs**: Embedded dedicated sub-tabs under `/risk` for "VaR & Expected Shortfall", "Scenario Stress Testing", and "VaR Backtest & Kupiec".
1050. **SVG Loss Distribution Histogram**: Visualized empirical and simulated loss histograms with 25 bins, VaR threshold marker, shaded tail loss region, quantile chips, and hover tooltips.
1051. **Interactive Scenario Builder Modal**: Created dialog enabling multi-shock scenario design across securities, sectors, FX, and portfolio-wide targets with magnitude validation.
1052. **Comparative Stress Matrix**: Rendered comparative table and ranked performance across multiple historical episodes identifying worst-hit portfolio positions.
1053. **Rolling VaR vs Realized Loss Visualization**: Visualized historical backtest trajectories highlighting exception breach dots and tracking exceedance margins.
1054. **Strict Scope Discipline**: Stage 116 is strictly confined to VaR, Expected Shortfall, Scenarios, and Model Backtesting. Derivatives Greeks, Yield Curve Scenarios, and Stress Testing Limits are deferred to subsequent stages.

## Stage 117: Build Multi-Factor, Concentration, Currency, and Sector Risk Intelligence

### Architectural Positioning & System Invariants
1055. **Read-Only Risk Intelligence**: Factor, concentration, currency, and sector risk engines operate strictly as read-only decision-support analytics, never mutating Stage 110 positions, transactions, or cash balances, and never submitting live broker orders or automated rebalancing trades.
1056. **Comprehensive Stage 117 Domain Exceptions**: Added 19 typed domain exceptions (`RiskFactorNotFoundError`, `RiskFactorRegressionRankDeficientError`, `RiskFactorCollinearityDetectedError`, `RiskFactorCovarianceNotPSDError`, `RiskConcentrationInvalidWeightsError`, `RiskSectorReconciliationFailedError`, `RiskCrossExposureDimensionMismatchError`, etc.) mapped to explicit HTTP status codes.

### Systematic Multi-Factor Risk Decomposition
1057. **Canonical Factor Registry**: Implemented platform-wide factor definitions for Market Equity Risk (MKT), Size (SMB), Value (HML), Momentum (MOM), Quality (QMJ), and Investment (CMA) with standard excess return and long/short methodologies.
1058. **Ordinary Least Squares (OLS) Regression Engine**: Estimated security factor loadings with intercept alpha, residual variance s_eps^2 = (1 / df) sum eps^2, R^2, and t-statistics with design matrix rank and condition number diagnostics.
1059. **Part XIV Reference Fixture Verification**: Validated portfolio factor loading aggregation b = B^T w = [1.04, 0.22] for weights w = [0.6, 0.4] and security loading matrix B = [[1.2, 0.5], [0.8, -0.2]].
1060. **Part XXII Systematic vs Specific Euler Decomposition**: Reconciled reference fixture with weights w=[0.6, 0.4], b=[1.04, 0.22], F=diag(0.04, 0.01), and d=[0.0225, 0.0100], confirming V_sys = 0.043748, V_spec = 0.009700, V_total = 0.053448, sigma_P ~= 23.11882%, VC_MKT = 0.043264, VC_HML = 0.000484, and exact Euler additivity sum VC_k + V_spec === V_total.
1061. **Benchmark-Relative Active Factor Exposures**: Evaluated active factor tilts b_A = b_P - b_B relative to benchmark factor profiles.

### Concentration & Diversification Diagnostics
1062. **Herfindahl-Hirschman Index (HHI)**: Implemented HHI = sum w_i^2 across normalized portfolio capital partitions to quantify capital concentration.
1063. **Effective Number of Holdings**: Calculated N_eff = 1 / HHI representing the equivalent number of equally-weighted independent securities.
1064. **Top-N Cumulative Capital Concentration**: Evaluated cumulative sums for Top 1, Top 3, Top 5, and Top 10 holdings.
1065. **Part XXXI Reference Fixture Verification**: Reconciled fixture with w = [0.5, 0.3, 0.2], verifying HHI = 0.3800, N_eff ~= 2.63158, Top 1 = 50.00%, and Top 2 = 80.00%.
1066. **Canonical Issuer Consolidation**: Aggregated multi-share classes (e.g. Alphabet GOOG & GOOGL) and ADRs into consolidated issuer entities using the Stage 112 classification registry.
1067. **Multi-Dimensional Partitioning**: Extended concentration evaluation across Security, Issuer, Sector, Industry, Asset Class, Country, and Currency dimensions.

### Currency Risk & FX Sensitivity
1068. **Denomination Exposure Breakdown**: Partitioned portfolio market value and foreign cash balances across currency denominations.
1069. **Realized Annualized FX Volatility**: Evaluated sample standard deviation of discrete exchange rate returns annualized via sqrt(252).
1070. **Empirical FX Sensitivity Beta**: Computed regression beta beta_FX = Cov(R_P, R_FX) / Var(R_FX) to quantify portfolio currency sensitivity.
1071. **Part XLIV Discrete FX Multiplicative Compounding**: Replaced naive linear addition with rigorous discrete compounding 1 + R_base = (1 + R_local)(1 + R_FX) ⟹ R_base = R_local + R_FX + R_local * R_FX, reconciling Local +10%, FX -5%, Interaction -0.5%, Base +4.5%.

### Sector and Industry Euler Risk Attribution
1072. **Sector Euler Variance Contribution**: Decomposed covariance risk across sectors via VC_s = sum_{i in s} w_i (Sigma w)_i and volatility contribution RC_s = VC_s / sigma_P.
1073. **Part LVII Sector Risk Fixture Verification**: Reconciled fixture with Tech 50%, Fin 50%, Sigma = diag(0.04, 0.09), confirming V_P = 0.0325, VC_Tech = 0.0100, VC_Fin = 0.0225, and exact additivity VC_Tech + VC_Fin === V_P.
1074. **Industry Hierarchy Drilldown**: Enabled hierarchical drilldown from Sector into Industry and constituent securities.
1075. **Active Sector Benchmark Tilts**: Evaluated active sector weights w_A,s = w_s - w_B,s relative to standard benchmark sector profiles.

### 2D Cross-Exposure Intelligence
1076. **Factor by Sector 2D Matrix**: Constructed b_s,k = sum_{i in s} w_i beta_{i,k} with strict row-sum reconciliation sum_s b_s,k === b_k.
1077. **Currency by Sector 2D Matrix**: Evaluated joint capital allocation across currency denominations and economic sectors.

### REST API, UI Workspaces & Scope Boundaries
1078. **16 Production REST Endpoints**: Implemented complete REST router under `/api/v1/risk/...` covering factor catalog, factor calculation, exposures, contributions, diagnostics, concentration snapshots, issuer consolidation, currency risks, sector attribution, cross-exposures, and benchmark active factors.
1079. **Interactive Bloomberg-Style UI Workspaces**: Built `<FactorRiskWorkspace />`, `<ConcentrationWorkspace />`, `<CurrencyRiskWorkspace />`, `<SectorRiskWorkspace />`, and `<CrossExposureWorkspace />` embedded in `/risk`.
1080. **Strict Roadmap Scope Discipline**: Options Greeks (Delta, Gamma, Vega, Theta, Rho), Fixed-Income Duration, Convexity, DV01, Key Rate Duration, and credit spread duration are strictly deferred to Stage 118.

## Stage 118: Build Options and Fixed-Income Risk Foundations

### Architectural Positioning & System Invariants
1081. **Read-Only Derivatives & Bond Analytics**: Options Greeks and Fixed-Income duration/convexity/DV01 calculations operate strictly as read-only decision-support risk intelligence, never mutating Stage 110 positions, transactions, or cash balances, and never submitting live broker orders or automated hedging trades.
1082. **Comprehensive Stage 118 Domain Exceptions**: Added 25 typed domain exceptions (RiskOptionContractIncompleteError, RiskOptionExerciseStyleUnsupportedError, RiskOptionExpiredError, RiskOptionImpliedVolatilityNonPositiveError, RiskOptionUnderlyingPriceNonPositiveError, RiskOptionStrikeNonPositiveError, RiskOptionTimeToExpiryNegativeError, RiskOptionMultiplierInvalidError, RiskOptionParityCheckFailedError, RiskBondCashflowIncompleteError, RiskBondYieldSolverFailedError, RiskBondCleanPriceNonPositiveError, RiskBondDirtyPriceNonPositiveError, RiskBondMaturityBeforeSettlementError, RiskBondCouponFrequencyInvalidError, RiskBondDayCountConventionUnsupportedError, RiskBondFaceValueNonPositiveError, RiskBondKeyRateTenorInvalidError, RiskBondCurveMissingError, etc.) mapped to explicit HTTP status codes.

### Black-Scholes-Merton Options Pricing & Greek Sensitivities
1083. **Closed-Form European BSM Engine**: Implemented standard Black-Scholes-Merton model for European calls and puts: d1 = [ln(S/K) + (r - q + 0.5 * sigma^2)T] / (sigma * sqrt(T)), d2 = d1 - sigma * sqrt(T), C = S e^(-qT) N(d1) - K e^(-rT) N(d2), and P = K e^(-rT) N(-d2) - S e^(-qT) N(-d1).
1084. **Analytical Greek Formulations**:
   - Delta (Δ): Call Delta = e^(-qT) N(d1), Put Delta = -e^(-qT) N(-d1) = e^(-qT) [N(d1) - 1.0].
   - Gamma (Γ): Identical for Call and Put: Gamma = [e^(-qT) phi(d1)] / [S * sigma * sqrt(T)].
   - Vega (V): Identical for Call and Put: Vega_unit = S e^(-qT) phi(d1) sqrt(T); Vega per 1% vol point = 0.01 * Vega_unit.
   - Theta (Θ): Calendar-year Theta_year and calendar-day Theta_day = Theta_year / 365.
   - Rho (ρ): Unit rate Rho_unit and basis-point Rho_1bp = 0.0001 * Rho_unit.
1085. **Part XVII Reference Fixture Verification**: Reconciled European Call BSM parameters to 10 decimal places with S=100, K=100, r=0.05, q=0.0, sigma=0.20, T=1.0:
   - Call Price = 10.4505835722
   - Delta = 0.6368306512
   - Gamma = 0.01876201735
   - Vega (unit vol) = 37.5240346917
   - Vega (per 1% vol point) = 0.3752403469
   - Theta (calendar year) = -6.4140275464
   - Theta (calendar day, /365) = -0.0175726782
   - Rho (unit rate) = 53.2324815454
   - Rho (per 1 bp) = 0.0053232482
   - Intrinsic Value = 0.0, Time Value = 10.4505835722
   - Put-Call Parity Difference < 1e-10.
1086. **Exact Put-Call Parity Balance**: Enforced no-arbitrage condition C - P = S e^(-qT) - K e^(-rT) with automated validation diagnostics.
1087. **Finite-Difference Bump Verification**: Validated analytical Greeks against central finite difference perturbations (Delta_num, Gamma_num, Vega_num) within 1e-4 tolerance.

### Position Multipliers & Nonlinear Taylor Repricing
1088. **Position Multiplier Scaling (QM = Q × M)**: Formally scaled per-contract Greeks by total contracts quantity Q and contract multiplier M (e.g. 100 shares per equity option contract), ensuring position Delta units = QM * Delta, Delta notional = QM * Delta * S, and Vega = QM * Vega_1vp.
1089. **Part XXI Reference Fixture Verification**: Reconciled 2 Long Contracts x 100 Multiplier (QM = 200) on the reference call, verifying Delta Units = 127.3661302, Delta-Equivalent Notional = ,736.61302, and Vega per 1% vol point = 75.04806938.
1090. **Nonlinear Taylor Approximation vs Full Model Repricing**: Evaluated simultaneous Greek Taylor series dV ~= Delta * dS + 0.5 * Gamma * dS^2 + Vega * dvol - Theta * dt + Rho * dr against exact full BSM model re-evaluations across spot (+/-1%), implied volatility (+/-1 pt), interest rates (+25 bps), and 1-day time decay shocks.
1091. **Portfolio-Level Net vs Gross Derivatives Aggregation**: Aggregated Net Delta Notional (directional exposure), Gross Delta Notional (total size), Net Vega, Gross Vega, Net Theta, Net Rho, and underlying asset buckets across all options positions.

### Fixed-Income Cash-Flow Engine & Day-Count Conventions
1092. **Day-Count Accrual Mechanics**: Implemented exact year-fraction calculations across Actual/Actual (ACT_ACT), Actual/365 Fixed (ACT_365F), Actual/360 (ACT_360), and 30/360 US/Bond Basis (THIRTY_360).
1093. **Clean Price vs Dirty Price Accounting**: Maintained rigorous market convention Dirty Price = Clean Price + Accrued Interest, correctly accruing interest between previous coupon payment date and settlement date.
1094. **Multi-Period Cash-Flow Schedules**: Projected exact payment dates, periodic coupon cash flows, and principal repayments across Annual, Semi-Annual, Quarterly, and Monthly coupon frequencies.

### Yield to Maturity (YTM) Solver & Duration/Convexity
1095. **Robust Root-Finding YTM Solver**: Implemented Newton-Raphson solver with analytical price derivative dP/dy with automatic bisection fallback across [-0.30, 3.0] yields matching target dirty prices to 1e-9 precision.
1096. **Macaulay & Modified Duration Analytics**: Formulated Macaulay duration D_Mac = (1/P) sum t_j PV(CF_j) and Modified duration D_mod = D_Mac / (1 + y/m) quantifying first-order percentage price sensitivity to interest rate shifts.
1097. **Bond Convexity Curvature**: Formulated analytical convexity C = (1/P) sum [t_j (t_j + 1/m) CF_j] / (1 + y/m)^(m*t_j + 2) capturing second-order curvature effects.
1098. **DV01 / PV01 Risk Measurement**: Computed Dollar Value of an 01 (DV01) as positive risk magnitude P * D_mod * 0.0001 (and position DV01 = MV * D_mod * 0.0001), representing portfolio P&L per +1 bp yield shift.
1099. **Part XLII Reference Fixture Verification**: Reconciled Zero-Coupon Bond fixture (Face=100, T=1.0, Coupon=0%, y=5%, m=1) to 10 decimal places:
   - Price P = 100 / 1.05 = 95.2380952381
   - Macaulay Duration = 1.0
   - Modified Duration = 1 / 1.05 = 0.9523809524
   - Convexity = 2 / (1.05)^2 = 1.8140589569
   - DV01 per 100 Face = 100 / (1.05)^2 * 0.0001 = 0.0090702948.
1100. **Part XLIII Reference Fixture Verification**: Reconciled Two-Year 5% Par Bond fixture (Face=100, Coupon=5% annual, y=5%, T=2, m=1) to 10 decimal places:
   - Cash flows: Year 1 = 5, Year 2 = 105
   - Dirty Price = 5 / 1.05 + 105 / 1.05^2 = 100.0
   - Macaulay Duration = [1(5/1.05) + 2(105/1.05^2)] / 100 = 1.9523809524
   - Modified Duration = 1.9523809524 / 1.05 = 1.8594104308.

### Key-Rate Duration & Term-Structure Sensitivities
1101. **Linear Key-Rate Tenor Allocation**: Allocated individual bond cash flows across standardized key-rate tenor vertices (6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y) using linear triangle weighting w_k = (T_{k+1} - t_j) / (T_{k+1} - T_k).
1102. **Exact Key-Rate Additivity**: Proved and verified that the sum of Key-Rate Durations across all tenors identically equals the bond's Modified Duration (sum KRD_k === D_mod), and sum KRD_DV01_k === DV01, eliminating residual leakage.
1103. **Calibrated Sovereign Yield Curve**: Modeled zero/par rate term structure (1M to 30Y) with exact continuous discount factors DF(T) = exp(-r * T) and linear tenor interpolation.

### Portfolio Synthesis, UI Workspaces & Scope Boundaries
1104. **Cross-Asset Instrument Sensitivities Synthesis**: United direct Equity delta (1.0 per unit), Options Delta-Equivalent Notional ($), and Fixed-Income DV01 ($) into a unified cross-asset risk synthesis under /risk.
1105. **12 Production REST Endpoints**: Implemented complete REST router under /api/v1/risk/... covering options models, option calculation, portfolio options risk summary, position Greeks, underlying buckets, fixed income models, bond calculation, portfolio fixed income summary, bond cash flows, portfolio DV01, yield curves, and cross-asset sensitivities.
1106. **Professional Bloomberg-Style Terminals**: Delivered <OptionsRiskWorkspace /> and <FixedIncomeRiskWorkspace /> featuring real-time Greeks calculation, nonlinear shock comparison, cash flow schedule drilldown, key-rate term structure, and yield curve visualization.
1107. **Strict Roadmap Scope Discipline**: Global Saved module (/saved), full exchange-grade options order routing, comprehensive QuantLib bindings, paper trading, and autonomous AI trading agents (Stages 141-149) are strictly deferred.

## Stage 119: Universal Saved System and Cross-Module Library

### Canonical Architecture & Boundaries
1108. **Strict Read-Only Reference Model**: The Saved library strictly stores durable references and view configurations. Saving, modifying metadata for, or deleting a saved reference NEVER mutates underlying financial positions, cash, transactions, research articles, market data, or execution orders.
1109. **Architectural Isolation**:
   - Saved is NOT Watchlists (monitoring instruments vs saving cross-module bookmarks).
   - Saved is NOT Research storage (references only; no document body duplication).
   - Saved is NOT Portfolio or Risk storage (stores reference IDs & analytical view configurations only; never triggers heavy recalculations automatically).
   - Stage 120 (Workspaces: multi-panel desktop layouts, floating panes, tab docking, cross-panel synchronization) is strictly deferred.
1110. **22 Canonical Saved Target Types**: Explicitly registered 22 target types across 14 modules: `INSTRUMENT`, `COMPANY`, `CHART_CONFIG`, `WATCHLIST_REFERENCE`, `SCREENER_CONFIG`, `ECONOMIC_SERIES`, `NEWS_ARTICLE`, `RESEARCH_REPORT`, `RESEARCH_INVESTIGATION`, `RESEARCH_DOCUMENT`, `MAP_LAYER`, `INTELLIGENCE_REPORT`, `OPTIONS_CHAIN_VIEW`, `OPTIONS_STRATEGY`, `TRADING_LAYOUT`, `PORTFOLIO_REFERENCE`, `PORTFOLIO_VIEW_CONFIG`, `PORTFOLIO_ANALYSIS_RUN`, `RISK_RUN`, `RISK_SCENARIO`, `AI_CONVERSATION`, `AI_ARTIFACT`.
1111. **Internal Deep-Link Enforcement**: All generated URLs are strictly relative paths resolved against whitelisted module routes (e.g. `/markets?symbol={id}`, `/charts?id={id}`, `/risk?run_id={id}`). Absolute URLs, external host redirects, protocol injection (`javascript:`, `data:`), and unvalidated route parameters are completely disallowed.
1112. **Idempotent Save Semantics**: Saving the same item multiple times returns the existing record rather than creating duplicates or raising unique constraint errors. Deduplication key is composed of `(user_id, target_type, target_id, target_revision_id, view_configuration_id)`.

### Domain Logic, Configurations & Resolvers
1113. **Thread-Safe Repository Architecture**: Implemented `SavedRepository` using Python's `threading.RLock()` to guarantee memory safety in concurrent execution environments, with optimistic concurrency control via monotonic `row_version` integer counters.
1114. **Hierarchical Collections Tree**: Multi-level hierarchical folder organization with cycle detection (preventing a collection from becoming its own ancestor) and hard depth-bounding enforced at a maximum of 5 levels.
1115. **Normalized Tag Taxonomy**: Tags are automatically sanitized, lowercased, whitespace-trimmed, and validated to alphanumeric and hyphen/underscore characters between 1 and 50 characters in length.
1116. **Safe View Configuration Storage**: View configurations enforce a maximum payload limit of 256 KB, recursive credential scrubbing (`[REDACTED_SECRET]` masking on keys matching `token`, `secret`, `key`, `password`, `auth`), and deterministic SHA-256 payload content hashing.
1117. **Backward-Compatible Configuration Versioning**: View configuration schema migrations (e.g. `ChartConfig` v1 to v2 migration preserving indicators and layout settings) allow seamless upgrades without breaking existing user bookmarks.
1118. **Runtime Target Resolution & 10 Availability Statuses**: Standardized `TargetResolver` evaluates whether the underlying resource still exists, whether its schema has updated, whether the user holds active permissions, and maps results to one of 10 explicit statuses: `AVAILABLE`, `AVAILABLE_WITH_WARNINGS`, `TARGET_UPDATED`, `TARGET_SUPERSEDED`, `PERMISSION_REVOKED`, `SOURCE_RESTRICTED`, `TARGET_DELETED`, `TARGET_NOT_FOUND`, `RESOURCE_UNAVAILABLE`, `UNSUPPORTED_CONFIG_VERSION`.
1119. **Tenant & User Isolation**: Saved items are strictly isolated per `user_id`. Tenant-scoped organization membership is evaluated without ever leaking confidential resource bodies of unauthorized targets.
1120. **Partial Failure Atomic Bulk Operations**: Bulk actions (`TAG`, `UNTAG`, `ADD_TO_COLLECTION`, `REMOVE_FROM_COLLECTION`, `FAVORITE`, `UNFAVORITE`, `PIN`, `UNPIN`, `DELETE`) execute with granular per-item error tracking, returning `BulkResult` indicating processed, succeeded, and failed item IDs with specific reason strings.
1121. **Comprehensive Audit Trail**: Every item creation, modification, note update, tag addition, collection membership change, and deletion produces a typed `SavedAuditEvent` with timestamp, actor ID, action type, and JSON metadata.

### Relational Schema & Persistence
1122. **Seven Dedicated Relational Tables**:
   - `saved_items`: Core bookmark records with user, target, override titles, notes, pin/favorite flags, row version.
   - `saved_collections`: Hierarchical folders with parent IDs, color markers, and descriptions.
   - `saved_collection_memberships`: Many-to-many relationship linking items to collections.
   - `saved_tags`: System and user-defined tags with usage counters.
   - `saved_item_tags`: Many-to-many mapping of items to tags.
   - `saved_view_configurations`: Sanitized JSON configurations with version, schema hash, and type.
   - `saved_audit_events`: Durable append-only audit trail.
1123. **Production Alembic Migration**: Added migration `stage119_universal_saved_system.py` chained cleanly off `stage80_watchlist_alerts`, establishing foreign keys, unique composite indexes, and performance indices on user, type, and creation date.

### REST API Architecture
1124. **19 Production REST Endpoints**: Mounted at `/api/v1/saved` with full authentication and validation:
   - `GET /api/v1/saved/targets`: Catalog of supported target types and schema definitions.
   - `POST /api/v1/saved/items`: Idempotent item creation with optional configuration and collections.
   - `GET /api/v1/saved/items`: Filtered, paginated, sorted search across all saved items.
   - `GET /api/v1/saved/items/{id}`: Detailed item retrieval with resolution status.
   - `PATCH /api/v1/saved/items/{id}`: Metadata update (title, note, pin, favorite).
   - `DELETE /api/v1/saved/items/{id}`: Safe deletion with audit trail.
   - `POST /api/v1/saved/items/{id}/resolve`: Dynamic runtime target resolution.
   - `POST /api/v1/saved/bulk`: Bulk batch mutation across multiple items.
   - `POST /api/v1/saved/collections`: Collection folder creation.
   - `GET /api/v1/saved/collections`: Hierarchical collection tree retrieval.
   - `PATCH /api/v1/saved/collections/{id}`: Collection metadata modification.
   - `DELETE /api/v1/saved/collections/{id}`: Collection deletion (with child item orphan handling).
   - `POST /api/v1/saved/collections/{id}/items`: Batch add items to collection.
   - `DELETE /api/v1/saved/collections/{id}/items`: Batch remove items from collection.
   - `GET /api/v1/saved/tags`: List active tags with usage frequencies.
   - `POST /api/v1/saved/items/{id}/tags`: Tag addition.
   - `DELETE /api/v1/saved/items/{id}/tags/{name}`: Tag removal.
   - `POST /api/v1/saved/configurations`: Safe view configuration storage.
   - `GET /api/v1/saved/configurations/{id}`: Configuration retrieval.

### Frontend UI & Terminal Experience
1125. **Dedicated `/saved` Global Route**: Implemented Next.js page at `apps/web/src/app/(atlas)/saved/page.tsx` within the persistent ATLAS shell, preserving all 20 canonical top-level navigation routes.
1126. **Bloomberg-Style Saved Terminal UI**: Built `<SavedTerminalWorkspace />` featuring dark-mode terminal aesthetics, tabular layouts, monospace numbers, and real-time status badges.
1127. **Three-Pane Operational Layout**:
   - Left Sidebar: Hierarchical collections tree, smart filter categories (Favorites, Pinned, Recent), and tag cloud.
   - Central Stage: Interactive data table and grid view with search, filter tabs, sorting, and floating bulk toolbar.
   - Right Drawer: Inspector pane providing deep link launching, personal note editing, tag assignment, and collection management.
1128. **Dual View Presentation**: Seamless switching between high-density Data Table view (ideal for large libraries) and Card Grid view (visual preview with badges and metadata).
1129. **Floating Multi-Select Toolbar**: Appears dynamically upon item selection, providing batch operations (Add to Collection, Add Tag, Pin, Favorite, Delete) without navigating away.
1130. **Universal `<SaveToLibraryButton />` Component**: Standardized, reusable cross-module button usable across all 14 supported modules with 1-click quick-save and modal customization.
1131. **Modal `<SaveToLibraryDialog />` Component**: Comprehensive dialog allowing title overrides, collection selection, tag input, and personal investment thesis notes at save time.
1132. **In-Place Research Thesis & Personal Notes**: Full Markdown/text note editor allowing up to 5,000 characters of user annotations preserved alongside the resource reference.
1133. **Truthful Resource Availability Indicators**: Explicit visual badges for missing, deleted, or restricted targets, warning the user rather than crashing or showing broken links.
1134. **Frontend & Backend Test Rigor**: 16 backend integration tests passing with 100% coverage of domain rules; 6 frontend unit tests validating DTO integrity, badge mappings, and bulk actions; 100% clean Next.js production build and TypeScript typecheck.
1135. **Strict Scope Discipline**: Workspaces multi-panel desktop layouts, floating panes, cross-panel synchronization, tab docking, and window managers (Stage 120) remain strictly deferred.


## Stage 120: Institutional-Grade Multi-Panel Financial Workspaces & Analytical Desktop

### Architecture, Layout Engine & Validation
1136. **Dedicated `/workspaces` Global Route**: Implemented Next.js route at `apps/web/src/app/(atlas)/workspaces/page.tsx` within the persistent ATLAS shell, preserving all 20 canonical top-level navigation routes without displacement.
1137. **Deterministic Recursive Layout Model**: Modeled workspace layouts as strict, cycle-free hierarchical trees composed of `SplitNode` (horizontal or vertical partitions), `TabStackNode` (stacked panels sharing a frame), and `PanelNode` (leaf nodes referencing live panel instances).
1138. **Strict Layout Invariant Validation**: Enforced tree invariants in `LayoutValidator`: maximum tree depth of 8 levels, maximum 24 panel instances per desk, and strict size ratio normalization where child ratios must sum to 1.0 ± 1e-4.
1139. **Self-Healing Layout Recovery**: Implemented `create_safe_recovery_layout()` which, upon detecting layout tree corruption or schema violations, automatically restructures active panel instances into a safe balanced split without dropping user analytical context.
1140. **Optimistic Concurrency Control**: Desks maintain monotonic `layout_revision` integer counters. Concurrent save attempts presenting outdated revisions are rejected with HTTP 409 Conflict to prevent multi-device race conditions.
1141. **Dual Conflict Resolution UI**: Provided users with interactive resolution options on 409 Conflict: reload latest desk state from server, or force-overwrite external updates.
1142. **Thread-Safe Repository Architecture**: Implemented `WorkspaceRepository` utilizing Python `threading.RLock()` to guarantee memory safety under concurrent multi-tenant execution.

### Cross-Panel Context & Financial Dimensions
1143. **Color-Coded Cross-Panel Link Groups**: Supported multiple independent link channels (Group A Blue, Group B Green, Group C Amber, Group D Rose) enabling synchronized workflows across disparate panel types.
1144. **Eight Standard Financial Context Dimensions**: Coordinated cross-panel context along 8 standardized financial dimensions: `INSTRUMENT`, `COMPANY`, `PORTFOLIO`, `BENCHMARK`, `DATE_RANGE`, `AS_OF_DATE`, `TIMEFRAME`, and `REPORTING_CURRENCY`.
1145. **Event Loop Suppression Engine**: Context synchronization bus tracks monotonic group version numbers and originating caller panel IDs, discarding self-broadcasts and preventing cyclic update loops.
1146. **Independent Panel Mode**: Panels can detach from global link groups via `independent_mode = true` or `link_group_id = null`, preserving static pinned views (e.g. macro indicators) while linked panels respond to ticker selection.

### Panel Registry & Specialized Adapters
1147. **Catalog of 14 Canonical Registered Panel Types**: Registered 14 core institutional panel types (`MARKET_OVERVIEW`, `INSTRUMENT_CHART`, `WATCHLIST`, `SCREENER`, `COMPANY_OVERVIEW`, `ECONOMIC_SERIES`, `NEWS_FEED`, `RESEARCH_DOCUMENT`, `RESEARCH_REPORT`, `PORTFOLIO_SUMMARY`, `PORTFOLIO_PERFORMANCE`, `RISK_OVERVIEW`, `RISK_ANALYSIS`, `DATA_TABLE`) with typed metadata and context capabilities.
1148. **Resilient Panel Error Boundaries**: Implemented `<WorkspacePanelErrorBoundary />` around every individual panel frame, isolating runtime exceptions and enabling isolated panel reload without unmounting the entire desk.
1149. **Bloomberg-Style Panel Header & Toolbar**: Provided high-density panel frame (`<WorkspacePanelHost />`) with title override editing, link group color badge, maximize/restore toggle, split right, split bottom, and panel close actions.
1150. **Native `react-resizable-panels` Integration**: Seamlessly integrated `react-resizable-panels` using ATLAS design-system components (`AtlasSplit`, `AtlasPanel`, `AtlasResizeHandle`) for smooth, high-performance resizing.

### Institutional Templates & Saved Library Integration
1151. **Six Canonical Institutional Desk Templates**: Built-in templates for `BLANK_DESK`, `EQUITY_RESEARCH_DESK`, `MARKET_MONITORING_DESK`, `MACRO_DESK`, `PORTFOLIO_DESK`, and `RISK_DESK`.
1152. **One-Click Template Instantiation**: Factory instantiation creates custom workspace instances pre-populated with docked panels, layout trees, and default link groups.
1153. **Stage 119 Saved Library Integration**: Workspace panels reference saved view configurations and saved items without duplicating records, and entire desks can be bookmarked to the universal library.
1154. **Soft-Deletion & Lifecycle Management**: Workspaces support soft-deletion (`deleted_at`), restoration, and complete deletion auditing.
1155. **Workspace Duplication**: Deep duplication duplicating layout trees, panel instances, and link groups into an independent workspace copy.
1156. **Default Workspace Designation**: Users can mark a workspace as `DEFAULT`, which is automatically restored upon entering `/workspaces`.
1157. **Append-Only Audit Trail**: Layout modifications, panel additions/removals, and link group mutations produce structured `workspace_audit_events`.

### Relational Schema, REST Endpoints & Quality Verification
1158. **Six Dedicated Relational Tables**: Created `workspaces`, `workspace_panel_instances`, `workspace_link_groups`, `workspace_templates`, `workspace_layout_revisions`, and `workspace_audit_events` with complete foreign key integrity and performance indexes.
1159. **Production Alembic Migration**: Added `stage120_workspaces_foundation.py` chained cleanly off `stage119_universal_saved_system`.
1160. **Complete REST API Architecture**: Mounted `/api/v1/workspaces` endpoints for CRUD, duplication, template listing, panel management, link groups, and layout persistence.
1161. **Full-Featured `WorkspaceHome` Dashboard**: Overview page featuring metric summary cards, category tabs (All, Favorites, Recent, Templates), search, sorting, and card grid.
1162. **Institutional Bloomberg-Style Terminal Aesthetics**: High-density typography, monospace metrics, clean divider handles, and dark-theme surface layers.
1163. **Zero Mutation of Accounting or Trading State**: The workspace layer operates strictly as an orchestration container with read-only bindings to underlying financial ledgers.
1164. **Strict Scope Discipline**: Multi-monitor window pop-outs, WebSockets sync gateways, and mobile responsiveness optimizations (Stage 121) remain strictly deferred.
1165. **Comprehensive Verification**: 17 backend integration tests passed in 7.71s, 11 frontend unit tests passed in 891ms, 0 TypeScript errors, 100% clean Ruff checks and formatting, and successful Next.js production build across 38 pages.


## Stage 121: Global Workspace Linking & Cross-Module Context Synchronization

### Context Dimensions, Scopes & Subscription Contracts
1166. **Ten Standardized Context Dimensions**: Established non-colliding financial dimensions: `INSTRUMENT`, `COMPANY`, `PORTFOLIO`, `BENCHMARK`, `ECONOMIC_SERIES`, `DATE_RANGE`, `AS_OF_DATE`, `TIMEFRAME`, `REPORTING_CURRENCY`, and `REGION`.
1167. **Four Hierarchical Context Scopes**: Partitioned channel distribution boundaries into `PANEL_LOCAL` (isolated widget state), `WORKSPACE` (active desk scope), `USER_APPLICATION` (cross-module window scope), and `USER_CROSS_TAB` (cross-window scope).
1168. **Four Deterministic Subscription Modes**: Panels bind to link channels with explicit subscription contracts: `PUBLISH` (outbound selection only), `SUBSCRIBE` (inbound listening only), `BIDIRECTIONAL` (full duplex synchronization), or `INDEPENDENT` (completely isolated from external events).
1169. **Canonical Panel Capability Registry**: Implemented `CAPABILITIES_CATALOG` specifying publishable dimensions, subscribable dimensions, accepted entity types, and required transformations across all 14 canonical institutional panel types.
1170. **Deterministic Canonical Entity Resolution**: Enforced strict lookup resolution (`CanonicalEntityResolver`) with zero speculative guessing or synthetic ticker interpolation.
1171. **Standardized Cross-Entity Transformations**: Implemented validated bi-directional entity mapping: `INSTRUMENT_TO_COMPANY`, `COMPANY_TO_PRIMARY_LISTING`, `PORTFOLIO_TO_BENCHMARK`, `OPTION_TO_UNDERLYING`, and `GENERIC_RESOLVE`.

### Concurrency, Ordering & Loop Prevention
1172. **Monotonic Revision Sequencing**: All context channels track an integer `revision` sequence number incremented on each state change.
1173. **Stale Asynchronous Event Rejection**: Panels track their last processed revision number and drop incoming payloads with `revision <= last_applied_revision` to eliminate out-of-order asynchronous races.
1174. **Causation-Chain Loop Prevention & Echo Suppression**: Suppressed cyclic ping-pong updates by filtering events matching `origin_panel_instance_id` and terminating propagation when an event ID appears in its own causation chain.
1175. **In-Memory Event Deduplication Ring Buffer**: Client and server event buses maintain LRU deduplication caches to silently discard duplicate dispatches within 10-second replay windows.
1176. **Cross-Window Multi-Monitor Coordination**: Integrated HTML5 `BroadcastChannel('atlas_global_context_channel')` to synchronize context across detached windows and multi-monitor setups without requiring persistent server WebSockets.
1177. **Independent Panel Mode**: Explicitly decoupled panels (`channel_id = null` or `independent_mode = true`) preserve static analytical configurations (e.g., macro benchmarks) while adjacent linked panels update.
1178. **Per-Dimension Local Overrides**: Linked panels can maintain localized overrides for specific dimensions (e.g., a chart panel adhering to a linked instrument while holding an independent `5Y` timeframe).

### Storage, REST API & Security
1179. **Four Institutional Default Link Channels**: Out-of-the-box support for Group A (Blue), Group B (Green), Group C (Amber), and Group D (Rose) link channels with high-contrast institutional color tokens.
1180. **Channel Capacity Guardrails**: Enforced maximum limit of 32 active channels per user/workspace scope to prevent memory leakage and subscription sprawl.
1181. **Thread-Safe Memory Concurrency**: Implemented `ContextRepository` using Python `threading.RLock()` ensuring thread safety across concurrent FastAPI worker threads.
1182. **Four Dedicated Relational Tables**: Created `global_context_channels`, `global_context_channel_memberships`, `global_context_snapshots`, and `global_context_audit_events` with strict referential integrity and performance indexes.
1183. **Production Alembic Migration**: Authored `stage121_global_workspace_linking.py` chained cleanly off `stage120_workspaces_foundation`.
1184. **Ten REST Endpoints**: Implemented complete `/api/v1/context` router supporting channel lifecycle, membership management, event dispatching, and entity resolution.
1185. **Typed Client-Side API Layer**: Built `src/lib/context/api.ts` with typed error handling and optimistic client-side fallbacks.

### User Interface & Integration
1186. **Universal React Context Architecture**: Created `<GlobalContextProvider>` and `useGlobalContext()` hook managing multi-channel state and event routing.
1187. **Specialized Panel Hook (`usePanelContext`)**: Provided high-level hook managing panel channel subscriptions, dimension filtering, and safe context dispatching.
1188. **Global Context Bar (`<GlobalContextBar />`)**: Mounted Bloomberg-style context toolbar in `WorkspaceHeader` displaying active channel badge, current ticker, base currency, and timeframe.
1189. **Panel Link Control (`<PanelLinkControl />`)**: Added high-density dropdown toolbar control inside `<WorkspacePanelHost />` enabling instant link group switching.
1190. **Channel Manager Modal (`<LinkChannelManagerModal />`)**: Implemented full management dialog displaying connected panels, current context snapshots, and channel creation controls.
1191. **Context Compatibility Status Indicator (`<ContextCompatibilityStatus />`)**: Rendered visual status badges indicating whether a panel is synchronized, transforming, or ignoring channel context.
1192. **Zero Mutation of Financial Books**: Guaranteed that context synchronization is strictly analytical and never triggers automated orders, executions, or portfolio balance modifications.
1193. **Preservation of 20 Canonical Routes**: Operates entirely within `/workspaces` and the persistent AppShell chrome without introducing extraneous top-level routes.
1194. **Stage 119 Universal Saved Library Compatibility**: Linked workspace views and context snapshots integrate cleanly with the universal library.
1195. **Stage 120 Multi-Panel Workspace Integration**: Preserved the recursive layout tree and panel registry without duplicating layout logic.
1196. **Truthful Entity Presentation**: Panels display clear unmapped badges when an entity does not support a requested dimension rather than guessing fake values.

### Quality, Verification & Boundaries
1197. **12 Backend Integration Tests**: Validated full test coverage in `test_context_stage121_v1.py` covering CRUD, memberships, entity transformations, loop suppression, and REST endpoints.
1198. **9 Frontend Integration Tests**: Validated all reference fixtures A through I in `context_stage121_v1.test.ts` with 100% pass rate.
1199. **100% Production Build Clean**: Verified Next.js production build across all 38 application routes with 0 TypeScript compilation errors and 0 lint warnings.
1200. **Strict Future Scope Discipline**: VS Code-style Terminal Shell (`/terminal`, CLI, Python REPL, MCP) remains strictly deferred to Stage 122.

## Stage 122 — Integrated ATLAS Terminal and Developer Console

### Architecture & Placement
1201. **Universal Bottom Taskbar Placement**: The Integrated ATLAS Terminal Shell is mounted in the global Bottom Taskbar drawer, preserving the 20 canonical top-level routes without introducing a /terminal route.
1202. **VS Code-Inspired Tabbed Multi-Session Architecture**: Supports independent concurrent sessions across six principal console types (ATLAS_CLI, PYTHON, SQL, LOGS, AGENTS, MCP).
1203. **Independent Per-Session Draft Isolation**: Every session maintains its own isolated uncommitted draft buffer, scrollback history, and connection state.
1204. **Bloomberg-Density Status Bar**: Terminal footer displays active session type, connection state, RLS status, cursor coordinates, and execution capability indicators.
1205. **Global Toggle Shortcut**: Integrated Ctrl+\` / Cmd+\` hotkey and command palette action 	erminal.toggle for immediate console access from any platform view.

### Consoles & Capabilities
1206. **ATLAS CLI Console**: Command-line interface with registered command syntax help, command history, and auto-completion.
1207. **Python Scratchpad Console**: Multiline quantitative editor with line numbering, syntax formatting, and draft persistence.
1208. **SQL Analytics Console**: Relational query editor with read-only target schema indicators and query drafting.
1209. **Real Operational Logs Console**: Real-time application log stream with severity filtering, service search, and secret redaction.
1210. **Agents Status Inspector**: Truthful diagnostic view of registered background workers and autonomous agents.
1211. **MCP Registry Inspector**: Truthful connection and capability inspection of Model Context Protocol configurations.

### Security & Sanitization
1212. **Secret Redaction**: Real-time regex scrubber strips bearer tokens, JWT signatures, API secret keys, and passwords from log records before transmission.
1213. **Safe ANSI Parsing**: ANSI color escape sequences are safely parsed into styled React spans without dangerouslySetInnerHTML.
1214. **OSC Sequence Stripping**: Malicious OSC escape sequences (such as OSC 8 hyperlinks and OSC 52 clipboard hijacking) are stripped prior to rendering.
1215. **URL Sanitization**: Interactive links validate against safe http/https schemes, rejecting javascript:, data:, and bscript:.
1216. **Strict Denial of Arbitrary Execution**: In Stage 122, arbitrary execution attempts fail closed with TERMINAL_EXECUTION_UNAVAILABLE (HTTP 501), establishing typed contracts for Stage 123.
1217. **Bounded Memory & Scrollback**: Terminal scrollback buffers and drafts enforce strict upper bounds (max 2,000 lines, max 64KB per draft).
1218. **User Preference Persistence**: User font size, family, line height, cursor style, and terminal height persist in 	erminal_user_preferences.
1219. **Production Database Migration**: Production Alembic migration stage122_terminal_shell.py establishes persistent tables for sessions, preferences, and audit trails.
1220. **Stage 123 Preparation Contracts**: Formalized ExecutionCapabilityDefinition, ExecutionRequestSchemaContract, and ExecutionOutputStreamingContract.

---

## Stage 123 — Sandboxed Terminal Execution Platform

### Roadmap & Isolation
1241. **Canonical Roadmap Discipline**: Stage 123 delivers sandboxed execution for Python, read-only SQL, and approved ATLAS CLI commands; Stage 124 AI Assistant milestones remain strictly deferred.
1242. **Separation of Execution Services**: Untrusted user code never executes inside the FastAPI server, production worker, or browser main thread.
1243. **Zero Host Shell Execution**: Terminal commands are strictly parsed via application routers; unrestricted OS shells (cmd.exe, powershell.exe, sh, ash) are never invoked.
1244. **Subprocess-Isolated Python Sandbox**: Python executes in dedicated ephemeral subprocesses with unprivileged credentials and ephemeral directories.
1245. **Environment Variable Scrubbing**: All sensitive credentials, tokens, database URLs, and cloud keys are purged from the child process environment.
1246. **Filesystem Isolation & Ephemeral Cleanup**: Executions operate strictly within isolated temporary folders that are recursively removed upon process termination.
1247. **Path Redaction in Tracebacks**: Absolute host operating-system filesystem paths in Python exception traces are sanitized to /sandbox/main.py.

### Python Runtime
1248. **Resource Boundaries & Quotas**: Compute profiles enforce 1 core, 512MB RAM, 10s default timeout (max 30s), and 64KB output limits.
1249. **Deterministic Package Manifest**: Approved runtime pins Python standard libraries and NumPy; unauthorized modules fail closed.
1250. **Structured Tabular Output**: Tabular results from DataFrames and queries are typed and bound to prevent memory exhaustion in the browser.
1251. **Graceful Timeout & Cancellation**: Active child processes are terminated immediately upon reaching execution timeout or receiving user cancellation tokens.

### SQL Execution Engine
1252. **Read-Only SQL Baseline**: SQL execution defaults strictly to read-only analytical statements.
1253. **Statement Allowlist Defense-in-Depth**: Query parser strictly enforces SELECT and WITH ... SELECT only.
1254. **Prohibited SQL Keyword Denial**: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, MERGE, GRANT, COPY, CALL, DO, EXEC, multiple statements, and destructive CTEs are rejected with TERMINAL_SQL_STATEMENT_NOT_ALLOWED.
1255. **Engine-Level Authorizer**: SQLite in-memory instance enforces action codes SQLITE_SELECT, SQLITE_READ, and SQLITE_FUNCTION (action 31), returning SQLITE_DENY for all non-read actions.
1256. **Controlled Pricing Test Fixture**: Seeded 	est_prices table with AAA 100, BBB 150, CCC 200 supports verified analytical queries and aggregations (AVG(price) = 150).

### ATLAS CLI Router
1257. **Approved ATLAS CLI Command Router**: Pure application-level router dispatches approved institutional operations without shell interpolation.
1258. **Rejection of Unknown Commands**: Any unknown command or shell script string (
m -rf /) returns TERMINAL_CLI_COMMAND_UNKNOWN.
1259. **Immutable Baseline Commands**: All baseline CLI commands are classified as READ_ONLY or COMPUTATIONAL; mutations are blocked with TERMINAL_CLI_MUTATION_NOT_ALLOWED.

### Lifecycle, Streaming & State Machine
1260. **Monotonic Execution State Machine**: State transitions follow strict DAG ordering (CREATED -> QUEUED -> RUNNING -> COMPLETED/FAILED/CANCELLED/TIMED_OUT/SECURITY_DENIED).
1261. **Terminal Status Locking**: Once an execution enters a terminal state, subsequent state transitions are rejected.
1262. **Monotonic State Revisions**: Every state transition increments state_revision to prevent asynchronous race conditions.
1263. **User Execution Isolation**: Executions are strictly scoped to the authenticated user ID; cross-user execution access or cancellation raises TERMINAL_EXECUTION_ACCESS_DENIED.
1264. **Bounded Output Streaming**: Execution output chunks are emitted with monotonic sequence numbers and categorized by stream type (stdout, stderr, 	abular, error).
1265. **Output Truncation Guardrail**: Output exceeding configured memory quotas is truncated with clear markers rather than causing memory exhaustion.
1266. **Fast Status Polling**: Dedicated lightweight /api/v1/terminal/executions/{id}/status endpoint enables real-time client polling without transferring large payloads.

### Financial Integrity & Security
1267. **No Implicit Financial Data Injection**: Global financial context does not silently copy private portfolio or trade records into the Python sandbox without explicit authorization.
1268. **Preservation of Financial Records**: Execution is strictly analytical; zero trading orders, portfolio mutations, or broker side-effects can occur from terminal execution.
1269. **Database Connection Safety**: Service-role keys and database administrator credentials are never exposed or passed to execution contexts.
1270. **Sanitized Error Envelopes**: All execution errors return standardized ATLAS error envelopes with typed codes and redacted stack traces.
1271. **Append-Only Audit Trail**: All execution submissions, cancellations, and status transitions are recorded in 	erminal_execution_audit_events.
1272. **Alembic Database Migration**: Production migration stage123_terminal_execution.py creates execution, output, and audit tables chained from Stage 122.
1273. **Per-User Concurrency Limiting**: Scheduler enforces a maximum of 2 concurrent executions per user, returning TERMINAL_EXECUTION_QUOTA_EXCEEDED on violation.

### APIs & Frontend User Experience
1274. **REST API Namespace**: All execution endpoints operate under /api/v1/terminal/executions, /python, /sql, and /cli.
1275. **Pre-flight Query Validation**: Dedicated POST /api/v1/terminal/sql/validate endpoint allows clients to check query validity before submission.
1276. **Typed Execution Client**: Frontend library src/lib/terminal/executionApi.ts provides typed async interfaces for all execution routes.
1277. **Interactive Python Console**: Upgraded PythonConsole provides real Run/Stop controls, environment picker, duration tracking, and stdout/stderr split view.
1278. **Institutional SQL Grid**: Upgraded SqlConsole features SqlResultGrid with sorting, formatted numbers, row counts, and CSV/JSON export.
1279. **Structured CLI Terminal**: Upgraded AtlasCliConsole renders command suggestions, arrow-key history, status badges, and structured tables.
1280. **Verification & Acceptance**: 100% test pass rate across 33 backend pytest tests (Stage 122 & 123), 217 frontend unit tests, 0 lint warnings, and clean Next.js production build.


---

## Stage 124 — AI ASSISTANT V1 and Universal ATLAS AI Overlay

### Core Architecture & AppShell Integration
1281. **Universal AI Trigger in TopBar**: Positioned in the upper-right of the ATLAS AppShell header across all 20 canonical routes, featuring a Bot icon, live state indicator, and keyboard shortcut badge (`Ctrl+Alt+A`).
1282. **Sliding Docked AI Overlay**: Resizable side-panel overlay (`AtlasAiOverlay.tsx`) with draggable left edge handle supporting user width customization between 340px and 750px.
1283. **Preservation of Underlying Workspaces**: Opening, closing, resizing, and conversing with the overlay does not unmount, reload, or navigate away from the active financial workspace.
1284. **Zustand State Management**: Global `useAiOverlayStore` coordinates overlay visibility, active conversation ID, panel width, history drawer toggle, and docking configuration.
1285. **Global Shortcut Binding**: `Ctrl+Alt+A` / `Cmd+Alt+A` toggles the overlay from anywhere across the operating system without hijacking browser defaults.
1286. **Shared Backend Infrastructure**: The global overlay and the dedicated `/ai` full-screen route share the exact same backend conversation sessions, messages, models, and streaming pipelines.

### Data Model & Persistence
1287. **PostgreSQL / Supabase Schema**: Dedicated persistence layer featuring `ai_conversations`, `ai_messages`, `ai_generation_runs`, `ai_assistant_user_preferences`, and `ai_conversation_audit_events`.
1288. **Alembic Migration**: Migration `stage124_ai_assistant_v1.py` created with `down_revision = "stage123_terminal_execution"`.
1289. **Tenant & User Isolation**: All conversations, messages, generation runs, and preferences are strictly filtered by authenticated user `owner_user_id` and `tenant_id`.
1290. **Message Truncation Guardrail**: User prompt input is strictly validated and capped at 16,000 characters; oversized inputs raise `AI_MESSAGE_TOO_LARGE`.
1291. **Cascade Message Deletion**: Foreign key constraints cascade message deletions upon conversation deletion.
1292. **Conversation Search & Ordering**: Conversations support title search, pinned status prioritization, and sorting by last message timestamp.

### Provider-Agnostic Model Layer
1293. **Model Capabilities Catalog**: Canonical models `atlas-intelligence-v1` (Default), `atlas-reasoning-v1`, and `atlas-speed-v1` configured with parameter windows and streaming flags.
1294. **Deterministic Mock Provider**: `MockAiProvider` delivers high-fidelity, deterministic streaming responses for testing and local environments without API keys.
1295. **OpenAI-Compatible HTTP Streaming**: `OpenAiCompatibleProvider` connects to standard inference endpoints (OpenAI, Groq, NVIDIA NIM) using `httpx.AsyncClient`.
1296. **Zero Credential Exposure**: Provider API keys reside exclusively in server-side environment variables and are never transmitted to client code or serialized in responses.
1297. **Provider Factory Resolution**: `get_ai_provider(...)` automatically resolves configured credentials or safely falls back to `MockAiProvider`.

### Financial Intelligence & Capability Honesty
1298. **Institutional Financial Persona**: Formally defined persona in `system_instructions.py` providing mathematical precision, calm analytical tone, and structured markdown.
1299. **Mathematical Concept Rigor**: Built-in accurate formulations for Duration vs Convexity, Sharpe/Sortino ratios, Black-Scholes-Merton model, VaR, and CVaR.
1300. **Step-by-Step Numerical Reasoning**: Step-by-step arithmetic verification for user-supplied portfolio and risk calculation inputs.
1301. **Strict Live Price Boundary**: Refusal to hallucinate real-time streaming tick quotes; clearly directs users to `/markets` or `/charts`.
1302. **Strict Trade Execution Boundary**: Refusal to execute unilateral broker trades or modify portfolios directly from chat; directs users to `/trading` or `/portfolios`.
1303. **Strict Terminal Execution Boundary**: Refusal to run code directly from conversational text without passing through the Stage 123 sandboxed terminal interface.

### Context Budgeting & Minimal Route Descriptors
1304. **Allowlisted Route Descriptors**: Minimal `RouteContext` mapping pathname to canonical module name and institutional description across all 20 canonical top-level routes.
1305. **Stage 124 Context-Light Boundary**: Deep DOM inspection, full workspace state extraction, and arbitrary panel scraping are strictly deferred to Stage 125.
1306. **Prompt Budgeting & Windowing**: `PromptBuilder` windows recent turns to 20 messages and 32,000 characters, preserving system prompt and active route context.

### Streaming Transport & Cancellation
1307. **Server-Sent Events (SSE)**: `GET /api/v1/ai/generations/{generation_id}/stream` delivers typed events: `run_started`, `delta`, `run_completed`, `run_cancelled`, and `error`.
1308. **Instant Generation Cancellation**: `POST /api/v1/ai/generations/{generation_id}/cancel` triggers cancellation tokens, halts provider streaming, and marks run status as `CANCELLED`.
1309. **Client-Side Text Streaming**: `streamAiGeneration` utility decodes SSE streams and updates React state in real-time with smooth typing cursor effects.
1310. **Response Regeneration**: `POST /api/v1/ai/conversations/{id}/regenerate` re-runs generation from the target turn or the latest user prompt.

### Frontend UI & User Experience
1311. **Markdown & Code Rendering**: Custom lightweight markdown parser rendering headings, fenced code blocks with Copy buttons, tables, and KaTeX math blocks.
1312. **Auto-Growing Composer**: Textarea dynamically expands up to 160px with `Enter` to send and `Shift+Enter` for newlines.
1313. **History Drawer**: In-overlay slide drawer for searching, pinning, unpinning, and deleting past conversations.
1314. **Editable Titles**: Users can rename conversation titles inline with immediate backend synchronization.
1315. **Context Banner**: Active module descriptor pill displayed at the top of the overlay informing users of their active platform location.
1316. **Copy to Clipboard**: Quick copy button for full assistant responses and individual code blocks.
1317. **Empty State Financial Prompts**: One-click quick-start prompt cards covering Duration/Convexity, Sharpe math, and Risk navigation.

### Dedicated Full-Screen Route (`/ai`)
1318. **Tri-Pane Institutional Canvas**: `apps/web/src/app/(atlas)/ai/page.tsx` upgraded with `AtlasSplit` (History, Main Chat, Intelligence Inspector).
1319. **Intelligence Inspector**: Displays active model engine parameters, session token telemetry, and Stage 124 governance notices.

### Verification & Quality Gates
1320. **Stage 124 Quality Signoff**: 100% test pass rate across 13 backend pytest tests, 223 frontend unit tests, 0 lint warnings, and clean Next.js production build of all 38 routes.


## Stage 125: ATLAS AI Context Awareness Engine

### Architectural Foundations & Scope Boundaries
1321. **Read-Only Context Intelligence**: Stage 125 strictly functions as an authorized, read-only analytical context assembly engine. AI tool invocation, terminal command execution, autonomous external API calls, MCP tool execution, and agent autonomy are strictly deferred to Stage 126.
1322. **Zero DOM Scraping Invariant**: Context items are never scraped from client HTML elements, CSS trees, or canvas screenshots. All context is resolved deterministically from canonical backend data services, verified state stores, and Stage 121 entity resolvers.
1323. **Point-in-Time Fact Accuracy**: Every context item immutably binds its `as_of` date, observation timestamp, source reference URL (`atlas://...`), schema version, and reporting currency to eliminate temporal look-ahead bias.
1324. **Prompt Injection Data Fencing**: All verified context data is injected within `<atlas_verified_financial_context data-purpose="untrusted-read-only-financial-context">` blocks with explicit model directives stating the block contains DATA ONLY and cannot issue system commands or override instructions.
1325. **Universal 20-Module Platform Coverage**: Full context intelligence support across `/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, `/maps`, `/intelligence`, `/options`, `/trading`, `/portfolios`, `/risk`, `/ai`, `/data`, `/saved`, `/workspaces`, and `/agents`.

### Canonical Context Types & Domain Models
1326. **19 Canonical Context Types**: Full enumeration `ContextType` covering `PAGE_CONTEXT`, `MODULE_CONTEXT`, `INSTRUMENT_CONTEXT`, `COMPANY_CONTEXT`, `CHART_CONTEXT`, `WATCHLIST_CONTEXT`, `SCREENER_CONTEXT`, `ECONOMICS_CONTEXT`, `NEWS_CONTEXT`, `RESEARCH_CONTEXT`, `PORTFOLIO_CONTEXT`, `RISK_CONTEXT`, `OPTIONS_CONTEXT`, `DATA_CONTEXT`, `SAVED_RESOURCE_CONTEXT`, `WORKSPACE_CONTEXT`, `WORKSPACE_PANEL_CONTEXT`, `LINKED_CONTEXT`, and `USER_SUPPLIED_CONTEXT`.
1327. **AtlasAiContextItem Dataclass**: Normalized context container carrying `context_item_id`, `canonical_target_id`, `source_module`, `source_reference`, `as_of`, `data_quality_status`, `model_disclosure_status`, `content_summary`, `structured_payload`, SHA-256 `content_hash`, `estimated_tokens`, and `relevance_score`.
1328. **AtlasAiContextEnvelope Dataclass**: Root context envelope binding `context_request_id`, `conversation_id`, `generation_id`, `authenticated_user_scope`, `source_page`, `active_workspace_id`, `focused_panel_id`, `context_mode`, `resolved_context_items`, `excluded_items`, `quality_summary`, and `token_budget`.
1329. **Deterministic Content Hashing**: Every context item computes an immutable SHA-256 hash of its serialized payload for provenance verification and cache validation.
1330. **Four Operating Context Modes**: `OFF` (zero workspace/entity sharing), `FOCUSED` (active entity and focused panel only, default), `WORKSPACE` (full multi-panel inventory and link channels), and `CUSTOM` (user-pinned entities and explicit parameters).

### 16 Server-Side Context Adapters
1331. **PageContextAdapter**: Resolves canonical route descriptors, active module metadata, and top-level institutional layout modes.
1332. **InstrumentContextAdapter**: Leverages Stage 121 `CanonicalEntityResolver` to resolve tickers to canonical instruments, FIGIs, ISINs, exchanges, countries, and sectors.
1333. **CompanyContextAdapter**: Resolves point-in-time corporate financial statement facts, reporting periods, fiscal years, currencies, and verified ratios without look-ahead bias.
1334. **ChartContextAdapter**: Extracts active timeframe, interval, indicator overlays (SMA, RSI, MACD), last close price, realized annualized volatility, and data coverage.
1335. **WatchlistContextAdapter**: Resolves watchlist securities, active selections, column layouts, and sort order.
1336. **ScreenerContextAdapter**: Resolves active screening universe, filter criteria rules, sort dimensions, and sample matching results.
1337. **EconomicsContextAdapter**: Resolves macro time series, reporting countries, observation frequency, units, and vintage publication dates.
1338. **NewsContextAdapter**: Resolves licensed wire headlines, publisher attribution, timestamp, and licensed content excerpts.
1339. **ResearchContextAdapter**: Resolves report titles, authors, published dates, access levels, and executive summaries while gating unreleased drafts.
1340. **PortfolioContextAdapter**: Resolves asset allocation breakdowns, benchmark comparisons, and concentration metrics while enforcing holdings privacy policies.
1341. **RiskContextAdapter**: Resolves parametric VaR 95%, CVaR 95%, factor exposures, and stress tests bound immutably to historical Risk Run instances.
1342. **OptionsContextAdapter**: Resolves underlying strikes, expiry dates, implied volatility, and Black-Scholes Greeks (Delta, Gamma, Theta, Vega).
1343. **DataContextAdapter**: Resolves dataset catalog metadata, schema definitions, row counts, and vendor provenance (e.g. WRDS, CRSP, FactSet).
1344. **SavedResourceContextAdapter**: Bridges Stage 119 Universal Saved Resources, resolving saved target types, versions, and permissions.
1345. **WorkspaceContextAdapter**: Bridges Stage 120 Multi-Panel Workspaces, resolving panel inventories, active split trees, and focused panel states.
1346. **GlobalLinkingContextAdapter**: Bridges Stage 121 Global Workspace Linking, resolving active link channels, synchronized entity dimensions, and channel revisions.

### Ambiguity Detection, Relevance & Token Budgeting
1347. **Multi-Panel Ambiguity Detection**: Detects deictic queries (e.g., "what's the RSI of this chart?") when multiple instances of the same panel type exist in a workspace without a focused panel, prompting the user for clarification instead of hallucinating.
1348. **Relevance Scoring Engine**: Deterministic additive scoring model awarding weights for explicit entity matches (+4), focused panel membership (+3), active module alignment (+2), and recent updates (+1), while penalizing stale data (-2).
1349. **Token Budgeting & Rank-and-Trim**: Knapsack-style budget allocator ranking items by relevance score and trimming candidates exceeding the 8,000 token context window, recording detailed exclusion reasons.

### Privacy, Governance & Provider Disclosure
1350. **Granular Portfolio Holdings Privacy**: Portfolio holdings and lot-level allocations are redacted by default (`holdings_redacted = True`); granular positions are only disclosed when `allow_portfolio_holdings_context` is explicitly consented to by the user.
1351. **Research Draft Compliance**: Unpublished research drafts and confidential analyst notes are excluded from AI context unless `allow_research_drafts_context` is explicitly enabled.
1352. **Vendor Provider Disclosure Policies**: Data items bearing `ProviderDisclosureStatus.PROHIBITED` are strictly filtered out before transmission to external third-party LLM providers.
1353. **Immutable Source Manifests**: Every generation run records an immutable `AiContextSourceManifest` capturing the exact list of context items, timestamps, hashes, and token allocations used.
1354. **Append-Only Context Audit Trail**: Context resolution requests, privacy overrides, and mode transitions are recorded in `ai_context_audit_events`.

### Database Schema & Persistence
1355. **SQLAlchemy Models**: Implemented `AiContextPreferencesModel`, `AiContextSourceManifestModel`, and `AiContextAuditEventModel` in `atlas.ai.context.db_models`.
1356. **Alembic Migration**: Created migration `stage125_ai_context_awareness.py` with foreign key and generation run linking.
1357. **Generation Run Correlation**: `ai_generation_runs` extended with `source_manifest_id` column to correlate assistant generations with verified context manifests.

### FastAPI Context Endpoints
1358. **`GET /api/v1/ai/context/capabilities`**: Discovers all registered module context capabilities, disclosure policies, and sensitivity tiers.
1359. **`GET /api/v1/ai/context/preferences`**: Retrieves user context mode, sharing consents, pinned items, and exclusion lists.
1360. **`PUT /api/v1/ai/context/preferences`**: Updates user context modes, sharing toggles, and pinned references.
1361. **`POST /api/v1/ai/context/preview`**: Performs dry-run context assembly returning a preview envelope for the frontend Context Inspector.
1362. **`POST /api/v1/ai/context/resolve`**: Explicitly resolves a single typed context item by target identifier and parameters.
1363. **`GET /api/v1/ai/context/manifests/{generation_id}`**: Retrieves the immutable source manifest for any past AI generation run.

### Frontend Architecture & User Experience
1364. **Context Inspector & Active Chips**: Implemented `AiContextInspector`, `AiContextChips`, `AiContextModeSelector`, and `AiContextQualityBadge` in `apps/web/src/components/ai/context/`.
1365. **Global "Ask AI About This" Handoff**: `askAiAboutThis(...)` dispatches custom events across the application shell to open the AI overlay, pin the target financial entity, and prepare the analytical turn.


## Stage 126: Institutional-Grade ATLAS AI Tool Gateway

### Canonical Roadmap & Security Boundaries
1366. **Stage 126 Tool Gateway Ownership**: Stage 126 establishes the central, permission-aware AI Tool Gateway connecting the Stage 124 AI Assistant V1 and Stage 125 Context Awareness Engine to real, authorized, read-only ATLAS financial foundations.
1367. **Stage 125 Context Awareness Reused**: Leverages Stage 125 route contexts, canonical entity resolvers, and context adapters without duplication.
1368. **Stage 124 AI Assistant Reused**: Extends Stage 124 multi-turn chat, SSE streaming, and persistent conversation models without regression.
1369. **Stage 127 AI Research & RAG Deferred**: Broad vector document indexing, semantic embedding pipelines, and citation graphs are strictly deferred to Stage 127.
1370. **Stage 128 Financial AI Actions Deferred**: AI-driven mutations (chart mutations, portfolio rebalancing, order placement, screener execution jobs) are strictly deferred to Stage 128.
1371. **Strict Prohibition of Arbitrary Terminal Execution**: Tools cannot invoke `execute_python`, `execute_sql`, or `execute_shell`. Interactive terminal operations remain sandboxed in Stage 123.
1372. **Strict Prohibition of Broker Trading Execution**: Zero broker connectivity or live trading execution from AI tools.
1373. **Strict Prohibition of Autonomous Background Agents**: Standing background agents and multi-agent coordination are strictly isolated to Stage 146.
1374. **Preserving Twenty Global Routes**: All twenty canonical ATLAS sidebar navigation routes remain completely untouched.

### Universal Tool Registry
1375. **Canonical Tool ID Namespacing**: Enforced stable hierarchical naming format `atlas.<module>.<action>` (e.g. `atlas.instrument.search`).
1376. **Tool ID Regex Policy**: Validated via strict regex `^atlas\.[a-z0-9_]+\.[a-z0-9_]+$` to prevent collisions or malformed identifiers.
1377. **SemVer Tool Versioning**: Every registered tool specifies a semantic version (default `1.0.0`) for reproducible invocation histories.
1378. **Strict Typed Parameter Schemas**: Input schemas defined via Pydantic models and converted to OpenAI JSON function declarations.
1379. **Standard Return Envelope Contract**: Standardized `AtlasAiToolResult` envelope binding tool ID, success flag, payload, manifest, execution time, and SHA-256 content hash.
1380. **Central Handler Registration**: `AtlasAiToolRegistry` singleton maps definitions to verified `BaseAiToolAdapter` implementation classes.
1381. **Tool Lifecycle State Machine**: Registered tools transition through `REGISTERED`, `ENABLED`, `DISABLED`, `DEPRECATED`, and `UNAVAILABLE`.
1382. **Administrative Deprecation**: Deprecated tools emit deprecation warnings while maintaining backward compatibility until retired.
1383. **Tool Capability Classes**: Classified into `DISCOVERY`, `DATA_READ`, `ANALYTICAL_READ`, `STATUS_READ`, `COMPUTATIONAL`, `USER_STATE_MUTATION`, `FINANCIAL_MUTATION`, `EXTERNAL_SIDE_EFFECT`, and `PRIVILEGED_OPERATION`.
1384. **Action Risk Categorization**: Read-only tools require no approval by default; sensitive scopes require user confirmation.
1385. **Context-Aware Tool Discovery**: `ToolDiscoveryService` filters available tools by user permissions and ranks them dynamically by route affinity.
1386. **Model Capability Filtering**: Only tool definitions supported by the target LLM provider/model are emitted to the function-calling interface.
1387. **Rejection of Dynamic Code Loading**: Adapters must be statically compiled and registered within the codebase; runtime script loading is forbidden.

### Execution & Security
1388. **Normalization of Model Proposals**: Tool arguments proposed by untrusted model outputs are normalized and strictly validated before execution.
1389. **Typed Argument Schema Validation**: Missing required fields or schema violations raise `AiToolArgumentInvalidError` (`AI_TOOL_ARGUMENT_INVALID`).
1390. **Server-Authoritative Zero-Trust Gateways**: The model cannot assert its own permissions or bypass server authorization checks.
1391. **Fine-Grained Capability Scopes**: Access requires specific scopes (e.g. `tools:instrument:read`, `tools:portfolio:read`, `tools:risk:read`).
1392. **Anti-IDOR Resource Authorization**: Resource parameters (`portfolio_id`, `run_id`, `screener_id`) enforce strict owner-bound ACL checks.
1393. **Third-Party Provider Disclosure Policies**: Data marked `ProviderDisclosurePolicy.PROHIBITED` is blocked from external model transmission.
1394. **Cryptographic Approval Hash Binding**: Approval tokens bind a deterministic SHA-256 hash of normalized arguments (`normalized_arguments_hash`).
1395. **Approval TTL & Replay Protection**: Approvals expire after 5 minutes and enforce single-use consumption (`consumed_at`).
1396. **Tool Sequence Limit Enforcement**: Generation runs are capped at a maximum of 4 tool invocations to prevent infinite loops (`AiToolSequenceLimitExceededError`).
1397. **Bounded Execution Timeouts**: Per-tool execution timeout is strictly capped at 10 seconds (`AiToolTimeoutError`).

### Financial Tools & Integrity
1398. **Canonical Instrument Search**: `atlas.instrument.search` matches canonical instruments without guessing listing identities.
1399. **Direct Market Quote Verification**: `atlas.market.quote` returns verified quotes or explicit `quote_available: false` (no fabricated live prices).
1400. **Point-in-Time Corporate Financials**: `atlas.company.financials` returns verified 10-K line items with explicit currencies and units.
1401. **Private Portfolio RLS & Redaction**: `atlas.portfolio.get_summary` redacts granular holdings by default unless explicitly consented.
1402. **GIPS-Compliant Performance Metrics**: `atlas.portfolio.get_performance` returns verified returns, benchmark comparison, alpha, beta, and tracking error.
1403. **Immutable Risk Run Inspection**: `atlas.risk.get_run_summary` retrieves original historical VaR/CVaR metrics from the vault without recomputing.
1404. **Official Macroeconomic Series**: `atlas.economics.get_observations` fetches chronological economic indicators from FRED and BLS.
1405. **Indirect Prompt-Injection Fencing**: `atlas.news.search_headlines` sanitizes and encloses wire copy in `<atlas_verified_financial_context>` tags.
1406. **Read-Only Screener Definition**: `atlas.screener.get_definition` inspects screening criteria without triggering expensive search jobs or mutations.
1407. **Universal Saved & Workspace Bridges**: `atlas.saved.list` and `atlas.workspace.list` integrate Stage 119 and Stage 120 metadata.

### Model Integration, User Interface & Verification
1408. **Structured Function Calling Protocol**: Bridges OpenAI-compatible function declarations into the streaming generation loop.
1409. **Continuation Turns for Grounded Synthesis**: Verified tool results are injected back into model prompt turns as `role: "tool"` for final synthesis.
1410. **Real-Time Tool Activity Chips**: `AiToolCallCard` displays running status, execution latency, and completion state within chat turns.
1411. **Grounded Tool Result Inspector**: `AiToolResultInspector` displays verified JSON payloads, source manifests, timestamps, and content hashes.
1412. **Human-in-the-Loop Approval Modal**: `AiToolApprovalDialog` presents proposed parameters and confirmation controls for sensitive actions.
1413. **AI Tool Governance Settings**: `AiToolSettings` enables users to configure auto-approval policies and toggle individual tools.
1414. **Reference Fixtures A–J End-to-End Verification**: Validated all 10 canonical reference fixtures across automated pytest test suites.
1415. **Zero Regression on Platform Test Suites**: Maintained 100% pass rate across 32 backend pytest tests and 232 frontend vitest tests.


## Stage 127 Decisions — Build Institutional-Grade AI Research and Retrieval-Augmented Generation (RAG) Platform

### Roadmap & Scope Boundaries
1416. **Stage 127 Authority**: Stage 127 owns AI Research, Multi-Source Ingestion, Hybrid Search, Dense Vector Indexing, Evidence Assembly, and Claim Citation Grounding.
1417. **Tool Gateway Foundation**: Reuses Stage 126 AI Tool Gateway for executing approved research search and comparison tools.
1418. **Context Engine Foundation**: Reuses Stage 125 AI Context Awareness for token budgeting and focus document priority.
1419. **Conversational Assistant Foundation**: Reuses Stage 124 AI Assistant V1 for streaming generation, chat session persistence, and cancellation.
1420. **Stage 128 Financial Action Deferral**: Defers chart mutations, portfolio rebalancing, order staging, and screener execution jobs strictly to Stage 128.
1421. **Autonomous Agent Research Deferral**: No recurring unsupervised multi-agent swarms or autonomous background research loops.
1422. **Zero Shell/Python/SQL Arbitrary Execution**: RAG pipelines do not execute arbitrary shell commands, SQL queries, or Python scripts outside sandboxed engines.
1423. **Twenty Platform Routes Unchanged**: Sidebar navigation and platform top-level routes remain exactly the canonical 20 routes.

### Source Governance & Security
1424. **Canonical Source Registry**: Institutional catalog (`AtlasResearchSourceRegistry`) maintains regulatory, corporate, research, and private user repositories.
1425. **Multi-Tenant Source Isolation**: Sources and documents enforce strict tenant-level isolation (`tenant_id`); cross-tenant discovery raises `ResearchSourceAccessDeniedError`.
1426. **User-Private Vault Security**: Documents marked `USER_PRIVATE` are restricted exclusively to their creator (`owner_user_id`), invisible to all other tenant users (Fixture D).
1427. **Licensing Tiers**: Sources enforce explicit distribution licensing (`PUBLIC_DOMAIN`, `PROPRIETARY_LICENSED`, `INTERNAL_CONFIDENTIAL`, `USER_PRIVATE`).
1428. **Third-Party Model Disclosure Governance**: Evidence with `ProviderDisclosurePolicy.PROHIBITED` is blocked from external LLM transmission (`ProviderDisclosureChecker`).
1429. **Revocation Propagation**: Revoking a document (`is_revoked = True`) immediately purges it from candidate retrieval and blocks citation resolution (Fixture I).
1430. **Source Reliability Hierarchy**: Distinguishes `PRIMARY_REGULATORY` (SEC/EDGAR), `PRIMARY_OFFICIAL` (IR), `BROKER_CONSENSUS`, and `FINANCIAL_WIRE`.
1431. **Tamper-Evident Content Hashes**: Documents, revisions, and chunks carry cryptographic SHA-256 content hashes for immutability verification.
1432. **Tenant-Isolated Caching**: Redis/in-memory caches bind tenant ID prefix (`tenant_id:namespace:hash`) preventing cross-tenant leakage.
1433. **Audit Event Logging**: Research queries, passage retrieval, and citation inspection are recorded in `ResearchObservability` with user, tenant, and latency metrics.

### Document Ingestion & Chunking
1434. **Format Validation**: Accepts PDF, text, markdown, CSV, and JSON up to 50MB; rejects binaries, executable payloads, and directory-traversal filenames.
1435. **Financial Text Normalization**: Preserves financial currencies (`$`, `USD`, `EUR`), negative parentheses `(100)`, basis points, units, and fiscal periods (`FY2024`).
1436. **Structural Section Extraction**: Parses documents along `Section`, `Item`, and page boundary markers (`[Page X]`).
1437. **Paragraph-Bounded Chunking**: Structurally chunks text at section and paragraph breaks (target: 512 tokens with 50-token overlap) to avoid cutting numbers or tables.
1438. **Stable Chunk Identification**: Chunks carry deterministic, stable identifiers (`chk_<doc_id>_<idx>`) tied to document revisions.
1439. **Point-in-Time Revision Tracking**: Maintains discrete revisions (`ResearchDocumentRevision`) for annual reports, amendments, and restatements.
1440. **Async Ingestion Job Tracking**: Ingestion pipeline progresses through `PENDING -> PARSING -> EXTRACTED -> CHUNKING -> EMBEDDING -> INDEXED -> COMPLETED`.
1441. **Hierarchical Large Document Handling**: Documents exceeding context windows are summarized across structural section chunks without false claims of full reading (Fixture J).
1442. **Untrusted Document Context Fencing**: Retrieved text is tagged with `<atlas_verified_financial_context>` and marked untrusted to prevent prompt injection (Fixture F).
1443. **Zero Data Fabrication**: System never fabricates document titles, filing dates, quotes, page numbers, or URLs.

### Dense Embeddings & Hybrid Search
1444. **384-Dimensional Dense Vectors**: Uses normalized 384-dimensional dense vectors (`AtlasDeterministicEmbeddingProvider`, model: `atlas-fin-embed-v1`).
1445. **L2 Unit Normalization**: Embeddings are normalized to the unit sphere so dot-product equals cosine similarity.
1446. **Lexical BM25 Search**: Sublinear term frequency scoring with English stopword filtering preventing false positives on common words (`what`, `is`, `in`).
1447. **Semantic Vector Search**: Cosine similarity retrieval with thresholding (`score > 0.15`) ensuring only semantically aligned passages rank.
1448. **Reciprocal Rank Fusion (RRF)**: Combines lexical and semantic rankings using standard $RRF(d) = \sum \frac{1}{60 + \text{rank}_m(d)}$.
1449. **Hard Security & Temporal Filtering**: Evaluates revocation, tenant isolation, user privacy, and historical as-of dates *before* ranking.
1450. **Historical Point-in-Time Cutoff**: Query historical as-of dates (`historical_as_of`) strictly filter out sources published after the cutoff date, preventing look-ahead bias (Fixture C).
1451. **Candidate Deduplication**: Deduplicates redundant chunks based on content hash while preserving distinct document revision numbers (e.g. restatements).
1452. **Regulatory Tier Reranking**: Applies institutional score boosts (1.15x) for audited regulatory filings (10-K, 10-Q).
1453. **Extensible Embedding Provider Registry**: `EmbeddingProviderRegistry` enables hot-swapping deterministic or transformer embedding providers.

### Financial Accuracy, Evidence & Citations
1454. **Grounded Mathematical Reasoning**: Computes financial growth rates and differences with explicit periods and stated currencies (Fixture A: 25% revenue growth, 100M to 125M USD).
1455. **Comparative Variance Analysis**: Analyzes planned CapEx changes across document revisions, identifying exact numerical differences (Fixture B: 30M USD expansion).
1456. **Conflicting Source Reconciliation**: Reconciles differing figures across documents, explaining distinct accounting definitions (Fixture H: GAAP 35M vs Non-GAAP 52M).
1457. **Insufficient Evidence Handling**: When evidence is absent, returns `INSUFFICIENT_EVIDENCE` status rather than hallucinating estimates (Fixture G).
1458. **Bounded Context Assembly**: Context assembler packs evidence units into fenced blocks respecting exact token budgets (`token_budget`).
1459. **Source Manifest Transparency**: Research answers include `ResearchSourceManifest` summarizing sources evaluated, used, excluded, and conflict notes.
1460. **Server-Authoritative Citation Validation**: Server parses model citation tokens (`[cite:...]`); fabricated tokens like `[Source 999]` are rejected and stripped (Fixture E).
1461. **Claim-Level Grounding**: Citations tie assertions to verified evidence units with exact quote spans and page numbers.
1462. **Re-Authorized Citation Resolution**: Interactive citation resolution checks document revocation and user permissions at click time (`GET /api/v1/ai/research/citations/{id}`).
1463. **Interactive UI Citation Badges**: `AiResearchCitation` renders clickable badges with verification status (`VERIFIED`, `REJECTED`, `EXPIRED`).
1464. **Citation & Evidence Viewers**: `AiResearchCitationViewer` and `AiResearchEvidenceInspector` display verified source spans and metadata.
1465. **Stage 128 Financial Actions Handoff**: Research platform is fully read-only and prepared to pass grounded evidence to Stage 128 financial actions.


## Stage 128: AI Financial Action Engine

### Roadmap & Scope Boundaries
1466. **Stage 128 Financial Action Engine Ownership**: Stage 128 owns natural-language action translation, preview generation, human approval, and execution for Charts, Screeners, Portfolios, and Risk.
1467. **Stage 124 Assistant & Overlay Integration**: Directly surfaces action preview cards and confirmation controls in `AtlasAiOverlay` and `/ai`.
1468. **Stage 125 Context Awareness Engine Reuse**: Context resolver maps focused chart panels, active portfolios, and security universes without duplicate context builders.
1469. **Stage 126 Secure Tool Gateway Enforcement**: Action tools invoke backend services through the Stage 126 Gateway with zero-trust validation.
1470. **Stage 127 Grounded Evidence Handoff**: Actions consume verified research outputs without allowing untrusted text to trigger side effects.
1471. **Stage 129 Maps Separation**: Future geospatial analysis and Maps milestones remain completely untouched.
1472. **Live Broker Orders Prohibited**: Real trading and order submissions are strictly blocked at the service boundary (`AiActionBrokerExecutionProhibitedError`).
1473. **Autonomous Agent Swarms Prohibited**: No recurring unsupervised trading or mutation loops.
1474. **Preservation of 20 Platform Routes**: All 20 canonical sidebar routes remain intact.

### Action Architecture & Domain
1475. **Singleton Action Registry**: `AtlasActionRegistry` discovers and indexes all supported action types, schemas, and adapters.
1476. **Deterministic Action Identification**: Every planned action receives a stable identifier (`act_<uuid>`).
1477. **SemVer Action Versioning**: Actions carry explicit schema versions (`1.0.0`).
1478. **Action Classification Taxonomy**: Operations are classified as `READ_ONLY`, `SESSION_UI_CHANGE`, `PERSISTENT_CONFIGURATION_CHANGE`, `SAVED_ANALYTICAL_DRAFT`, or `COMPUTATION_JOB`.
1479. **Multi-Action Plan Graphs**: Multi-step plans maintain explicit prerequisite dependency graphs (`AiFinancialActionPlan`).
1480. **Intent Interpretation & Parameter Extraction**: Translates natural language into typed parameter dictionaries.
1481. **Canonical Context Binding**: Automatically resolves active chart IDs, portfolio IDs, and security symbols from session context.
1482. **Strict Parameter Validation**: Validates all arguments against domain schemas prior to preview generation.
1483. **Cryptographic Action Previews**: Previews compute before/after diffs, financial impact, and cryptographic preview hashes `sha256(canonical_json(args + diffs))`.
1484. **Human Approval Binding**: User confirmation binds strictly to `(user_id, tenant_id, action_id, target_resource, resource_revision, normalized_args_hash, preview_hash, expires_at)`.
1485. **Verified Service Execution**: Only real service responses can finalize an action as completed.
1486. **Immutable Execution Receipts**: Successful executions generate verifiable receipts (`AiActionExecutionReceipt`) recording revisions before/after.
1487. **Rollback & Compensation for Reversible Actions**: Supports undoing reversible configuration changes by restoring prior snapshots.
1488. **Privacy-Preserving Audit Logging**: Action audits record intent, hashes, and diffs without leaking unrestricted raw private financial data.

### Approval, Security & Concurrency
1489. **Server Authority**: The backend evaluates permissions and safety; model proposals are treated as untrusted input.
1490. **Approval Substitution Defense**: Attempting to execute an action with a different resource or modified arguments triggers `AiActionApprovalMismatchError` (Fixture E).
1491. **15-Minute Approval Expiration**: Approvals expire after 15 minutes, requiring renewed confirmation.
1492. **Single-Use Approval Replay Protection**: Approvals are marked consumed upon execution; duplicate use raises `AiActionReplayDetectedError`.
1493. **Optimistic Concurrency Revision Locking**: Validates target resource revision before execution; concurrent modifications raise `AiActionResourceConflictError` (Fixture F).
1494. **Fresh Re-Authorization**: Permissions are re-checked at dispatch time even if previously approved.
1495. **Idempotency Caching**: Client idempotency keys ensure duplicate network requests return cached receipts without repeated execution (Fixture G).
1496. **Multi-Tenant & RLS Enforcement**: Database tables enforce tenant and user isolation across all action plans and receipts.
1497. **External Model Disclosure Guardrails**: Verifies tenant disclosure policies before sending financial parameters to AI providers.
1498. **Source Entitlement Verification**: Enforces licensing and entitlement boundaries across data sources.
1499. **Prohibited Trading Detection**: Rejects broker order requests with institutional explanations (Fixture I).
1500. **Prohibited Ledger Mutation Detection**: Rejects direct cash or accounting ledger mutations (Fixture H).
1501. **Prompt Injection Defense**: Injected commands in research text are isolated and ignored.

### Domain Adapters: Charts, Screeners, Portfolios, Risk
1502. **Chart Configuration Adapter**: Coordinates instrument selection, timeframes (`1m` to `1M`), chart types, and comparisons.
1503. **Supported Indicator Verification**: Validates parameter bounds for SMA, EMA, RSI, MACD, BOLL, VOL, ATR, and VWAP (Fixture A).
1504. **Normalized Comparison Charts**: Automatically normalizes comparison instruments to common percentage bases.
1505. **Reversible Chart Snapshots**: Maintains layout snapshots enabling full undo restoration.
1506. **Screener Natural-Language Adapter**: Translates natural language into typed filter rules (`revenue_growth_yoy`, `net_profit_margin`, `market_cap`).
1507. **Metric Registry Validation**: Rejects unrecognized financial metrics and unsupported operators.
1508. **Genuine Screener Query Execution**: Executes queries over real security datasets without fabricated matches (Fixture B).
1509. **Screener Revision Concurrency**: Detects concurrent updates to saved screeners, preventing accidental overwrites.
1510. **Portfolio Analytical Simulation Only**: Restricts portfolio actions to analytical comparisons and hypothetical target weights.
1511. **Portfolio Weight Normalization Constraint**: Enforces target weights sum to 100% (within 0.5% tolerance) and long-only constraints.
1512. **Mathematical Allocation Deltas**: Computes exact percentage point and notional currency deltas (Fixture C: -10 pp / -$10k Equity, +10 pp / +$10k Bonds).
1513. **Mandatory Hypothetical Disclaimer**: All scenario outputs carry prominent "Hypothetical Allocation Proposal — Not Executed" badges.
1514. **Worker-Backed Risk Computation**: Schedules real risk models (Historical VaR, Parametric VaR, Expected Shortfall, Stress Testing) on worker infrastructure.
1515. **Immutable Risk Run Records**: Completed risk calculations are permanently archived; undo attempts are strictly rejected (`AiActionUndoUnavailableError`).
