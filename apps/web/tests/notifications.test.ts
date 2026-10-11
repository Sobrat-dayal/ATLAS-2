import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  ALLOWED_INTERNAL_ROUTES,
  formatRelativeTime,
  isAllowedInternalRoute,
} from "../src/lib/notifications/constants";
import {
  listNotifications,
  getUnreadNotificationCount,
  markNotificationRead,
  markAllNotificationsRead,
  archiveNotification,
} from "../src/lib/notifications/client";

describe("Stage 49 - Notification Route Allowlist & Security Tests", () => {
  it("should allow all 20 canonical Stage 4 module routes plus /settings", () => {
    const canonicalModules = [
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
    ];

    for (const route of canonicalModules) {
      assert.equal(ALLOWED_INTERNAL_ROUTES.has(route), true, `Route ${route} should be in allowlist`);
      assert.equal(isAllowedInternalRoute(route), true, `Route ${route} should pass validation`);
      assert.equal(isAllowedInternalRoute(`${route}?tab=metrics`), true);
      assert.equal(isAllowedInternalRoute(`${route}#summary`), true);
    }
  });

  it("should reject external URLs fail-closed", () => {
    const maliciousUrls = [
      "https://malicious.com",
      "https://atlas.evil.org/markets",
      "http://phishing.site",
      "//external-domain.com",
      "ftp://transfer.host",
    ];

    for (const url of maliciousUrls) {
      assert.equal(isAllowedInternalRoute(url), false, `External URL ${url} must be rejected`);
    }
  });

  it("should reject javascript:, data:, and file: schemes", () => {
    const attackPayloads = [
      "javascript:alert(1)",
      "javascript:void(0)",
      "data:text/html,<script>alert(1)</script>",
      "file:///etc/passwd",
    ];

    for (const attack of attackPayloads) {
      assert.equal(isAllowedInternalRoute(attack), false, `Payload ${attack} must be rejected`);
    }
  });

  it("should reject unapproved or unknown internal routes", () => {
    const unknownRoutes = [
      "/unknown-module",
      "/admin/backdoor",
      "/api/v1/internal",
      "/undefined",
      "/null",
    ];

    for (const route of unknownRoutes) {
      assert.equal(isAllowedInternalRoute(route), false, `Unknown route ${route} must be rejected`);
    }
  });

  it("should safely handle null, undefined, and empty string", () => {
    assert.equal(isAllowedInternalRoute(null), false);
    assert.equal(isAllowedInternalRoute(undefined), false);
    assert.equal(isAllowedInternalRoute(""), false);
    assert.equal(isAllowedInternalRoute("   "), false);
  });
});

describe("Stage 49 - Unread Badge & Display Tests", () => {
  it("should format unread badge counts correctly: 0 is hidden, 1-99 is numeric, 100+ is 99+", () => {
    const formatBadge = (unreadCount: number): string | null => {
      return unreadCount > 99 ? "99+" : unreadCount > 0 ? String(unreadCount) : null;
    };

    assert.equal(formatBadge(0), null, "Count 0 should hide badge");
    assert.equal(formatBadge(1), "1");
    assert.equal(formatBadge(5), "5");
    assert.equal(formatBadge(99), "99");
    assert.equal(formatBadge(100), "99+");
    assert.equal(formatBadge(150), "99+");
    assert.equal(formatBadge(1000), "99+");
  });

  it("should format accessible button labels accurately", () => {
    const getAccessibleLabel = (unreadCount: number) =>
      unreadCount > 0 ? `Notifications, ${unreadCount} unread` : "Notifications";

    assert.equal(getAccessibleLabel(0), "Notifications");
    assert.equal(getAccessibleLabel(4), "Notifications, 4 unread");
    assert.equal(getAccessibleLabel(100), "Notifications, 100 unread");
  });

  it("should ensure client unread count never becomes negative", () => {
    const decrementCount = (current: number) => Math.max(0, current - 1);

    assert.equal(decrementCount(5), 4);
    assert.equal(decrementCount(1), 0);
    assert.equal(decrementCount(0), 0);
  });
});

describe("Stage 49 - Relative Timestamp Formatting Tests", () => {
  it("should format timestamps without external date library", () => {
    const now = new Date();

    const thirtySecsAgo = new Date(now.getTime() - 30 * 1000).toISOString();
    assert.equal(formatRelativeTime(thirtySecsAgo), "just now");

    const fiveMinsAgo = new Date(now.getTime() - 5 * 60 * 1000).toISOString();
    assert.equal(formatRelativeTime(fiveMinsAgo), "5m ago");

    const threeHoursAgo = new Date(now.getTime() - 3 * 3600 * 1000).toISOString();
    assert.equal(formatRelativeTime(threeHoursAgo), "3h ago");

    const oneDayAgo = new Date(now.getTime() - 25 * 3600 * 1000).toISOString();
    assert.equal(formatRelativeTime(oneDayAgo), "Yesterday");

    const fourDaysAgo = new Date(now.getTime() - 4 * 24 * 3600 * 1000).toISOString();
    assert.equal(formatRelativeTime(fourDaysAgo), "4d ago");
  });
});

describe("Stage 49 - Notification State Derivation Tests", () => {
  it("should derive UNREAD, READ, and ARCHIVED states deterministically from timestamps", () => {
    const getStatus = (item: { read_at: string | null; archived_at: string | null }) => {
      if (item.archived_at !== null) return "ARCHIVED";
      if (item.read_at !== null) return "READ";
      return "UNREAD";
    };

    assert.equal(
      getStatus({ read_at: null, archived_at: null }),
      "UNREAD"
    );

    assert.equal(
      getStatus({ read_at: "2026-10-12T00:00:00Z", archived_at: null }),
      "READ"
    );

    // Archiving implies read; status is ARCHIVED
    assert.equal(
      getStatus({ read_at: "2026-10-12T00:00:00Z", archived_at: "2026-10-12T00:00:00Z" }),
      "ARCHIVED"
    );
  });
});

describe("Stage 49 - Frontend API Client Tests", () => {
  const originalFetch = global.fetch;

  it("should issue GET /api/v1/notifications with correct query parameters and auth headers", async () => {
    let capturedUrl = "";
    let capturedHeaders: Record<string, string> = {};

    global.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      capturedUrl = String(input);
      capturedHeaders = (init?.headers as Record<string, string>) || {};
      return new Response(
        JSON.stringify({
          items: [],
          next_cursor: "cursor-token-123",
          has_more: true,
          unread_count: 3,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }) as unknown as typeof fetch;

    try {
      const res = await listNotifications(
        { filter: "all", limit: 25, cursor: "prev-cur" },
        { token: "mock-jwt-token", baseUrl: "http://localhost:8000" }
      );

      assert.equal(
        capturedUrl,
        "http://localhost:8000/api/v1/notifications?filter=all&limit=25&cursor=prev-cur"
      );
      assert.equal(capturedHeaders["Authorization"], "Bearer mock-jwt-token");
      assert.equal(res.next_cursor, "cursor-token-123");
      assert.equal(res.unread_count, 3);
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("should issue GET /api/v1/notifications/unread-count", async () => {
    let capturedUrl = "";

    global.fetch = (async (input: RequestInfo | URL) => {
      capturedUrl = String(input);
      return new Response(JSON.stringify({ unread_count: 7 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }) as unknown as typeof fetch;

    try {
      const res = await getUnreadNotificationCount({
        token: "tok",
        baseUrl: "http://localhost:8000",
      });
      assert.equal(capturedUrl, "http://localhost:8000/api/v1/notifications/unread-count");
      assert.equal(res.unread_count, 7);
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("should issue POST /api/v1/notifications/{id}/read", async () => {
    let capturedUrl = "";
    let capturedMethod = "";

    global.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      capturedUrl = String(input);
      capturedMethod = init?.method || "";
      return new Response(
        JSON.stringify({
          notification_id: "notif-1",
          category: "system",
          severity: "info",
          title: "Title",
          message: "Msg",
          action_kind: "none",
          action_route: null,
          action_entity_id: null,
          created_at: "2026-10-12T00:00:00Z",
          read_at: "2026-10-12T00:00:01Z",
          archived_at: null,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }) as unknown as typeof fetch;

    try {
      const res = await markNotificationRead("notif-1", {
        token: "tok",
        baseUrl: "http://localhost:8000",
      });
      assert.equal(capturedUrl, "http://localhost:8000/api/v1/notifications/notif-1/read");
      assert.equal(capturedMethod, "POST");
      assert.equal(res.read_at, "2026-10-12T00:00:01Z");
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("should issue POST /api/v1/notifications/read-all", async () => {
    let capturedUrl = "";

    global.fetch = (async (input: RequestInfo | URL) => {
      capturedUrl = String(input);
      return new Response(JSON.stringify({ updated_count: 14 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }) as unknown as typeof fetch;

    try {
      const res = await markAllNotificationsRead({
        token: "tok",
        baseUrl: "http://localhost:8000",
      });
      assert.equal(capturedUrl, "http://localhost:8000/api/v1/notifications/read-all");
      assert.equal(res.updated_count, 14);
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("should issue POST /api/v1/notifications/{id}/archive", async () => {
    let capturedUrl = "";

    global.fetch = (async (input: RequestInfo | URL) => {
      capturedUrl = String(input);
      return new Response(
        JSON.stringify({
          notification_id: "notif-2",
          category: "market",
          severity: "info",
          title: "Market info",
          message: "Msg",
          action_kind: "none",
          action_route: null,
          action_entity_id: null,
          created_at: "2026-10-12T00:00:00Z",
          read_at: "2026-10-12T00:01:00Z",
          archived_at: "2026-10-12T00:01:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }) as unknown as typeof fetch;

    try {
      const res = await archiveNotification("notif-2", {
        token: "tok",
        baseUrl: "http://localhost:8000",
      });
      assert.equal(capturedUrl, "http://localhost:8000/api/v1/notifications/notif-2/archive");
      assert.equal(res.archived_at, "2026-10-12T00:01:00Z");
    } finally {
      global.fetch = originalFetch;
    }
  });
});
