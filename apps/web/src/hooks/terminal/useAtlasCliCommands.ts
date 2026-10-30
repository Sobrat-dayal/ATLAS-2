/**
 * React hook for accessing approved ATLAS CLI commands catalog and auto-suggestions.
 */

import { useCallback, useEffect, useState } from "react";
import { executionApi } from "@/lib/terminal/executionApi";
import type { CliCommandDef } from "@/lib/terminal/executionTypes";

export function useAtlasCliCommands() {
  const [commands, setCommands] = useState<CliCommandDef[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadCommands = useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await executionApi.getCliCommands();
      setCommands(list);
    } catch {
      // Fallback registered commands
      setCommands([
        {
          command_id: "cli.help",
          namespace: "atlas",
          name: "help",
          description: "Display documented syntax and capabilities for approved ATLAS CLI commands.",
          usage: "atlas help [command_name]",
          examples: ["atlas help", "atlas help workspace"],
          arguments_schema: [],
          mutability_class: "READ_ONLY",
        },
        {
          command_id: "cli.version",
          namespace: "atlas",
          name: "version",
          description: "Display authoritative ATLAS kernel build version.",
          usage: "atlas version [--json]",
          examples: ["atlas version"],
          arguments_schema: [],
          mutability_class: "READ_ONLY",
        },
        {
          command_id: "cli.status",
          namespace: "atlas",
          name: "status",
          description: "Inspect genuine system diagnostic state and connected services.",
          usage: "atlas status",
          examples: ["atlas status"],
          arguments_schema: [],
          mutability_class: "READ_ONLY",
        },
        {
          command_id: "cli.workspace",
          namespace: "atlas",
          name: "workspace",
          description: "List and inspect authorized user analytical workspace desks.",
          usage: "atlas workspace list",
          examples: ["atlas workspace list"],
          arguments_schema: [],
          mutability_class: "READ_ONLY",
        },
        {
          command_id: "cli.context",
          namespace: "atlas",
          name: "context",
          description: "Display active global workspace linking context.",
          usage: "atlas context show",
          examples: ["atlas context show"],
          arguments_schema: [],
          mutability_class: "READ_ONLY",
        },
        {
          command_id: "cli.instrument",
          namespace: "atlas",
          name: "instrument",
          description: "Inspect authoritative institutional master financial instrument records.",
          usage: "atlas instrument inspect <SYMBOL>",
          examples: ["atlas instrument inspect AAPL"],
          arguments_schema: [],
          mutability_class: "READ_ONLY",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCommands();
  }, [loadCommands]);

  const getSuggestions = useCallback(
    (input: string): CliCommandDef[] => {
      const clean = input.trim().toLowerCase();
      if (!clean) return [];
      const prefix = clean.startsWith("atlas ") ? clean.replace("atlas ", "") : clean;
      return commands.filter(
        (c) =>
          c.name.toLowerCase().startsWith(prefix) ||
          `atlas ${c.name}`.toLowerCase().startsWith(clean)
      );
    },
    [commands]
  );

  return {
    commands,
    isLoading,
    getSuggestions,
    reloadCommands: loadCommands,
  };
}
