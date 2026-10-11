/**
 * Constants and validation utilities for Stage 49 Persistent Notifications.
 */

export const ALLOWED_INTERNAL_ROUTES = new Set<string>([
  "/home",
  "/markets",
  "/charts",
  "/watchlists",
  "/screeners",
  "/companies",
  "/economics",
  "/news",
  "/research",
  "/maps",
  "/intelligence",
  "/options",
  "/trading",
  "/portfolios",
  "/risk",
  "/ai",
  "/data",
  "/saved",
  "/workspaces",
  "/agents",
  "/settings",
]);

export const UNREAD_COUNT_POLL_INTERVAL_MS = 30000; // 30 seconds

/**
 * Validates whether a target route belongs to the approved ATLAS internal route allowlist.
 * Explicitly rejects external URLs, javascript: schemas, data: URIs, and unknown paths.
 */
export function isAllowedInternalRoute(route: string | null | undefined): boolean {
  if (!route || typeof route !== "string") {
    return false;
  }

  const trimmed = route.trim();

  // Reject external schemes or dangerous protocols
  if (
    trimmed.startsWith("http://") ||
    trimmed.startsWith("https://") ||
    trimmed.startsWith("javascript:") ||
    trimmed.startsWith("data:") ||
    trimmed.startsWith("file:") ||
    trimmed.startsWith("//")
  ) {
    return false;
  }

  // Exact allowlist match (strip query/hash for validation)
  const pathname = trimmed.split("?")[0].split("#")[0];
  return ALLOWED_INTERNAL_ROUTES.has(pathname);
}

/**
 * Format relative time using native browser locale without heavy external date libraries.
 */
export function formatRelativeTime(isoString: string): string {
  try {
    const then = new Date(isoString).getTime();
    const now = Date.now();
    const diffSec = Math.floor((now - then) / 1000);

    if (isNaN(diffSec) || diffSec < 0) {
      return "just now";
    }

    if (diffSec < 60) {
      return "just now";
    }
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) {
      return `${diffMin}m ago`;
    }
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) {
      return `${diffHours}h ago`;
    }
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) {
      return "Yesterday";
    }
    if (diffDays < 7) {
      return `${diffDays}d ago`;
    }

    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: diffDays > 365 ? "numeric" : undefined,
    }).format(new Date(isoString));
  } catch {
    return "recently";
  }
}
