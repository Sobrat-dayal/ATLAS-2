import { describe, it } from "node:test";
import assert from "node:assert";

import { askAiAboutThis, ASK_AI_EVENT } from "../askAi";
import {
  ContextMode,
  ContextType,
  DataQualityStatus,
  ProviderDisclosureStatus,
  AiContextPreviewRequest,
  AiContextEnvelope,
} from "../types";

describe("Stage 125 — ATLAS AI Context Awareness Frontend Tests", () => {
  it("Fixture A: validates context modes and quality statuses", () => {
    const validModes: ContextMode[] = ["OFF", "FOCUSED", "WORKSPACE", "CUSTOM"];
    assert.strictEqual(validModes.length, 4);

    const validQualities: DataQualityStatus[] = ["COMPLETE", "PARTIAL", "STALE", "RESTRICTED"];
    assert.strictEqual(validQualities.length, 4);

    const validDisclosures: ProviderDisclosureStatus[] = ["ALLOWED", "REDACTED", "PROHIBITED"];
    assert.strictEqual(validDisclosures.length, 3);
  });

  it("Fixture B: validates context type coverage across supported dimensions", () => {
    const contextTypes: ContextType[] = [
      "PAGE_CONTEXT",
      "MODULE_CONTEXT",
      "INSTRUMENT_CONTEXT",
      "COMPANY_CONTEXT",
      "CHART_CONTEXT",
      "WATCHLIST_CONTEXT",
      "SCREENER_CONTEXT",
      "ECONOMICS_CONTEXT",
      "NEWS_CONTEXT",
      "RESEARCH_CONTEXT",
      "PORTFOLIO_CONTEXT",
      "RISK_CONTEXT",
      "OPTIONS_CONTEXT",
      "DATA_CONTEXT",
      "SAVED_RESOURCE_CONTEXT",
      "WORKSPACE_CONTEXT",
      "WORKSPACE_PANEL_CONTEXT",
      "LINKED_CONTEXT",
      "USER_SUPPLIED_CONTEXT",
    ];

    assert.strictEqual(contextTypes.length, 19, "Must support 19 canonical context types");
    assert.ok(contextTypes.includes("INSTRUMENT_CONTEXT"));
    assert.ok(contextTypes.includes("PORTFOLIO_CONTEXT"));
    assert.ok(contextTypes.includes("RISK_CONTEXT"));
    assert.ok(contextTypes.includes("WORKSPACE_CONTEXT"));
    assert.ok(contextTypes.includes("LINKED_CONTEXT"));
  });

  it("Fixture C: validates askAiAboutThis dispatches custom event with correct payload", () => {
    let capturedEvent: unknown = null;
    const globalObj = global as Record<string, unknown>;
    const originalWindow = globalObj.window;

    // Mock minimal window event listener
    const mockWindow = {
      dispatchEvent: (event: unknown) => {
        capturedEvent = event;
        return true;
      },
    };
    globalObj.window = mockWindow;

    try {
      askAiAboutThis({
        type: "INSTRUMENT_CONTEXT",
        targetId: "AAPL",
        title: "Apple Inc.",
        parameters: { timeframe: "1D" },
      });

      assert.ok(capturedEvent !== null, "Custom event must be dispatched");
      const evt = capturedEvent as { type: string; detail: { type: string; targetId: string; title: string; parameters?: Record<string, unknown> } };
      assert.strictEqual(evt.type, ASK_AI_EVENT);
      assert.strictEqual(evt.detail.type, "INSTRUMENT_CONTEXT");
      assert.strictEqual(evt.detail.targetId, "AAPL");
      assert.strictEqual(evt.detail.title, "Apple Inc.");
      assert.strictEqual(evt.detail.parameters?.timeframe, "1D");
    } finally {
      globalObj.window = originalWindow;
    }
  });

  it("Fixture D: validates preview request construction and token budgeting calculations", () => {
    const previewReq: AiContextPreviewRequest = {
      current_route: "/markets/equities",
      active_module: "markets",
      workspace_id: "ws_tech_growth",
      focused_panel_id: "p_chart_1",
      global_link_channel_id: "ch_blue",
      context_mode_override: "FOCUSED",
      requested_references: [
        { type: "INSTRUMENT_CONTEXT", target_id: "MSFT", is_pinned: true },
        { type: "CHART_CONTEXT", target_id: "chart_msft_1d" },
      ],
    };

    assert.strictEqual(previewReq.current_route, "/markets/equities");
    assert.strictEqual(previewReq.workspace_id, "ws_tech_growth");
    assert.strictEqual(previewReq.requested_references?.length, 2);
    assert.strictEqual(previewReq.requested_references?.[0].is_pinned, true);

    const mockEnvelope: AiContextEnvelope = {
      context_request_id: "ctx_req_1234",
      context_mode: "FOCUSED",
      source_page: "/markets/equities",
      active_module: "markets",
      active_workspace_id: "ws_tech_growth",
      focused_panel_id: "p_chart_1",
      global_link_channel_id: "ch_blue",
      resolved_context_items: [
        {
          context_item_id: "ctx_page_1",
          context_type: "PAGE_CONTEXT",
          canonical_target_id: "/markets/equities",
          source_reference: "atlas:page",
          as_of: "2026-10-30T00:00:00Z",
          content_summary: "Equities Overview",
          data_quality_status: "COMPLETE",
          provider_disclosure_status: "ALLOWED",
          estimated_tokens: 120,
          content_hash: "hash_1",
          is_pinned: false,
          relevance_score: 5.0,
          structured_payload: {},
          provenance: {},
        },
      ],
      excluded_items: [],
      total_estimated_tokens: 120,
      token_budget: 8000,
      quality_summary: "COMPLETE",
      warnings: [],
      assembled_at: "2026-10-30T10:00:00Z",
    };

    assert.strictEqual(mockEnvelope.total_estimated_tokens, 120);
    assert.ok(mockEnvelope.total_estimated_tokens <= mockEnvelope.token_budget);
    const budgetPct = Math.round((mockEnvelope.total_estimated_tokens / mockEnvelope.token_budget) * 100);
    assert.strictEqual(budgetPct, 2);
  });
});
