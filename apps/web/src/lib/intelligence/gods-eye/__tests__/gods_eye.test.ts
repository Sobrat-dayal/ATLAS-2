import { describe, it } from "node:test";
import assert from "node:assert";
import {
  GodsEyeLensType,
  GodsEyeViewMode,
  GodsEyeDamageAssessmentStatus,
  GodsEyeInvestigationResult,
} from "../types";

describe("God's Eye Financial Intelligence Client Types & Invariants", () => {
  it("enforces 8 canonical investigation lenses", () => {
    const validLenses: GodsEyeLensType[] = [
      "GLOBAL_EVENTS",
      "MONETARY_POLICY",
      "CORPORATE_INTELLIGENCE",
      "GEOPOLITICAL",
      "COMMODITY_INFRASTRUCTURE",
      "PHYSICAL_WORLD",
      "PORTFOLIO_INTELLIGENCE",
      "HISTORICAL_RESEARCH",
    ];
    assert.strictEqual(validLenses.length, 8);
    assert.ok(validLenses.includes("MONETARY_POLICY"));
    assert.ok(validLenses.includes("PHYSICAL_WORLD"));
  });

  it("supports 2D, 3D Globe, and Hybrid split view modes", () => {
    const viewModes: GodsEyeViewMode[] = [
      "TWO_DIMENSIONAL",
      "THREE_DIMENSIONAL_GLOBE",
      "HYBRID_SPLIT",
    ];
    assert.strictEqual(viewModes.length, 3);
  });

  it("verifies damage status defaults to UNKNOWN for proximity features", () => {
    const mockFacilityFeature = {
      id: "feat_tsmc_fab18",
      feature_type: "FACILITY",
      name: "TSMC Fab 18",
      coordinates: [120.28, 23.11],
      geometry_type: "Point",
      properties: { distance_km: 74.2 },
      confidence: 1.0,
      verified: true,
      damage_status: "UNKNOWN" as GodsEyeDamageAssessmentStatus,
    };

    assert.strictEqual(mockFacilityFeature.damage_status, "UNKNOWN");
  });

  it("validates investigation result structure with observational disclaimers", () => {
    const mockResult: GodsEyeInvestigationResult = {
      investigation_id: "ge_test_123",
      lens: "MONETARY_POLICY",
      as_of: "2024-05-01T14:00:00Z",
      is_historical_reconstruction: false,
      view_mode: "TWO_DIMENSIONAL",
      events: [],
      map_features: [],
      knowledge_graph_subgraph: {
        root_node: "CENTRAL_BANK_FED",
        traversal_depth: 2,
        node_count: 5,
        edge_count: 4,
        nodes: [{ id: "CENTRAL_BANK_FED", label: "Federal Reserve", type: "ROOT" }],
        edges: [],
      },
      market_context: {
        benchmark_symbol: "US2Y_YIELD",
        price_before: 4.72,
        price_after: 4.64,
        pct_change: -1.69,
        time_window: "14:00 - 15:30 EST",
        is_observational_only: true,
        disclaimer: "Correlation is not causation.",
      },
      evidence_sources: [],
      section_statuses: {
        events: "READY",
        graph: "READY",
        exposure: "READY",
        scoring: "READY",
        geography: "READY",
        market_context: "READY",
      },
      disclaimers: {
        causality: "Correlation is not causation.",
        damage: "Spatial proximity does not imply confirmed physical damage.",
      },
      coverage_notes: ["Jurisdictions [KP, IR] lack direct exchange feeds."],
      telemetry: { query_latency_ms: 12.4 },
    };

    assert.strictEqual(mockResult.lens, "MONETARY_POLICY");
    assert.strictEqual(mockResult.market_context?.is_observational_only, true);
    assert.ok(mockResult.disclaimers.causality.includes("Correlation is not causation"));
    assert.ok(mockResult.disclaimers.damage.includes("proximity does not imply confirmed physical damage"));
  });
});

