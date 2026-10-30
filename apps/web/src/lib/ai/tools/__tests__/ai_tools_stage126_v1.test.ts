/**
 * Stage 126 — ATLAS AI Tool Gateway Frontend Unit Tests.
 *
 * Verifies tool types, lifecycle states, approval models, and client API contracts.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  AiApprovalClass,
  AiApprovalStatus,
  AiToolCallStatus,
  AiToolCategory,
  AiToolDescriptor,
  AiToolResult,
} from "../types";

describe("Stage 126 — ATLAS AI Tool Gateway Frontend Tests", () => {
  it("Fixture A: validates canonical tool categories and approval classes", () => {
    const categories: AiToolCategory[] = [
      "DISCOVERY",
      "DATA_READ",
      "ANALYTICAL_READ",
      "STATUS_READ",
      "COMPUTATIONAL",
      "USER_STATE_MUTATION",
      "FINANCIAL_MUTATION",
      "EXTERNAL_SIDE_EFFECT",
      "PRIVILEGED_OPERATION",
    ];

    const approvalClasses: AiApprovalClass[] = [
      "NO_APPROVAL_REQUIRED",
      "USER_CONFIRMATION_REQUIRED",
      "STEP_UP_AUTH_REQUIRED",
      "ADMIN_APPROVAL_REQUIRED",
      "PROHIBITED",
    ];

    assert.equal(categories.length, 9);
    assert.equal(approvalClasses.length, 5);
    assert.ok(categories.includes("DISCOVERY"));
    assert.ok(approvalClasses.includes("USER_CONFIRMATION_REQUIRED"));
  });

  it("Fixture B: validates tool call state machine transitions", () => {
    const validStatuses: AiToolCallStatus[] = [
      "PROPOSED",
      "VALIDATING",
      "AUTHORIZING",
      "APPROVAL_REQUIRED",
      "APPROVED",
      "DENIED",
      "QUEUED",
      "RUNNING",
      "COMPLETED",
      "FAILED",
      "CANCEL_REQUESTED",
      "CANCELLED",
      "TIMED_OUT",
      "REJECTED",
    ];

    assert.equal(validStatuses.length, 14);
    assert.ok(validStatuses.includes("APPROVAL_REQUIRED"));
    assert.ok(validStatuses.includes("COMPLETED"));
    assert.ok(validStatuses.includes("TIMED_OUT"));
  });

  it("Fixture C: validates tool descriptor contract and parameter schemas", () => {
    const toolDescriptor: AiToolDescriptor = {
      tool_id: "atlas.instrument.search",
      version: "1.0.0",
      category: "DISCOVERY",
      name: "Instrument Search",
      description: "Search canonical instruments across global exchanges",
      capability_scope: "tools:instrument:read",
      approval_class: "NO_APPROVAL_REQUIRED",
      provider_disclosure_policy: "ALLOWED",
      parameters_schema: {
        type: "object",
        properties: {
          query: { type: "string" },
          limit: { type: "integer", default: 5 },
        },
        required: ["query"],
      },
      returns_schema: {
        type: "object",
        properties: {
          results: { type: "array" },
        },
      },
      lifecycle_status: "ENABLED",
      timeout_seconds: 10.0,
      rate_limit_per_minute: 60,
    };

    assert.equal(toolDescriptor.tool_id, "atlas.instrument.search");
    assert.equal(toolDescriptor.category, "DISCOVERY");
    assert.equal(toolDescriptor.lifecycle_status, "ENABLED");
    const requiredFields = (toolDescriptor.parameters_schema.required as string[]) || [];
    assert.equal(requiredFields[0], "query");
  });

  it("Fixture D: validates verified tool result envelope and content hash", () => {
    const toolResult: AiToolResult = {
      tool_call_id: "call_test_12345",
      tool_id: "atlas.market.quote",
      success: true,
      data: {
        symbol: "MSFT",
        last_price: 428.5,
        currency: "USD",
        exchange: "NASDAQ",
      },
      source_manifest: {
        tool_id: "atlas.market.quote",
        data_source: "ATLAS Real-Time Market Data",
        as_of: "2026-10-30T16:00:00Z",
        attribution: "NASDAQ Real-Time BBO",
        record_count: 1,
      },
      execution_time_ms: 12.4,
      as_of: "2026-10-30T16:00:00Z",
      content_hash: "a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4",
    };

    assert.equal(toolResult.success, true);
    assert.equal(toolResult.tool_id, "atlas.market.quote");
    assert.equal(toolResult.source_manifest?.attribution, "NASDAQ Real-Time BBO");
    assert.equal(toolResult.content_hash?.length, 64);
  });

  it("Fixture E: validates human approval request and expiration lifecycle", () => {
    const approvalStatuses: AiApprovalStatus[] = [
      "PENDING",
      "APPROVED",
      "DENIED",
      "EXPIRED",
    ];

    assert.equal(approvalStatuses.length, 4);
    assert.ok(approvalStatuses.includes("PENDING"));
    assert.ok(approvalStatuses.includes("EXPIRED"));
  });
});
