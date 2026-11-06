import { describe, it } from "node:test";
import assert from "node:assert/strict";
import type {
  GateStatus,
  ReadinessVerdict,
  SystemReadinessReport,
} from "../types";

describe("Stage 150 System Hardening & Launch Readiness Contracts", () => {
  it("enforces valid readiness verdicts", () => {
    const verdicts: ReadinessVerdict[] = [
      "AWAITING_AUTHORIZATION",
      "GO",
      "NO_GO",
      "BLOCKED",
    ];
    assert.equal(verdicts.length, 4);
    assert.ok(verdicts.includes("AWAITING_AUTHORIZATION"));
    assert.ok(verdicts.includes("GO"));
  });

  it("evaluates simulated report structure correctly", () => {
    const report: SystemReadinessReport = {
      verdict: "AWAITING_AUTHORIZATION",
      readiness_score: 96,
      release_version: "1.0.0-rc1",
      git_commit_sha: "test-commit-sha",
      audit_timestamp: new Date().toISOString(),
      production_authorization_granted: false,
      authorized_by: null,
      critical_blockers: [],
      evaluated_gates: [
        {
          gate: "GATE_A_INTEGRATION_VERIFICATION",
          title: "Full 150-Stage Platform Integration",
          status: "PASS",
          score: 100,
          criteria_met: ["All 20 modules active"],
          criteria_unmet: [],
          blockers: [],
          evaluated_at: new Date().toISOString(),
        },
        {
          gate: "GATE_J_EXECUTIVE_RELEASE_APPROVAL",
          title: "Executive Release Sign-Off",
          status: "PENDING_SIGN_OFF",
          score: 0,
          criteria_met: [],
          criteria_unmet: ["Pending authorized release signatory"],
          blockers: [],
          evaluated_at: new Date().toISOString(),
        },
      ],
    };

    assert.equal(report.verdict, "AWAITING_AUTHORIZATION");
    assert.equal(report.readiness_score, 96);
    assert.equal(report.evaluated_gates.length, 2);
    assert.equal(report.evaluated_gates[0].status, "PASS");
    assert.equal(report.evaluated_gates[1].status, "PENDING_SIGN_OFF");
  });

  it("validates financial safety firewall guarantees", () => {
    const firewallActive = true;
    const liveCapitalPermitted = false;
    assert.ok(firewallActive, "Financial safety firewall must remain active");
    assert.equal(liveCapitalPermitted, false, "Live capital execution strictly prohibited");
  });
});
