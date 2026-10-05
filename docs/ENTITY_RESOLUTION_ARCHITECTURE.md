# Entity Resolution Architecture

## Selected Entity Context Flow
In Stage 25 and beyond, resolution integrates with the frontend context as follows:

```text
resolver (e.g. Stage 22)
→ entity_id
→ selectEntity(entity_id)
```

The Resolver itself does not own the global state. Its role is solely to map ambiguous inputs (like a ticker string) to a canonical `entity_id`. Once resolved, the frontend may commit this ID to the Global Selected Entity Context.
