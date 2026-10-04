# ATLAS Appearance System

This document outlines the core architecture and conventions for the ATLAS appearance engine, implemented in Stage 7.

## Core Concepts

The ATLAS Appearance System is a pure CSS-variable based theming engine designed for high performance and zero-hydration-flash rendering. It allows multiple dimensions of appearance configuration:

1. **Theme Mode**
   - `dark` (Default): Deep space navy/charcoal for low eye strain.
   - `light`: Clean, institutional light mode.
   - `terminal`: High contrast, monochrome tech-focused mode.
   - `system`: Automatically inherits the OS preference (`prefers-color-scheme`).

2. **Density**
   - `compact` (Default): High information density, ideal for complex dashboards.
   - `default`: Standard web sizing.
   - `comfortable`: Larger hit areas and increased padding for touch or relaxed viewing.

3. **Accent Color**
   - `blue` (Default): The signature ATLAS blue.
   - `cyan`, `emerald`, `amber`: Additional semantic palettes.

## State Management and Persistence

State is managed via the `useAppearance` React context.
- **Persistence**: Saved securely to `localStorage` under the key `atlas.appearance.v1`.
- **Hydration Protection**: A blocking inline script in `layout.tsx` reads `localStorage` before React hydrates and sets appropriate `data-theme`, `data-density`, and `data-accent` attributes on the `<html>` element. This guarantees zero flashing on initial load.

## Token Taxonomy

Never use hardcoded Tailwind hex codes (e.g. `bg-[#0F131C]`). Always use semantic tokens prefixed with `atlas-`.

### Backgrounds
- `bg-atlas-bg-0`: Deepest background (e.g., behind cards, workspace root).
- `bg-atlas-surface-1`: Primary surface (e.g., sidebars, panels).
- `bg-atlas-surface-2`: Elevated surface (e.g., inputs, secondary panels).
- `bg-atlas-surface-3`: Hover/Interactive elevation.
- `bg-atlas-surface-hover`: Generic hover state for interactive rows/buttons.
- `bg-atlas-surface-selected`: Selected/Active state for navigation and tabs.

### Text
- `text-atlas-text-primary`: Primary reading text.
- `text-atlas-text-secondary`: Secondary, slightly muted text.
- `text-atlas-text-muted`: Disabled, placeholder, or highly subdued text.

### Borders
- `border-atlas-border-subtle`: Extremely faint borders.
- `border-atlas-border-default`: Standard structural borders (layout panels).
- `border-atlas-border-strong`: Interactive/hovered borders.

### Accents & Semantics
- `bg-atlas-accent` / `text-atlas-accent`: The primary brand accent (changes based on preference).
- `bg-atlas-accent-hover`: Hover state for accent surfaces.
- `bg-atlas-accent-soft`: Faded accent (for badges or subtle selections).
- `text-atlas-positive` / `bg-atlas-positive`: Semantic green (independent of accent).
- `text-atlas-negative` / `bg-atlas-negative`: Semantic red.
- `text-atlas-warning` / `bg-atlas-warning`: Semantic yellow.

## Development Preview

A temporary `DevAppearanceSwitcher` is located in the TopBar for development environments (hidden in production). This allows instantaneous testing of the appearance matrix.
