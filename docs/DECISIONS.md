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


