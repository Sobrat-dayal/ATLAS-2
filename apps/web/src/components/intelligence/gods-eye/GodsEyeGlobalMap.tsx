"use client";

import React, { useState, useEffect } from "react";
import {
  GodsEyeMapFeature,
  GodsEyeViewMode,
  GodsEyeDamageAssessmentStatus,
} from "@/lib/intelligence/gods-eye/types";
import {
  Globe,
  MapPin,
  Anchor,
  Building2,
  Flame,
  Radio,
  Layers,
  AlertTriangle,
  Info,
  Maximize2,
  Minimize2,
} from "lucide-react";

interface GodsEyeGlobalMapProps {
  features: GodsEyeMapFeature[];
  viewMode: GodsEyeViewMode;
  selectedFeatureId?: string | null;
  onSelectFeature: (feature: GodsEyeMapFeature) => void;
  disclaimerText?: string;
}

export function GodsEyeGlobalMap({
  features,
  viewMode,
  selectedFeatureId,
  onSelectFeature,
  disclaimerText,
}: GodsEyeGlobalMapProps) {
  const [activeLayerFilter, setActiveLayerFilter] = useState<string>("ALL");
  const [zoomLevel, setZoomLevel] = useState<number>(2);

  // Simulated cleanup for WebGL resources on unmount / mode transition (Fixture R)
  useEffect(() => {
    return () => {
      // Release any WebGL or Cesium contexts gracefully
    };
  }, [viewMode]);

  const filteredFeatures = features.filter((f) => {
    if (activeLayerFilter === "ALL") return true;
    if (activeLayerFilter === "FACILITIES") return f.feature_type === "FACILITY";
    if (activeLayerFilter === "PORTS") return f.feature_type === "PORT";
    if (activeLayerFilter === "HAZARDS") return f.feature_type === "EVENT_EPICENTER" || f.feature_type === "HAZARD_PERIMETER";
    return true;
  });

  const getDamageBadge = (status: GodsEyeDamageAssessmentStatus) => {
    switch (status) {
      case "CONFIRMED_OPERATIONAL":
        return <span className="px-1.5 py-0.5 rounded text-[9px] bg-emerald-950/80 border border-emerald-700 text-emerald-400 font-semibold">OPERATIONAL</span>;
      case "REPORTED_DISRUPTED":
        return <span className="px-1.5 py-0.5 rounded text-[9px] bg-amber-950/80 border border-amber-700 text-amber-400 font-semibold">DISRUPTED</span>;
      case "CONFIRMED_DAMAGED":
      case "DESTROYED":
        return <span className="px-1.5 py-0.5 rounded text-[9px] bg-rose-950/80 border border-rose-700 text-rose-400 font-semibold">DAMAGED</span>;
      case "UNKNOWN":
      default:
        return (
          <span
            className="px-1.5 py-0.5 rounded text-[9px] bg-zinc-800 border border-zinc-600 text-zinc-300 font-semibold flex items-center gap-1"
            title="Spatial proximity does not imply damage; status is UNKNOWN until verified"
          >
            <span>STATUS: UNKNOWN</span>
            <span className="text-amber-400 font-bold">?</span>
          </span>
        );
    }
  };

  const getFeatureIcon = (type: string) => {
    switch (type) {
      case "PORT":
        return <Anchor className="w-3.5 h-3.5 text-sky-400" />;
      case "FACILITY":
        return <Building2 className="w-3.5 h-3.5 text-amber-400" />;
      case "EVENT_EPICENTER":
        return <Flame className="w-3.5 h-3.5 text-rose-500 animate-pulse" />;
      default:
        return <MapPin className="w-3.5 h-3.5 text-emerald-400" />;
    }
  };

  return (
    <div className="relative w-full h-full bg-zinc-950 overflow-hidden flex flex-col font-mono text-xs select-none">
      {/* Top Map HUD: Layer Controls & Mode Indicator */}
      <div className="absolute top-2 left-2 z-10 flex items-center gap-1.5 bg-zinc-900/90 backdrop-blur border border-zinc-800 p-1 rounded shadow">
        <span className="text-[10px] text-zinc-400 font-semibold px-1">LAYERS:</span>
        {(["ALL", "FACILITIES", "PORTS", "HAZARDS"] as const).map((layer) => (
          <button
            key={layer}
            onClick={() => setActiveLayerFilter(layer)}
            className={`px-2 py-0.5 rounded text-[10px] transition-colors ${
              activeLayerFilter === layer
                ? "bg-amber-600 text-white font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {layer}
          </button>
        ))}
      </div>

      <div className="absolute top-2 right-2 z-10 flex items-center gap-2 bg-zinc-900/90 backdrop-blur border border-zinc-800 px-2 py-1 rounded shadow text-[10px] text-zinc-300">
        <span className="text-zinc-500">ENGINE:</span>
        <span className="font-bold text-sky-400">
          {viewMode === "THREE_DIMENSIONAL_GLOBE" ? "CESIUMJS 3D GLOBE" : "MAPLIBRE 2D"}
        </span>
      </div>

      {/* Main Map Canvas Area */}
      <div className="flex-1 w-full h-full relative overflow-hidden bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-zinc-900 via-zinc-950 to-black flex items-center justify-center p-4">
        {/* Subtle grid pattern background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#27272a_1px,transparent_1px),linear-gradient(to_bottom,#27272a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-20" />

        {/* World Map Representation & Placed Feature Cards */}
        <div className="w-full max-w-4xl h-full flex flex-col justify-between z-0 relative">
          <div className="text-center py-2">
            <span className="text-[11px] text-zinc-500 uppercase tracking-widest">
              Global Financial Situational Awareness Grid
            </span>
          </div>

          {/* Interactive Feature Markers Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 p-2 overflow-y-auto max-h-[70vh]">
            {filteredFeatures.map((feat) => {
              const isSelected = selectedFeatureId === feat.id;
              return (
                <div
                  key={feat.id}
                  onClick={() => onSelectFeature(feat)}
                  className={`p-3 rounded border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-zinc-900 border-amber-500 ring-1 ring-amber-500/50 shadow-lg shadow-amber-950/40"
                      : "bg-zinc-900/80 hover:bg-zinc-850 border-zinc-800 hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-1.5">
                      {getFeatureIcon(feat.feature_type)}
                      <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-semibold">
                        {feat.feature_type.replace("_", " ")}
                      </span>
                    </div>
                    {getDamageBadge(feat.damage_status)}
                  </div>

                  <div className="text-xs font-semibold text-zinc-100 mb-1 leading-snug">
                    {feat.name}
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-zinc-400 mt-2 pt-2 border-t border-zinc-800/80">
                    <span>
                      Coords: [{feat.coordinates[0]?.toFixed(2)}, {feat.coordinates[1]?.toFixed(2)}]
                    </span>
                    {feat.properties?.distance_to_epicenter_km && (
                      <span className="text-amber-400 font-bold">
                        {feat.properties.distance_to_epicenter_km} km to epicenter
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Map Disclaimer Bar (Proximity != Damage) */}
          <div className="bg-zinc-950/90 border border-zinc-800 p-2 rounded text-[10px] text-zinc-400 flex items-center gap-2">
            <Info className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span className="truncate">
              {disclaimerText || "Spatial proximity to a physical hazard does not imply confirmed structural damage or business interruption."}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

