/**
 * Time, Category, and Provenance Formatting Utilities for Financial News (Stage 99).
 */

export function formatPublishedTime(isoString: string): string {
  if (!isoString) return "--:-- UTC";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "--:-- UTC";

    const hours = String(d.getUTCHours()).padStart(2, "0");
    const minutes = String(d.getUTCMinutes()).padStart(2, "0");
    return `${hours}:${minutes} UTC`;
  } catch {
    return "--:-- UTC";
  }
}

export function formatFullUtcTime(isoString: string): string {
  if (!isoString) return "N/A";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "N/A";

    const year = d.getUTCFullYear();
    const month = String(d.getUTCMonth() + 1).padStart(2, "0");
    const day = String(d.getUTCDate()).padStart(2, "0");
    const hours = String(d.getUTCHours()).padStart(2, "0");
    const minutes = String(d.getUTCMinutes()).padStart(2, "0");
    const seconds = String(d.getUTCSeconds()).padStart(2, "0");

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} UTC`;
  } catch {
    return "N/A";
  }
}

export function formatRelativeTime(isoString: string): string {
  if (!isoString) return "";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "";

    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    if (diffMs < 0) return "Just now";

    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  } catch {
    return "";
  }
}

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export function formatUtcDate(isoString?: string | null): string {
  if (!isoString) return "—";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "—";
    const year = d.getUTCFullYear();
    const month = String(d.getUTCMonth() + 1).padStart(2, "0");
    const day = String(d.getUTCDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  } catch {
    return "—";
  }
}

export function formatUtcDateTime(isoString?: string | null): string {
  if (!isoString) return "N/A";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "N/A";
    const year = d.getUTCFullYear();
    const month = String(d.getUTCMonth() + 1).padStart(2, "0");
    const day = String(d.getUTCDate()).padStart(2, "0");
    const hours = String(d.getUTCHours()).padStart(2, "0");
    const minutes = String(d.getUTCMinutes()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes} UTC`;
  } catch {
    return "N/A";
  }
}

export function formatShortUtcDateTime(isoString?: string | null): string {
  if (!isoString) return "N/A";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "N/A";
    const month = MONTH_NAMES[d.getUTCMonth()];
    const day = d.getUTCDate();
    const hours = String(d.getUTCHours()).padStart(2, "0");
    const minutes = String(d.getUTCMinutes()).padStart(2, "0");
    return `${month} ${day}, ${hours}:${minutes} UTC`;
  } catch {
    return "N/A";
  }
}

export function getCategoryBadgeStyle(category: string): {
  bg: string;
  text: string;
  border: string;
} {
  switch (category.toUpperCase()) {
    case "CENTRAL_BANKS":
      return {
        bg: "bg-blue-500/10 dark:bg-blue-900/20",
        text: "text-blue-700 dark:text-blue-300",
        border: "border-blue-500/20",
      };
    case "ECONOMICS":
      return {
        bg: "bg-emerald-500/10 dark:bg-emerald-900/20",
        text: "text-emerald-700 dark:text-emerald-300",
        border: "border-emerald-500/20",
      };
    case "EQUITIES":
    case "COMPANY":
      return {
        bg: "bg-violet-500/10 dark:bg-violet-900/20",
        text: "text-violet-700 dark:text-violet-300",
        border: "border-violet-500/20",
      };
    case "REGULATION":
      return {
        bg: "bg-amber-500/10 dark:bg-amber-900/20",
        text: "text-amber-700 dark:text-amber-300",
        border: "border-amber-500/20",
      };
    case "TECHNOLOGY":
      return {
        bg: "bg-sky-500/10 dark:bg-sky-900/20",
        text: "text-sky-700 dark:text-sky-300",
        border: "border-sky-500/20",
      };
    case "CORPORATE_ACTIONS":
      return {
        bg: "bg-orange-500/10 dark:bg-orange-900/20",
        text: "text-orange-700 dark:text-orange-300",
        border: "border-orange-500/20",
      };
    case "COMMODITIES":
      return {
        bg: "bg-yellow-500/10 dark:bg-yellow-900/20",
        text: "text-yellow-700 dark:text-yellow-300",
        border: "border-yellow-500/20",
      };
    default:
      return {
        bg: "bg-zinc-500/10 dark:bg-zinc-800/40",
        text: "text-zinc-700 dark:text-zinc-300",
        border: "border-zinc-500/20",
      };
  }
}

export function isSafeExternalUrl(url: string): boolean {
  if (!url) return false;
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return false;
    }
    const host = parsed.hostname.toLowerCase();
    if (
      host === "localhost" ||
      host === "127.0.0.1" ||
      host === "169.254.169.254" ||
      host.endsWith(".local") ||
      host.endsWith(".internal")
    ) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}
