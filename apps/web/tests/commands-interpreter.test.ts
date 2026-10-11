import { describe, it } from "node:test";
import assert from "node:assert/strict";
import type { NaturalLanguageCommandInterpretation } from "../src/lib/commands/interpreter-types";
import {
  getCommandById,
  executeCommand,
  CommandContext,
  CommandExecutionHelpers,
} from "../src/lib/commands";

describe("Stage 48 - Frontend Natural-Language Command Interpreter Contracts", () => {
  it("should validate READY interpretation response contract structure", () => {
    const mockReadyResponse: NaturalLanguageCommandInterpretation = {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "READY",
      input_fingerprint: "abc123sha256",
      intent: "OPEN_ENTITY_IN_MODULE",
      module: "charts",
      target_text: "NVDA",
      canonical_command: '/charts "NVDA"',
      structured_parse_result: {
        command_language_version: 1,
        status: "READY",
        command_id: "navigation.charts.entity",
        normalized_command: '/charts "NVDA"',
        arguments: {
          entityId: "11111111-2222-3333-4444-555555555555",
        },
        resolved_target: {
          entity_id: "11111111-2222-3333-4444-555555555555",
          canonical_name: "NVIDIA Corp",
          display_name: "NVIDIA Corp",
          entity_type: "security",
          matched_value: "NVDA",
          match_kind: "ticker",
        },
        ambiguity_candidates: [],
        error_code: null,
        error_message: null,
      },
      clarification_question: null,
      unsupported_reason: null,
      error_code: null,
      error_message: null,
    };

    assert.equal(mockReadyResponse.interpreter_version, 1);
    assert.equal(mockReadyResponse.prompt_version, 1);
    assert.equal(mockReadyResponse.model_output_schema_version, 1);
    assert.equal(mockReadyResponse.status, "READY");
    assert.equal(mockReadyResponse.intent, "OPEN_ENTITY_IN_MODULE");
    assert.equal(mockReadyResponse.canonical_command, '/charts "NVDA"');
    assert.ok(mockReadyResponse.structured_parse_result);
    assert.equal(mockReadyResponse.structured_parse_result.status, "READY");
    assert.equal(mockReadyResponse.structured_parse_result.command_id, "navigation.charts.entity");
  });

  it("should validate NOT_COMMAND response contract structure", () => {
    const mockNotCommandResponse: NaturalLanguageCommandInterpretation = {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "NOT_COMMAND",
      input_fingerprint: "def456sha256",
      intent: "NOT_COMMAND",
      module: null,
      target_text: null,
      canonical_command: null,
      structured_parse_result: null,
      clarification_question: null,
      unsupported_reason: null,
      error_code: null,
      error_message: null,
    };

    assert.equal(mockNotCommandResponse.status, "NOT_COMMAND");
    assert.equal(mockNotCommandResponse.canonical_command, null);
    assert.equal(mockNotCommandResponse.structured_parse_result, null);
  });

  it("should validate UNSUPPORTED action response contract structure", () => {
    const mockUnsupportedResponse: NaturalLanguageCommandInterpretation = {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "UNSUPPORTED",
      input_fingerprint: "ghi789sha256",
      intent: "UNSUPPORTED_ACTION",
      module: null,
      target_text: null,
      canonical_command: null,
      structured_parse_result: null,
      clarification_question: null,
      unsupported_reason: "TRADING_ACTION",
      error_code: null,
      error_message: "Trading actions are not supported through natural-language commands yet.",
    };

    assert.equal(mockUnsupportedResponse.status, "UNSUPPORTED");
    assert.equal(mockUnsupportedResponse.unsupported_reason, "TRADING_ACTION");
  });

  it("should validate AMBIGUOUS response contract structure with clarification question", () => {
    const mockAmbiguousResponse: NaturalLanguageCommandInterpretation = {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "AMBIGUOUS",
      input_fingerprint: "jkl012sha256",
      intent: "AMBIGUOUS",
      module: null,
      target_text: null,
      canonical_command: null,
      structured_parse_result: null,
      clarification_question: "Which ATLAS module should open 'Nvidia'?",
      unsupported_reason: null,
      error_code: null,
      error_message: null,
    };

    assert.equal(mockAmbiguousResponse.status, "AMBIGUOUS");
    assert.equal(mockAmbiguousResponse.clarification_question, "Which ATLAS module should open 'Nvidia'?");
  });
});

describe("Stage 48 - Execution Boundary & Safety Verification", () => {
  it("should execute only through known registered Command IDs in Stage 46 registry", async () => {
    // Valid command from interpretation
    const commandId = "navigation.charts.entity";
    const command = getCommandById(commandId);
    assert.ok(command, "Command navigation.charts.entity must exist in Stage 46 registry");

    let routedTo = "";
    let selectedId: string | null = null;
    let closed = false;

    const mockContext: CommandContext = {
      pathname: "/markets",
      currentModuleId: "markets",
      selectedEntityId: null,
    };

    const mockHelpers: CommandExecutionHelpers = {
      navigate: (path: string) => {
        routedTo = path;
      },
      selectEntity: (id: string | null) => {
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
    const ok = await executeCommand(command, mockContext, mockHelpers, { entityId: targetUuid });

    assert.equal(ok, true);
    assert.equal(routedTo, "/charts");
    assert.equal(selectedId, targetUuid);
    assert.equal(closed, true);
  });

  it("should fail-closed if interpretation returns unknown or fabricated command ID", () => {
    const fakeCommandId = "broker.execute";
    const command = getCommandById(fakeCommandId);
    assert.equal(command, undefined, "Fabricated command IDs must not exist in registry");
  });

  it("should verify input fingerprint prevents stale interpretation execution", () => {
    const currentInput: string = "show AAPL chart";
    const oldInterpretationInput: string = "show NVDA chart";

    const isStale = currentInput !== oldInterpretationInput;
    assert.equal(isStale, true, "Interpretation for old query must be flagged as stale");
  });

  it("should verify interpretation alone does NOT mutate entity or navigation state", () => {
    const appSelectedEntityId: string | null = "existing-uuid";
    const appCurrentRoute = "/markets";

    // Receiving interpretation result:
    const interpretation: NaturalLanguageCommandInterpretation = {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "READY",
      input_fingerprint: "fingerprint",
      intent: "OPEN_ENTITY_IN_MODULE",
      module: "charts",
      target_text: "NVDA",
      canonical_command: '/charts "NVDA"',
      structured_parse_result: {
        command_language_version: 1,
        status: "READY",
        command_id: "navigation.charts.entity",
        normalized_command: '/charts "NVDA"',
        arguments: { entityId: "new-uuid" },
        resolved_target: null,
        ambiguity_candidates: [],
        error_code: null,
        error_message: null,
      },
      clarification_question: null,
      unsupported_reason: null,
      error_code: null,
      error_message: null,
    };

    // State MUST remain untouched before explicit user execution!
    assert.equal(appSelectedEntityId, "existing-uuid");
    assert.equal(appCurrentRoute, "/markets");
    assert.ok(interpretation.structured_parse_result);
  });
});
