import type { NaturalLanguageCommandInterpretation } from "./interpreter-types";

export interface InterpretAtlasCommandOptions {
  text: string;
  signal?: AbortSignal;
}

/**
 * Invokes the backend natural language command interpretation endpoint:
 * POST /api/v1/commands/interpret.
 * Single-turn, side-effect free, read-only.
 */
export async function interpretAtlasCommand(
  options: InterpretAtlasCommandOptions
): Promise<NaturalLanguageCommandInterpretation> {
  const { text, signal } = options;
  const trimmed = text.trim();
  if (!trimmed) {
    return {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "NOT_COMMAND",
      input_fingerprint: "",
      error_message: "Input text is empty.",
    };
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  try {
    const res = await fetch(`${apiUrl}/api/v1/commands/interpret`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ text: trimmed }),
      signal,
    });

    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        return {
          interpreter_version: 1,
          prompt_version: 1,
          model_output_schema_version: 1,
          status: "INVALID_MODEL_OUTPUT",
          input_fingerprint: "",
          error_code: "COMMAND_FORBIDDEN",
          error_message: "Access to command interpretation is forbidden.",
        };
      }

      return {
        interpreter_version: 1,
        prompt_version: 1,
        model_output_schema_version: 1,
        status: "INTERPRETER_UNAVAILABLE",
        input_fingerprint: "",
        error_code: "INTERPRETER_UNAVAILABLE",
        error_message: "Natural-language interpretation is temporarily unavailable.",
      };
    }

    const data = (await res.json()) as NaturalLanguageCommandInterpretation;
    return data;
  } catch (err: unknown) {
    if (err instanceof Error && err.name === "AbortError") {
      throw err;
    }
    return {
      interpreter_version: 1,
      prompt_version: 1,
      model_output_schema_version: 1,
      status: "INTERPRETER_UNAVAILABLE",
      input_fingerprint: "",
      error_code: "NETWORK_ERROR",
      error_message: "Failed to connect to command interpretation endpoint.",
    };
  }
}
