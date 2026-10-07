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
