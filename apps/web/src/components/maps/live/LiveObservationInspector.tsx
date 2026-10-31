"use client";

import React, { useState } from "react";
import {
  X,
  Compass,
  Clock,
  ShieldCheck,
  AlertTriangle,
  Factory,
  Layers,
  ChevronRight,
  ExternalLink,
} from "lucide-react";
import { AtlasGeoObservation } from "@/lib/maps/live/types";
import {
  formatFreshnessAge,
  getDataClassBadge,
  getFreshnessBadge,
  getCategoryLabel,
} from "@/lib/maps/live/freshness";

interface LiveObservationInspectorProps {
  observation: AtlasGeoObservation;
  onClose: () => void;
  onCheckProximity: (obs: AtlasGeoObservation) => void;
}

export function LiveObservationInspector({
  observation,
  onClose,
  onCheckProximity,
}: LiveObservationInspectorProps) {
  const freshnessBadge = getFreshnessBadge(observation.freshness_state);
  const dataClassBadge = getDataClassBadge(observation.data_class);

  return (
    <div className="w-80 bg-zinc-950/95 border border-zinc-800 rounded-lg shadow-2xl backdrop-blur-md p-4 flex flex-col gap-3 font-mono text-xs text-zinc-300">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-zinc-800 pb-2.5">
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-1.5">
            <span
              className={`text-[9px] px-1.5 py-0.5 rounded border uppercase font-bold ${freshnessBadge.bg} ${freshnessBadge.text} ${freshnessBadge.border}`}
            >
              {freshnessBadge.label}
            </span>
            <span
              className={`text-[9px] px-1.5 py-0.5 rounded border uppercase font-semibold ${dataClassBadge.color}`}
            >
              {dataClassBadge.tag}
            </span>
          </div>
          <h4 className="font-bold text-zinc-100 text-sm truncate max-w-[210px] mt-1">
            {observation.entity_name || observation.entity_id}
          </h4>
          <span className="text-[10px] text-zinc-500">
            {getCategoryLabel(observation.category)} • Rev #{observation.source_revision}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Temporal Clocks Breakdown */}
      <div className="bg-zinc-900/60 border border-zinc-800/80 rounded p-2.5 flex flex-col gap-1.5 text-[11px]">
        <div className="flex items-center justify-between text-zinc-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-zinc-500" />
            Physical Measured:
          </span>
          <span className="text-zinc-200 font-semibold">
            {new Date(observation.observed_at).toLocaleTimeString()} (
            {formatFreshnessAge(observation.freshness_age_seconds)})
          </span>
        </div>
        {observation.source_published_at && (
          <div className="flex items-center justify-between text-zinc-500 text-[10px]">
            <span>Source Published:</span>
            <span>{new Date(observation.source_published_at).toLocaleTimeString()}</span>
          </div>
        )}
        <div className="flex items-center justify-between text-zinc-500 text-[10px]">
          <span>ATLAS Ingested:</span>
          <span>{new Date(observation.ingested_at).toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Spatial Telemetry */}
      <div className="grid grid-cols-2 gap-2 text-[11px] bg-zinc-900/30 border border-zinc-900 rounded p-2">
        <div>
          <span className="text-zinc-500 block text-[10px]">Longitude</span>
          <span className="text-zinc-200 font-semibold">{observation.longitude.toFixed(4)}°</span>
        </div>
        <div>
          <span className="text-zinc-500 block text-[10px]">Latitude</span>
          <span className="text-zinc-200 font-semibold">{observation.latitude.toFixed(4)}°</span>
        </div>
        {observation.altitude_m !== undefined && observation.altitude_m !== null && (
          <div>
            <span className="text-zinc-500 block text-[10px]">Altitude</span>
            <span className="text-zinc-200">{Math.round(observation.altitude_m)} m</span>
          </div>
        )}
        {observation.speed_mps !== undefined && observation.speed_mps !== null && (
          <div>
            <span className="text-zinc-500 block text-[10px]">Speed</span>
            <span className="text-zinc-200">
              {Math.round(observation.speed_mps * 3.6)} km/h
            </span>
          </div>
        )}
        {observation.heading_deg !== undefined && observation.heading_deg !== null && (
          <div className="col-span-2 flex items-center justify-between pt-1 border-t border-zinc-900">
            <span className="text-zinc-500 text-[10px]">Heading / True Track:</span>
            <span className="text-zinc-200 flex items-center gap-1">
              <Compass className="w-3 h-3 text-emerald-400" />
              {Math.round(observation.heading_deg)}°
            </span>
          </div>
        )}
      </div>

      {/* Category Specific Properties */}
      {observation.properties && Object.keys(observation.properties).length > 0 && (
        <div className="flex flex-col gap-1 border-t border-zinc-900 pt-2 text-[10px]">
          <span className="text-zinc-500 font-semibold uppercase">Telemetry Attributes</span>
          <div className="grid grid-cols-2 gap-x-2 gap-y-1 bg-zinc-900/20 p-1.5 rounded">
            {Object.entries(observation.properties)
              .filter(([k]) => k !== "revision_history")
              .slice(0, 6)
              .map(([key, value]) => (
                <div key={key} className="truncate">
                  <span className="text-zinc-500">{key}: </span>
                  <span className="text-zinc-300 font-medium">{String(value)}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Provenance & Attribution */}
      <div className="flex flex-col gap-0.5 text-[9px] text-zinc-500 border-t border-zinc-900 pt-1.5">
        <span className="truncate">Source: {observation.source_attribution}</span>
        {observation.provenance_note && (
          <span className="text-zinc-400 truncate">{observation.provenance_note}</span>
        )}
      </div>

      {/* Proximity Correlation Action Button */}
      <button
        onClick={() => onCheckProximity(observation)}
        className="mt-1 w-full flex items-center justify-center gap-2 px-3 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded transition-all font-semibold text-xs"
      >
        <Factory className="w-3.5 h-3.5" />
        <span>Correlate Infrastructure (Stage 133)</span>
        <ChevronRight className="w-3 h-3" />
      </button>
    </div>
  );
}

