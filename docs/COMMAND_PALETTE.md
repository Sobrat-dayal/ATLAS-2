# COMMAND PALETTE ARCHITECTURE (STAGE 46)

## 1. Overview & Core Architecture

The Command Palette is the keyboard-first, accessible control surface for discovering and executing explicitly registered ATLAS application commands.

```text
                       User
                         │
                  Cmd/Ctrl + K
                         │
                         ▼
                 Command Palette
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
          Navigation   Shell     Existing
           Commands   Commands    Actions
              │          │          │
              └──────────┼──────────┘
                         ▼
                  Command Registry
                         │
                         ▼
                 Typed Command ID
                         │
                         ▼
                Command Executor
                         │
                         ▼
               Existing ATLAS APIs
                / frontend actions
```

### Core Principle
Stage 46 builds a **discoverable command palette**, not the ATLAS command language.
- Stage 47 builds **ATLAS Command Parsing** (parsing textual grammar like `NVDA CHART`, `/markets`, etc.).
- Stage 48 builds **Natural-Language Command Interpretation**.
- Stage 46 performs **deterministic local command matching** against explicitly registered commands.

---

## 2. Global Search vs. Command Palette Boundaries

| Feature | Stage 45 Global Search | Stage 46 Command Palette |
|---|---|---|
| **Primary Domain** | Universal Entities (Securities, Companies, Macro, etc.) | Registered application actions & module navigation |
| **Identity Model** | `GlobalSearchEntityResult` (`entity_id` UUID) | `CommandDefinition` (stable string command ID) |
| **Backend Engine** | PostgreSQL (B-tree + `pg_trgm`) | Frontend-local static registry (0 network requests) |
| **Trigger** | Clicking search input / "Search Entities" command | `Cmd+K` (macOS), `Ctrl+K` (Windows/Linux) or badge button |
| **Interaction** | Updates global selected entity context | Executes application action (navigates, toggles shell, etc.) |

When a user selects the "Search Entities" command inside the Command Palette:
1. The Command Palette closes cleanly.
2. The Stage 45 Global Search bar receives focus and expands.

---

## 3. Shortcut & Context Rules

### Global Hotkeys
- **macOS**: `Cmd + K`
- **Windows / Linux**: `Ctrl + K`
- **Escape**: Closes the Command Palette and restores previous focus.

### Editing Context Exclusion
To prevent interfering with active code or multiline text editing, `useCommandPaletteShortcut` checks `isEditingContext`:
- Ignored if event target is inside Monaco Editor (`.monaco-editor`) or explicit `[data-skip-command-palette="true"]`.
- Ignored if event target is an active multiline `textarea` or `contenteditable` node.

---

## 4. Command Definition Model

```typescript
export interface CommandDefinition {
  id: string; // Stable, machine-readable identifier (e.g. "navigation.markets")
  label: string; // Human-readable label (e.g. "Go to Markets")
  description?: string; // Concise explanation of action
  category: CommandCategory; // "navigation" | "search" | "selection" | "settings" | "shell"
  keywords?: string[]; // Curated search keywords
  aliases?: string[]; // Search aliases
  icon?: ComponentType<{ className?: string }>;
  shortcut?: string; // Optional platform shortcut display
  availability?: (context: CommandContext) => CommandAvailability; // "available" | "hidden" | "disabled"
  execute: (context: CommandContext, helpers: CommandExecutionHelpers) => Promise<void> | void;
}
```

---

## 5. Registered Commands

### Exactly 20 Module Navigation Commands
Mapped directly from Stage 4 `ATLAS_MODULES_LIST`:
1. `navigation.home` (`/home`): Go to Home
2. `navigation.markets` (`/markets`): Go to Markets
3. `navigation.charts` (`/charts`): Go to Charts
4. `navigation.watchlists` (`/watchlists`): Go to Watchlists
5. `navigation.screeners` (`/screeners`): Go to Screeners
6. `navigation.companies` (`/companies`): Go to Companies
7. `navigation.economics` (`/economics`): Go to Economics
8. `navigation.news` (`/news`): Go to News
9. `navigation.research` (`/research`): Go to Research
10. `navigation.maps` (`/maps`): Go to Maps
11. `navigation.intelligence` (`/intelligence`): Go to Intelligence
12. `navigation.options` (`/options`): Go to Options
13. `navigation.trading` (`/trading`): Go to Trading
14. `navigation.portfolios` (`/portfolios`): Go to Portfolios
15. `navigation.risk` (`/risk`): Go to Risk
16. `navigation.ai` (`/ai`): Go to AI Assistant
17. `navigation.data` (`/data`): Go to Data
18. `navigation.saved` (`/saved`): Go to Saved
19. `navigation.workspaces` (`/workspaces`): Go to Workspaces
20. `navigation.agents` (`/agents`): Go to Agents

### Shell & Utility Commands
- `settings.global.open`: "Open Global Settings" (navigates to `/settings`)
- `settings.section.open`: "Open Current Section Settings" (opens drawer for active module if settings exist)
- `search.focus`: "Search Entities" (focuses Stage 45 Global Search)
- `entity.selection.clear`: "Clear Selected Entity" (visible only when an entity is selected; clears global selection)
- `shell.sidebar.toggle`: "Toggle Sidebar" (collapses/expands sidebar)
- `shell.agent_dock.toggle`: "Toggle Agent Dock" (opens/closes agent dock)

---

## 6. Deterministic Matching & Ranking

Matching is executed 100% locally on the client without network requests or external dependencies:

| Tier | Matching Strategy |
|---|---|
| **Tier 1** | Exact label match |
| **Tier 2** | Exact alias match |
| **Tier 3** | Label prefix match (full label or word prefix) |
| **Tier 4** | Alias prefix match |
| **Tier 5** | Keyword exact or prefix match |
| **Tier 6** | Label substring match |
| **Tier 7** | Description substring match |
| **Tier 8** | Lightweight deterministic fuzzy match (subsequence or bounded edit distance <= 2) |

### Deterministic Tie-Breaking
1. Match Tier (ascending, Tier 1 is best)
2. Category order (`navigation` -> `search` -> `selection` -> `settings` -> `shell`)
3. Shorter label length
4. Alphabetical label
5. Stable command ID

---

## 7. Accessibility & UI Specifications

- **Dialog & Combobox semantics**:
  - `role="dialog"`, `aria-modal="true"`, `aria-label="Command Palette"`
  - `role="combobox"`, `aria-expanded="true"`, `aria-autocomplete="list"`
  - `role="listbox"`, `role="option"`, `aria-selected`
  - `aria-activedescendant` synced with highlighted command
- **Keyboard navigation**:
  - `ArrowDown` & `ArrowUp` cycle through results (with wraparound at ends)
  - `Home` & `End` jump to top and bottom
  - `Enter` executes the currently highlighted command
  - `Escape` closes the palette and restores previous DOM focus
- **Zero auto-run**:
  - Typing a command never runs it automatically; explicit selection via Enter or mouse click is required.

---

## 8. Stage 47 Integration: Structured Command Language & Preview

In Stage 47, the Command Palette was augmented with structured command parsing:
- **Detection (`looksLikeAtlasStructuredCommand`)**:
  - Inputs starting with `/` (e.g. `/markets`, `/charts NVDA`).
  - Inputs with shorthand keywords (e.g. `NVDA CHART`, `MAP TSMC`, `OPTIONS NVDA`, `NVDA FA`, `PORT RISK`).
- **Debounced Backend Parsing**:
  - Queries `POST /api/v1/commands/parse` with a 150ms debounce.
  - AbortController cancels pending requests when input changes to prevent stale responses.
- **Command Preview Card**:
  - Shows `READY` preview with destination module and resolved target (display name, ticker/exchange).
  - Shows `INCOMPLETE` with target requirement prompt.
  - Shows `AMBIGUOUS` with candidate picker list.
  - Shows `INVALID` with concise error message.
  - Shows `UNAVAILABLE` with deferred feature notice (e.g. `NVDA FA`).
- **Explicit Execution**:
  - User must press `Enter` or click the preview card to execute.
  - Executes bound command ID with typed arguments (e.g. `entityId`), updating global selected entity and navigating router.

---

## 9. Stage 48 Integration: Natural-Language Command Interpretation

In Stage 48, the Command Palette integrates bounded natural-language command interpretation:
- **Zero Keystroke Model Calls**: Typing in the search bar performs fast local Stage 46 matching and Stage 47 syntax detection. It never triggers the model automatically.
- **"Interpret as ATLAS command" Option**: For non-empty unstructured input, a dedicated action row (`Sparkles` icon) appears at the bottom of the palette results list.
- **Explicit Trigger**: The user must explicitly press Enter on or click "Interpret as ATLAS command".
- **Visual Progress**: A compact, non-intrusive spinner displays while the single-turn backend call `POST /api/v1/commands/interpret` is running.
- **Preview & Confirmation (No Autoexecution)**:
  - `READY`: Displays a preview card showing the destination module, resolved entity details, and an explicit action button ("Open" / "Run command"). User executes via Enter or click.
  - `AMBIGUOUS`: Renders the clarification question or entity candidate selector.
  - `NOT_COMMAND`: Informs the user that the query is an informational question rather than an actionable command.
  - `UNSUPPORTED`: Displays server-owned refusal banner for unpermitted actions (e.g. trading, agents, shell).
  - `INTERPRETER_UNAVAILABLE`: Displays graceful degradation notice indicating structured commands remain functional.
- **Stale Response Protection & Reset**:
  - An `input_fingerprint` ensures an in-flight interpretation for query A is discarded if the query text changed to query B.
  - Closing the palette aborts active requests and clears all interpretation state.


