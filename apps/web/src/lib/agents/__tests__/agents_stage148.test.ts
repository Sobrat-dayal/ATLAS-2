import { describe, it } from "node:test";
import assert from "node:assert/strict";
import type { DepartmentDefinition, TeamDefinition, AgentTask, TeamMember } from "../types.js";

describe("Stage 148 Frontend Domain Contracts", () => {
  it("creates valid DepartmentDefinition structure", () => {
    const dept: DepartmentDefinition = {
      department_id: "dept-1",
      name: "Financial Research",
      description: "Fundamental and quantitative analysis",
      purpose: "Produce evidence-grounded research",
      status: "ACTIVE",
      knowledge_scope: "TENANT_SHARED",
      budget_limit_usd: 1000.0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    assert.equal(dept.name, "Financial Research");
    assert.equal(dept.status, "ACTIVE");
    assert.equal(dept.budget_limit_usd, 1000.0);
  });

  it("validates TeamDefinition coordinator presence and membership", () => {
    const member1: TeamMember = { agent_id: "a1", role: "COORDINATOR", max_concurrency: 2 };
    const member2: TeamMember = { agent_id: "a2", role: "SPECIALIST", max_concurrency: 3 };

    const team: TeamDefinition = {
      team_id: "t1",
      name: "Quant Squad",
      description: "Statistical modeling",
      objective: "Identify alpha anomalies",
      status: "ACTIVE",
      version: 1,
      execution_enabled: false,
      coordinator_agent_id: "a1",
      budget_limit_usd: 200.0,
      max_concurrency: 5,
      review_required: true,
      members: [member1, member2],
    };

    assert.equal(team.members.length, 2);
    assert.equal(team.coordinator_agent_id, "a1");
    assert.equal(team.review_required, true);
  });

  it("validates AgentTask priority, dependencies and artifacts structure", () => {
    const task: AgentTask = {
      task_id: "tsk-1",
      title: "Evaluate Sector Beta",
      description: "Analyze market sensitivity",
      priority: "HIGH",
      status: "COMPLETED",
      delegation_depth: 1,
      input_data: { ticker: "SPY" },
      dependencies: ["tsk-0"],
      subtask_ids: [],
      budget_limit_usd: 50.0,
      cost_estimate_usd: 0.05,
      tokens_used: 1250,
      model_calls: 1,
      requires_human_approval: false,
      artifacts: [
        {
          artifact_id: "art-1",
          title: "Beta Attribution",
          type: "REPORT",
          content_summary: "Beta is 1.05",
          source_citations: [{ source: "CRSP", verified: true }],
          created_at: new Date().toISOString(),
        },
      ],
      created_at: new Date().toISOString(),
    };

    assert.equal(task.priority, "HIGH");
    assert.equal(task.status, "COMPLETED");
    assert.equal(task.dependencies[0], "tsk-0");
    assert.equal(task.artifacts.length, 1);
    assert.equal(task.artifacts[0].source_citations?.[0].verified, true);
  });
});
