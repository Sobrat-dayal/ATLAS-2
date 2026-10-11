# ATLAS Authentication Architecture

## 1. Overview
The ATLAS platform uses Supabase Authentication (Stage 13) for user identity and session management. All protected API requests include a bearer JWT in the HTTP `Authorization` header.

The FastAPI backend validates the JWT using `get_current_user` in `apps/api/src/atlas_api/auth/dependencies.py`, producing an authenticated `AuthPrincipal` containing:
- `sub`: The canonical user UUID.
- `email`: The verified email address.
- `aud`: Audience claim (`authenticated`).
- `role`: Supabase role claim.

---

## 2. Authenticated Model-Backed Command Interpretation (Stage 48)

Stage 48 integrates single-turn natural-language command interpretation through `POST /api/v1/commands/interpret`:

### Security & Privacy Protections
1. **Mandatory Authentication**: The endpoint requires a valid session bearer token. Unauthenticated requests are rejected immediately with HTTP 401.
2. **Zero Client Credentials**: The browser never receives model API keys or provider secrets. Model credentials are strictly server-side environment secrets.
3. **Identity Privacy**: The user's `sub`, `email`, profile information, portfolio data, watchlist contents, and authentication tokens are **never** included in the prompt payload sent to the language model.
4. **Data Isolation**: The language model receives only the user's plain text command string wrapped in a strictly delimited JSON object alongside allowed static module metadata.
5. **No Persistent Session**: Interpretation requests are entirely stateless. No server-side or provider-side interpretation sessions, conversation histories, or threads are established.

---

## 3. Authenticated User-Scoped Notification Access (Stage 49)

Stage 49 provides durable in-app notifications tied strictly to authenticated user identity:

1. **Derived Recipient Identity**: All notification read/mutation endpoints derive the recipient exclusively from `AuthPrincipal.sub` (`principal.user_id`). The client API never accepts `user_id` or `recipient_id` from query parameters or request bodies.
2. **Horizontal Privilege Escalation Prevention**: Queries and mutations filter strictly on `(notification_id, recipient_user_id)`. If User A attempts to inspect or mutate User B's notification, the API returns HTTP 404 (does not reveal notification existence).
3. **Session Switch Cache Isolation**: When the authenticated principal changes (login, switch account, logout), all frontend notification query caches, items, and badge counters are completely purged from browser memory.
4. **No Storage Leakage**: Notification contents are strictly held in memory and are never persisted to `localStorage` or `sessionStorage`.

