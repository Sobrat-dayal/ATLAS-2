# Settings System

The Settings system is the global configuration control center for ATLAS. It provides a centralized interface for users to configure application-wide behavior.

## Architecture

The main settings system is structurally distinct from section-specific settings. 

- **Main Settings**: Application-wide behavior (e.g. appearance, security, notifications).
- **Section Settings**: Module-specific behavior (e.g. charts, news).

### Category Registry

All settings categories are defined in a centralized registry (`config/settings-registry.ts`). This ensures a single source of truth for:
- Routing
- Search indexing
- Sidebar rendering
- Future AI discovery

Categories include: `General`, `Appearance`, `Account`, `Security`, `Privacy`, `Notifications`, `AI`, `Models`, `Agents`, `MCP`, `API Keys`, `Data Providers`, `Market Data`, `Trading`, `Brokers`, `Storage`, `Integrations`, `Developer`, `Terminal`, `Keyboard`, `Accessibility`, `Billing`, `Advanced`.

### Routing

The canonical route for global settings is `/settings`, which dynamically redirects to `/settings/general`. Individual categories follow a dynamic route pattern (`/settings/[category]`), mapping to the exact ID listed in the registry.

### Search

The settings search utilizes the metadata from the category registry. It matches search queries against category labels, descriptions, and predefined keywords, dynamically filtering the sidebar for quick navigation.

### Setting Definitions and Foundation States

Future functionality that is not yet implemented (e.g., API Keys, Agents, AI Models, Broker connections) uses a consistent "Foundation" state indicating that the feature will become available once the underlying infrastructure is connected. This preserves a professional and honest UI.

### Persistence

- **Immediate Apply**: Low-risk UI settings (e.g., Theme, Density) apply immediately and are persisted directly to `localStorage` (or `IndexedDB` for background images).
- **Explicit Save**: (Planned) High-risk settings or credentials will require explicit save actions and secure vaults.

Global settings use targeted stores instead of a monolithic state (e.g. `AppearanceStore`, `BackgroundStore`, `GlobalPreferencesStore`).

## Secret Handling Rules

Settings pages must never expose or insecurely store secrets (e.g., API keys, broker tokens). Currently, API Keys and Brokers are rendered as structural foundations and do not read/write to `localStorage`. Future implementation will rely on a dedicated secure vault.

## Reset Behavior

Resets are explicitly scoped:
- **Reset Appearance**: Reverts theme, density, and accent.
- **Clear Background Assets**: Deletes custom uploaded images.
- **Reset All Local Preferences**: Resets UI preferences but does not delete background assets, saved workspaces, or future portfolios.

## Precedence

The intended precedence for ATLAS configurations is:
`Defaults` → `Global Main Settings` → `Section Settings` → `Workspace Overrides` → `Widget Overrides`.

## Import / Export Rules

Settings import/export foundation is architected but its implementation is deferred to subsequent stages. Once implemented, it must explicitly exclude any secrets, background image bytes, or broker credentials.

## Cloud Sync

Currently, global settings are stored locally. The architecture natively supports adding cloud sync capabilities in future stages once user authentication is introduced.


## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.
