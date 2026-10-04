# UX Architecture

ATLAS follows a consistent global layout.

## App Shell
The persistent UI wrapping all core features.
Includes:
- Background System
- Top Bar (Global Controls, Navigation)
- Sidebar (Module Navigation, Main Settings utility)
- Agent Dock
- Main Workspace
- Bottom Taskbar
- Market Ticker

## Module Navigation
- 20 distinct domain modules (e.g., Home, Markets, Charts).
- Located in the primary sidebar.

## Settings System
Two levels of configuration exist:

1. **Main Settings (Global)**
   - Located at `/settings` and accessed via the bottom-left gear icon in the Sidebar.
   - It is a global utility surface, not one of the 20 main modules.
   - Responsible for application-wide behavior (Appearance, Security, Background, Global Preferences).
   - Organized centrally by the Settings Category Registry (`config/settings-registry.ts`).

2. **Section Settings (Module-specific)**
   - Configures behavior isolated to specific modules (e.g., Chart-specific settings).
   - Can override global defaults selectively where permitted.

## Precedence
`Defaults` → `Global Main Settings` → `Section Settings` → `Workspace Overrides` → `Widget Overrides`.
