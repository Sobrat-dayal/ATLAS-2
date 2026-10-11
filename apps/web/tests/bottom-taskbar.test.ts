import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  PANEL_DEFINITIONS,
  getAllPanelDefinitions,
  getPrimaryPanelDefinitions,
  getTrailingPanelDefinitions,
  getPanelDefinition,
  validatePanelRegistry,
  DEFAULT_BOTTOM_PANEL_HEIGHT,
  MIN_BOTTOM_PANEL_HEIGHT,
  MAX_BOTTOM_PANEL_HEIGHT_RATIO,
  clampBottomPanelHeight,
  getNextBottomPanelState,
  BottomPanelId,
  BottomPanelDefinition,
} from "../src/lib/bottom-taskbar";
import { ATLAS_MODULES_LIST } from "../src/config/atlas-modules";

describe("Stage 50 - Panel Registry Tests", () => {
  it("should have exactly 7 canonical panels registered", () => {
    assert.equal(PANEL_DEFINITIONS.length, 7);
    assert.equal(getAllPanelDefinitions().length, 7);
  });

  it("should have stable panel IDs in exact canonical order", () => {
    const expectedIds: BottomPanelId[] = [
      "tasks",
      "agents",
      "jobs",
      "alerts",
      "downloads",
      "system-health",
      "terminal",
    ];

    const actualIds = PANEL_DEFINITIONS.map((p) => p.id);
    assert.deepEqual(actualIds, expectedIds);
  });

  it("should have exactly 6 primary panels and 1 trailing panel", () => {
    const primary = getPrimaryPanelDefinitions();
    const trailing = getTrailingPanelDefinitions();

    assert.equal(primary.length, 6);
    assert.equal(trailing.length, 1);

    assert.equal(trailing[0].id, "terminal");
    assert.equal(trailing[0].label, "Terminal");
    assert.equal(trailing[0].placement, "trailing");

    const primaryIds = primary.map((p) => p.id);
    assert.deepEqual(primaryIds, ["tasks", "agents", "jobs", "alerts", "downloads", "system-health"]);
  });

  it("should have non-empty labels, descriptions, icons, and components for all panels", () => {
    for (const panel of PANEL_DEFINITIONS) {
      assert.ok(panel.label && panel.label.length > 0, `Panel ${panel.id} has empty label`);
      assert.ok(panel.description && panel.description.length > 0, `Panel ${panel.id} has empty description`);
      assert.ok(
        typeof panel.icon === "function" || typeof panel.icon === "object",
        `Panel ${panel.id} must have an icon component`
      );
      assert.equal(typeof panel.component, "function", `Panel ${panel.id} must have a component function`);
      assert.equal(panel.availability, "reserved", `Panel ${panel.id} availability must be reserved in Stage 50`);
    }
  });

  it("should be frozen and immutable", () => {
    assert.equal(Object.isFrozen(PANEL_DEFINITIONS), true);
  });

  it("should retrieve individual panel definitions by id", () => {
    const jobs = getPanelDefinition("jobs");
    assert.ok(jobs);
    assert.equal(jobs?.id, "jobs");
    assert.equal(jobs?.label, "Jobs");

    const terminal = getPanelDefinition("terminal");
    assert.ok(terminal);
    assert.equal(terminal?.id, "terminal");
    assert.equal(terminal?.placement, "trailing");

    // Unknown ID
    const unknown = getPanelDefinition("nonexistent" as BottomPanelId);
    assert.equal(unknown, undefined);
  });

  it("should reject invalid registry shapes", () => {
    // Missing panel count
    assert.throws(() => {
      validatePanelRegistry(PANEL_DEFINITIONS.slice(0, 5));
    }, /Expected exactly 7 bottom panels/);

    // Duplicate IDs
    assert.throws(() => {
      const duplicated = [...PANEL_DEFINITIONS.slice(0, 6), PANEL_DEFINITIONS[0]];
      validatePanelRegistry(duplicated as readonly BottomPanelDefinition[]);
    }, /Duplicate bottom panel id/);

    // Incorrect placement for terminal
    assert.throws(() => {
      const badTerminal = PANEL_DEFINITIONS.map((p) =>
        p.id === "terminal" ? { ...p, placement: "primary" as const } : p
      );
      validatePanelRegistry(badTerminal);
    }, /Terminal panel must have placement='trailing'/);
  });
});

describe("Stage 50 - Panel Layout & Height Clamping Tests", () => {
  it("should have valid layout constants", () => {
    assert.equal(DEFAULT_BOTTOM_PANEL_HEIGHT, 280);
    assert.equal(MIN_BOTTOM_PANEL_HEIGHT, 160);
    assert.equal(MAX_BOTTOM_PANEL_HEIGHT_RATIO, 0.45);
  });

  it("should clamp heights below minimum to MIN_BOTTOM_PANEL_HEIGHT (160px)", () => {
    assert.equal(clampBottomPanelHeight(50, 1000), 160);
    assert.equal(clampBottomPanelHeight(0, 1000), 160);
    assert.equal(clampBottomPanelHeight(-100, 1000), 160);
    assert.equal(clampBottomPanelHeight(159, 1000), 160);
  });

  it("should clamp heights above maximum allowed ratio to 45% of viewport", () => {
    // Viewport height 1000px: 45% = 450px
    assert.equal(clampBottomPanelHeight(500, 1000), 450);
    assert.equal(clampBottomPanelHeight(800, 1000), 450);

    // Viewport height 800px: 45% = 360px
    assert.equal(clampBottomPanelHeight(400, 800), 360);
  });

  it("should preserve valid heights within range", () => {
    assert.equal(clampBottomPanelHeight(200, 1000), 200);
    assert.equal(clampBottomPanelHeight(280, 1000), 280);
    assert.equal(clampBottomPanelHeight(350, 1000), 350);
  });

  it("should handle NaN, undefined, or invalid inputs safely", () => {
    assert.equal(clampBottomPanelHeight(NaN, 1000), DEFAULT_BOTTOM_PANEL_HEIGHT);
    assert.equal(clampBottomPanelHeight(undefined as unknown as number, 1000), DEFAULT_BOTTOM_PANEL_HEIGHT);
  });
});

describe("Stage 50 - Panel State Transition Tests", () => {
  it("should open panel when clicking from closed (null) state", () => {
    const nextState = getNextBottomPanelState(null, "tasks");
    assert.equal(nextState, "tasks");
  });

  it("should toggle/close panel when clicking already active item", () => {
    const nextState = getNextBottomPanelState("tasks", "tasks");
    assert.equal(nextState, null);

    const nextJobs = getNextBottomPanelState("jobs", "jobs");
    assert.equal(nextJobs, null);
  });

  it("should switch active panel when clicking different item", () => {
    const switchedToJobs = getNextBottomPanelState("tasks", "jobs");
    assert.equal(switchedToJobs, "jobs");

    const switchedToTerminal = getNextBottomPanelState("jobs", "terminal");
    assert.equal(switchedToTerminal, "terminal");

    const switchedToSystem = getNextBottomPanelState("terminal", "system-health");
    assert.equal(switchedToSystem, "system-health");
  });
});

describe("Stage 50 - AppShell Route Integration Tests", () => {
  it("should verify all 20 canonical Stage 4 modules are defined for authenticated AppShell", () => {
    assert.equal(ATLAS_MODULES_LIST.length, 20);

    const canonicalModules = [
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

    const actualIds = ATLAS_MODULES_LIST.map((m) => m.id);
    assert.deepEqual(actualIds, canonicalModules);

    // Verify taskbar is not a 21st module in the list
    assert.equal(actualIds.includes("taskbar" as unknown as typeof actualIds[number]), false);
    assert.equal(actualIds.includes("bottom-taskbar" as unknown as typeof actualIds[number]), false);
  });
});

describe("Stage 50 - Boundaries & No Fake Data Verification", () => {
  it("should verify panel availability is strictly reserved and honest", () => {
    for (const panel of PANEL_DEFINITIONS) {
      assert.equal(panel.availability, "reserved");
    }
  });

  it("should ensure Terminal panel is designated as a reserved launcher without execution", () => {
    const terminalDef = getPanelDefinition("terminal");
    assert.ok(terminalDef);
    assert.equal(terminalDef?.placement, "trailing");
    assert.equal(terminalDef?.availability, "reserved");
    assert.ok(terminalDef?.description.includes("Stage 122"));
  });

  it("should confirm Alerts panel is designated as condition monitoring distinct from Stage 49 Notification Center", () => {
    const alertsDef = getPanelDefinition("alerts");
    assert.ok(alertsDef);
    assert.equal(alertsDef?.id, "alerts");
    assert.equal(alertsDef?.availability, "reserved");
    assert.ok(alertsDef?.description.includes("Alert monitoring"));
  });
});
