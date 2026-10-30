/**
 * Selector dropdown for approved Python sandbox environments.
 */

import React from "react";
import type { PythonEnvironment } from "@/lib/terminal/executionTypes";
import { Cpu } from "lucide-react";

interface PythonEnvironmentSelectorProps {
  environments: PythonEnvironment[];
  selectedEnvId: string;
  onSelect: (envId: string) => void;
  disabled?: boolean;
}

export const PythonEnvironmentSelector: React.FC<PythonEnvironmentSelectorProps> = ({
  environments,
  selectedEnvId,
  onSelect,
  disabled = false,
}) => {
  return (
    <div className="flex items-center gap-1.5 text-xs font-mono">
      <Cpu className="w-3.5 h-3.5 text-blue-400" />
      <select
        value={selectedEnvId}
        onChange={(e) => onSelect(e.target.value)}
        disabled={disabled}
        className="bg-neutral-900 text-neutral-300 border border-neutral-800 rounded px-2 py-1 text-xs font-mono focus:outline-none focus:border-blue-500 cursor-pointer disabled:opacity-50"
      >
        {environments.map((env) => (
          <option key={env.environment_id} value={env.environment_id}>
            {env.name} (v{env.python_version})
          </option>
        ))}
      </select>
    </div>
  );
};
