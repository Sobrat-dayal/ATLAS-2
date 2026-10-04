# Background System

The Stage 8 Background & Watermark Engine manages custom user-uploaded backgrounds and visual filters.

## Integration with Settings

The primary global configuration for backgrounds is integrated into the Main Settings page under `/settings/appearance` (added in Stage 9). 

The `BackgroundQuickControl` popover in the top-bar remains available for quick on-the-fly edits, while the Main Settings page offers the same comprehensive controls (Enable, Image Selection, Opacity, Blur, Filters, Overlay Readability).

The `BackgroundProvider` (`useBackground` hook) continues to manage both drafted and active states, syncing metadata with `localStorage` and image blobs via `IndexedDB`.
