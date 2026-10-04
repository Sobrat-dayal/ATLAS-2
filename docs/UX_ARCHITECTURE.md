# ATLAS UX Architecture

*Note: The fundamental UI Shell was implemented in Stage 3. Refer to [APP_SHELL.md](./APP_SHELL.md) for shell-specific layout rules and state management.*
ATLAS utilizes a professional, desktop-first terminal layout designed to accommodate serious financial workflows.

## Global Application Layout

### Left Side
Persistent primary navigation containing exactly 20 modules in this order: Home, Markets, Charts, Watchlists, Screeners, Companies, Economics, News, Research, Maps, Intelligence, Options, Trading, Portfolios, Risk, AI Assistant, Data, Saved, Workspaces, Agents.
At the bottom of the left navigation:
- Main Settings
- Account/Profile access
- Help/Documentation access

### Top Bar
- ATLAS logo/product identity
- Universal search
- Command palette
- Current Context indicator
- ATLAS AI button (top right)
- Notifications
- Profile/Account controls
- Global status controls

### Center
The active module or workspace.

### Right Side: Agent Dock
A collapsible dock that allows the user to:
- See pinned agents
- Monitor working/idle/waiting agents
- Inspect current agent activity
- Open an agent or assign quick tasks
- Create a new agent
- Jump to the full Agents module

### Bottom
A VS Code-style bottom taskbar exposing:
- Tasks, Agents, Jobs, Alerts, Downloads, System status
- **Terminal:** The Terminal launch control is located toward the bottom-right. The browser terminal must use controlled/sandboxed environments and not expose unrestricted production shell access. Future modes include ATLAS CLI, Python, SQL, Agents, MCP, Logs, and Tasks.

## ATLAS AI: Overlay vs. Module

ATLAS AI exists as two distinct conceptual surfaces using shared infrastructure:
1. **ATLAS AI Overlay:** Accessible globally via the top-right button. Used for quick questions, page context, navigation, command execution, quick analysis, and delegating simple tasks.
2. **AI Assistant Module:** The full workstation (Module 16) designed for long conversations, deep research, data analysis, multi-agent collaboration, and detailed artifact generation.

## Global Context System

ATLAS automatically propagates context across the application. The system understands the currently selected:
- User, Module, Workspace
- Financial Entity (e.g., Company, Security)
- Portfolio, Watchlist
- Date/Time range
- Chart, Map location/layers, Geographic object
- Open documents, Active filters, Agent/Task

When an entity like "NVIDIA" is selected, linked modules automatically filter data (e.g., Charts show NVDA, Maps show NVIDIA facilities). ATLAS AI also understands this context inherently.

## Global Command System

Input is routed through a unified command system supporting:
- **Slash commands:** e.g., `/markets movers us`
- **Bloomberg-style aliases:** e.g., `NVDA CHART`
- **Natural language:** e.g., `Show me Nvidia's latest earnings and compare them with AMD.`

## Settings Model

Precedence dictates that the most specific applicable setting wins: `Global -> Section -> Workspace -> Widget`.

### Main Settings (Global)
Accessible bottom-left. Categories include: General, Appearance, Account, Security, Privacy, AI, Agents, MCP, API Keys, Data Providers, Trading, Terminal, etc.

### Section Settings
Contextual settings specific to a module. Examples:
- **Charts:** Appearance, indicators, drawings.
- **News:** Sources, regions, sentiment, AI summaries.
- **Agents:** Default model, autonomy, budgets, permissions.

## Background / Watermark System

Users can customize the application background without compromising financial readability. Stage 8 introduced the foundational global background engine.
- **Visual Layer**: The custom background resides in a separate visual layer beneath all application content (`AtlasBackgroundLayer`), preventing the need for content opacity manipulation (glassmorphism).
- **Features**: Image upload (local-only via IndexedDB), configurable opacity, blur, brightness, contrast, saturation, grayscale, fit, position, and readability overlay.
- **Quick Access**: Accessible via a top-bar quick control button for fast adjustments and live previewing.
- **Scope**: The architecture supports a Global Background state and prepares hooks for future Workspace Override logic.
- **Future Integration**: The background state (`BackgroundProvider`) is built to seamlessly integrate with the Stage 9 Global Settings module.
