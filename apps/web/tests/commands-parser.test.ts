import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  looksLikeAtlasStructuredCommand,
  getCommandById,
  executeCommand,
  CommandContext,
  CommandExecutionHelpers,
} from "../src/lib/commands";

describe("Stage 47 - Frontend Structured Command Detector Tests", () => {
  it("should detect slash commands as structured command syntax", () => {
    assert.equal(looksLikeAtlasStructuredCommand("/"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/markets"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/charts NVDA"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/charts open NVDA"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/companies 'NVIDIA Corporation'"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/settings"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/search"), true);
    assert.equal(looksLikeAtlasStructuredCommand("/clear entity"), true);
  });

  it("should detect recognized shorthand suffixes", () => {
    assert.equal(looksLikeAtlasStructuredCommand("NVDA CHART"), true);
    assert.equal(looksLikeAtlasStructuredCommand("NVDA NEWS"), true);
    assert.equal(looksLikeAtlasStructuredCommand("NVDA RESEARCH"), true);
    assert.equal(looksLikeAtlasStructuredCommand("NVDA FA"), true);
  });

  it("should detect recognized shorthand prefixes and exact commands", () => {
    assert.equal(looksLikeAtlasStructuredCommand("MAP TSMC"), true);
    assert.equal(looksLikeAtlasStructuredCommand("OPTIONS NVDA"), true);
    assert.equal(looksLikeAtlasStructuredCommand("PORT RISK"), true);
    assert.equal(looksLikeAtlasStructuredCommand("BUY NVDA"), true);
    assert.equal(looksLikeAtlasStructuredCommand("SELL AAPL"), true);
  });

  it("should NOT treat normal queries or natural language as structured commands", () => {
    assert.equal(looksLikeAtlasStructuredCommand("markets"), false);
    assert.equal(looksLikeAtlasStructuredCommand("apple"), false);
    assert.equal(looksLikeAtlasStructuredCommand("show me nvidia chart"), false);
    assert.equal(looksLikeAtlasStructuredCommand("what is happening with Apple"), false);
    assert.equal(looksLikeAtlasStructuredCommand("take me to semiconductor stocks"), false);
    assert.equal(looksLikeAtlasStructuredCommand("find cheap companies"), false);
    assert.equal(looksLikeAtlasStructuredCommand("what should I buy"), false);
    assert.equal(looksLikeAtlasStructuredCommand("compare Nvidia and AMD"), false);
  });
});

describe("Stage 47 - Entity-Context Navigation Registry Tests", () => {
  const expectedEntityCommandIds = [
    "navigation.charts.entity",
    "navigation.news.entity",
    "navigation.research.entity",
    "navigation.maps.entity",
    "navigation.options.entity",
    "navigation.companies.entity",
    "navigation.markets.entity",
    "navigation.intelligence.entity",
  ];

  it("should register all 8 entity-context navigation commands with unique IDs", () => {
    for (const id of expectedEntityCommandIds) {
      const cmd = getCommandById(id);
      assert.ok(cmd, `Command "${id}" must be registered`);
      assert.equal(cmd.id, id);
      assert.equal(typeof cmd.execute, "function");
    }
  });

  it("should execute entity navigation by selecting entity and routing to module", async () => {
    const chartsCmd = getCommandById("navigation.charts.entity");
    assert.ok(chartsCmd);

    let selectedId: string | null = null;
    let navigatedRoute: string | null = null;
    let closed = false;

    const dummyContext: CommandContext = {
      pathname: "/home",
      currentModuleId: "home",
      selectedEntityId: null,
    };

    const dummyHelpers: CommandExecutionHelpers = {
      navigate: (r) => {
        navigatedRoute = r;
      },
      selectEntity: (id) => {
        selectedId = id;
      },
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => {},
      openSectionSettings: () => {},
      closePalette: () => {
        closed = true;
      },
    };

    const targetUuid = "11111111-2222-3333-4444-555555555555";
    const ok = await executeCommand(chartsCmd, dummyContext, dummyHelpers, {
      entityId: targetUuid,
    });

    assert.equal(ok, true);
    assert.equal(selectedId, targetUuid, "Must update selected entity context");
    assert.equal(navigatedRoute, "/charts", "Must navigate to /charts route");
    assert.equal(closed, true, "Must close command palette on successful execution");
  });

  it("should preserve existing entity selection if entityId argument is omitted", async () => {
    const marketsCmd = getCommandById("navigation.markets.entity");
    assert.ok(marketsCmd);

    let selectedCalled = false;
    let navigatedRoute: string | null = null;

    const dummyContext: CommandContext = {
      pathname: "/home",
      selectedEntityId: "pre-existing-id",
    };

    const dummyHelpers: CommandExecutionHelpers = {
      navigate: (r) => {
        navigatedRoute = r;
      },
      selectEntity: () => {
        selectedCalled = true;
      },
      clearSelectedEntity: () => {},
      focusGlobalSearch: () => {},
      openSectionSettings: () => {},
      closePalette: () => {},
    };

    await executeCommand(marketsCmd, dummyContext, dummyHelpers);
    assert.equal(selectedCalled, false, "Should not update selection if no entityId provided");
    assert.equal(navigatedRoute, "/markets");
  });
});

describe("Stage 47 - Frontend / Backend Command ID Parity Tests", () => {
  it("should have matching frontend command IDs for all canonical module navigations", () => {
    const canonicalModules = [
      "home", "markets", "charts", "watchlists", "screeners",
      "companies", "economics", "news", "research", "maps",
      "intelligence", "options", "trading", "portfolios", "risk",
      "ai", "data", "saved", "workspaces", "agents",
    ];

    for (const mod of canonicalModules) {
      const cmd = getCommandById(`navigation.${mod}`);
      assert.ok(cmd, `Expected navigation.${mod} to exist in frontend registry`);
    }
  });

  it("should have matching shell utility command IDs", () => {
    assert.ok(getCommandById("settings.global.open"));
    assert.ok(getCommandById("search.focus"));
    assert.ok(getCommandById("entity.selection.clear"));
  });
});
