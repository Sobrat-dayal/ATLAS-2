"use client";

import React, { useState } from "react";
import { Globe, AlertTriangle, Building2, Radio, ShieldCheck, MapPin, Layers } from "lucide-react";

interface IntelligenceGeographyViewProps {
  initialEventId?: string;
  onNavigateToView: (view: string, entityOrEventId?: string) => void;
}

export function IntelligenceGeographyView({
  initialEventId,
  onNavigateToView
}: IntelligenceGeographyViewProps) {
  const [selectedLayer, setSelectedLayer] = useState<"ALL" | "EVENTS" | "FACILITIES" | "INFRASTRUCTURE">("ALL");

  return (
    <div className="h-full flex flex-col bg-black text-zinc-100 font-mono text-xs select-none">
      {/* Top Filter & Layer Bar */}
      <div className="p-3 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-zinc-500 uppercase text-[10px] font-semibold tracking-wider">
            GEOSPATIAL LAYERS:
          </span>
          <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 p-0.5 rounded">
            {(["ALL", "EVENTS", "FACILITIES", "INFRASTRUCTURE"] as const).map((layer) => (
              <button
                key={layer}
                onClick={() => setSelectedLayer(layer)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  selectedLayer === layer
                    ? "bg-emerald-600 text-white font-bold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {layer}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <a
            href="/maps"
            className="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 flex items-center gap-1.5"
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span>Open in /maps (2D/3D Engine)</span>
          </a>
        </div>
      </div>

      {/* Main Map Presentation Workspace */}
      <div className="flex-1 p-4 grid grid-cols-1 md:grid-cols-3 gap-4 overflow-y-auto">
        {/* Interactive Co-location Demonstration Canvas */}
        <div className="md:col-span-2 bg-zinc-950 border border-zinc-800 rounded p-4 flex flex-col justify-between relative overflow-hidden">
          {/* Mock Spatial Grid Canvas Visual */}
          <div className="absolute inset-0 opacity-10 pointer-events-none bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:16px_16px]" />

          <div className="relative z-10 space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
              <div className="flex items-center gap-2 font-bold text-zinc-100">
                <Globe className="w-4 h-4 text-emerald-400" />
                <span>CO-LOCATED ASSET & EVENT TOPOLOGY (MIYAGI PREFECTURE)</span>
              </div>
              <span className="text-[10px] text-zinc-400">EPSG:4326 WGS84</span>
            </div>

            {/* Event & Asset Card */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              {/* Event Locus */}
              <div className="p-3 rounded bg-zinc-900/80 border border-rose-900/40 space-y-1.5">
                <div className="flex items-center gap-1.5 text-rose-400 font-bold">
                  <Radio className="w-3.5 h-3.5" />
                  <span>MAGNITUDE 7.1 OFFSHORE QUAKE</span>
                </div>
                <div className="text-[11px] text-zinc-300">
                  Coordinates: 38.297° N, 142.372° E
                </div>
                <div className="text-[10px] text-zinc-500">
                  Depth: 35.0 km • Source: USGS Sensor Network
                </div>
              </div>

              {/* Verified Facility */}
              <div className="p-3 rounded bg-zinc-900/80 border border-sky-900/40 space-y-1.5">
                <div className="flex items-center gap-1.5 text-sky-400 font-bold">
                  <Building2 className="w-3.5 h-3.5" />
                  <span>MIYAGI PRECISION ASSEMBLY PLANT</span>
                </div>
                <div className="text-[11px] text-zinc-300">
                  Coordinates: 38.268° N, 140.869° E
                </div>
                <div className="text-[10px] text-zinc-500">
                  Operator: Acme Global Corp • Distance: 25.0 km
                </div>
              </div>
            </div>

            {/* Proximity Metric Banner */}
            <div className="p-3 rounded bg-zinc-900/60 border border-zinc-800 flex items-center justify-between">
              <span className="text-zinc-400">MEASURED GREAT-CIRCLE DISTANCE:</span>
              <span className="text-sm font-bold text-zinc-100">25.0 km (Threshold: 50.0 km)</span>
            </div>
          </div>

          {/* Mandatory Proximity vs Loss Invariant Disclaimer */}
          <div className="relative z-10 mt-4 p-3 bg-amber-950/20 border border-amber-800/80 rounded flex items-start gap-2.5 text-amber-300">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-[11px] leading-relaxed">
              <span className="font-bold uppercase tracking-wider block">PHYSICAL PROXIMITY SCOPE BOUNDARY</span>
              Geographic proximity confirms spatial co-location only. Operational interruption, structural asset damage, and financial losses are strictly UNKNOWN and cannot be inferred from distance.
            </div>
          </div>
        </div>

        {/* Spatial Properties & Actions Panel */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-4 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="font-bold text-zinc-100 border-b border-zinc-800 pb-2">
              ASSOCIATED RELATIONSHIPS
            </div>
            <div className="space-y-2 text-[11px]">
              <div className="p-2 rounded bg-zinc-900/60 border border-zinc-800 space-y-1">
                <span className="text-[10px] text-zinc-500 block">PRIMARY ASSET OPERATOR</span>
                <span className="font-semibold text-zinc-200">Acme Global Corporation</span>
              </div>
              <div className="p-2 rounded bg-zinc-900/60 border border-zinc-800 space-y-1">
                <span className="text-[10px] text-zinc-500 block">JURISDICTION & PREFECTURE</span>
                <span className="font-semibold text-zinc-200">Miyagi Prefecture, Japan</span>
              </div>
              <div className="p-2 rounded bg-zinc-900/60 border border-zinc-800 space-y-1">
                <span className="text-[10px] text-zinc-500 block">INFRASTRUCTURE CATEGORY</span>
                <span className="font-semibold text-zinc-200">Precision Electronics Manufacturing</span>
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-4 border-t border-zinc-800">
            <button
              onClick={() => onNavigateToView("GRAPH")}
              className="w-full py-2 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-sky-400 font-bold"
            >
              Open in Knowledge Graph →
            </button>
            <button
              onClick={() => onNavigateToView("EXPOSURE")}
              className="w-full py-2 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-amber-400 font-bold"
            >
              Inspect Company Exposure →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
