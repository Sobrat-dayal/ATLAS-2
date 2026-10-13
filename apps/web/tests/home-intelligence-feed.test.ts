import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { getWidgetDefinition } from "../src/lib/home/widget-registry";
import {
  INTELLIGENCE_VIEW_STATES,
  isSupportedViewState,
  IntelligenceFeedViewState,
  IntelligenceFeedViewItem,
} from "../src/lib/intelligence-feed/types";
import { ATLAS_MODULES } from "../src/config/atlas-modules";

describe("Stage 55 - Home Intelligence Feed Presentation Foundation Tests", () => {
  it("should confirm widget registry marks home-intelligence-feed as reserved for Stage 55", () => {
    const widget = getWidgetDefinition("home-intelligence-feed");
    assert.ok(widget !== undefined, "home-intelligence-feed must be registered");
    assert.equal(widget?.id, "home-intelligence-feed");
    assert.equal(widget?.targetStage, 55);
    // Section 66: Domain readiness is explicitly "reserved"
    assert.equal(widget?.status, "reserved");
    assert.equal(widget?.defaultState, "reserved");
    assert.equal(widget?.placement, "secondary");
  });

  it("should verify the minimal presentation-only view states contract", () => {
    const expectedStates: IntelligenceFeedViewState[] = [
      "reserved",
      "loading",
      "ready",
      "empty",
      "unavailable",
      "error",
    ];

    assert.deepEqual([...INTELLIGENCE_VIEW_STATES], expectedStates);

    assert.equal(isSupportedViewState("reserved"), true);
    assert.equal(isSupportedViewState("loading"), true);
    assert.equal(isSupportedViewState("ready"), true);
    assert.equal(isSupportedViewState("empty"), true);
    assert.equal(isSupportedViewState("unavailable"), true);
    assert.equal(isSupportedViewState("error"), true);

    assert.equal(isSupportedViewState("live_monitoring"), false);
    assert.equal(isSupportedViewState("scanning"), false);
    assert.equal(isSupportedViewState("ai_processing"), false);
  });

  it("should verify future view-item structure is strictly presentation-only", () => {
    const item: IntelligenceFeedViewItem = {
      id: "signal-001",
      title: "Regulatory update regarding cross-border financial transactions",
      summary: "Published official bulletin detailing new disclosure guidelines.",
      observedAt: "2026-10-13T12:00:00Z",
      sourceLabel: "Official Bulletin",
      sourceCount: 2,
      entityIds: ["00000000-0000-0000-0000-000000000001"],
      internalTarget: {
        moduleId: "intelligence",
      },
    };

    assert.equal(item.id, "signal-001");
    assert.equal(typeof item.title, "string");
    assert.ok(item.entityIds && item.entityIds.length === 1);
    assert.equal(item.internalTarget?.moduleId, "intelligence");
  });

  it("should verify canonical navigation target is /intelligence and uses canonical module registry", () => {
    assert.ok(ATLAS_MODULES.intelligence !== undefined);
    assert.equal(ATLAS_MODULES.intelligence.id, "intelligence");
    assert.equal(ATLAS_MODULES.intelligence.route, "/intelligence");

    const headerContent = fs.readFileSync(
      path.resolve(__dirname, "../src/components/home/IntelligenceFeedHeader.tsx"),
      "utf-8"
    );
    assert.ok(headerContent.includes("ATLAS_MODULES.intelligence.route"));

    const reservedContent = fs.readFileSync(
      path.resolve(__dirname, "../src/components/home/IntelligenceFeedReservedState.tsx"),
      "utf-8"
    );
    assert.ok(reservedContent.includes("ATLAS_MODULES.intelligence.route"));
  });

  it("should verify truthful reserved-state copy and absence of deceptive monitoring claims", () => {
    const reservedFile = fs.readFileSync(
      path.resolve(__dirname, "../src/components/home/IntelligenceFeedReservedState.tsx"),
      "utf-8"
    );

    // Truthful copy assertions (Section 70)
    assert.ok(reservedFile.includes("Intelligence feed not connected"));
    assert.ok(
      reservedFile.includes(
        "Verified intelligence updates will appear here when the ATLAS Intelligence service becomes available."
      )
    );

    // Negative assertions: No deceptive live scanning claims (Section 12, 85, 86)
    assert.equal(reservedFile.includes("Live Monitoring"), false);
    assert.equal(reservedFile.includes("Scanning 24/7"), false);
    assert.equal(reservedFile.includes("AI Analyzing"), false);
    assert.equal(reservedFile.includes("Global Threats"), false);
    assert.equal(reservedFile.includes("Critical Alert"), false);
  });

  it("should verify zero broker, zero agent, zero workflow, and zero dangerous HTML in intelligence feed code", () => {
    const filesToCheck = [
      path.resolve(__dirname, "../src/lib/intelligence-feed/types.ts"),
      path.resolve(__dirname, "../src/components/home/HomeIntelligenceFeed.tsx"),
      path.resolve(__dirname, "../src/components/home/IntelligenceFeedHeader.tsx"),
      path.resolve(__dirname, "../src/components/home/IntelligenceFeedReservedState.tsx"),
      path.resolve(__dirname, "../src/components/home/IntelligenceFeedItemCard.tsx"),
    ];

    const forbiddenPatterns = [
      "dangerouslySetInnerHTML",
      "eval(",
      "exec(",
      "spawnAgent",
      "agentRunner",
      "workflowEngine",
      "broker",
      "executeTrade",
      "placeOrder",
      "localStorage.setItem",
      "indexedDB",
      "97% confidence",
      "High Market Impact",
      "Bullish",
      "Bearish",
    ];

    for (const filePath of filesToCheck) {
      if (!fs.existsSync(filePath)) continue;
      const content = fs.readFileSync(filePath, "utf-8");
      const basename = path.basename(filePath);
      for (const pattern of forbiddenPatterns) {
        assert.equal(
          content.includes(pattern),
          false,
          `File ${basename} must not contain forbidden pattern '${pattern}'`
        );
      }
    }
  });

  it("should confirm Home components export cleanly from index.ts", () => {
    const homeIndex = fs.readFileSync(
      path.resolve(__dirname, "../src/components/home/index.ts"),
      "utf-8"
    );

    assert.ok(homeIndex.includes("HomeIntelligenceFeed"));
    assert.ok(homeIndex.includes("IntelligenceFeedHeader"));
    assert.ok(homeIndex.includes("IntelligenceFeedReservedState"));
    assert.ok(homeIndex.includes("IntelligenceFeedItemCard"));
  });
});
