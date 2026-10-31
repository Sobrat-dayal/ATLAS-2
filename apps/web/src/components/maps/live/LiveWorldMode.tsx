"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  AtlasGeoObservation,
  InfrastructureProximityMatch,
  LiveGeoProvider,
  LiveObservationCategory,
  LivePlaybackState,
} from "@/lib/maps/live/types";
import {
  fetchLiveProviders,
  fetchLiveSnapshot,
  fetchLivePlayback,
  correlateInfrastructureProximity,
} from "@/lib/maps/live/api";
import { LiveLayerPanel } from "./LiveLayerPanel";
import { LiveSourceStatusModal } from "./LiveSourceStatusModal";
import { LiveTimelinePlayback } from "./LiveTimelinePlayback";
import { LiveObservationInspector } from "./LiveObservationInspector";
import { LiveProximityPanel } from "./LiveProximityPanel";

interface LiveWorldModeProps {
  onSelectObservation?: (obs: AtlasGeoObservation) => void;
  onNavigateToCoordinates?: (lon: number, lat: number, zoom?: number) => void;
}

const DEFAULT_ACTIVE_CATEGORIES: Set<LiveObservationCategory> = new Set([
  "AIRCRAFT",
  "VESSEL",
  "SATELLITE",
  "WEATHER_ALERT",
  "EARTHQUAKE",
  "ACTIVE_FIRE",
]);

export function LiveWorldMode({
  onSelectObservation,
  onNavigateToCoordinates,
}: LiveWorldModeProps) {
  const [activeCategories, setActiveCategories] = useState<Set<LiveObservationCategory>>(
    DEFAULT_ACTIVE_CATEGORIES
  );
  const [providers, setProviders] = useState<LiveGeoProvider[]>([]);
  const [observations, setObservations] = useState<AtlasGeoObservation[]>([]);
  const [selectedObservation, setSelectedObservation] = useState<AtlasGeoObservation | null>(null);
  const [proximityMatches, setProximityMatches] = useState<InfrastructureProximityMatch[]>([]);
  const [isProximityOpen, setIsProximityOpen] = useState(false);
  const [isSourceStatusOpen, setIsSourceStatusOpen] = useState(false);
  const [playbackState, setPlaybackState] = useState<LivePlaybackState>({
    mode: "LIVE",
    playbackTimeUtc: "",
    speedMultiplier: 1,
    windowSeconds: 3600,
  });

  // Load providers on mount
  useEffect(() => {
    fetchLiveProviders()
      .then(setProviders)
      .catch((err) => console.warn("Failed to load live providers:", err));
  }, []);

  // Fetch observations based on active categories and mode
  const refreshObservations = useCallback(async () => {
    try {
      const cats = Array.from(activeCategories);
      if (cats.length === 0) {
        setObservations([]);
        return;
      }

      if (playbackState.mode === "HISTORICAL" && playbackState.playbackTimeUtc) {
        const res = await fetchLivePlayback(
          playbackState.playbackTimeUtc,
          cats,
          playbackState.windowSeconds
        );
        setObservations(res.observations);
      } else {
        const res = await fetchLiveSnapshot(cats);
        setObservations(res.observations);
      }
    } catch (err) {
      console.warn("Failed to refresh live observations:", err);
    }
  }, [activeCategories, playbackState]);

  useEffect(() => {
    refreshObservations();
    if (playbackState.mode === "LIVE") {
      const interval = setInterval(refreshObservations, 10000); // 10s poll cadence
      return () => clearInterval(interval);
    }
  }, [refreshObservations, playbackState.mode]);

  const handleToggleCategory = (cat: LiveObservationCategory) => {
    const next = new Set(activeCategories);
    if (next.has(cat)) {
      next.delete(cat);
    } else {
      next.add(cat);
    }
    setActiveCategories(next);
  };

  const handleSelectAll = () => {
    setActiveCategories(
      new Set([
        "AIRCRAFT",
        "VESSEL",
        "SATELLITE",
        "WEATHER_ALERT",
        "EARTHQUAKE",
        "ACTIVE_FIRE",
      ])
    );
  };

  const handleClearAll = () => {
    setActiveCategories(new Set());
  };

  const handleCheckProximity = async (obs: AtlasGeoObservation) => {
    try {
      const res = await correlateInfrastructureProximity(obs, 150);
      setProximityMatches(res.matches);
      setIsProximityOpen(true);
    } catch (err) {
      console.error("Proximity correlation failed:", err);
    }
  };

  // Group counts by category
  const countsByCategory = observations.reduce<Record<string, number>>((acc, obs) => {
    acc[obs.category] = (acc[obs.category] || 0) + 1;
    return acc;
  }, {});

  return (
    <>
      {/* Top Left: Layer Selector Panel */}
      <div className="absolute top-16 left-4 z-20">
        <LiveLayerPanel
          activeCategories={activeCategories}
          onToggleCategory={handleToggleCategory}
          onSelectAll={handleSelectAll}
          onClearAll={handleClearAll}
          countsByCategory={countsByCategory}
          onOpenSourceStatus={() => setIsSourceStatusOpen(true)}
        />
      </div>

      {/* Top Right: Observation Inspector & Proximity Panel */}
      <div className="absolute top-16 right-4 z-20 flex flex-col gap-3">
        {selectedObservation && (
          <LiveObservationInspector
            observation={selectedObservation}
            onClose={() => setSelectedObservation(null)}
            onCheckProximity={handleCheckProximity}
          />
        )}

        {isProximityOpen && (
          <LiveProximityPanel
            matches={proximityMatches}
            eventName={selectedObservation?.entity_name || "Active Event"}
            onClose={() => setIsProximityOpen(false)}
            onSelectFacility={(match) => {
              onNavigateToCoordinates?.(
                match.facility_coordinates[0],
                match.facility_coordinates[1],
                12
              );
            }}
          />
        )}
      </div>

      {/* Bottom Center: Timeline Playback Bar */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20">
        <LiveTimelinePlayback
          playbackState={playbackState}
          onModeChange={(mode) =>
            setPlaybackState((prev) => ({
              ...prev,
              mode,
              playbackTimeUtc: mode === "LIVE" ? "" : prev.playbackTimeUtc || new Date().toISOString(),
            }))
          }
          onTimeChange={(timeIso) =>
            setPlaybackState((prev) => ({ ...prev, playbackTimeUtc: timeIso }))
          }
          onSpeedChange={(speed) =>
            setPlaybackState((prev) => ({ ...prev, speedMultiplier: speed }))
          }
        />
      </div>

      {/* Source Status & Feed Health Modal */}
      <LiveSourceStatusModal
        isOpen={isSourceStatusOpen}
        onClose={() => setIsSourceStatusOpen(false)}
        providers={providers}
      />
    </>
  );
}

