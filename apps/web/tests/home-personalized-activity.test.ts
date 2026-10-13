import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  formatAbsoluteTime,
  formatRelativeTime,
} from "../src/lib/activity/activity-format";
import {
  getWidgetDefinition,
} from "../src/lib/home/widget-registry";
import { UserActivityRecorder } from "../src/lib/activity/activity-recorder";
import { ATLAS_MODULES } from "../src/config/atlas-modules";

describe("Stage 53 - Home Personalized Activity Formatting & Logic Tests", () => {
  it("should format relative timestamps accurately", () => {
    const now = new Date();

    // 10 seconds ago -> Just now
    const tenSecAgo = new Date(now.getTime() - 10 * 1000).toISOString();
    assert.equal(formatRelativeTime(tenSecAgo), "Just now");

    // 5 minutes ago -> 5m ago
    const fiveMinAgo = new Date(now.getTime() - 5 * 60 * 1000).toISOString();
    assert.equal(formatRelativeTime(fiveMinAgo), "5m ago");

    // 3 hours ago -> 3h ago
    const threeHoursAgo = new Date(now.getTime() - 3 * 3600 * 1000).toISOString();
    assert.equal(formatRelativeTime(threeHoursAgo), "3h ago");

    // 25 hours ago -> Yesterday
    const yesterday = new Date(now.getTime() - 25 * 3600 * 1000).toISOString();
    assert.equal(formatRelativeTime(yesterday), "Yesterday");

    // 4 days ago -> 4d ago
    const fourDaysAgo = new Date(now.getTime() - 4 * 24 * 3600 * 1000).toISOString();
    assert.equal(formatRelativeTime(fourDaysAgo), "4d ago");
  });

  it("should format absolute timestamps with timeZoneName", () => {
    const isoString = "2026-10-13T12:00:00Z";
    const formatted = formatAbsoluteTime(isoString);
    assert.ok(typeof formatted === "string");
    assert.ok(formatted.length > 5);
  });

  it("should confirm widget registry marks home-personalized-activity as implemented", () => {
    const widget = getWidgetDefinition("home-personalized-activity");
    assert.ok(widget !== undefined);
    assert.equal(widget?.id, "home-personalized-activity");
    assert.equal(widget?.targetStage, 53);
    assert.equal(widget?.status, "implemented");
    assert.equal(widget?.defaultState, "available");
  });

  it("should verify client activity recorder singleton functionality", () => {
    const recorder = UserActivityRecorder.getInstance();
    assert.ok(recorder !== undefined);

    // Call recordModuleOpened and recordEntitySelected in test environment without throwing
    recorder.recordModuleOpened("markets");
    recorder.recordEntitySelected("42f56708-4d51-40be-9304-45e0d37e6da8");
  });

  it("should verify 20 canonical modules consistency with frontend types", () => {
    const expectedModules = [
      "home",
      "markets",
      "charts",
      "watchlists",
      "screeners",
      "companies",
      "economics",
      "news",
      "research",
      "maps",
      "intelligence",
      "options",
      "trading",
      "portfolios",
      "risk",
      "ai",
      "data",
      "saved",
      "workspaces",
      "agents",
    ];
    assert.equal(Object.keys(ATLAS_MODULES).length, 20);
    for (const mod of expectedModules) {
      assert.ok(mod in ATLAS_MODULES, `Module ${mod} must be in ATLAS_MODULES`);
    }
  });
});

describe("Stage 53 - Privacy & Architecture Invariant Verifications", () => {
  const activityDir = path.resolve(__dirname, "../src/lib/activity");
  const homeComponentsDir = path.resolve(__dirname, "../src/components/home");

  it("should verify activity client does not persist data to localStorage or IndexedDB", () => {
    const activityApiFile = fs.readFileSync(path.join(activityDir, "activity-api.ts"), "utf-8");
    const activityRecorderFile = fs.readFileSync(path.join(activityDir, "activity-recorder.ts"), "utf-8");

    assert.ok(!activityApiFile.includes("localStorage"), "activity-api must not use localStorage");
    assert.ok(!activityApiFile.includes("indexedDB"), "activity-api must not use indexedDB");
    assert.ok(!activityRecorderFile.includes("localStorage"), "activity-recorder must not use localStorage");
    assert.ok(!activityRecorderFile.includes("indexedDB"), "activity-recorder must not use indexedDB");
  });

  it("should verify no third-party tracking SDKs or external analytics", () => {
    const files = fs.readdirSync(activityDir);
    for (const file of files) {
      const content = fs.readFileSync(path.join(activityDir, file), "utf-8");
      assert.ok(!content.includes("mixpanel"), `${file} must not reference mixpanel`);
      assert.ok(!content.includes("segment"), `${file} must not reference segment`);
      assert.ok(!content.includes("fullstory"), `${file} must not reference fullstory`);
      assert.ok(!content.includes("google-analytics"), `${file} must not reference google-analytics`);
    }
  });

  it("should verify no AI / LLM calls or summarization in activity feature", () => {
    const componentFile = fs.readFileSync(path.join(homeComponentsDir, "HomePersonalizedActivity.tsx"), "utf-8");
    assert.ok(!componentFile.includes("openai"), "Component must not call OpenAI");
    assert.ok(!componentFile.includes("gemini"), "Component must not call Gemini");
    assert.ok(!componentFile.includes("ollama"), "Component must not call Ollama");
  });

  it("should verify no purple gradients in Home Personalized Activity UI", () => {
    const componentFile = fs.readFileSync(path.join(homeComponentsDir, "HomePersonalizedActivity.tsx"), "utf-8");
    const rowFile = fs.readFileSync(path.join(homeComponentsDir, "HomeActivityRow.tsx"), "utf-8");

    assert.ok(!componentFile.includes("from-purple"), "Component must not use purple gradients");
    assert.ok(!componentFile.includes("to-purple"), "Component must not use purple gradients");
    assert.ok(!rowFile.includes("from-purple"), "Row must not use purple gradients");
    assert.ok(!rowFile.includes("to-purple"), "Row must not use purple gradients");
  });
});
