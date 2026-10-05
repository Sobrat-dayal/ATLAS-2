# Global Selected Entity Context

## Purpose
The Global Selected Entity Context allows the entire ATLAS application to agree on **one currently selected Universal Entity**. It ensures that modules across the application (e.g. Markets, Charts, Companies, News) share the same canonical entity reference, instead of maintaining competing, disjoint state.

## Global vs Local Selection
- **Global Context**: Represents the singular, committed subject of user interaction. When set, `selectedEntityId` is shared across ATLAS.
- **Local Module State**: Temporary or UI-specific state such as hovered rows, checked boxes for bulk actions, or keyboard focus.
Local UI selection does not automatically become the Global Selected Entity. Only deliberate, semantic user actions (e.g., clicking to open an entity detail) change the global context.

## Entity ID Identity
The canonical selected value is the `entity_id` (a UUID), which references the primary key in the entities system.
**ATLAS never stores** aliases, tickers, FIGIs, ISINs, or company names as the canonical global selection.

## Company vs Security Behavior
Company and Security are distinct entities in the architecture. 
If a user resolves "NVDA" and selects the resulting Security entity (Entity ID `B`), the global context stores `B`. If the user explicitly selects "NVIDIA Corporation" (Entity ID `A`), the global context stores `A`. The context does not automatically jump from the security to its issuing company. 

## Provider / Store Architecture
The context was originally managed by `SelectedEntityProvider` in Stage 25. As of Stage 26, it is managed as a focused slice within the **Global Application Context** (`GlobalApplicationContextProvider`). The legacy `useSelectedEntity()` hook acts as a compatibility layer over the new architecture, ensuring that consumers experience zero breakage.

## Session Persistence
The `selectedEntityId` is persisted via `sessionStorage`. Originally stored as `atlas.selectedEntity.v1`, it has been migrated into the unified `atlas.applicationContext.v1` payload.
This ensures:
- The working context survives page refreshes and route transitions.
- Independent contexts can exist per browser tab.
- Stale selections are not preserved long-term.
Full Entity payloads are **never** persisted to browser storage.

## Query Loading
When `selectedEntityId` is updated, the provider issues a fetch to `GET /api/v1/entities/{entity_id}` using the authenticated session token.
It avoids stale-request overwrites by tracking the latest active fetch.
It does not automatically fetch Identifiers, Aliases, Relationships, or Provenance. Modules should fetch domain-specific data on-demand using the `entity_id`.

## Error and Auth Lifecycle
- **404 Stale Selection**: If an entity fetch returns 404, the selected entity and its persistence are cleanly cleared.
- **500 Temporary Error**: The `entity_id` remains selected, allowing the user to retry.
- **Logout / Account Switch**: When the authenticated principal changes or logs out, the selected entity state is immediately cleared to prevent cross-account context leakage.

## Top Bar Indicator
A compact `SelectedEntityControl` sits in the App Shell Top Bar. 
It displays the entity's humanized type (with icon) and canonical name, adapting responsively. It provides a quick action to clear the selection.

## Module Integration Rules
Modules may consume `useSelectedEntity()` to read or update the context.
Modules must **not** implement their own competing global Entity identity state.
If a module does not support the type of the globally selected Entity (e.g. Research module encountering a Security), it should elegantly fall back but it must **not** automatically clear the global selection.

## Future Context Integrations
This is Stage 25 context. Stage 26 will introduce the broader Global Application Context.
Future integrations:
- **Search (Stage 45)**: Selecting a result will call `selectEntity(entity_id)`.
- **Command Palette (Stage 46)**: Resolved entities can be set here.
- **ATLAS AI (Stage 124+)**: Can read `selectedEntityId` for conversational context.
- **Agents (Stage 146+)**: Can use the selected entity as task input.
