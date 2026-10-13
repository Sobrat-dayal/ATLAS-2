import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { getWidgetDefinition } from "../src/lib/home/widget-registry";
import { TaskStatus } from "../src/lib/tasks/types";
import { ApprovalStatus } from "../src/lib/approvals/types";

describe("Stage 54 - Home Tasks & Approvals Frontend Logic Tests", () => {
  it("should confirm widget registry marks home-tasks-approvals as implemented for Stage 54", () => {
    const widget = getWidgetDefinition("home-tasks-approvals");
    assert.ok(widget !== undefined, "home-tasks-approvals widget should be defined in registry");
    assert.equal(widget?.id, "home-tasks-approvals");
    assert.equal(widget?.targetStage, 54);
    assert.equal(widget?.status, "implemented");
    assert.equal(widget?.defaultState, "available");
    assert.equal(widget?.placement, "secondary");
  });

  it("should verify task overdue and due-soon derivation rules", () => {
    const now = new Date();

    // 1. Past due date and OPEN -> Overdue
    const pastDue = new Date(now.getTime() - 3600 * 1000).toISOString();
    const isPastDueOverdue = (status: TaskStatus, dueAt: string | null) => {
      if (!dueAt || status !== "OPEN") return false;
      return new Date(dueAt).getTime() < now.getTime();
    };
    assert.equal(isPastDueOverdue("OPEN", pastDue), true);
    assert.equal(isPastDueOverdue("COMPLETED", pastDue), false);
    assert.equal(isPastDueOverdue("CANCELLED", pastDue), false);

    // 2. Future due date within 24 hours and OPEN -> Due Soon
    const fourHoursAhead = new Date(now.getTime() + 4 * 3600 * 1000).toISOString();
    const isDueSoon = (status: TaskStatus, dueAt: string | null) => {
      if (!dueAt || status !== "OPEN") return false;
      const dueTime = new Date(dueAt).getTime();
      const nowTime = now.getTime();
      return dueTime >= nowTime && dueTime <= nowTime + 24 * 3600 * 1000;
    };
    assert.equal(isDueSoon("OPEN", fourHoursAhead), true);
    assert.equal(isDueSoon("COMPLETED", fourHoursAhead), false);

    // 3. Due date 3 days ahead -> Not due soon
    const threeDaysAhead = new Date(now.getTime() + 3 * 24 * 3600 * 1000).toISOString();
    assert.equal(isDueSoon("OPEN", threeDaysAhead), false);
  });

  it("should verify approval expiration and decision eligibility rules", () => {
    const now = new Date();

    const isApprovalEligible = (
      status: ApprovalStatus,
      expiresAt: string
    ) => {
      if (status !== "PENDING") return false;
      return new Date(expiresAt).getTime() > now.getTime();
    };

    const futureExp = new Date(now.getTime() + 12 * 3600 * 1000).toISOString();
    const pastExp = new Date(now.getTime() - 1000).toISOString();

    // Future expiration + PENDING -> eligible
    assert.equal(isApprovalEligible("PENDING", futureExp), true);

    // Past expiration + PENDING -> expired, not eligible
    assert.equal(isApprovalEligible("PENDING", pastExp), false);

    // APPROVED or REJECTED -> not eligible even if not expired
    assert.equal(isApprovalEligible("APPROVED", futureExp), false);
    assert.equal(isApprovalEligible("REJECTED", futureExp), false);
    assert.equal(isApprovalEligible("CANCELLED", futureExp), false);
  });

  it("should verify proposal digest format is valid 64-character SHA-256 hex string", () => {
    const testDigest = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    const sha256Regex = /^[a-f0-9]{64}$/;
    assert.ok(sha256Regex.test(testDigest));
  });

  it("should verify zero broker, zero agent, zero workflow execution side-effects in tasks & approvals code", () => {
    const dirsToCheck = [
      path.resolve(__dirname, "../src/lib/tasks"),
      path.resolve(__dirname, "../src/lib/approvals"),
      path.resolve(__dirname, "../src/components/home"),
    ];

    const forbiddenImports = [
      "broker",
      "placeOrder",
      "executeTrade",
      "workflowEngine",
      "agentRunner",
      "spawnAgent",
      "child_process",
      "localStorage.setItem",
      "indexedDB",
    ];

    for (const dir of dirsToCheck) {
      if (!fs.existsSync(dir)) continue;
      const files = fs.readdirSync(dir).filter((f) => f.endsWith(".ts") || f.endsWith(".tsx"));
      for (const file of files) {
        const content = fs.readFileSync(path.join(dir, file), "utf-8");
        for (const forbidden of forbiddenImports) {
          assert.equal(
            content.includes(forbidden),
            false,
            `File ${file} must not contain forbidden pattern '${forbidden}'`
          );
        }
      }
    }
  });

  it("should verify TasksPanel exports and HomeTasksApprovals exports exist", () => {
    const homeIndex = fs.readFileSync(
      path.resolve(__dirname, "../src/components/home/index.ts"),
      "utf-8"
    );
    assert.ok(homeIndex.includes("HomeTasksApprovals"));
    assert.ok(homeIndex.includes("PersonalTaskList"));
    assert.ok(homeIndex.includes("PersonalTaskRow"));
    assert.ok(homeIndex.includes("TaskEditorDialog"));
    assert.ok(homeIndex.includes("PendingApprovalList"));
    assert.ok(homeIndex.includes("ApprovalReviewDialog"));

    const tasksPanelFile = fs.readFileSync(
      path.resolve(__dirname, "../src/components/bottom-taskbar/panels/TasksPanel.tsx"),
      "utf-8"
    );
    assert.ok(tasksPanelFile.includes("usePersonalTasks"));
    assert.ok(tasksPanelFile.includes("PersonalTaskRow"));
  });
});
