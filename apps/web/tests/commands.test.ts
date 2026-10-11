import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  getAllCommands,
  getCommandById,
} from "../src/lib/commands/registry";
import {
  filterCommands,
  normalizeQuery,
} from "../src/lib/commands/matcher";
import {
  executeCommand,
  CommandExecutionError,
} from "../src/lib/commands/executor";
import type {
  CommandContext,
  CommandExecutionHelpers,
  CommandDefinition,
} from "../src/lib/commands/types";
import { ATLAS_MODULES_LIST } from "../src/config/atlas-modules";

describe("Stage 46 - Command Registry Tests", () => {
  it("should have unique, non-empty IDs for all registered commands", () => {
    const commands = getAllCommands();
    assert.ok(commands.length >= 24, "Expected at least 24 registered commands");

    const idSet = new Set<string>();
    for (const cmd of commands) {
      assert.ok(cmd.id && cmd.id.trim() !== "", "Command ID must not be empty");
      assert.ok(!idSet.has(cmd.id), `Duplicate command ID found: ${cmd.id}`);
      idSet.add(cmd.id);

      assert.ok(cmd.label && cmd.label.trim() !== "", `Command ${cmd.id} must have a label`);
      assert.ok(cmd.category, `Command ${cmd.id} must have a category`);
      assert.equal(typeof cmd.execute, "function", `Command ${cmd.id} must have execute function`);
    }
  });

  it("should register exactly 20 module navigation commands matching Stage 4 routes", () => {
    const navCommands = getAllCommands().filter((c) => c.category === "navigation");
    assert.equal(navCommands.length, 20, "Must have exactly 20 module navigation commands");

    const expectedRoutes = [
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
    ];

    for (const mod of ATLAS_MODULES_LIST) {
      const cmd = getCommandById(`navigation.${mod.id}`);
      assert.ok(cmd, `Missing navigation command for module: ${mod.id}`);
      assert.equal(cmd.label, `Go to ${mod.label}`);

      let navigatedRoute = "";
      const dummyHelpers: CommandExecutionHelpers = {
        navigate: (route) => {
          navigatedRoute = route;
        },
        clearSelectedEntity: () => {},
        focusGlobalSearch: () => {},
        openSectionSettings: () => {},
        closePalette: () => {},
      };
      const dummyContext: CommandContext = { pathname: "/" };

      cmd.execute(dummyContext, dummyHelpers);
      assert.equal(navigatedRoute, mod.route, `Navigation command ${cmd.id} must navigate to ${mod.route}`);
      assert.ok(expectedRoutes.includes(mod.route), `Unexpected route: ${mod.route}`);
    }
  });

  it("should register Open Global Settings command", () => {
    const cmd = getCommandById("settings.global.open");
    assert.ok(cmd, "Missing settings.global.open command");
    assert.equal(cmd.label, "Open Global Settings");
    assert.equal(cmd.category, "settings");

    let navigated = "";
    cmd.execute({ pathname: "/markets" }, {
      navigate: (r) => { navigated = r; },
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => {},
      openSectionSettings: () => {},
      closePalette: () => {},
    });
    assert.equal(navigated, "/settings");
  });

  it("should register Search Entities command that triggers global search", () => {
    const cmd = getCommandById("search.focus");
    assert.ok(cmd, "Missing search.focus command");
    assert.equal(cmd.label, "Search Entities");
    assert.equal(cmd.category, "search");

    let searchFocused = false;
    cmd.execute({ pathname: "/home" }, {
      navigate: () => {},
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => { searchFocused = true; },
      openSectionSettings: () => {},
      closePalette: () => {},
    });
    assert.equal(searchFocused, true, "search.focus must invoke focusGlobalSearch");
  });

  it("should respect Clear Selected Entity availability", () => {
    const cmd = getCommandById("entity.selection.clear");
    assert.ok(cmd, "Missing entity.selection.clear command");
    assert.ok(cmd.availability, "Must have availability check");

    // When no entity selected -> hidden
    assert.equal(cmd.availability({ pathname: "/markets", selectedEntityId: null }), "hidden");
    assert.equal(cmd.availability({ pathname: "/markets", selectedEntityId: undefined }), "hidden");

    // When entity selected -> available
    assert.equal(
      cmd.availability({ pathname: "/markets", selectedEntityId: "123e4567-e89b-12d3-a456-426614174000" }),
      "available"
    );
  });

  it("should respect module permission authorization", () => {
    const cmd = getCommandById("navigation.trading");
    assert.ok(cmd?.availability);

    // Permitted
    assert.equal(
      cmd.availability({ pathname: "/", canViewModule: (mod) => mod === "trading" }),
      "available"
    );

    // Forbidden
    assert.equal(
      cmd.availability({ pathname: "/", canViewModule: (mod) => mod !== "trading" }),
      "hidden"
    );
  });
});

describe("Stage 46 - Command Matcher & Ranking Tests", () => {
  const dummyContext: CommandContext = { pathname: "/home" };

  it("should normalize query string correctly", () => {
    assert.equal(normalizeQuery("  GO   TO   MARKETS  "), "go to markets");
    assert.equal(normalizeQuery(""), "");
    assert.equal(normalizeQuery("   "), "");
  });

  it("should return curated default ordering on empty query", () => {
    const results = filterCommands("", dummyContext);
    assert.ok(results.length > 0);

    // Category ordering: navigation -> search -> selection -> settings -> shell
    const firstCat = results[0].category;
    assert.equal(firstCat, "navigation", "First category for empty query must be navigation");
  });

  it("should match exact label with highest priority (Tier 1)", () => {
    const results = filterCommands("Go to Markets", dummyContext);
    assert.ok(results.length > 0);
    assert.equal(results[0].id, "navigation.markets");
  });

  it("should match exact alias with Tier 2 priority", () => {
    const results = filterCommands("ai", dummyContext);
    assert.ok(results.length > 0);
    assert.equal(results[0].id, "navigation.ai");
  });

  it("should match label prefix with Tier 3 priority", () => {
    const results = filterCommands("mark", dummyContext);
    assert.ok(results.length > 0);
    assert.equal(results[0].id, "navigation.markets");
  });

  it("should match keywords with Tier 5 priority", () => {
    const results = filterCommands("portfolio", dummyContext);
    assert.ok(results.length > 0);
    assert.equal(results[0].id, "navigation.portfolios");
  });

  it("should match lightweight deterministic fuzzy subsequence (Tier 8)", () => {
    // Typo: "mrakets" contains subsequence of "Go to Markets"
    const results = filterCommands("mrakets", dummyContext);
    assert.ok(results.length > 0);
    assert.ok(results.some((c) => c.id === "navigation.markets"));
  });

  it("should return empty list on non-matching query", () => {
    const results = filterCommands("zzzzzzzzzzzzz", dummyContext);
    assert.equal(results.length, 0);
  });

  it("should be deterministic: same query produces identical ordering", () => {
    const run1 = filterCommands("screen", dummyContext);
    const run2 = filterCommands("screen", dummyContext);
    assert.deepEqual(
      run1.map((c) => c.id),
      run2.map((c) => c.id)
    );
  });
});

describe("Stage 46 - Command Parser & Boundary Non-Scope Tests", () => {
  const dummyContext: CommandContext = { pathname: "/" };

  it("should treat slash command input as plain string without executing syntax", () => {
    // "/markets" is plain search text in Stage 46
    const results = filterCommands("/markets", dummyContext);
    // Does not throw, does not execute parser, does not navigate
    assert.ok(Array.isArray(results));
  });

  it("should treat 'NVDA CHART' as plain search string without parsing", () => {
    const results = filterCommands("NVDA CHART", dummyContext);
    // Plain search string, no entity resolution or chart action execution
    assert.ok(Array.isArray(results));
  });

  it("should treat 'PORT RISK' as plain search string without parsing", () => {
    const results = filterCommands("PORT RISK", dummyContext);
    assert.ok(Array.isArray(results));
  });

  it("should treat natural-language query as plain search string without LLM calls", () => {
    const results = filterCommands("show me Nvidia's chart please", dummyContext);
    assert.ok(Array.isArray(results));
  });
});

describe("Stage 46 - Command Executor Tests", () => {
  it("should safely execute available command and close palette", async () => {
    let closed = false;
    let navigated = "";

    const cmd = getCommandById("navigation.charts")!;
    const dummyHelpers: CommandExecutionHelpers = {
      navigate: (r) => { navigated = r; },
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => {},
      openSectionSettings: () => {},
      closePalette: () => { closed = true; },
    };

    const success = await executeCommand(cmd, { pathname: "/" }, dummyHelpers);
    assert.equal(success, true);
    assert.equal(navigated, "/charts");
    assert.equal(closed, true);
  });

  it("should not execute disabled command", async () => {
    const disabledCmd: CommandDefinition = {
      id: "test.disabled",
      label: "Disabled Test",
      category: "shell",
      availability: () => "disabled",
      execute: () => {
        throw new Error("Should not be executed");
      },
    };

    let closed = false;
    const dummyHelpers: CommandExecutionHelpers = {
      navigate: () => {},
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => {},
      openSectionSettings: () => {},
      closePalette: () => { closed = true; },
    };

    const success = await executeCommand(disabledCmd, { pathname: "/" }, dummyHelpers);
    assert.equal(success, false);
    assert.equal(closed, false);
  });

  it("should wrap execution errors in CommandExecutionError safely", async () => {
    const failingCmd: CommandDefinition = {
      id: "test.failing",
      label: "Failing Test",
      category: "shell",
      execute: () => {
        throw new Error("Simulated failure");
      },
    };

    const dummyHelpers: CommandExecutionHelpers = {
      navigate: () => {},
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => {},
      openSectionSettings: () => {},
      closePalette: () => {},
    };

    await assert.rejects(
      async () => {
        await executeCommand(failingCmd, { pathname: "/" }, dummyHelpers);
      },
      (err: unknown) => {
        assert.ok(err instanceof CommandExecutionError);
        assert.equal(err.commandId, "test.failing");
        return true;
      }
    );
  });
});
