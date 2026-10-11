import type {
  CommandDefinition,
  CommandContext,
  CommandExecutionHelpers,
} from "./types";

export class CommandExecutionError extends Error {
  public readonly commandId: string;

  constructor(commandId: string, message: string, cause?: unknown) {
    super(`Failed to execute command "${commandId}": ${message}`);
    this.name = "CommandExecutionError";
    this.commandId = commandId;
    if (cause) {
      this.cause = cause;
    }
  }
}

/**
 * Executes a command within the provided context and helpers.
 * Checks availability and ensures safe execution without leaking stack traces.
 */
export async function executeCommand(
  command: CommandDefinition,
  context: CommandContext,
  helpers: CommandExecutionHelpers,
  args?: Record<string, unknown>
): Promise<boolean> {
  // Check availability
  if (command.availability) {
    const status = command.availability(context);
    if (status === "disabled" || status === "hidden") {
      return false;
    }
  }

  try {
    await Promise.resolve(command.execute(context, helpers, args));
    // Execution succeeded: close palette by default unless helper explicitly handled it
    helpers.closePalette();
    return true;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "An unexpected error occurred.";
    console.error(`[CommandExecutor] Command ${command.id} error:`, message);
    throw new CommandExecutionError(command.id, message, err);
  }
}
