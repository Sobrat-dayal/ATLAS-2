# ATLAS — STAGE 51: HOME V1 ARCHITECTURE
## The ATLAS Operational Command Center

---

## 1. Executive Summary & Purpose

`Home V1` represents the primary entry point and operational dashboard of the entire ATLAS operating system, implemented at canonical route `/home` (Module 1).

ATLAS Home is **an operational command center, not a marketing landing page**. It provides:
1. **Operational Header & Global Entry Actions**: Direct invocation of Stage 45 Global Search, Stage 46 Command Palette, and core workspaces without duplicate implementations.
2. **Current Focus Context**: Truthful, real-time reflection of the Stage 25 Universal Entity Context (`selectedEntityId: UUID`), preserving entity identity authority without implicit conversions or artificial mocks.
3. **Canonical Quick Launch**: Accessible navigation into core ATLAS analytical workspaces using the Stage 4 canonical module registry and honoring Stage 14 module authorization.
4. **Extensible Dashboard Architecture**: A typed, responsive widget grid (`HomeDashboardGrid`, `HomeWidgetSurface`, `HomeReservedState`, `widget-registry.ts`) that strictly delineates Stage 51 foundations from subsequent data stages (Stage 52 Market Summary, Stage 53 Personalized Activity, Stage 54 Tasks & Approvals, Stage 55 Intelligence Feed).

---

## 2. Component Hierarchy

```text
HomePage
   │
   ├── HomeHeader
   │      │
   │      └── HomeQuickActions
   │             ├── Search Entities   (invokes Stage 45 Global Search focus)
   │             ├── Commands          (invokes Stage 46 Command Palette)
   │             ├── AI Assistant      (navigates to canonical /ai)
   │             ├── Markets           (navigates to canonical /markets)
   │             ├── Research          (navigates to canonical /research)
   │             └── Maps              (navigates to canonical /maps)
   │
   └── HomeDashboardGrid
          │
          ├── Column 1 (Primary / 7 cols)
          │      ├── HomeCurrentContext (Stage 25 Universal Entity Context)
          │      │      ├── Loading State (Skeleton / Loader)
          │      │      ├── Error State (Retryable error / Clear)
          │      │      ├── Empty State (No selection + Search Entities launcher)
          │      │      └── Ready State (Display name, entity type, UUID, context links)
          │      │
          │      └── HomeWidgetSurface [Market Overview]
          │             └── HomeReservedState (Stage 52 Roadmap Slot)
          │
          └── Column 2 (Secondary / 5 cols)
                 ├── HomeQuickLaunch (Canonical Workspaces)
                 │      ├── Curated Workspaces (10 core analytical workspaces)
                 │      ├── Expandable All Workspaces (20 canonical modules)
                 │      └── Permission Boundary (Locked disabled states)
                 │
                 └── HomeWidgetSurface [Operations & Intelligence]
                        └── HomeReservedState (Stages 53–54 Framework Slots)
```

---

## 3. Data Ownership & Authorities

| Home Area | Authority / Source of Truth | Implementation Mechanism |
|---|---|---|
| **Module Route** | Stage 4 Module Registry (`ATLAS_MODULES.home`) | `/home` canonical route |
| **Quick Actions: Search** | Stage 45 Global Search | `triggerSearchFocus()` from `useCommandPalette()` |
| **Quick Actions: Commands** | Stage 46 Command Palette | `openCommandPalette()` from `useCommandPalette()` |
| **Module Navigation** | Stage 4 Canonical Module Metadata | Next.js client-side `<Link>` components |
| **Module Authorization** | Stage 14 Authorization System | `canViewModule(moduleId)` from `useAuthorization()` |
| **Selected Entity** | Stage 25 Universal Entity Context | `useSelectedEntity()` from `@/hooks/entity` |
| **Entity Metadata** | Stage 16 Canonical Entity API | Cached React Query / Application Context state |
| **Shell & Panels** | Stage 6 & Stage 50 Application Shell | `AppShell`, `BottomTaskbar`, `AgentDock` |
| **Appearance & Theme** | Stage 7 & Stage 8 Appearance Systems | Semantic CSS variables (`globals.css`) |

---

## 4. Future Widget Roadmap Ownership

Stage 51 strictly establishes layout integration contracts and widget slots without premature feature implementation:

| Future Home Feature | Roadmap Stage | Stage 51 Status | Boundary Policy |
|---|---|---|---|
| **Home Market Summary** | Stage 52 | Implemented (Stage 52) | Integrated data-driven overview (see `HOME_MARKET_SUMMARY.md`). |
| **Personalized Activity** | Stage 53 | Reserved Slot | No localStorage tracking, recent entity logs, or history querying. |
| **Tasks & Approvals** | Stage 54 | Reserved Slot | No approval buttons, task queues, or mock job execution states. |
| **Intelligence Feed** | Stage 55 | Reserved Slot | No simulated geopolitical alerts, LLM intelligence, or sample signals. |
| **Macroeconomics Preview** | Stage 89 | Planned | Reserved in static registry; no mock calendars rendered. |
| **News Preview** | Stage 99 | Planned | Reserved in static registry; no simulated news headlines. |
| **Portfolio Summary** | Stage 110 | Planned | Reserved in static registry; no fabricated valuations or balances. |
| **Geospatial Preview** | Stage 129 | Planned | Reserved in static registry; no heavy map engines loaded. |
| **Agent Operations** | Stage 146 | Planned | Reserved in static registry; no simulated autonomous cycles. |

---

## 5. Universal Entity Semantics in Home

1. **UUID Identity Authority**: Global entity identity is strictly governed by `selectedEntityId: UUID`. Display names, tickers, and labels are derived presentations, not selection authorities.
2. **Type Segregation**: `Company` and `Security` remain strictly distinct. Selecting an equity security displays the security; selecting a company displays the company. Home performs no implicit conversion or automatic issuer traversal.
3. **Preservation Across Navigation**: Client-side navigation from Home into any module (e.g., `/home` -> `/charts`) preserves `selectedEntityId` intact.
4. **Truthful States**:
   - `loading`: Skeletons / spinner with entity ID.
   - `error`: Non-destructive error message with retry and clear controls.
   - `empty`: Honest message indicating no selection with working "Search Entities" launcher.
   - `ready`: Real display name, humanized type, canonical name, and UUID.

---

## 6. Layout, Shell, & Responsiveness

- **Desktop (Wide & Normal)**: Responsive 12-column grid (`7 cols` primary, `5 cols` secondary) with maximum width constraint (`max-w-[1600px] mx-auto`).
- **Tablet & Mobile**: Flex/single-column flow with touch-friendly spacing and clear hierarchy.
- **Agent Dock Compatibility**: Central workspace uses `min-w-0` to gracefully shrink horizontally when the 320px+ right Agent Dock is open.
- **Bottom Taskbar Compatibility**: Main workspace independently handles scrolling (`overflow-y-auto`) above the persistent bottom taskbar and open panels (e.g., 240px Tasks/Agents/Terminal panels).
- **Background & Theme**: Text, borders, and surfaces use theme tokens (`--atlas-bg-0`, `--atlas-surface-1`, `--atlas-border-default`, `--atlas-text-primary`) ensuring high contrast and legibility across dark and light modes, as well as custom user backgrounds/watermarks.

---

## 7. No Fake Data Guarantee

Home V1 contains zero synthetic metrics:
- No hardcoded stock indices or tickers (e.g., removed old mock 5,123.41 S&P 500).
- No hardcoded 24h price changes (+1.2%, -0.5%).
- No hardcoded portfolio balances ($12,450,000).
- No simulated risk indicators (34).
- No fabricated agent counts or pipeline tasks.
- No artificial marketing copy ("Revolutionize your future").

---

## 8. Verification & Test Coverage

- **Registry Tests**: 11 widget definitions validated, immutability confirmed, lookup helpers tested.
- **Quick Launch Tests**: Verified 10 primary curated workspaces and 20 canonical modules.
- **Data Integrity Tests**: Static analysis verifying zero hardcoded prices, portfolio numbers, or mock arrays in production components.
- **Accessibility Tests**: Semantic `<header>`, `<main>`, `<section aria-labelledby>`, `<button>`, `<Link>`, and `<kbd>` elements verified.
- **Next.js Production Build**: Turbopack production compilation passing cleanly with 0 TypeScript errors.
