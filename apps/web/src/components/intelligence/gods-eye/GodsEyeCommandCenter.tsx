"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  GodsEyeInvestigationResult,
  GodsEyeLensType,
  GodsEyeMapFeature,
  GodsEyeViewMode,
} from "@/lib/intelligence/gods-eye/types";
import { fetchGodsEyeInvestigation } from "@/lib/intelligence/gods-eye/api";
import { GodsEyeToolbar } from "./GodsEyeToolbar";
import { GodsEyeGlobalMap } from "./GodsEyeGlobalMap";
import { GodsEyeEventFeed } from "./GodsEyeEventFeed";
import { GodsEyeInspector } from "./GodsEyeInspector";
import { AlertCircle, RefreshCw } from "lucide-react";

export function GodsEyeCommandCenter() {
  const [activeLens, setActiveLens] = useState<GodsEyeLensType>("GLOBAL_EVENTS");
  const [viewMode, setViewMode] = useState<GodsEyeViewMode>("TWO_DIMENSIONAL");
  const [asOfDate, setAsOfDate] = useState<string | null>(null);
  const [entityFilter, setEntityFilter] = useState<string>("");
  const [selectedFeature, setSelectedFeature] = useState<GodsEyeMapFeature | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const [investigation, setInvestigation] = useState<GodsEyeInvestigationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadInvestigation = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetchGodsEyeInvestigation({
        lens: activeLens,
        as_of: asOfDate,
        selected_entity_id: entityFilter.trim() ? entityFilter.trim() : null,
        view_mode: viewMode,
      });
      setInvestigation(res);
      // Select first feature by default if available
      if (res.map_features && res.map_features.length > 0) {
        setSelectedFeature(res.map_features[0]);
      } else {
        setSelectedFeature(null);
      }
      if (res.events && res.events.length > 0) {
        setSelectedEventId(res.events[0].event_id);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load God's Eye situational intelligence.");
    } finally {
      setIsLoading(false);
    }
  }, [activeLens, asOfDate, entityFilter, viewMode]);

  useEffect(() => {
    loadInvestigation();
  }, [loadInvestigation]);

  return (
    <div className="flex h-full flex-col bg-black text-zinc-100 overflow-hidden font-mono text-xs select-none">
      {/* Top Toolbar */}
      <GodsEyeToolbar
        activeLens={activeLens}
        onSelectLens={(lens) => {
          setActiveLens(lens);
          setSelectedFeature(null);
          setSelectedEventId(null);
        }}
        viewMode={viewMode}
        onSelectViewMode={setViewMode}
        asOfDate={asOfDate}
        onChangeAsOfDate={setAsOfDate}
        entityFilter={entityFilter}
        onChangeEntityFilter={setEntityFilter}
        onRefresh={loadInvestigation}
        isLoading={isLoading}
      />

      {/* Main Viewport */}
      {error ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-zinc-950">
          <AlertCircle className="w-8 h-8 text-rose-500 mb-2" />
          <div className="text-sm font-semibold text-zinc-200 mb-1">
            Situational Query Failed
          </div>
          <div className="text-xs text-zinc-400 max-w-md mb-4">{error}</div>
          <button
            onClick={loadInvestigation}
            className="px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Query</span>
          </button>
        </div>
      ) : (
        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
          {/* Left/Center: Interactive Map Canvas */}
          <div className="flex-1 h-1/2 lg:h-full relative overflow-hidden">
            <GodsEyeGlobalMap
              features={investigation?.map_features || []}
              viewMode={viewMode}
              selectedFeatureId={selectedFeature?.id}
              onSelectFeature={(feat) => setSelectedFeature(feat)}
              disclaimerText={investigation?.disclaimers?.damage}
            />
          </div>

          {/* Right/Bottom Sidecars: Event Feed & Situational Inspector */}
          <div className="w-full lg:w-[480px] xl:w-[540px] h-1/2 lg:h-full flex flex-col sm:flex-row divide-y sm:divide-y-0 sm:divide-x divide-zinc-800 bg-zinc-950 border-t lg:border-t-0 border-zinc-800">
            {/* Prioritized Event Feed */}
            <div className="w-full sm:w-1/2 h-full overflow-hidden">
              <GodsEyeEventFeed
                events={investigation?.events || []}
                selectedEventId={selectedEventId}
                onSelectEvent={(id) => setSelectedEventId(id)}
                disclaimerText={investigation?.disclaimers?.priority}
              />
            </div>

            {/* Deep Situational Inspector */}
            <div className="w-full sm:w-1/2 h-full overflow-hidden">
              <GodsEyeInspector
                investigation={investigation}
                selectedFeature={selectedFeature}
                selectedEventId={selectedEventId}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

