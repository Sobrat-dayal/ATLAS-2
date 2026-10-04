# ATLAS Navigation Architecture

This document describes the centralized navigation architecture established in Stage 4.

## Module Registry
The ATLAS application is strictly governed by exactly 20 core modules defined in `apps/web/src/config/atlas-modules.ts`. This registry serves as the single source of truth for navigation, route mapping, settings namespaces, active state detection, and future permission/AI context boundaries.

### Canonical Routes
1. `/home`
2. `/markets`
3. `/charts`
4. `/watchlists`
5. `/screeners`
6. `/companies`
7. `/economics`
8. `/news`
9. `/research`
10. `/maps`
11. `/intelligence`
12. `/options`
13. `/trading`
14. `/portfolios`
15. `/risk`
16. `/ai`
17. `/data`
18. `/saved`
19. `/workspaces`
20. `/agents`

### Legacy Route Support
To ensure older links or prototype bookmarks continue to function correctly, next.config.ts implements `permanent` (308) redirects for:
- `/screener` -> `/screeners`
- `/economy` -> `/economics`
- `/map` -> `/maps`
- `/portfolio` -> `/portfolios`
- `/analytics` -> `/risk`
- `/` -> `/home`

## Navigation UI
The left `Sidebar` consumes `ATLAS_MODULES_LIST` (sorted by the predefined integer order) to dynamically render the navigation elements. This guarantees that visual navigation never desyncs from the application's true route definition. Active states are reliably computed even on deep nested paths (e.g., `/markets/equities`).

## Missing Features vs. Foundation Pages
Missing modules are rendered using a standardized `ModuleFoundation.tsx` placeholder. This prevents "404 Not Found" errors when users click on incomplete features. ATLAS avoids marketing-style "Coming Soon!" banners in the primary Sidebar, favoring an honest foundation page approach to reveal its ultimate architecture.

## Distinction from Shell Surfaces
- **Agent Dock:** This is a persistent right-side shell surface, NOT the `/agents` module itself (which acts as the full autonomous agent management workstation).
- **ATLAS AI:** The top-bar button is a quick overlay/assistant hook. The `/ai` module is the full AI workspace.
