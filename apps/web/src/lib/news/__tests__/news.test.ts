import test from "node:test";
import assert from "node:assert/strict";

import {
  formatFullUtcTime,
  formatPublishedTime,
  formatRelativeTime,
  getCategoryBadgeStyle,
  isSafeExternalUrl,
} from "../formatting";

test("Stage 99: formatPublishedTime produces standard UTC hours and minutes", () => {
  const ts = "2026-10-26T14:35:00Z";
  const formatted = formatPublishedTime(ts);
  assert.equal(formatted, "14:35 UTC");

  const invalid = formatPublishedTime("invalid-date");
  assert.equal(invalid, "--:-- UTC");

  const empty = formatPublishedTime("");
  assert.equal(empty, "--:-- UTC");
});

test("Stage 99: formatFullUtcTime formats standard YYYY-MM-DD HH:MM:SS UTC", () => {
  const ts = "2026-10-26T12:00:00Z";
  const formatted = formatFullUtcTime(ts);
  assert.equal(formatted, "2026-10-26 12:00:00 UTC");

  const invalid = formatFullUtcTime("");
  assert.equal(invalid, "N/A");
});

test("Stage 99: formatRelativeTime computes human-readable intervals", () => {
  const now = new Date();
  const fiveMinAgo = new Date(now.getTime() - 5 * 60 * 1000).toISOString();
  assert.equal(formatRelativeTime(fiveMinAgo), "5m ago");

  const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString();
  assert.equal(formatRelativeTime(twoHoursAgo), "2h ago");

  const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString();
  assert.equal(formatRelativeTime(threeDaysAgo), "3d ago");
});

test("Stage 99: getCategoryBadgeStyle maps categories to institutional styling", () => {
  const cbStyle = getCategoryBadgeStyle("CENTRAL_BANKS");
  assert.ok(cbStyle.text.includes("blue"));

  const econStyle = getCategoryBadgeStyle("ECONOMICS");
  assert.ok(econStyle.text.includes("emerald"));

  const techStyle = getCategoryBadgeStyle("TECHNOLOGY");
  assert.ok(techStyle.text.includes("sky"));

  const defaultStyle = getCategoryBadgeStyle("OTHER");
  assert.ok(defaultStyle.text.includes("zinc"));
});

test("Stage 99: isSafeExternalUrl blocks SSRF destinations and dangerous schemes", () => {
  // Valid external URLs
  assert.equal(isSafeExternalUrl("https://www.reuters.com/markets"), true);
  assert.equal(isSafeExternalUrl("https://www.bloomberg.com/news"), true);
  assert.equal(isSafeExternalUrl("https://economictimes.indiatimes.com"), true);

  // Dangerous protocols
  assert.equal(isSafeExternalUrl("javascript:alert(1)"), false);
  assert.equal(isSafeExternalUrl("data:text/html;base64,PHNjcmlwdD4="), false);
  assert.equal(isSafeExternalUrl("file:///etc/hosts"), false);

  // SSRF loopback & metadata IPs
  assert.equal(isSafeExternalUrl("http://localhost:8000"), false);
  assert.equal(isSafeExternalUrl("http://127.0.0.1/admin"), false);
  assert.equal(isSafeExternalUrl("http://169.254.169.254/latest/meta-data"), false);
  assert.equal(isSafeExternalUrl("http://internal.service.local"), false);
  assert.equal(isSafeExternalUrl(""), false);
});
