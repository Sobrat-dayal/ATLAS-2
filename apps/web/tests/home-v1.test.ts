import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  HOME_WIDGET_DEFINITIONS,
  getAllWidgetDefinitions,
  getWidgetDefinition,
  getImplementedWidgetDefinitions,
  getReservedWidgetDefinitions,
} from "../src/lib/home/widget-registry";
import {
  PRIMARY_QUICK_LAUNCH_IDS,
  getCuratedQuickLaunchItems,
  getAllQuickLaunchItems,
} from "../src/lib/home/quick-launch";
import { HomeWidgetId } from "../src/lib/home/types";
import { ATLAS_MODULES, ATLAS_MODULES_LIST } from "../src/config/atlas-modules";

describe("Stage 51 - Home Widget Registry Tests", () => {
  it("should have all canonical Home widget definitions registered", () => {
    const widgets = getAllWidgetDefinitions();
    assert.equal(widgets.length, 11);
    assert.equal(HOME_WIDGET_DEFINITIONS.length, 11);
  });

  it("should have stable widget IDs in authoritative registry", () => {
    const expectedIds: HomeWidgetId[] = [
      "current-context",
      "quick-launch",
      "home-market-summary",
      "home-personalized-activity",
      "home-tasks-approvals",
      "home-intelligence-feed",
      "home-portfolio-summary",
      "home-news-preview",
      "home-economics-preview",
      "home-map-preview",
      "home-agent-activity",
    ];

    const actualIds = HOME_WIDGET_DEFINITIONS.map((w) => w.id);
    assert.deepEqual(actualIds, expectedIds);
  });

  it("should define implemented widgets including Stage 52 Market Summary, Stage 53 Activity, and Stage 54 Tasks & Approvals", () => {
    const implemented = getImplementedWidgetDefinitions();
    assert.equal(implemented.length, 5);
    const implementedIds = implemented.map((w) => w.id);
    assert.deepEqual(implementedIds, [
      "current-context",
      "quick-launch",
      "home-market-summary",
      "home-personalized-activity",
      "home-tasks-approvals",
    ]);
  });

  it("should define reserved widgets for Stage 55 Intelligence Feed", () => {
    const reserved = getReservedWidgetDefinitions();
    assert.equal(reserved.length, 1);

    const stage52 = getWidgetDefinition("home-market-summary");
    assert.ok(stage52);
    assert.equal(stage52?.targetStage, 52);
    assert.equal(stage52?.status, "implemented");

    const stage53 = getWidgetDefinition("home-personalized-activity");
    assert.ok(stage53);
    assert.equal(stage53?.targetStage, 53);
    assert.equal(stage53?.status, "implemented");

    const stage54 = getWidgetDefinition("home-tasks-approvals");
    assert.ok(stage54);
    assert.equal(stage54?.targetStage, 54);
    assert.equal(stage54?.status, "implemented");

    const stage55 = getWidgetDefinition("home-intelligence-feed");
    assert.ok(stage55);
    assert.equal(stage55?.targetStage, 55);
    assert.equal(stage55?.status, "reserved");
  });

  it("should be frozen and immutable", () => {
    assert.ok(Object.isFrozen(HOME_WIDGET_DEFINITIONS));
    assert.throws(() => {
      // @ts-expect-error mutating frozen array
      HOME_WIDGET_DEFINITIONS.push({ id: "arbitrary" });
    });
  });

  it("should retrieve individual widget definitions by id", () => {
    const contextWidget = getWidgetDefinition("current-context");
    assert.ok(contextWidget);
    assert.equal(contextWidget?.title, "Current Focus");
    assert.equal(contextWidget?.targetStage, 51);

    const nonExistent = getWidgetDefinition("unknown-widget" as HomeWidgetId);
    assert.equal(nonExistent, undefined);
  });
});

describe("Stage 51 - Canonical Quick Launch Tests", () => {
  it("should curate exactly 10 primary workspace modules", () => {
    assert.equal(PRIMARY_QUICK_LAUNCH_IDS.length, 10);
    const expectedPrimary = [
      "markets",
      "charts",
      "companies",
      "economics",
      "research",
      "maps",
      "intelligence",
      "portfolios",
      "ai",
      "agents",
    ];
    assert.deepEqual([...PRIMARY_QUICK_LAUNCH_IDS], expectedPrimary);
  });

  it("should derive curated items strictly from canonical module registry", () => {
    const curated = getCuratedQuickLaunchItems();
    assert.equal(curated.length, 10);

    for (const item of curated) {
      const canonical = ATLAS_MODULES[item.id];
      assert.ok(canonical, `Item ${item.id} must exist in canonical ATLAS_MODULES`);
      assert.equal(item.route, canonical.route);
      assert.equal(item.label, canonical.label);
      assert.equal(item.requiredPermission, canonical.requiredPermission);
      assert.ok(item.route.startsWith("/"), `Route must start with /`);
    }
  });

  it("should derive all 20 canonical modules for expanded Quick Launch", () => {
    const all = getAllQuickLaunchItems();
    assert.equal(all.length, 20);
    assert.equal(ATLAS_MODULES_LIST.length, 20);

    const actualIds = all.map((m) => m.id);
    const expectedIds = ATLAS_MODULES_LIST.map((m) => m.id);
    assert.deepEqual(actualIds, expectedIds);
  });

  it("should ensure all Quick Launch routes match canonical module routes exactly", () => {
    const all = getAllQuickLaunchItems();
    for (const item of all) {
      assert.equal(item.route, ATLAS_MODULES[item.id].route);
      assert.equal(item.label, ATLAS_MODULES[item.id].label);
    }
  });
});

describe("Stage 51 - No Fake Data Verification", () => {
  it("should verify home/page.tsx does not contain fabricated financial data", () => {
    const homePageContent = fs.readFileSync(
      path.resolve(__dirname, "../src/app/(atlas)/home/page.tsx"),
      "utf8"
    );

    // Assert absence of old mock values
    assert.equal(homePageContent.includes("12450000"), false, "Must not contain fake portfolio value");
    assert.equal(homePageContent.includes("5123.41"), false, "Must not contain fake stock price");
    assert.equal(homePageContent.includes("mockMarketData"), false, "Must not contain mockMarketData");
    assert.equal(homePageContent.includes("Global Risk Indicator"), false, "Must not contain fake risk indicator");
    assert.equal(homePageContent.includes("Active Tasks"), false, "Must not contain fake tasks");
  });

  it("should verify home components do not contain hardcoded stock prices or metrics", () => {
    const componentsDir = path.resolve(__dirname, "../src/components/home");
    const files = fs.readdirSync(componentsDir);

    for (const file of files) {
      if (!file.endsWith(".tsx") && !file.endsWith(".ts")) continue;
      const content = fs.readFileSync(path.join(componentsDir, file), "utf8");

      assert.equal(content.includes("5123.41"), false, `${file} must not contain fake price`);
      assert.equal(content.includes("12450000"), false, `${file} must not contain fake balance`);
      assert.equal(content.includes("mockMarketData"), false, `${file} must not contain mockMarketData`);
      assert.equal(content.includes("16234.52"), false, `${file} must not contain fake NASDAQ price`);
    }
  });
});

describe("Stage 51 - Architecture & Boundary Verification", () => {
  it("should verify Home route is canonical /home and not /dashboard", () => {
    assert.equal(ATLAS_MODULES.home.route, "/home");
    assert.equal(fs.existsSync(path.resolve(__dirname, "../src/app/(atlas)/home/page.tsx")), true);
    assert.equal(fs.existsSync(path.resolve(__dirname, "../src/app/(atlas)/dashboard/page.tsx")), false);
  });

  it("should confirm Home components export cleanly from index.ts", async () => {
    const homeIndex = await import("../src/components/home");
    assert.ok(homeIndex.HomePage);
    assert.ok(homeIndex.HomeHeader);
    assert.ok(homeIndex.HomeQuickActions);
    assert.ok(homeIndex.HomeCurrentContext);
    assert.ok(homeIndex.HomeQuickLaunch);
    assert.ok(homeIndex.HomeWidgetSurface);
    assert.ok(homeIndex.HomeReservedState);
    assert.ok(homeIndex.HomeDashboardGrid);
  });
});
