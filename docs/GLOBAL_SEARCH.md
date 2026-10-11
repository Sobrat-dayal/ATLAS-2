# GLOBAL SEARCH ARCHITECTURE (STAGE 45)

## 1. Overview & Core Purpose

Global Search in ATLAS provides fast, deterministic, typo-tolerant entity search across the local canonical Universal Entity universe.

```text
User Query
    │
    ▼
Global Search UI (TopBar)
    │
    ▼
Search API (`/api/v1/search/entities`)
    │
    ▼
GlobalSearchService
    │
    ├── Entity Names (canonical_name, display_name)
    ├── Aliases (current aliases)
    └── Identifiers (current curated identifiers)
            │
            ▼
        PostgreSQL (B-tree & pg_trgm GIN)
            │
            ▼
      Ranked Candidates
            │
            ▼
  Selected Entity Context (`selectEntity(entity_id)`)
```

Global Search searches **ATLAS's canonical local Entity universe only**. It is not:
- Web search
- Provider discovery
- ClickHouse search
- Redis/Valkey search cache
- Vector / embedding search
- Document full-text or filing body search
- Command execution / natural language parsing

---

## 2. Canonical Identity

The canonical identity of any Search result is strictly its:
```text
entity_id (UUID)
```
Tickers, company names, ISIN, CIK, LEI, country codes, or provider IDs are never used as canonical entity identity.
- Searching a ticker (e.g. `NVDA`) returns the Security financial instrument, not the issuer Company.
- Searching a company name (e.g. `NVIDIA Corporation`) returns the Company entity.
- If a ticker is ambiguous across multiple exchange scopes, all scoped Securities are returned.

---

## 3. Search Scope & Normalization

### Searchable Sources
- `entities.canonical_name_normalized`
- `entities.display_name_normalized`
- `entity_aliases.normalized_value` (where `is_current = TRUE`)
- `entity_identifiers.normalized_value` (where `is_current = TRUE` across curated schemes)

`provider_external_id` is excluded from user Global Search.

### Text Normalization Reuse
- Reuses Stage 22 `normalize_entity_name`:
  - Unicode NFKC
  - Strip leading/trailing whitespace
  - Collapse internal whitespace
  - Casefold
  - Preserve punctuation (e.g. `-`, `.`, `/`, `:`)

### Identifier Normalization Reuse
- Reuses Stage 21 scheme strategies:
  - `compact_uppercase` for tickers, CIK, LEI, MIC, IATA, ISO country codes
  - `doi` for DOIs
  - `lowercase_trim` for FRED series and economic identifiers

---

## 4. Match Kinds & Deterministic Ranking

| Match Kind | Meaning | Rank Tier |
|---|---|---|
| `EXACT_IDENTIFIER` | Exact match against current identifier | Tier 1 |
| `EXACT_CANONICAL_NAME` | Exact match against canonical name | Tier 2 |
| `EXACT_DISPLAY_NAME` | Exact match against display name | Tier 2 |
| `EXACT_ALIAS` | Exact match against current alias | Tier 3 |
| `PREFIX_IDENTIFIER` | Prefix match against curated human identifier | Tier 4 |
| `PREFIX_CANONICAL_NAME` | Prefix match against canonical name | Tier 5 |
| `PREFIX_DISPLAY_NAME` | Prefix match against display name | Tier 5 |
| `PREFIX_ALIAS` | Prefix match against current alias | Tier 6 |
| `FUZZY_CANONICAL_NAME` | Trigram similarity on canonical name (>= 0.35) | Tier 7 |
| `FUZZY_DISPLAY_NAME` | Trigram similarity on display name (>= 0.35) | Tier 7 |
| `FUZZY_ALIAS` | Trigram similarity on current alias (>= 0.35) | Tier 8 |

### Deduplication & Tie-Breaking
1. An entity appearing multiple times is returned exactly once with its highest-ranking match.
2. Tie-break:
   - Rank Tier (ascending, Tier 1 is highest)
   - Trigram similarity score (descending)
   - Shorter matched text length
   - Display name alphabetical
   - Entity UUID

---

## 5. Technology & Indexes

Backed directly by PostgreSQL source-of-truth tables without denormalized search index tables:
- `entities`:
  - B-tree on `canonical_name_normalized`
  - B-tree on `display_name_normalized`
  - GIN (`gin_trgm_ops`) on `canonical_name_normalized`
  - GIN (`gin_trgm_ops`) on `display_name_normalized`
- `entity_aliases`:
  - B-tree on `normalized_value` where `is_current = TRUE`
  - GIN (`gin_trgm_ops`) on `normalized_value` where `is_current = TRUE`
- `entity_identifiers`:
  - B-tree on `(scheme_key, normalized_value)` where `is_current = TRUE`
  - Identifiers are **never** fuzzy matched.

---

## 6. Selection Behavior

When a user selects an entity from Global Search:
1. Calls Stage 25 `selectEntity(entity_id, source="global_search")`.
2. Closes the search dropdown and clears the search input.
3. Does **not** automatically navigate or change routes. The user remains on the current workspace module.

---

## 7. Global Search vs. Stage 47 Command Target Resolution

| Dimension | Stage 45 Global Search | Stage 47 Command Target Resolution |
|---|---|---|
| **Purpose** | Fuzzy human entity discovery | Exact deterministic target binding |
| **Fuzzy Matching** | Yes (Trigram similarity >= 0.35 on names/aliases) | **No** (Strictly exact identifier/alias/canonical match) |
| **Spelling Errors** | Tolerates spelling mistakes (e.g. `Appel` -> `Apple Inc.`) | Returns `TARGET_NOT_FOUND` (no auto-correction) |
| **Action on Selection** | Updates selected entity; preserves current route | Updates selected entity AND navigates to target module |
| **Resolution Engine** | PostgreSQL GIN trigram queries | Stage 22 `EntityResolutionService` exact match |

