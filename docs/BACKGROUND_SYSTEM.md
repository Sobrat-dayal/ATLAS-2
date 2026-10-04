# ATLAS Background & Watermark System

This document outlines the architecture, constraints, and configuration of the Stage 8 Background engine.

## Core Concepts

The ATLAS Background System provides customizable visual backgrounds (image/watermark) beneath the primary application shell without interfering with financial readability.

- **Separate Visual Layer**: Rendered at `z-index: -20`, entirely distinct from the `AppShell` content layer. App content `opacity` is never manipulated; only the background image layer opacity is affected.
- **Independent from Theme**: Theme handles colors, spacing, and geometry. The background system renders *between* the root Theme base layer and the application popups/panels.
- **Readability Overlay**: A configurable overlay layer (`z-index: -15`) sits between the background image and application to ensure text contrast.

## State Management and Persistence

- **Context (`useBackground`)**: Provides background configurations (`opacity`, `blur`, `brightness`, `contrast`, `saturation`, `grayscale`, `fit`, `position`, `overlay`).
- **localStorage**: Stores metadata only (`atlas.background.v1`) – opacity, blur settings, and the selected asset ID.
- **IndexedDB (`background-db.ts`)**: Securely stores the actual uploaded `Blob` files and user asset metadata. This prevents polluting localStorage with massive Base64 strings.

## Image Upload Constraints

- **File Support**: JPEG, PNG, WebP, AVIF.
- **Size Limit**: 20 MB.
- **Optimization**: Images are validated natively in the browser via `Image` decode before IndexedDB storage.
- **Live Previewing**: A `draftSettings` object allows for live previews without immediately saving to `localStorage`. Cancel reverts to original settings.

## Background Layer (AtlasBackgroundLayer.tsx)

- Renders an `<img>` tag (or a tiling `<div>`) using an object URL created directly from IndexedDB blobs.
- Converts React Context configuration values into direct inline styles and CSS `filter()` functions (blur, brightness, etc.).
- Scales slightly when blur is applied to avoid empty edges (`transform: scale(...)`).

## Configuration Matrix

- **Fit Modes**: Cover, Contain, Stretch, Tile.
- **Positioning**: Center, Top, Bottom, Left, Right, Top/Bottom Left/Right.
- **Presets**: The "Watermark" preset provides a quick configuration for brand-aligned subtle backgrounds (Contain, Opacity 8%, Saturation 40%).

## Scope and Settings Reuse

- Currently implements **Global Scope**.
- The `BackgroundQuickControl` popover provides a subset (and advanced section) of background tools.
- The `BackgroundProvider` context will be fully reused by the **Stage 9 Settings App**, preventing multiple disjoint stores. Future architecture prepares for Workspace-specific overrides.
