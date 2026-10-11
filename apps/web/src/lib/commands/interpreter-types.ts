import type { AtlasCommandParseResult } from "./types";

export type NaturalLanguageCommandIntent =
  | "NAVIGATE_MODULE"
  | "OPEN_ENTITY_IN_MODULE"
  | "OPEN_GLOBAL_SETTINGS"
  | "FOCUS_ENTITY_SEARCH"
  | "CLEAR_SELECTED_ENTITY"
  | "AMBIGUOUS"
  | "NOT_COMMAND"
  | "UNSUPPORTED_ACTION";

export type UnsupportedActionReason =
  | "TRADING_ACTION"
  | "BROKER_ACTION"
  | "PORTFOLIO_ACTION"
  | "RISK_ACTION"
  | "AGENT_ACTION"
  | "WORKFLOW_ACTION"
  | "TERMINAL_ACTION"
  | "SYSTEM_ACTION"
  | "EXTERNAL_ACTION"
  | "MULTI_COMMAND"
  | "OTHER_UNSUPPORTED";

export type NaturalLanguageCommandInterpretationStatus =
  | "READY"
  | "AMBIGUOUS"
  | "NOT_COMMAND"
  | "UNSUPPORTED"
  | "INVALID_MODEL_OUTPUT"
  | "INTERPRETER_UNAVAILABLE";

export interface NaturalLanguageCommandInterpretRequest {
  text: string;
}

export interface NaturalLanguageCommandInterpretation {
  interpreter_version: number;
  prompt_version: number;
  model_output_schema_version: number;
  status: NaturalLanguageCommandInterpretationStatus;
  input_fingerprint: string;
  intent?: NaturalLanguageCommandIntent | null;
  module?: string | null;
  target_text?: string | null;
  canonical_command?: string | null;
  structured_parse_result?: AtlasCommandParseResult | null;
  clarification_question?: string | null;
  unsupported_reason?: UnsupportedActionReason | null;
  error_code?: string | null;
  error_message?: string | null;
}
