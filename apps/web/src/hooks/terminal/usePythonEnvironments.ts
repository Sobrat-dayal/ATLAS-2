/**
 * React hook for inspecting approved Python sandbox environments.
 */

import { useCallback, useEffect, useState } from "react";
import { executionApi } from "@/lib/terminal/executionApi";
import type { PythonEnvironment } from "@/lib/terminal/executionTypes";

export function usePythonEnvironments() {
  const [environments, setEnvironments] = useState<PythonEnvironment[]>([]);
  const [selectedEnvId, setSelectedEnvId] = useState<string>("env_python_standard");
  const [isLoading, setIsLoading] = useState(false);

  const loadEnvironments = useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await executionApi.getPythonEnvironments();
      setEnvironments(list);
      if (list.length > 0 && !list.some((e) => e.environment_id === selectedEnvId)) {
        setSelectedEnvId(list[0].environment_id);
      }
    } catch {
      // Fallback baseline
      setEnvironments([
        {
          environment_id: "env_python_standard",
          name: "Python 3 Standard Financial Quantitative Sandbox",
          version: "1.0.0",
          python_version: "3.12",
          packages: { python: "3.12", numpy: "2.5.4", math: "built-in" },
          is_default: true,
          resource_profiles: ["standard_v1"],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedEnvId]);

  useEffect(() => {
    loadEnvironments();
  }, [loadEnvironments]);

  return {
    environments,
    selectedEnvId,
    setSelectedEnvId,
    isLoading,
  };
}

