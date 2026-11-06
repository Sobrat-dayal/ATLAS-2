/**
 * ATLAS Stage 146: Node type registry for the visual workflow editor.
 */

import type { NodeType } from "./types";

export interface NodeMeta {
  type: NodeType;
  label: string;
  category: "trigger" | "ai" | "control" | "data" | "action" | "approval";
  description: string;
  color: string;
  inputs: number;
  outputs: number;
}

export const NODE_REGISTRY: Record<NodeType, NodeMeta> = {
  MANUAL_TRIGGER: { type: "MANUAL_TRIGGER", label: "Manual Trigger", category: "trigger", description: "Start workflow manually", color: "#1a4a1a", inputs: 0, outputs: 1 },
  SCHEDULE_TRIGGER: { type: "SCHEDULE_TRIGGER", label: "Schedule Trigger", category: "trigger", description: "Start on a cron schedule", color: "#1a4a1a", inputs: 0, outputs: 1 },
  EVENT_TRIGGER: { type: "EVENT_TRIGGER", label: "Event Trigger", category: "trigger", description: "Start on ATLAS event", color: "#1a4a1a", inputs: 0, outputs: 1 },
  AI_AGENT: { type: "AI_AGENT", label: "AI Agent", category: "ai", description: "Run an ATLAS agent with bounded tools", color: "#1a2a4a", inputs: 1, outputs: 1 },
  LLM_PROMPT: { type: "LLM_PROMPT", label: "LLM Prompt", category: "ai", description: "Single LLM call with structured prompt", color: "#1a2a4a", inputs: 1, outputs: 1 },
  STRUCTURED_OUTPUT: { type: "STRUCTURED_OUTPUT", label: "Structured Output", category: "ai", description: "Extract typed output from LLM", color: "#1a2a4a", inputs: 1, outputs: 1 },
  CONDITION: { type: "CONDITION", label: "Condition", category: "control", description: "Branch on a boolean condition", color: "#3a2a0a", inputs: 1, outputs: 2 },
  SWITCH: { type: "SWITCH", label: "Switch", category: "control", description: "Branch on multiple conditions", color: "#3a2a0a", inputs: 1, outputs: 4 },
  MERGE: { type: "MERGE", label: "Merge", category: "control", description: "Merge parallel branches", color: "#3a2a0a", inputs: 4, outputs: 1 },
  DATA_MAPPING: { type: "DATA_MAPPING", label: "Data Mapping", category: "data", description: "Transform and map data fields", color: "#2a1a3a", inputs: 1, outputs: 1 },
  SCHEMA_VALIDATE: { type: "SCHEMA_VALIDATE", label: "Schema Validate", category: "data", description: "Validate data against JSON schema", color: "#2a1a3a", inputs: 1, outputs: 2 },
  WAIT: { type: "WAIT", label: "Wait", category: "control", description: "Pause for duration or until condition", color: "#3a2a0a", inputs: 1, outputs: 1 },
  ATLAS_TOOL: { type: "ATLAS_TOOL", label: "ATLAS Tool", category: "action", description: "Call an approved ATLAS system tool", color: "#1a3a2a", inputs: 1, outputs: 1 },
  MCP_TOOL: { type: "MCP_TOOL", label: "MCP Tool", category: "action", description: "Call an approved MCP tool (SSRF-protected)", color: "#1a3a2a", inputs: 1, outputs: 1 },
  RESEARCH_QUERY: { type: "RESEARCH_QUERY", label: "Research Query", category: "action", description: "ATLAS research and RAG query", color: "#1a3a2a", inputs: 1, outputs: 1 },
  HUMAN_APPROVAL: { type: "HUMAN_APPROVAL", label: "Human Approval", category: "approval", description: "Pause and require human approval", color: "#3a1a1a", inputs: 1, outputs: 2 },
  ERROR_HANDLER: { type: "ERROR_HANDLER", label: "Error Handler", category: "control", description: "Handle node errors with retry/fallback", color: "#3a1a1a", inputs: 1, outputs: 1 },
  RETURN: { type: "RETURN", label: "Return", category: "control", description: "End workflow and return output", color: "#1a1a3a", inputs: 1, outputs: 0 },
};

export const NODE_CATEGORIES = {
  trigger: { label: "Triggers", nodes: ["MANUAL_TRIGGER", "SCHEDULE_TRIGGER", "EVENT_TRIGGER"] as NodeType[] },
  ai: { label: "AI", nodes: ["AI_AGENT", "LLM_PROMPT", "STRUCTURED_OUTPUT"] as NodeType[] },
  control: { label: "Control Flow", nodes: ["CONDITION", "SWITCH", "MERGE", "WAIT", "ERROR_HANDLER", "RETURN"] as NodeType[] },
  data: { label: "Data", nodes: ["DATA_MAPPING", "SCHEMA_VALIDATE"] as NodeType[] },
  action: { label: "Actions", nodes: ["ATLAS_TOOL", "MCP_TOOL", "RESEARCH_QUERY"] as NodeType[] },
  approval: { label: "Human", nodes: ["HUMAN_APPROVAL"] as NodeType[] },
};
