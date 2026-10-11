# Entity Resolution Architecture

## Selected Entity Context Flow
In Stage 25 and beyond, resolution integrates with the frontend context as follows:

```text
resolver (e.g. Stage 22)
→ entity_id
→ selectEntity(entity_id)
```

The Resolver itself does not own the global state. Its role is solely to map ambiguous inputs (like a ticker string) to a canonical `entity_id`. Once resolved, the frontend may commit this ID to the Global Selected Entity Context.

## Stage 47 Command Parsing Consumer Integration
In Stage 47, `AtlasCommandTargetResolver` delegates directly to Stage 22 `EntityResolutionService` for deterministic command target binding:
- **Exact resolution only**: No fuzzy corrections or heuristics.
- **Historical exclusion**: `include_historical = False` by default.
- **Provider external ID exclusion**: Normal commands cannot resolve via raw provider external IDs.
- **Ticker identity = Financial Instrument**: Ticker symbols resolve strictly to Securities/Financial Instruments. No implicit security-to-company conversion.
- **Target-type enforcement**: Strict type guards validate that the resolved entity type matches the command spec's allowed types.
- **Ambiguity preservation**: If an identifier matches multiple scoped securities across exchanges, up to 10 candidates are returned for user disambiguation.

