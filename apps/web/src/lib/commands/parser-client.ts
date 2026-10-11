import type { AtlasCommandParseResult } from "./types";

export interface ParseAtlasCommandOptions {
  text: string;
  signal?: AbortSignal;
}

/**
 * Invokes the backend deterministic command parsing endpoint: POST /api/v1/commands/parse.
 * Side-effect free, read-only.
 */
export async function parseAtlasCommand(
  options: ParseAtlasCommandOptions
): Promise<AtlasCommandParseResult> {
  const { text, signal } = options;
  const trimmed = text.trim();
  if (!trimmed) {
    return {
      command_language_version: 1,
      status: "INVALID",
      normalized_command: "",
      error_code: "NOT_STRUCTURED_COMMAND",
      error_message: "Command text is empty.",
    };
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const res = await fetch(`${apiUrl}/api/v1/commands/parse`, {
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
        command_language_version: 1,
        status: "INVALID",
        normalized_command: trimmed,
        error_code: "COMMAND_FORBIDDEN",
        error_message: "Access to command parser is not authorized.",
      };
    }
    throw new Error(`Command parse request failed with HTTP status ${res.status}`);
  }

  const data = (await res.json()) as AtlasCommandParseResult;
  return data;
}
