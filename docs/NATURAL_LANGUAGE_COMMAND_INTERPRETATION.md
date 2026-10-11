# ATLAS Natural-Language Command Interpretation

> **Source of Truth** for Stage 48.

---

## 1. Executive Summary & Core Principle

Stage 48 establishes **ATLAS Natural-Language Command Interpretation v1**. It provides a safe, bounded, single-turn interpretation layer translating human instructions (e.g. `"show me NVDA's chart"`, `"take me to markets"`, `"open NVIDIA Corporation in companies"`) into deterministic Stage 47 canonical commands (`/charts "NVDA"`, `/markets`, `/companies "NVIDIA Corporation"`).

### The Inviolable Principle
> **The language model may interpret intent, but it may NEVER directly execute anything.**

The model does **not**:
- Navigate routes
- Select entities
- Call market data providers
- Call OpenBB
- Call brokers or place orders
- Query databases directly
- Run shell or terminal commands
- Write files
- Execute Python, JavaScript, or bash
- Invoke AI agents or workflows
- Use tools (0 tool calls provided)

Every interpretation passes through deterministic ATLAS compilation, parsing, entity resolution, authorization, and preview before explicit user execution.

---

## 2. Core Architecture Pipeline

```text
Natural-Language Text
        │
        ▼
Natural-Language Command Interpreter (Single-Turn)
        │
        ▼
Strict Structured Intent (Pydantic, extra="forbid")
        │
        ▼
Intent Compiler (NaturalLanguageIntentCompiler)
        │
        ▼
Canonical Stage 47 Command (`/module "target"`)
        │
        ▼
Stage 47 Parser & Semantic Binder
        │
        ▼
Stage 22 Entity Resolution (Exact, deterministic)
        │
        ▼
Stage 14 Authorization Verification
        │
        ▼
READY Preview Card in Command Palette
        │
        ▼
Explicit User Execution (Enter key / Run click)
        │
        ▼
Stage 46 Command Executor
```

---

## 3. Trust Boundaries

| Component | Role | Authority Boundary |
|---|---|---|
| **Language Model** | Untrusted Interpretation Aid | Emits bounded intent enum and plain text target only. Zero execution or identification authority. |
| **Stage 47 Command System** | Deterministic Syntax & Parsing Authority | Reparses and validates compiled command against command specifications. |
| **Stage 22 Entity Resolution** | Entity Identity Authority | Sole source of truth for Entity UUIDs (`entity_id`). No model-invented identities allowed. |
| **Stage 14 Authorization** | Access Control Authority | Evaluates RBAC permissions (`atlas.access`, `module.<id>.view`). Model cannot grant or bypass rights. |
| **Stage 46 Command Executor** | Execution Boundary | Dispatches validated command with typed arguments upon explicit user trigger. |

---

## 4. Architectural Boundaries

### Stage 47 vs. Stage 48 Boundary
- **Stage 47**: Deterministic structured command syntax (`/module target`, `TICKER MODULE` shorthand), lexer, parser, semantic binder, and exact entity resolution. Operates with zero dependency on AI or models.
- **Stage 48**: Single-turn natural-language interpretation layer. It translates unstructured human phrasing into Stage 47 canonical syntax and hands execution off to Stage 47 and Stage 46.

### Stage 48 vs. Stage 124 Boundary
- **Stage 48**: Single-turn command interpretation only. Zero conversation memory, zero chat history, zero RAG, zero agents, zero autonomous planning, zero tool calling.
- **Stage 124**: Full ATLAS AI Assistant V1 (interactive chat, conversational context, assistants, and autonomous tools).

---

## 5. Versioning Controls

```text
Interpreter Version:           1
Prompt Version:                1
Model Output Schema Version:   1
```

Any modification to prompt semantics or output schema requires incrementing the corresponding version identifier.

---

## 6. Supported Natural-Language Intents

| Intent | Required Fields | Meaning | Compiles To Executable Command? |
|---|---|---|---|
| `NAVIGATE_MODULE` | `module` (valid module ID) | Direct navigation to a top-level module (e.g. `"take me to markets"`). | Yes (`/<module>`) |
| `OPEN_ENTITY_IN_MODULE` | `module`, `target_text` | Navigation to an entity-enabled module with a target entity (e.g. `"show NVDA in charts"`). | Yes (`/<module> "<target>"`) |
| `OPEN_GLOBAL_SETTINGS` | None | Open global application settings dialog/page. | Yes (`/settings`) |
| `FOCUS_ENTITY_SEARCH` | None | Focus global entity search dialog. | Yes (`/search`) |
| `CLEAR_SELECTED_ENTITY` | None | Deselect currently active entity context. | Yes (`/clear entity`) |
| `AMBIGUOUS` | `clarification_question` | Instruction lacks unambiguous module or action destination. | No (renders clarification banner) |
| `NOT_COMMAND` | None | Input is informational inquiry or question (e.g. `"what is NVDA"`). | No (renders informational notice) |
| `UNSUPPORTED_ACTION` | `unsupported_reason` | Action outside supported Stage 48 boundaries. | No (renders refusal banner) |

---

## 7. Unsupported Action Categories

The model rejects actions outside Stage 48 capabilities using the bounded enum `UnsupportedActionReason`:

- `TRADING_ACTION`: Order execution, buy/sell actions (`"buy 100 shares of NVDA"`).
- `BROKER_ACTION`: Direct broker interactions or account balance queries.
- `PORTFOLIO_ACTION`: Portfolio optimization, rebalancing (`"rebalance my portfolio"`).
- `RISK_ACTION`: Risk model calculations (`"calculate portfolio risk"`).
- `AGENT_ACTION`: Agent creation or execution (`"create a research agent"`).
- `WORKFLOW_ACTION`: Workflow execution (`"build a workflow"`).
- `TERMINAL_ACTION`: Python, shell, or terminal commands (`"run python"`).
- `SYSTEM_ACTION`: File operations or system modifications (`"rm -rf /"`).
- `EXTERNAL_ACTION`: External web URLs, messaging, email (`"open https://example.com"`).
- `MULTI_COMMAND`: Command chaining or sequential plans (`"open markets and then go to news"`).
- `OTHER_UNSUPPORTED`: General unsupported requests.

---

## 8. Model Output Schema

The model responds with a strictly validated Pydantic schema (`extra="forbid"`):

```json
{
  "schema_version": 1,
  "intent": "OPEN_ENTITY_IN_MODULE",
  "module": "charts",
  "target_text": "NVDA",
  "unsupported_reason": null,
  "clarification_question": null
}
```

### Conditional Cross-Field Validation Rules
1. `OPEN_ENTITY_IN_MODULE`: `module` and non-empty `target_text` are mandatory.
2. `NAVIGATE_MODULE`: `module` is mandatory; `target_text` must be `null`.
3. `OPEN_GLOBAL_SETTINGS`, `FOCUS_ENTITY_SEARCH`, `CLEAR_SELECTED_ENTITY`: `module` and `target_text` must be `null`.
4. `NOT_COMMAND`: `module`, `target_text`, `unsupported_reason` must be `null`.
5. `UNSUPPORTED_ACTION`: `unsupported_reason` is mandatory.
6. `AMBIGUOUS`: Executable fields must be `null`; optional `clarification_question` capped at 160 characters.
7. Any extra fields (e.g. hallucinated `command_id`, `entity_id`, `route`, `sql`) cause immediate schema rejection (`extra="forbid"`).

---

## 9. Entity Resolution & Target Integrity

### No Model-Generated Entity IDs
The model never emits UUIDs. Only Stage 22 `EntityResolutionService` produces `entity_id` UUIDs during Stage 47 semantic binding.

### No Ticker Inference
The model must not convert company names (e.g. `"NVIDIA Corporation"`) into tickers (`"NVDA"`). It extracts target text strictly as provided in user input.

### Target Type Distinction
The Stage 47 target rules remain authoritative:
- Charts requires a Financial Instrument (Security). If `"NVIDIA Corporation"` resolves to Company, Stage 47 returns `TARGET_TYPE_MISMATCH`.
- Companies requires a Company entity.
- No implicit issuer graph traversal occurs in Stage 48.

### No Fuzzy Matching in Commands
Exact deterministic matching only. A typo such as `"NVIDA"` results in `TARGET_NOT_FOUND`. Fuzzy discovery remains exclusively in Stage 45 Global Search.

---

## 10. Canonical Intent Compilation & Escaping

`NaturalLanguageIntentCompiler` compiles intents into Stage 47 command strings using strict escaping:

| Intent | Module | Target | Compiled Command |
|---|---|---|---|
| `NAVIGATE_MODULE` | `markets` | - | `/markets` |
| `OPEN_ENTITY_IN_MODULE` | `charts` | `NVDA` | `/charts "NVDA"` |
| `OPEN_ENTITY_IN_MODULE` | `companies` | `NVIDIA Corporation` | `/companies "NVIDIA Corporation"` |
| `OPEN_GLOBAL_SETTINGS` | - | - | `/settings` |
| `FOCUS_ENTITY_SEARCH` | - | - | `/search` |
| `CLEAR_SELECTED_ENTITY` | - | - | `/clear entity` |

Target text containing quotes or backslashes is safely escaped with backslash escapes (`\"` and `\\`) to prevent command injection.

---

## 11. Model Configuration & Guardrails

| Setting | Type | Secret? | Default | Purpose |
|---|---|---|---|---|
| `enabled` | `bool` | No | `False` | Feature toggle for natural language interpretation. |
| `mock_mode` | `bool` | No | `False` | Offline deterministic mock client for tests & local dev. |
| `model_base_url` | `str` | No | `https://api.openai.com/v1` | Server-configured model endpoint (never accepted from client). |
| `model_name` | `str` | No | `gpt-4o-mini` | Configured model identifier. |
| `model_api_key` | `SecretStr` | **Yes** | `None` | Server-side API credential (never exposed to frontend or logs). |
| `timeout_seconds` | `float` | No | `10.0` | Bounded HTTP client timeout. |
| `max_input_characters` | `int` | No | `1000` | Input length limit. |
| `max_output_tokens` | `int` | No | `256` | Bounded model generation limit. |
| `temperature` | `float` | No | `0.0` | Deterministic lowest-supported generation. |
| `max_ambiguity_candidates` | `int` | No | `5` | Maximum ambiguity candidates returned. |

### Call Limits & Retries
- **Normal model calls per interpretation request**: 1.
- **Model self-repair loop**: 0 (fails safely closed).
- **Transport retries**: 0 automatic retries by default.
- **Tools provided to model**: 0.

---

## 12. Privacy, Logging & Storage Boundaries

- **Zero Persistence**: No database tables, no Alembic migrations, no Redis keys, no localStorage histories, no prompt archives, no model response archives.
- **Zero INFO Logging of Sensitive Data**: Raw user text, raw prompts, raw model responses, API keys, and authorization tokens are strictly forbidden from INFO logs.
- **Structured Log Fields**: Only safe metadata is logged: `component="natural_language_command"`, `status`, `intent`, `input_length`, `duration_ms`.

---

## 13. API Endpoint Specification

### `POST /api/v1/commands/interpret`

**Authentication**: Required (Stage 13 bearer token).  
**Authorization**: `atlas.access` required.  
**Side Effects**: **Zero** (no database writes, no Redis writes, no ClickHouse writes, no navigation, no selection mutations).

#### Request Payload
```json
{
  "text": "show me NVDA's chart"
}
```

#### Response Payload (READY)
```json
{
  "interpreter_version": 1,
  "prompt_version": 1,
  "model_output_schema_version": 1,
  "status": "READY",
  "input_fingerprint": "8a35e29f...",
  "intent": "OPEN_ENTITY_IN_MODULE",
  "module": "charts",
  "target_text": "NVDA",
  "canonical_command": "/charts \"NVDA\"",
  "structured_parse_result": {
    "command_language_version": 1,
    "status": "READY",
    "source_kind": "slash",
    "normalized_command": "/charts \"NVDA\"",
    "command_id": "navigation.charts.entity",
    "module": "charts",
    "action": "open",
    "raw_target": "NVDA",
    "resolved_target": {
      "entity_id": "11111111-2222-3333-4444-555555555555",
      "entity_type": "security",
      "canonical_name": "NVIDIA Corp",
      "display_name": "NVIDIA Corp",
      "matched_value": "NVDA",
      "match_kind": "ticker",
      "scope_entity_id": null
    },
    "arguments": {
      "entityId": "11111111-2222-3333-4444-555555555555"
    },
    "error_code": null,
    "error_message": null,
    "ambiguity_candidates": [],
    "execution_summary": "Open NVIDIA Corp in Charts"
  },
  "clarification_question": null,
  "unsupported_reason": null,
  "error_code": null,
  "error_message": null
}
```

---

## 14. Frontend User Experience Workflow

```text
User Types Text in Command Palette
        │
        ├── Exact Stage 46 match? ──> Fast local command row (0 model calls)
        ├── Stage 47 syntax (/ or shorthand)? ──> Fast Stage 47 parse (0 model calls)
        │
        └── Unstructured Text: Shows "Interpret as ATLAS command" option (0 model calls)
                    │
                    ▼ (User explicitly presses Enter / clicks row)
                    │
           Interpreting State (Compact progress spinner)
                    │
                    ▼
           Validated Response Received
                    │
    ┌───────────────┼───────────────┬─────────────────┬────────────────┐
    ▼               ▼               ▼                 ▼                ▼
  READY         AMBIGUOUS      NOT_COMMAND       UNSUPPORTED      UNAVAILABLE
 Preview Card   Candidate       Question          Refusal          Fallback
  (Execution    Selector         Notice            Banner           Banner
   Details)         │
    │          User picks
    │          candidate
    ▼               │
Explicit Enter/Click ───┘
    │
Stage 46 Command Executor runs
```

### Safety Protections in UI
1. **No Autoexecution**: READY interpretation presents a preview card. The user must explicitly press Enter or click the execution button.
2. **Stale Response Protection**: An `input_fingerprint` and abort controller ensure an in-flight interpretation for query A never displays or executes if the user edited the text to query B.
3. **Palette Reset**: Closing the command palette aborts in-flight requests and clears all interpretation state.
4. **Command ID Allowlist**: Execution verifies the returned `command_id` against the Stage 46 Command Registry. Unknown or fabricated command IDs fail closed.
