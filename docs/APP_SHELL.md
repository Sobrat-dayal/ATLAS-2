# ATLAS Application Shell Architecture

This document describes the foundational desktop-first application shell designed in Stage 3.

## Shell Layout
The shell mimics a professional financial terminal, filling `100dvh` without standard browser body scrolling.

- **Top Bar**: Persistent header with brand, Context controls (Entity, Time Range), Global Search/Command input, ATLAS AI hook, UTC time, Notifications, and Profile.
- **Market Ticker**: Optional slim horizontal strip showing market indices or forex/crypto values.
- **Left Sidebar**: Expandable/collapsible navigation area for the 20 ATLAS modules.
- **Agent Dock**: Right-side resizable overlay/dock for Agent tracking and activity.
- **Bottom Taskbar**: Fixed status bar mimicking VS Code with entries for Tasks, Agents, Jobs, Alerts, System, and Terminal.
- **Main Workspace**: The primary scrollable content area where modules render their views.

## Component Hierarchy
```text
<ShellProvider>
  <GlobalApplicationContextProvider>
    <AppShell>
      <TopBar />
      <MarketTickerBar />
      <Sidebar />
      <MainWorkspace>{children}</MainWorkspace>
      <AgentDock />
      <BottomTaskbar />
    </AppShell>
  </GlobalApplicationContextProvider>
</ShellProvider>
```

## State and Persistence
Shell state is isolated from business logic and persisted using `localStorage` to ensure preferences survive reload:
- `sidebarCollapsed` (boolean)
- `agentDockOpen` (boolean)
- `agentDockWidth` (number)
- `activeBottomPanel` (string | null)

## Global Application Context
The App Shell mounts the `GlobalApplicationContextProvider` which maintains the canonical global semantic context (Selected Entity, Time Range, etc).
- Context is maintained across module navigation (Sidebar route changes do not clear context).
- Context indicators live in the Top Bar (`SelectedEntityControl`, `GlobalTimeRangeControl`).

## Future Extension Points
- **Agent Dock**: Currently contains empty state placeholders. Will handle AI chat and autonomous agent flows.
- **ATLAS AI / Top Bar Hooks**: UI entry points exist but have no backend integration yet.
- **Bottom Panel**: Clicking taskbar items toggles a placeholder bottom panel area. To be populated in subsequent stages.
- **Command Palette (Stage 46)**: Global keyboard shortcut `Cmd/Ctrl+K` opens the Command Palette overlay for discoverable module navigation and shell commands. Global Entity Search (Stage 45) remains active in the center TopBar.

## Dimensions (Tokens)
- Sidebar: 160px expanded, 56px collapsed
- TopBar: 44px
- Ticker: 28px
- Taskbar: 32px
- Agent Dock: 320px default, resizable to max 600px
