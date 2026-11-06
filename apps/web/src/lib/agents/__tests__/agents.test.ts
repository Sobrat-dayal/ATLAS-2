import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { NODE_REGISTRY, NODE_CATEGORIES } from "../nodeRegistry.js";
import type { NodeType } from "../types.js";

describe("agents node registry", () => {
  it("NODE_REGISTRY contains all expected node types", () => {
    const expected: NodeType[] = [
      "MANUAL_TRIGGER", "SCHEDULE_TRIGGER", "EVENT_TRIGGER",
      "AI_AGENT", "LLM_PROMPT", "STRUCTURED_OUTPUT",
      "CONDITION", "SWITCH", "MERGE", "DATA_MAPPING", "SCHEMA_VALIDATE",
      "WAIT", "ATLAS_TOOL", "MCP_TOOL", "RESEARCH_QUERY",
      "HUMAN_APPROVAL", "ERROR_HANDLER", "RETURN",
    ];
    for (const type of expected) {
      assert.ok(type in NODE_REGISTRY, `Missing node type: ${type}`);
    }
  });

  it("every registry entry has required fields", () => {
    for (const [type, meta] of Object.entries(NODE_REGISTRY)) {
      assert.ok(meta.label, `${type} missing label`);
      assert.ok(meta.category, `${type} missing category`);
      assert.ok(meta.description, `${type} missing description`);
      assert.ok(meta.color, `${type} missing color`);
      assert.ok(typeof meta.inputs === "number", `${type} inputs must be number`);
      assert.ok(typeof meta.outputs === "number", `${type} outputs must be number`);
    }
  });

  it("MANUAL_TRIGGER has 0 inputs and 1 output", () => {
    assert.equal(NODE_REGISTRY.MANUAL_TRIGGER.inputs, 0);
    assert.equal(NODE_REGISTRY.MANUAL_TRIGGER.outputs, 1);
  });

  it("RETURN node has 1 input and 0 outputs", () => {
    assert.equal(NODE_REGISTRY.RETURN.inputs, 1);
    assert.equal(NODE_REGISTRY.RETURN.outputs, 0);
  });

  it("HUMAN_APPROVAL is in approval category", () => {
    assert.equal(NODE_REGISTRY.HUMAN_APPROVAL.category, "approval");
  });

  it("NODE_CATEGORIES covers all categories", () => {
    const categories = Object.keys(NODE_CATEGORIES);
    assert.ok(categories.includes("trigger"));
    assert.ok(categories.includes("ai"));
    assert.ok(categories.includes("control"));
    assert.ok(categories.includes("data"));
    assert.ok(categories.includes("action"));
    assert.ok(categories.includes("approval"));
  });

  it("AI_AGENT category is ai", () => {
    assert.equal(NODE_REGISTRY.AI_AGENT.category, "ai");
  });

  it("CONDITION has 1 input and 2 outputs", () => {
    assert.equal(NODE_REGISTRY.CONDITION.inputs, 1);
    assert.equal(NODE_REGISTRY.CONDITION.outputs, 2);
  });

  it("all nodes in NODE_CATEGORIES exist in NODE_REGISTRY", () => {
    for (const [cat, def] of Object.entries(NODE_CATEGORIES)) {
      for (const nodeType of def.nodes) {
        assert.ok(nodeType in NODE_REGISTRY, `Category ${cat} references unknown node: ${nodeType}`);
      }
    }
  });
});
