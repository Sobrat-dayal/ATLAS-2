"use client";

import { useCallback } from "react";
import { useAuth } from "@/hooks/auth";
import { activityRecorder } from "@/lib/activity/activity-recorder";

export function useActivityRecorder() {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const recordModuleOpened = useCallback(
    (moduleId: string) => {
      activityRecorder.recordModuleOpened(moduleId, token);
    },
    [token]
  );

  const recordEntitySelected = useCallback(
    (entityId: string) => {
      activityRecorder.recordEntitySelected(entityId, token);
    },
    [token]
  );

  return {
    recordModuleOpened,
    recordEntitySelected,
  };
}
