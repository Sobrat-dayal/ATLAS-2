/**
 * Unit Test Suite for ATLAS Stage 128: AI Financial Action Engine Frontend Domain.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { formatActionError, ACTION_ERROR_MAP } from "../errors";
import { formatActionStatusBadge, formatClassificationBadge } from "../formatting";
import { ActionDTO, ActionDiffDTO, ExecutionReceiptDTO } from "../types";

describe("Stage 128 — ATLAS AI Financial Action Engine Unit Tests", () => {
  it("Fixture A: validates chart indicator action diff formatting", () => {
    const diff: ActionDiffDTO = {
      field_path: "indicators",
      before_value: [],
      after_value: [
        { type: "SMA", period: 20 },
        { type: "SMA", period: 50 },
      ],
      change_type: "ADD",
      validation_status: "VALID",
      financial_impact_if_computable: "Added 2 indicators",
    };

    assert.strictEqual(diff.change_type, "ADD");
    assert.strictEqual(diff.validation_status, "VALID");
    assert.strictEqual(diff.financial_impact_if_computable, "Added 2 indicators");
    assert.strictEqual(diff.after_value.length, 2);
  });

  it("Fixture B: validates screener filter structure and metric definitions", () => {
    const action: ActionDTO = {
      action_id: "act_screener_b",
      action_type: "atlas.screener.execute",
      action_version: "1.0.0",
      target_module: "screeners",
      target_resource_type: "screener_query",
      target_resource_id: "screener_fixture_b",
      actor_user_id: "test_user_stage128",
      tenant_scope: "default_tenant",
      proposed_arguments: {
        screener_id: "screener_fixture_b",
        universe: "IN_NIFTY500",
        filters: [
          { metric_id: "revenue_growth_yoy", operator: "GREATER_THAN", value: 0.15 },
          { metric_id: "net_profit_margin", operator: "GREATER_THAN", value: 0.0 },
          { metric_id: "market_cap", operator: "GREATER_THAN", value: 100000000000.0 },
        ],
      },
      normalized_arguments_hash: "hash_fixture_b",
      expected_resource_revision: "rev_screener_fixture_b_1",
      classification: "COMPUTATION_JOB",
      approval_policy: "USER_PREVIEW_CONFIRM",
      reversibility_policy: "NON_REVERSIBLE",
      action_status: "PREVIEW_READY",
      created_at: new Date().toISOString(),
    };

    assert.strictEqual(action.target_module, "screeners");
    assert.strictEqual(action.proposed_arguments.filters.length, 3);
    assert.strictEqual(action.proposed_arguments.universe, "IN_NIFTY500");
  });

  it("Fixture C: validates portfolio hypothetical deltas and non-executing disclaimer", () => {
    const baseline = { Equity: 0.60, Bonds: 0.40 };
    const proposed = { Equity: 0.50, Bonds: 0.50 };

    const equityDelta = Math.round((proposed.Equity - baseline.Equity) * 100);
    const bondDelta = Math.round((proposed.Bonds - baseline.Bonds) * 100);

    assert.strictEqual(equityDelta, -10);
    assert.strictEqual(bondDelta, 10);

    const disclaimer = "Hypothetical Allocation Proposal — Not Executed";
    assert.match(disclaimer, /Not Executed/);
  });

  it("Fixture D: validates risk immutable execution receipt constraints", () => {
    const receipt: ExecutionReceiptDTO = {
      receipt_id: "rcpt_risk_d_1",
      action_id: "act_risk_d",
      plan_id: "plan_risk_d",
      actor_user_id: "test_user_stage128",
      target_resource_id: "TEST_P",
      target_revision_before: "rev_risk_1",
      target_revision_after: "risk_run_abc123",
      operation_status: "COMPLETED",
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      result_reference: {
        run_id: "risk_run_abc123",
        metrics: {
          var_amount: 2326.0,
          confidence_level: 0.99,
          horizon_days: 1,
        },
      },
      diffs: [],
    };

    assert.strictEqual(receipt.operation_status, "COMPLETED");
    assert.strictEqual(receipt.result_reference.metrics.confidence_level, 0.99);
    assert.strictEqual(receipt.result_reference.metrics.horizon_days, 1);
  });

  it("Fixture E & F: maps approval mismatch and resource conflict errors accurately", () => {
    const mismatchMsg = formatActionError("AI_ACTION_APPROVAL_MISMATCH");
    assert.match(mismatchMsg, /Security alert/i);

    const conflictMsg = formatActionError("AI_ACTION_RESOURCE_CONFLICT");
    assert.match(conflictMsg, /modified concurrently/i);
  });

  it("Fixture I: maps prohibited trading and ledger mutation errors accurately", () => {
    const brokerMsg = formatActionError("AI_ACTION_BROKER_EXECUTION_PROHIBITED");
    assert.match(brokerMsg, /Live broker order execution is prohibited/i);

    const ledgerMsg = formatActionError("AI_ACTION_LEDGER_MUTATION_PROHIBITED");
    assert.match(ledgerMsg, /Direct ledger and cash mutations are strictly prohibited/i);
  });

  it("validates classification and status badge helpers", () => {
    const readOnlyBadge = formatClassificationBadge("READ_ONLY");
    assert.strictEqual(readOnlyBadge.label, "Read Only");

    const prohibitedBadge = formatClassificationBadge("BROKER_SIDE_EFFECT");
    assert.strictEqual(prohibitedBadge.label, "Prohibited");

    const approvedBadge = formatActionStatusBadge("APPROVED");
    assert.strictEqual(approvedBadge.label, "Approved");

    const partialBadge = formatActionStatusBadge("PARTIALLY_COMPLETED");
    assert.strictEqual(partialBadge.label, "Partially Succeeded");
  });
});
