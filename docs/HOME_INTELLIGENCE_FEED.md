# ATLAS — STAGE 55: HOME INTELLIGENCE FEED PLACEHOLDER
## Intelligence Dashboard Foundation, Future Event Integration and Source-Aware Intelligence Presentation

---

## 1. Executive Summary & Purpose

Stage 55 establishes the **Home Intelligence Feed presentation foundation** for the ATLAS Home operational command center (`/home`, Module 1).

ATLAS unites financial, economic, corporate, and real-world intelligence into an integrated operating environment. However, canonical intelligence collection, Universal Event architecture, geopolitical event scoring, exposure propagation, and AI intelligence analysis are dedicated capabilities scheduled for subsequent roadmap stages (Stages 135–140).

**Stage 55 is a frontend-first presentation foundation, not an operational Intelligence Engine.**

Its purpose is to:
1. Establish a visible, compact Intelligence Feed region on the Home dashboard.
2. Accurately communicate that full intelligence services are not yet connected (`Reserved` state).
3. Provide working, permission-aware navigation to the canonical `/intelligence` module.
4. Establish a minimal, typed presentation contract (`IntelligenceFeedViewState`, `IntelligenceFeedViewItem`) for future UI rendering without prematurely constraining the canonical Universal Event schema.
5. Define future source-aware provenance, timestamp, and Entity-navigation requirements.
6. Preserve responsive design, accessibility, and error isolation without fabricated events, fake scores, or synthetic alerts.

---

## 2. Actual Component Hierarchy

```text
HomePage (/home)
   │
   ├── HomeHeader
   │      └── HomeQuickActions
   │
   └── HomeDashboardGrid
          │
          ├── Column 1 (Primary / 7 cols)
          │      ├── HomeCurrentContext       (Stage 25 Selected Entity Context)
          │      ├── HomeMarketSummary        (Stage 52 Market Overview)
          │      └── HomePersonalizedActivity (Stage 53 Personalized Activity)
          │
          └── Column 2 (Secondary / 5 cols)
                 ├── HomeQuickLaunch          (Canonical Workspaces)
                 ├── HomeTasksApprovals       (Stage 54 Tasks & Approvals)
                 └── HomeIntelligenceFeed     (Stage 55 Intelligence Feed Foundation)
                        │
                        ├── IntelligenceFeedHeader
                        │      ├── Title ("Intelligence Feed")
                        │      ├── Status Badge ("Not Connected")
                        │      └── Open Intelligence Action (Links to /intelligence)
                        │
                        └── IntelligenceFeedReservedState
                               ├── Neutral Icon (Radio / Sensor)
                               ├── Heading ("Intelligence feed not connected")
                               ├── Truthful Explanatory Copy
                               └── Open Intelligence Workspace Button
```

---

## 3. Status Semantics: The Reserved State

| Status | Meaning | When Displayed |
|---|---|---|
| **Reserved** | The domain service is not yet implemented or connected. | **Stage 55 (Default & Authoritative)** |
| **Loading** | An authentic backend query is in progress. | Future (Stage 138+) |
| **Ready** | An authoritative service is connected and returned items to display. | Future (Stage 138+) |
| **Empty** | An authoritative service query executed successfully and returned 0 items. | Future (Stage 138+) |
| **Unavailable**| A previously operational service is temporarily offline or unreachable. | Future (Stage 138+) |
| **Error** | A real network request to an existing service failed. | Future (Stage 138+) |

### Mandatory Architectural Distinctions
- **Reserved vs Empty**: "Empty" means a connected service returned zero items. In Stage 55, no backend service exists; therefore the feed is **Reserved**, not Empty.
- **Mounted UI vs Operational System**: The fact that `HomeIntelligenceFeed` renders cleanly on the client does not imply the Intelligence Engine exists.
- **Zero is not Unknown**: No fake counts ("0 threats", "0 events") are displayed. When no service exists, counts are unknown.

---

## 4. Minimal Typed Presentation Contract

Location: `apps/web/src/lib/intelligence-feed/types.ts`

```typescript
export type IntelligenceFeedViewState =
  | "reserved"
  | "loading"
  | "ready"
  | "empty"
  | "unavailable"
  | "error";

export interface IntelligenceFeedViewItem {
  id: string;
  title: string;
  summary?: string | null;
  observedAt?: string | null;
  sourceLabel?: string | null;
  sourceCount?: number | null;
  entityIds?: string[];
  internalTarget?: {
    moduleId: string;
    entityId?: string;
  } | null;
}
```

### Presentation Boundary vs Universal Event Domain
- `IntelligenceFeedViewItem` is explicitly **presentation-only**.
- It does **not** define canonical event persistence, event deduplication, or event clustering.
- It does **not** introduce premature risk scores, impact percentages, or confidence rankings.
- All text fields are rendered as plain text. No `dangerouslySetInnerHTML`, markdown code execution, or dynamic script evaluation.

---

## 5. Future Intelligence Integration Architecture

```text
    Stage 135: Universal Event Architecture
    (Canonical event schemas, event deduplication, source validation)
                     │
                     ▼
    Stage 136: Event–Entity Relationship Graph
    (Linking events to Universal Entity UUIDs via Stage 16/23)
                     │
                     ▼
    Stage 137: Financial & Economic Exposure Engine
    (Determining direct and supply-chain exposure across entities)
                     │
                     ▼
    Stage 138: Operational Intelligence Service (Intelligence V1)
    (Validated read APIs, entity filters, pagination)
                     │
                     ▼
    Stage 139: Intelligence Scoring Engine
    (Methodological credibility, severity, and confidence scoring)
                     │
                     ▼
    Stage 140: God's Eye Intelligence
    (Geospatial 3D globe visualization, Cesium/deck.gl layers)
                     │
                     ▼
    Home Intelligence Feed Adapter (Future)
                     │
                     ▼
    HomeIntelligenceFeed (Stage 55 Presentation Surface)
```

---

## 6. Provenance & Source-Aware Presentation Requirements

Future intelligence items presented on Home must adhere to strict evidence standards:
1. **Source Attribution**: No substantive claim will be presented as verified without attributable provenance metadata from Stage 24.
2. **Timestamp Semantics**: Must distinguish:
   - Event occurrence time (`observedAt`)
   - Source publication time
   - ATLAS ingestion time
   - Last updated time
3. **No Decorative Source Walls**: Logos and source names must not be hardcoded to suggest relationships with publishers that do not exist.
4. **Untrusted Data Boundary**: External intelligence source text is untrusted display data. It must never be injected as instructions to the assistant, browser, or workflow engines.

---

## 7. Canonical Entity Integration & Navigation

- **Navigation Action**: The widget provides an "Open Intelligence" button targeting canonical `/intelligence` (`ATLAS_MODULES.intelligence.route`).
- **Authorization**: Access is governed by Stage 14 `canViewModule("intelligence")`. Unauthorized users see a disabled, restricted badge.
- **Selected Entity Context**: Reopening `/intelligence` preserves the Stage 25 Universal Entity Context (`selectedEntityId: UUID`).
- **No Entity Mutation Side-Effect**: Clicking the action does not alter the active entity selection, open a search query, or launch an agent.

---

## 8. Strict No Fake Data Policy

The implementation strictly avoids:
- Invented geopolitical conflicts, cyber incidents, or infrastructure disasters.
- Fabricated market impact predictions or sentiment classifications ("Bullish", "Bearish").
- Fake confidence scores ("97% confidence") or synthetic risk percentages.
- Deceptive "Live", "Scanning 24/7", or "AI Analyzing" status badges.
- Animated radar animations, spinning graphics, or glowing activity pulses.
- Stock photography, satellite imagery, or military art.

---

## 9. Infrastructure Boundaries

- **Backend APIs**: Zero new endpoints created (no `GET /api/v1/intelligence/feed`).
- **Database**: Zero PostgreSQL migrations, zero ClickHouse schemas, zero Redis keys or streams.
- **Transport**: Zero new WebSocket topics or event pipes. Stage 42 Market Quote updates (`market.quote.updated`) are NOT converted into intelligence events.
- **AI / LLMs**: Zero new model calls, zero embeddings, zero vector databases, zero RAG pipelines.
- **Agents & Workflows**: Zero autonomous agent runs, zero workflow executions, zero background workers.
- **Dependencies**: Zero new third-party dependencies added.

---

## 10. Responsiveness, Accessibility & Performance

- **Responsive Grid**: Fits cleanly into the 5-column secondary column of `HomeDashboardGrid.tsx` on desktop (`lg:col-span-5`) and stacks vertically on mobile without horizontal overflow (`min-w-0`).
- **Shell Compatibility**: Tested and compatible with the Agent Dock (open/closed) and Bottom Taskbar (open/closed).
- **Theme & Appearance**: Full support for dark mode, light mode, and custom watermark background contrast settings.
- **Accessibility**: Semantic heading hierarchy (`h3`, `h4`), accessible focus rings (`focus-visible:ring-atlas-teal`), keyboard activation, and screen-reader status text.
- **Performance**: 0 network requests on mount, 0 recurring timers, 0 direct provider calls. Lightweight bundle footprint.
