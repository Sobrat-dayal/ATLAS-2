"use client";

/**
 * React Hook for Historical Chart Replay V1 in ATLAS (Stage 75).
 *
 * Exposes:
 * - Reactive replay session state and revealed historical bars
 * - Playback controls (play, pause, step forward, step backward, restart, seek, speed)
 * - Single-panel replay isolation helpers
 * - Clean teardown and safe normal-mode restoration
 */

import { useCallback, useEffect, useState } from "react";
import {
  replayStore,
  ReplayStoreState,
  ReplayStartRequest,
  ReplaySeekRequest,
  ReplaySpeed,
} from "@/lib/charts/replay";

export function useChartReplay() {
  const [state, setState] = useState<ReplayStoreState>(() =>
    replayStore.getState()
  );

  useEffect(() => {
    const unsubscribe = replayStore.subscribe(() => {
      setState(replayStore.getState());
    });
    return unsubscribe;
  }, []);

  const isPanelInReplay = useCallback(
    (panelId: string): boolean => {
      return replayStore.isPanelInReplay(panelId);
    },
    []
  );

  const startReplay = useCallback(
    async (request: ReplayStartRequest) => {
      await replayStore.startReplay(request);
    },
    []
  );

  const play = useCallback(() => {
    replayStore.play();
  }, []);

  const pause = useCallback(() => {
    replayStore.pause();
  }, []);

  const stepForward = useCallback(async () => {
    await replayStore.stepForward();
  }, []);

  const stepBackward = useCallback(async () => {
    await replayStore.stepBackward();
  }, []);

  const restart = useCallback(async () => {
    await replayStore.restart();
  }, []);

  const seek = useCallback(async (request: ReplaySeekRequest) => {
    await replayStore.seek(request);
  }, []);

  const setSpeed = useCallback((speed: ReplaySpeed) => {
    replayStore.setSpeed(speed);
  }, []);

  const exitReplay = useCallback(async () => {
    await replayStore.exitReplay();
  }, []);

  return {
    ...state,
    isPanelInReplay,
    startReplay,
    play,
    pause,
    stepForward,
    stepBackward,
    restart,
    seek,
    setSpeed,
    exitReplay,
  };
}
