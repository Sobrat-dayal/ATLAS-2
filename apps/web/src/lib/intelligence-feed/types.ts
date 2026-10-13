/**
 * Stage 55 Home Intelligence Feed Presentation Types.
 *
 * CRITICAL ARCHITECTURAL BOUNDARY:
 * These types define a presentation-only contract for the Home Intelligence Feed UI.
 * They do NOT define the canonical Universal Event domain schema (Stage 135),
 * Event-Entity Graph (Stage 136), Exposure model (Stage 137), or Intelligence Engine (Stage 138).
 */

/**
 * Supported view states for the Home Intelligence Feed component.
 *
 * Distinct meanings:
 * - "reserved": The domain service is not yet implemented/connected (Stage 55 default).
 * - "loading": A real backend query is in progress.
 * - "ready": A verified service is connected and returned items to display.
 * - "empty": An authoritative service returned 0 items.
 * - "unavailable": A previously supported service is temporarily offline or unreachable.
 * - "error": An actual supported request failed.
 */
export type IntelligenceFeedViewState =
  | "reserved"
  | "loading"
  | "ready"
  | "empty"
  | "unavailable"
  | "error";

export const INTELLIGENCE_VIEW_STATES: readonly IntelligenceFeedViewState[] = Object.freeze([
  "reserved",
  "loading",
  "ready",
  "empty",
  "unavailable",
  "error",
]);

/**
 * Minimal presentation-only interface for future intelligence feed cards.
 *
 * NOTE: This is an untrusted UI view model. All text fields must be rendered
 * as safe plain text without HTML execution or dynamic code evaluation.
 */
export interface IntelligenceFeedViewItem {
  /** Unique presentation or event identity */
  id: string;
  /** Human-readable headline or event title */
  title: string;
  /** Optional brief plain-text summary */
  summary?: string | null;
  /** Timestamp when the event or observation occurred (ISO 8601 UTC) */
  observedAt?: string | null;
  /** Optional attributable primary source name (e.g. "SEC Filing", "Official Bulletin") */
  sourceLabel?: string | null;
  /** Optional count of verified attributable sources */
  sourceCount?: number | null;
  /** Canonical Universal Entity UUIDs related to this intelligence item */
  entityIds?: string[];
  /** Optional internal canonical navigation target */
  internalTarget?: {
    moduleId: string;
    entityId?: string;
  } | null;
}

/**
 * Validation predicate for supported view states.
 */
export function isSupportedViewState(state: string): state is IntelligenceFeedViewState {
  return (INTELLIGENCE_VIEW_STATES as readonly string[]).includes(state);
}
