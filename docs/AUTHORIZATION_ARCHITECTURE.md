# ATLAS Authorization Architecture

## Overview

The ATLAS platform uses a centralized, database-backed Role-Based Access Control (RBAC) system to authorize access to system capabilities. This system operates downstream of Supabase Authentication.

Supabase Auth proves **who** the user is.
ATLAS Authorization determines **what** the user can do.

## Core Concepts

### Principal
A user accessing the system, represented by an `AuthPrincipal` extracted from the Supabase JWT.

### Permission Code
A fine-grained, machine-readable string representing a specific capability (e.g., `module.markets.view`, `authz.manage`).

### Risk Class
A categorization of a permission (e.g., `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). Used for auditing and potential step-up authentication requirements.

### Role
A named collection of permissions.
* **Implicit Role**: The default role (`member`) automatically granted to all authenticated users.
* **Explicit Role**: Roles (like `admin` or `moderator`) explicitly assigned to a user via the database.

## Architecture & Flow

### Backend Flow (FastAPI)

1. A request arrives with a Supabase JWT in the `Authorization` header.
2. The `get_current_user` dependency validates the JWT and returns an `AuthPrincipal`.
3. The `get_authorization_context` dependency:
    - Queries the database for explicitly assigned roles (`authz_user_roles`).
    - Appends the implicit `member` role.
    - Resolves all associated permissions (`authz_role_permissions`).
    - Caches the resulting `AuthorizationContext` on `request.state`.
4. Endpoint-specific dependencies like `RequirePermission(PermissionCode.MARKETS_VIEW)` evaluate the context and raise a 403 Forbidden (`PermissionDeniedError`) if the capability is lacking.

### Frontend Flow (Next.js)

1. The `useAuth` hook establishes the user's session.
2. The `AuthorizationProvider` calls `GET /api/v1/authz/me` to retrieve the user's active roles and permissions.
3. The `useAuthorization` hook exposes utility functions like `hasPermission()` and `canViewModule()`.
4. Component-level enforcement:
    - **Sidebar**: Only displays modules the user is authorized to view.
    - **MainWorkspace**: Renders the `<AccessDenied />` component if a direct route is accessed without adequate permissions.

## Database Schema (PostgreSQL)

The source of truth for authorization resides in PostgreSQL (via SQLAlchemy/Alembic migrations).

- `authz_roles`: Defines roles (e.g., `admin`, `member`).
- `authz_permissions`: Defines permissions and risk classes.
- `authz_role_permissions`: Maps permissions to roles.
- `authz_user_roles`: Assigns roles to Supabase user IDs.

## Deny-by-Default

By default, any capability or module is inaccessible unless explicitly permitted by an assigned role. The only exception is the `member` role, which is implicitly granted to all valid users and typically contains permissions to view foundational modules (like Home, Markets, News).

## Management

A command-line tool exists in `apps/api/src/atlas_api/cli.py` to manage user roles directly against the database:

```bash
uv run python apps/api/src/atlas_api/cli.py grant-role --user-id <UUID> --role admin
```

## Command Parsing Authorization (Stage 47)

Commands processed through `POST /api/v1/commands/parse` undergo dual authorization checks:
1. **API Access**: The principal must possess the `atlas.access` permission.
2. **Module Access**: During semantic binding, bound commands requiring access to a specific module (e.g. `navigation.charts.entity` requires `atlas.charts`) check the caller's permissions. If the user lacks the permission, the parser returns status `INVALID` with error code `COMMAND_FORBIDDEN` without exposing internal implementation details.

## Natural-Language Command Interpretation Authorization (Stage 48)

Natural-language command interpretation through `POST /api/v1/commands/interpret` enforces strict authorization boundaries:
1. **API Access**: The caller must be authenticated and possess `atlas.access`. Unauthenticated requests receive HTTP 401; callers lacking `atlas.access` receive HTTP 403.
2. **Module Access via Stage 47**: After the model interprets user intent and compiles it into canonical Stage 47 syntax, Stage 47 semantic binding validates module view permissions (e.g. `module.charts.view`). If the caller lacks permission, Stage 47 returns `COMMAND_FORBIDDEN` / `INVALID`.
3. **Model Cannot Authorize**: The language model has zero authority over permissions and cannot grant, elevate, or bypass access rights.
4. **Execution Recheck**: Because permissions can change between preview and execution, Stage 46 Command Executor and Next.js route guards recheck permissions at execution time.

## Persistent Notifications Authorization (Stage 49)

Stage 49 notification operations enforce two-tier authorization:
1. **API Access Permission**: All Notification Center endpoints (`GET /notifications`, `GET /notifications/unread-count`, `POST /{id}/read`, `POST /{id}/unread`, `POST /read-all`, `POST /{id}/archive`) enforce `RequirePermission(PermissionCode.ATLAS_ACCESS)`.
2. **Recipient Ownership Boundary**: In addition to RBAC permissions, every notification query and mutation enforces row-level ownership strictly matching `recipient_user_id == principal.user_id`. Attempting to access or mutate another user's notification returns HTTP 404 (preventing horizontal privilege escalation or enumeration).
3. **Action Target Authorization**: Notification click-through navigation only issues Next.js client-side route transitions. The destination module and entity context remain guarded by the respective Stage 14 module authorization guards and Stage 25 entity permissions. Notification existence never grants module access.



