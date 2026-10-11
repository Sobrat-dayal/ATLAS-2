# Stage 50 — Persistent Bottom Taskbar & Workspace Panel Architecture

## 1. Overview & Architectural Role

ATLAS introduces a persistent, VS Code-inspired bottom taskbar and expandable bottom workspace panel (`Region E` in the frozen five-region UI layout).

The bottom taskbar is a global application-shell component permanently attached to the bottom edge of the authenticated ATLAS workstation. It persists across client-side module navigation between all 20 canonical ATLAS modules, without remounting or resetting panel state.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ ATLAS  │ Universal Search / Commands │ AI │ Notifications │ Profile     │
├──────────────┬───────────────────────────────────────────┬───────────────┤
│              │                                           │               │
│  SIDEBAR     │                                           │  AGENT DOCK   │
│              │             ACTIVE ATLAS MODULE           │               │
│  Home        │                                           │               │
│  Markets     │                                           │               │
│  Charts      │                                           │               │
│  Companies   │                                           │               │
│  ...         │                                           │               │
│  Agents      │                                           │               │
│              ├───────────────────────────────────────────┤               │
│              │             BOTTOM WORKSPACE PANEL        │               │
│              │                                           │               │
│              │    Active taskbar panel content           │               │
├──────────────┴───────────────────────────────────────────┴───────────────┤
│ Tasks │ Agents │ Jobs │ Alerts │ Downloads │ System │    >_ Terminal    │
└──────────────────────────────────────────────────────────────────────────┘
```

The component hierarchy in the authenticated AppShell is:

```text
Authenticated AppShell
         │
         ├── TopBar
         │
         ├── Middle Layer (Sidebar + Workspace Column + AgentDock)
         │    ├── Sidebar (20 canonical modules)
         │    ├── Workspace Column
         │    │    ├── MainWorkspace (Active module view, scrollable)
         │    │    └── BottomPanelHost (Active workspace panel, resizable)
         │    └── AgentDock (Persistent quick-access dock on right)
         │
         ├── BottomTaskbar (Pinned to bottom edge, full viewport width)
         │
         ├── NotificationCenter (Stage 49 TopBar overlay)
         └── CommandPalette (Stage 46 overlay)
```

---

## 2. Core Architectural Rule: Shell vs. Execution Systems

**Stage 50 builds the shell and hosting infrastructure, not the underlying execution systems.**

The taskbar establishes:
1. Permanent bottom taskbar (`BottomTaskbar`).
2. Taskbar navigation and button selection (`BottomTaskbarItem`).
3. Expandable bottom panel host (`BottomPanelHost`).
4. Resizable panel with pointer and keyboard controls (`BottomPanelResizeHandle`).
5. Responsive behavior and overflow menu (`BottomTaskbarOverflowMenu`).
6. Typed panel registry (`BottomPanelRegistry`).
7. Presentation lifecycle and toggle behavior.
8. Factual, grounded placeholder states where execution backends belong to future roadmap stages (`ReservedPanelState`).
9. Uninterrupted coexistence with existing shell systems (Search, Command Palette, Notification Center, Selected Entity, WebSockets).

Stage 50 does **not** implement:
- Task execution, scheduling, approvals, or task databases (Stage 54+).
- Agent runtime, execution, or autonomous teams (Stage 146+).
- Job queues, workers, cancellations, or retry engines (Future operational services).
- Alert rule builders, price alerts, risk alerts, or notification triggers (Future alert engines).
- File export queues, download workers, or browser download interception (Future artifact services).
- Terminal shell sessions, command prompts, xterm.js, or subprocess execution (Stage 122/123).
- Realtime taskbar transports, Redis keys, ClickHouse schemas, or backend API mutations.

---

## 3. Typed Panel Registry

Panel definitions are statically registered, typed, and validated:

| Panel ID | Label | Placement | Availability | Implementation Status (Stage 50) | Future Canonical Owner |
|---|---|---|---|---|---|
| `tasks` | Tasks | Primary | `reserved` | Operational shell & reserved state | Stage 54 (Home Tasks / Approvals) |
| `agents` | Agents | Primary | `reserved` | Operational shell & reserved state | Stage 146–148 (Agents V1 & Teams) |
| `jobs` | Jobs | Primary | `reserved` | Operational shell & reserved state | Future background job management |
| `alerts` | Alerts | Primary | `reserved` | Operational shell & reserved state | Future Watchlist / Risk alert engines |
| `downloads` | Downloads | Primary | `reserved` | Operational shell & reserved state | Future artifact & export services |
| `system-health` | System Health | Primary | `reserved` | Factual connectivity status | Future observability integration |
| `terminal` | Terminal | Trailing | `reserved` | Trailing launcher & reserved state | Stage 122 (Terminal) / 123 (Execution) |

### Registry Invariants
- Exactly 7 registered panels.
- Fixed canonical order: `tasks`, `agents`, `jobs`, `alerts`, `downloads`, `system-health`, `terminal`.
- `terminal` has placement `trailing` and renders aligned to the right edge.
- All other 6 panels have placement `primary` and render aligned to the left edge.
- Registry is frozen (`Object.freeze`) and validated at module import and in tests.

---

## 4. State & Lifecycle Architecture

### State Model
```typescript
interface BottomPanelState {
  activePanelId: BottomPanelId | null;
  isOpen: boolean;
  panelHeight: number;
}

interface BottomPanelController {
  activePanelId: BottomPanelId | null;
  isOpen: boolean;
  panelHeight: number;
  openPanel: (id: BottomPanelId) => void;
  closePanel: () => void;
  togglePanel: (id: BottomPanelId) => void;
  setPanelHeight: (height: number) => void;
}
```

### Lifecycle Semantics
- **Initial State**: Bottom panel is closed (`activePanelId = null`, `isOpen = false`), while `BottomTaskbar` is permanently visible.
- **Open Panel**: Clicking an inactive panel item (e.g. `Jobs`) sets `activePanelId = "jobs"`, expands `BottomPanelHost` to `panelHeight`, and renders the corresponding component.
- **Switch Panel**: Clicking a different panel item (e.g. `Alerts`) replaces content without closing or animating height recalculations.
- **Toggle / Close**: Clicking the already-active panel button toggles `activePanelId` to `null`, collapsing the bottom panel host.
- **Close Button**: Clicking the `X` icon in `BottomPanelHeader` sets `activePanelId = null`.
- **Keyboard Escape**: Pressing `Escape` closes the bottom panel if no higher-priority modal (Command Palette, Notification Center, Dialog) is open.

---

## 5. Panel Sizing & Resizing

- **Default Height**: `280px`.
- **Minimum Height**: `160px`.
- **Maximum Height**: `45%` of available viewport height (`Math.floor(window.innerHeight * 0.45)`), bounded to `640px`.
- **Height Clamping**: Enforced via `clampBottomPanelHeight(requestedHeight, viewportHeight)`.
- **Top Resize Handle**:
  - Pointer capture enables smooth drag up (increases height) and drag down (decreases height).
  - Double-click on handle restores default height (`280px`).
  - Keyboard accessible: `role="separator"`, `tabIndex={0}`, handles `ArrowUp` (+16px), `ArrowDown` (-16px), `Home` (min 160px), `End` (max 45%), `Enter` (reset 280px).
- **Workspace Adaptation**: When `BottomPanelHost` is open, `MainWorkspace` shares the vertical column via flexbox. The active module content automatically adjusts its height and retains its own independent vertical scrollbar.

---

## 6. Persistence & Context Isolation

- **AppShell Navigation**: Panel selection and height survive client-side routing across all 20 modules (`/home` -> `/markets` -> `/companies` -> `/agents`) because the shell remains mounted.
- **User Preference Storage**: State is persisted per authenticated principal in `atlas.user.${userId}.shell-state` (or fallback `atlas-shell-state`).
- **Principal Switch**: On user logout or authentication switch, shell state resets and rehydrates strictly for the active principal.
- **Selected Entity Context**: Taskbar panel selection, opening, closing, or resizing does **not** mutate or clear `selectedEntityId` (Stage 25).
- **WebSocket Preservation**: Taskbar operations do **not** trigger WebSocket reconnects or remounts (Stage 43).

---

## 7. Factual Grounding & No Fake Data Policy

In accordance with strict production principles:
1. **Tasks**: Displays factual reserved state. No fake "3 pending tasks" or fake task lists.
2. **Agents**: Explicitly indicates that autonomous runtime details belong to Stage 146+. Recommends navigating to `/agents` module route. Confirms separation from right Agent Dock.
3. **Jobs**: Factual reserved state. No fake progress bars, fake queue counters, or synthetic worker statuses.
4. **Alerts**: Factual reserved state. Explains that alerts represent monitoring trigger conditions, while delivered user messages are managed in the TopBar Notification Center (Stage 49).
5. **Downloads**: Factual reserved state. No fake downloadable files or browser download interception.
6. **System Health**: Grounded connectivity dimensions only:
   - Market Data WebSocket (Stage 43): Connected in AppShell.
   - FastAPI Backend API (Stage 11): Reachable.
   - PostgreSQL, ClickHouse, Redis, Workers: Grounded as "Status unavailable - detailed health telemetry not connected".
   - Clear notice: *Connectivity != service health*. No credentials, secrets, or IP addresses exposed.
7. **Terminal**: Trailing button opens informational reserved panel. No shell prompt, no executable input, no xterm.js, no subprocess.

---

## 8. Responsive & Accessibility Architecture

- **Desktop (>= 768px)**: All 6 primary items visible on the left; Terminal visible on the right.
- **Narrow Screens (< 768px)**: First 3 primary items visible directly; remaining items accessible via a keyboard-operable `More` overflow menu (`BottomTaskbarOverflowMenu`). Terminal remains accessible on the right.
- **ARIA Semantics**:
  - Taskbar container: `role="toolbar"`, `aria-label="Application Taskbar"`.
  - Taskbar buttons: `type="button"`, `aria-label="Open [Panel] panel"`, `aria-expanded`, `aria-controls`, `aria-pressed`.
  - Panel host: `role="region"`, `aria-label="[Panel] Panel"`, `h3` heading in header.
  - Resize handle: `role="separator"`, `aria-orientation="horizontal"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`.
  - Overflow menu: `aria-haspopup="true"`, `role="menu"`, `role="menuitem"`.
- **Keyboard Navigation**: Full Tab order, Enter/Space activation, Esc dismiss, and Arrow-key resizing.
