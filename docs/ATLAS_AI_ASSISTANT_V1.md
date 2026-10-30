# ATLAS — Stage 124: AI ASSISTANT V1 & Universal ATLAS AI Overlay

## 1. Executive Summary

Stage 124 establishes the **AI ASSISTANT V1 and Universal ATLAS AI Overlay** for the ATLAS Quantitative Research and Financial Intelligence Operating System.

The AI Assistant provides portfolio managers, quantitative researchers, and traders with a persistent, context-light conversational copilot available across all 20 canonical platform routes (`/home`, `/markets`, `/charts`, `/watchlists`, `/screeners`, `/companies`, `/economics`, `/news`, `/research`, `/maps`, `/intelligence`, `/options`, `/trading`, `/portfolios`, `/risk`, `/ai`, `/data`, `/saved`, `/workspaces`, `/agents`).

---

## 2. Architectural Pillars

### 2.1 Universal AppShell Trigger & Slide-Over Overlay
- **Persistent Global Trigger**: Mounted in the upper-right of `TopBar.tsx`, featuring a Bot icon, live state indicator, and keyboard shortcut badge (`Ctrl+Alt+A` / `Cmd+Alt+A`).
- **Sliding Dockable Overlay**: Resizable side-panel container (`AtlasAiOverlay.tsx`) with draggable left edge (width customizable between 340px and 750px).
- **Background Route Preservation**: Toggling, resizing, or conversing with the AI overlay does not unmount, reload, or navigate away from the underlying financial workspace or active workspace panels.

### 2.2 Server-Side Conversation Management
- **Persistence**: Backed by PostgreSQL / Supabase with row-level security and user tenant isolation.
- **Data Entities**:
  - `ai_conversations`: Conversation sessions with title, model selection, pinned state, archive flag, and token usage aggregates.
  - `ai_messages`: Multi-turn turns with role (`user`, `assistant`, `system`), status, token count, generation run ID, and route descriptor.
  - `ai_generation_runs`: Model inference run records with prompt/completion tokens, duration, error handling, and completion timestamps.
  - `ai_assistant_user_preferences`: User preferences for default model, temperature, send-on-enter, and overlay dock dimensions.
  - `ai_conversation_audit_events`: Append-only audit log for compliance.

### 2.3 Provider-Agnostic Model Abstraction Layer
- **Model Registry**:
  - `atlas-intelligence-v1` (Default): Balanced high-speed financial intelligence model.
  - `atlas-reasoning-v1`: Extended analytical reasoning for derivatives and risk mathematics.
  - `atlas-speed-v1`: Ultra-low latency model for immediate platform lookups and definitions.
- **Provider Adapters**:
  - `MockAiProvider`: Deterministic, high-fidelity mock generator used in testing, CI, and local offline modes without API keys.
  - `OpenAiCompatibleProvider`: Connects to standard OpenAI-compatible endpoints (OpenAI, Groq, NVIDIA NIM) via `httpx` with SSE streaming.
  - **Zero Credential Leakage**: Provider API keys are stored exclusively in server environment variables and never sent to the browser.

### 2.4 Server-Sent Events (SSE) Streaming & Cancellation
- **Streaming Endpoint**: `GET /api/v1/ai/generations/{generation_id}/stream` emitting standard SSE chunks:
  - `event: run_started`
  - `event: delta`
  - `event: run_completed`
  - `event: run_cancelled`
  - `event: error`
- **Cancellation**: Users can immediately stop an in-progress generation via `POST /api/v1/ai/generations/{generation_id}/cancel`.

### 2.5 Strict Stage 124 Operational Boundaries
- **No Live Tick Quote Hallucination**: AI Assistant V1 does not have direct streaming tick market feeds in this overlay. When asked for live tick prices, it clarifies this boundary and directs the user to `/markets` or `/charts`.
- **No Autonomous Execution**: AI Assistant V1 cannot place live orders, modify portfolios, or execute terminal commands directly (actions deferred to future stages).
- **Minimal Context-Light Route Descriptor**: Only allowlisted module descriptors (`route`, `module_name`, `summary`) are passed. Deep DOM scraping and arbitrary panel composition are deferred to Stage 125.

---

## 3. Dedicated Route Integration (`/ai`)

In addition to the global slide-over overlay, the existing route `/ai` has been upgraded to a full-screen Tri-Pane Institutional AI Workspace:
1. **Left Panel**: Conversation history with search, pinning, archiving, and deletion.
2. **Center Panel**: Multi-turn message canvas with Markdown rendering, KaTeX math blocks, syntax-highlighted code with copy buttons, and message regeneration.
3. **Right Inspector**: Intelligence telemetry showing active model parameters, token counts, and governance notices.

Both the overlay and the `/ai` route share the identical backend conversation database and real-time streaming infrastructure.

---

## 4. Verification & Testing

- **Backend Pytest**: 13/13 tests passing covering conversation lifecycle, message size limits, prompt builder windowing, streaming SSE, cancellation, numerical Sharpe calculations, boundary honesty, and user tenant isolation.
- **Frontend Unit Tests**: 223/223 tests passing across 14 test suites covering route registry, markdown block extraction, and text stripping.
- **Next.js Production Build**: All 38 routes compiled cleanly with 0 type errors.

