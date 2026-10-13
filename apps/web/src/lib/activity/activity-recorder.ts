/**
 * Client-side Activity Recorder for Stage 53 Workspace Continuity.
 * 
 * Rules:
 * - Best-effort: failures never block navigation or entity selection.
 * - Non-blocking: executes asynchronously.
 * - Idempotency: generates a unique UUID client_event_id per interaction.
 * - Debounces burst clicks on the same target within 2.5 seconds.
 * - Emits "atlas:activity-recorded" custom event for localized cache invalidation.
 */

import { recordHomeActivity } from "./activity-api";

// In-memory set of recent interactions to prevent client duplicate events
const recentInteractionCache = new Map<string, number>();
const DEBOUNCE_WINDOW_MS = 2500;

function isDebounced(key: string): boolean {
  const now = Date.now();
  const lastTime = recentInteractionCache.get(key);
  if (lastTime && now - lastTime < DEBOUNCE_WINDOW_MS) {
    return true;
  }
  recentInteractionCache.set(key, now);
  // Keep cache small
  if (recentInteractionCache.size > 100) {
    for (const [k, time] of recentInteractionCache.entries()) {
      if (now - time > DEBOUNCE_WINDOW_MS) {
        recentInteractionCache.delete(k);
      }
    }
  }
  return false;
}

function generateUUID(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback RFC4122 v4 UUID generator
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export class UserActivityRecorder {
  private static instance: UserActivityRecorder;

  public static getInstance(): UserActivityRecorder {
    if (!UserActivityRecorder.instance) {
      UserActivityRecorder.instance = new UserActivityRecorder();
    }
    return UserActivityRecorder.instance;
  }

  /**
   * Captures an explicit module navigation action.
   */
  public recordModuleOpened(moduleId: string, token?: string | null): void {
    if (!moduleId || typeof window === "undefined") return;

    const debounceKey = `MODULE_OPENED:${moduleId}`;
    if (isDebounced(debounceKey)) return;

    const clientEventId = generateUUID();

    // Fire and forget, strictly non-blocking
    recordHomeActivity(
      {
        event_type: "MODULE_OPENED",
        module_id: moduleId,
        client_event_id: clientEventId,
      },
      { token }
    )
      .then(() => {
        window.dispatchEvent(
          new CustomEvent("atlas:activity-recorded", {
            detail: { event_type: "MODULE_OPENED", module_id: moduleId },
          })
        );
      })
      .catch(() => {
        // Silently swallow recording errors: never block user navigation
      });
  }

  /**
   * Captures an explicit Universal Entity selection action.
   */
  public recordEntitySelected(entityId: string, token?: string | null): void {
    if (!entityId || typeof window === "undefined") return;

    const debounceKey = `ENTITY_SELECTED:${entityId}`;
    if (isDebounced(debounceKey)) return;

    const clientEventId = generateUUID();

    // Fire and forget, strictly non-blocking
    recordHomeActivity(
      {
        event_type: "ENTITY_SELECTED",
        entity_id: entityId,
        client_event_id: clientEventId,
      },
      { token }
    )
      .then(() => {
        window.dispatchEvent(
          new CustomEvent("atlas:activity-recorded", {
            detail: { event_type: "ENTITY_SELECTED", entity_id: entityId },
          })
        );
      })
      .catch(() => {
        // Silently swallow recording errors: never block user entity selection
      });
  }
}

export const activityRecorder = UserActivityRecorder.getInstance();
