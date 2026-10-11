# ATLAS Command Language Specification (v1)

## 1. Overview & Version
**Command Language Version:** `ATLAS Command Language v1` (`command_language_version = 1`)

ATLAS Command Language provides a deterministic, structured command syntax and Bloomberg-style shorthand for fast navigation, entity context selection, and shell utility triggers within the ATLAS application.

### Core Architectural Principle
**Parsing is strictly separated from execution.**
- Parsing is pure, deterministic, side-effect free, and read-only.
- Execution is handled explicitly by the client delegating to the Stage 46 Command Executor upon explicit user interaction (Enter key or click).
- **0 LLM calls, 0 embeddings, 0 vector search, 0 NLP intent routers.**

---

## 2. Processing Pipeline Architecture

```text
Raw Command Text
      │
      ▼
Command Lexer (AtlasCommandLexer)
      │  - Enforces length, token limits, character security
      │  - Tokenizes slash, words, quotes, parameters
      ▼
Syntactic Parser (AtlasCommandParser)
      │  - Generates typed syntax tree
      ▼
Command AST (AtlasCommandAst)
      │
      ▼
Semantic Binder (AtlasCommandBinder)
      │  - Resolves module & action aliases
      │  - Validates parameter schemas & target requirements
      │  - Checks static availability (e.g. FA/RISK reserved)
      ▼
Target Resolver (AtlasCommandTargetResolver)
      │  - Delegates to Stage 22 EntityResolutionService
      │  - Performs exact, deterministic identifier/alias/canonical match
      │  - Validates target entity types (Security vs. Company)
      ▼
Authorization & Availability (AtlasCommandParsingService)
      │  - Validates principal has atlas.access & module permission
      ▼
Bound Command (BoundAtlasCommand) / Parse Result (AtlasCommandParseResult)
      │
      ▼
Command Palette Preview Card (Frontend)
      │  - Displays preview, disambiguation candidates, or error
      ▼  [User presses Enter or clicks]
Stage 46 Command Executor (executeCommand)
      │  - Dispatches typed arguments to registered handler
      ▼
Navigation & Selection
      1. selectEntity(UUID)
      2. router.push(/destination)
```

---

## 3. Boundary Definitions

### Stage 46 vs. Stage 47 Boundary
- **Stage 46 (Command Palette):** Manages local client-side command discovery, indexing, ranking, and execution of registered shell commands. Local queries (e.g., `markets`, `settings`) match directly against registered items in memory.
- **Stage 47 (Command Parsing):** Translates structured text commands (`/charts NVDA`, `NVDA CHART`, `MAP TSMC`) into typed, authorized, entity-resolved executable command plans via deterministic parsing and backend target resolution.

### Stage 47 vs. Stage 48 Boundary
- **Stage 47:** Pure deterministic grammar and exact shorthand. Unknown natural language (e.g. `show me Nvidia's chart`, `what happened to Apple`) returns `NOT_STRUCTURED_COMMAND` or `UNKNOWN_COMMAND`.
- **Stage 48:** Natural-Language Command Interpretation. Stage 48 will interpret unstructured intent and translate it into Stage 47 structured commands or Stage 46 Command IDs. **Stage 48 is not implemented in Stage 47.**

---

## 4. Lexer Rules & Input Limits

### Input Bounds
- **Maximum command length:** 512 Unicode characters
- **Maximum token count:** 32 tokens
- **Maximum token length:** 256 characters
- **Maximum parameters:** 16 parameters

### Whitespace & Casing
- All leading, trailing, and redundant internal whitespace outside of quotes is normalized.
- Command names, module names, action names, parameters, and shorthand keywords are case-insensitive (`/MARKETS` == `/markets`, `NVDA CHART` == `nvda chart`).
- Quoted target text preserves interior capitalization and spacing.

### Quoted Strings & Escapes
Targets containing spaces or special characters can be enclosed in single (`'`) or double (`"`) quotes:
- `"NVIDIA Corporation"`
- `'Apple Inc.'`
- Escapes supported: `\"`, `\'`, `\\`.
- Unterminated quotes produce an immediate `UNTERMINATED_QUOTE` parse error.

### Character Security & Control Characters
- Non-display control characters (`\x00`–`\x08`, `\x0b`, `\x0c`, `\x0e`–`\x1f`, `\x7f`–`\x9f`) are strictly rejected with `CONTROL_CHARACTERS`.
- Standard tabs (`\t`) and spaces are normalized.

### Forbidden Shell Syntax
ATLAS Command Language is **not** a shell. The following characters and patterns are strictly forbidden:
- Pipes: `|`
- Chaining: `&&`, `||`, `;`
- Redirection: `>`, `>>`, `<`, `<<`
- Command substitution: `` ` ``, `$()`, `${}`

Detection of any forbidden shell syntax immediately aborts lexing with `FORBIDDEN_SYNTAX`.

---

## 5. Command AST & Parse Statuses

### AST Schema (`AtlasCommandAst`)
| Field | Type | Description |
|---|---|---|
| `source_kind` | `AtlasCommandSourceKind` | `SLASH` or `SHORTHAND` |
| `command_name` | `Optional[str]` | Canonical command name or module name |
| `action` | `Optional[str]` | Explicit action (e.g. `open`) |
| `target` | `Optional[str]` | Target entity identifier or quoted name |
| `parameters` | `Dict[str, str]` | Key-value dictionary of `--name value` parameters |
| `raw_text` | `str` | Original normalized input text |

### Parse Statuses (`AtlasCommandParseStatus`)
| Status | Description | Executable? |
|---|---|---|
| `READY` | Syntactically valid, semantically bound, target resolved, authorized, and available. | Yes (on Enter) |
| `INCOMPLETE` | Command recognized but missing a required target (e.g. `/charts open`). | No |
| `AMBIGUOUS` | Target matches multiple current entities (e.g. multiple exchange tickers). Disambiguation list provided. | No |
| `INVALID` | Syntax error, unknown command/module/action, forbidden operator, or target type mismatch. | No |
| `UNAVAILABLE` | Recognized reserved syntax whose functionality is deferred in the current stage (e.g. `NVDA FA`). | No |

### Error Codes (`AtlasCommandErrorCode`)
- `COMMAND_TOO_LONG`: Input exceeds 512 characters.
- `TOO_MANY_TOKENS`: Input exceeds 32 tokens.
- `TOKEN_TOO_LONG`: Individual token exceeds 256 characters.
- `UNTERMINATED_QUOTE`: Missing closing quote.
- `FORBIDDEN_SYNTAX`: Forbidden shell operator detected.
- `CONTROL_CHARACTERS`: Non-display ASCII or Unicode control character.
- `UNEXPECTED_TOKEN`: Syntax violation or out-of-order token.
- `UNKNOWN_COMMAND`: Unrecognized slash command.
- `UNKNOWN_MODULE`: Unrecognized module name or alias.
- `UNKNOWN_ACTION`: Unrecognized action for module.
- `UNKNOWN_PARAMETER`: Parameter passed to command that accepts no parameters.
- `DUPLICATE_PARAMETER`: Same parameter flag supplied multiple times.
- `MISSING_TARGET`: Command requires an entity target but none was provided.
- `TARGET_NOT_FOUND`: Target entity could not be resolved in Stage 22.
- `TARGET_AMBIGUOUS`: Target entity matches multiple candidates.
- `TARGET_TYPE_MISMATCH`: Target entity exists but is not an allowed type for the command.
- `COMMAND_UNAVAILABLE`: Reserved shorthand recognized but feature is deferred.
- `COMMAND_FORBIDDEN`: User lacks module authorization.
- `NOT_STRUCTURED_COMMAND`: Input does not conform to structured command grammar.

---

## 6. Grammar Specification

### EBNF Grammar
```ebnf
command           ::= slash_command | shorthand_command

slash_command     ::= "/" identifier [ command_tail ]
command_tail      ::= [ action ] [ target ] { parameter }

shorthand_command ::= suffix_shorthand | prefix_shorthand | reserved_shorthand
suffix_shorthand  ::= target ( "CHART" | "NEWS" | "RESEARCH" )
prefix_shorthand  ::= ( "MAP" | "OPTIONS" ) target
reserved_shorthand::= ( target "FA" ) | "PORT RISK"

target            ::= quoted_string | bare_token
parameter         ::= "--" param_name ( [ "=" ] param_value )
```

---

## 7. Canonical Modules, Aliases & Utility Commands

### The 20 Canonical Modules
| Module | Canonical Slash Name | Curated Aliases | Route | Entity Navigation Command ID |
|---|---|---|---|---|
| Home | `/home` | (none) | `/` | `navigation.home` |
| Markets | `/markets` | `market`, `mkt` | `/markets` | `navigation.markets.entity` |
| Charts | `/charts` | `chart` | `/charts` | `navigation.charts.entity` |
| Watchlists | `/watchlists` | `watchlist`, `watch` | `/watchlists` | `navigation.watchlists` |
| Screeners | `/screeners` | `screener`, `screen` | `/screeners` | `navigation.screeners` |
| Companies | `/companies` | `company` | `/companies` | `navigation.companies.entity` |
| Economics | `/economics` | `econ`, `macro` | `/economics` | `navigation.economics` |
| News | `/news` | (none) | `/news` | `navigation.news.entity` |
| Research | `/research` | `rsch` | `/research` | `navigation.research.entity` |
| Maps | `/maps` | `map` | `/maps` | `navigation.maps.entity` |
| Intelligence | `/intelligence` | `intel` | `/intelligence` | `navigation.intelligence.entity` |
| Options | `/options` | `option`, `opt` | `/options` | `navigation.options.entity` |
| Trading | `/trading` | `trade` | `/trading` | `navigation.trading` |
| Portfolios | `/portfolios` | `portfolio`, `port` | `/portfolios` | `navigation.portfolios` |
| Risk | `/risk` | (none) | `/risk` | `navigation.risk` |
| AI | `/ai` | `assistant` | `/ai` | `navigation.ai` |
| Data | `/data` | (none) | `/data` | `navigation.data` |
| Saved | `/saved` | (none) | `/saved` | `navigation.saved` |
| Workspaces | `/workspaces` | `workspace` | `/workspaces` | `navigation.workspaces` |
| Agents | `/agents` | `agent` | `/agents` | `navigation.agents` |

### Shell Utilities
| Utility | Slash Name | Aliases | Target Allowed | Mapped Command ID |
|---|---|---|---|---|
| Global Settings | `/settings` | `preferences`, `config` | No | `settings.global.open` |
| Global Search | `/search` | `find` | No | `search.focus` |
| Clear Selected Entity | `/clear entity` | `/clear` | No | `entity.selection.clear` |

*Note: Settings is a shell utility and is not module 21.*

### Default `open` Action Semantics
For entity-context modules (`charts`, `news`, `research`, `maps`, `options`, `companies`, `markets`, `intelligence`), specifying a target directly without an explicit action implies `open`:
- `/charts NVDA` $\equiv$ `/charts open NVDA`
- `/news "Apple Inc."` $\equiv$ `/news open "Apple Inc."`

---

## 8. Shorthand Registry

| Pattern | Bound Command ID | Target Allowed Entity Types | Availability |
|---|---|---|---|
| `<TARGET> CHART` | `navigation.charts.entity` | `financial_instrument` | `AVAILABLE` |
| `<TARGET> NEWS` | `navigation.news.entity` | Any entity (`financial_instrument`, `company`, `macro_series`, `document`, etc.) | `AVAILABLE` |
| `<TARGET> RESEARCH` | `navigation.research.entity` | Any entity | `AVAILABLE` |
| `MAP <TARGET>` | `navigation.maps.entity` | Any entity | `AVAILABLE` |
| `OPTIONS <TARGET>` | `navigation.options.entity` | `financial_instrument` | `AVAILABLE` |
| `<TARGET> FA` | `companies.fundamentals.open` | `company`, `financial_instrument` | `UNAVAILABLE` (reserved, deferred) |
| `PORT RISK` | `risk.portfolio.open` | None | `UNAVAILABLE` (reserved, deferred) |
| `BUY <TARGET>` | (none) | N/A | `INVALID` (not executable) |
| `SELL <TARGET>` | (none) | N/A | `INVALID` (not executable) |

---

## 9. Entity Target Resolution Policy

### Reusing Stage 22 Entity Resolution
- Target resolution delegates entirely to Stage 22 `EntityResolutionService`.
- **Exact matching only:** No fuzzy matching, no spell checking, no auto-correction. A misspelled target (e.g. `NVIDA CHART`) returns `TARGET_NOT_FOUND`.
- **Historical identifiers excluded:** `include_historical = False`.
- **Provider external IDs excluded:** Normal commands cannot resolve via raw provider external IDs.
- **Ticker identity = Financial Instrument:** A ticker symbol (e.g. `NVDA`) resolves to a `financial_instrument` (Security), never silently converted to a `company`.
- **No implicit issuer conversion:** `/companies NVDA` rejects the Security target with `TARGET_TYPE_MISMATCH`. Target must be an exact company name or company alias (`/companies "NVIDIA Corporation"`).

### Ambiguity Handling
- When a target (e.g., `ABC`) resolves to multiple active entities across different scopes/exchanges:
  - Status becomes `AMBIGUOUS`.
  - Up to 10 candidates (`max_disambiguation_candidates = 10`) are returned in `ambiguity_candidates`.
  - Frontend renders a candidate picker allowing the user to select the intended entity.

### Ambiguity Candidate Schema
```json
{
  "entity_id": "018f3a2b-...",
  "entity_type": "financial_instrument",
  "display_name": "ABC Corporation",
  "matched_text": "ABC",
  "scope": "US",
  "exchange": "NYSE"
}
```

---

## 10. API Specification

### Endpoint: `POST /api/v1/commands/parse`
- **Method:** `POST` (used to protect command content from appearing in URLs or access logs).
- **Semantics:** Purely read-only. Produces 0 database mutations, 0 Redis writes, 0 ClickHouse queries, 0 provider calls, 0 external network requests, 0 LLM calls.
- **Authentication:** Requires valid session bearer token (Stage 13).
- **Authorization:** Requires `atlas.access` permission (Stage 14). Additionally checks module permission (e.g. `atlas.charts`) for module-specific commands.

### Request Body
```json
{
  "text": "/charts NVDA"
}
```

### Response Body
```json
{
  "command_language_version": 1,
  "status": "READY",
  "source_kind": "SLASH",
  "normalized_command": "/charts NVDA",
  "command_id": "navigation.charts.entity",
  "module": "charts",
  "action": "open",
  "raw_target": "NVDA",
  "resolved_target": {
    "entity_id": "018f3a2b-4c5d-7e8f-9012-3456789abcde",
    "entity_type": "financial_instrument",
    "display_name": "NVIDIA Corporation",
    "ticker": "NVDA",
    "scope": "US",
    "exchange": "NASDAQ"
  },
  "arguments": {
    "entityId": "018f3a2b-4c5d-7e8f-9012-3456789abcde"
  },
  "error_code": null,
  "error_message": null,
  "ambiguity_candidates": [],
  "execution_summary": "Open NVIDIA Corporation (NVDA) in Charts"
}
```

---

## 11. Frontend Integration & Command Palette

### Structured Command Detection
`looksLikeAtlasStructuredCommand(text)` checks if input should be routed to the structured parser:
1. Starts with `/` (e.g. `/markets`, `/charts NVDA`).
2. Ends with reserved shorthand suffix (`CHART`, `NEWS`, `RESEARCH`, `FA`).
3. Starts with reserved shorthand prefix (`MAP`, `OPTIONS`).
4. Exactly matches reserved keywords (`PORT RISK`).

Normal queries (e.g. `markets`, `apple`, `show me nvidia chart`) return `false` and continue through Stage 46 local palette search.

### Execution Flow & Idempotence
- **Debounced parser queries:** 150ms debounce with `AbortController` cancellation to ignore stale responses.
- **No auto-execution:** Typing a command never triggers execution. The user must explicitly press **Enter** or click the preview card.
- **Execution dispatches:**
  ```typescript
  executeCommand(result.command_id, result.arguments)
  ```
  Updating `selectedEntityId` in Global Entity Context and executing router navigation to `/charts`.
- **Search selection difference:** Global Search selection (Stage 45) updates `selectedEntityId` without navigating. Structured commands explicitly select entity AND navigate to the target module.
- **AppShell preservation:** Navigation is handled via Next.js client-side router (`router.push`). No full page reload occurs and the Stage 43 WebSocket connection persists uninterrupted.

---

## 12. Privacy & Logging
- Raw command text is **never** logged at `INFO` level.
- Structured logs record only non-sensitive execution metrics:
  - `component = "atlas_command_parser"`
  - `status`
  - `source_kind`
  - `command_id`
  - `input_length`
  - `token_count`
  - `duration_ms`
- **Zero Command History:** Command strings are not stored in PostgreSQL, Redis, ClickHouse, or client `localStorage`.
