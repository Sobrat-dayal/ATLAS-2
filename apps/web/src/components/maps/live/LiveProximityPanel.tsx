"use client";

import React from "react";
import { X, AlertTriangle, ShieldCheck, Factory, Navigation } from "lucide-react";
import { InfrastructureProximityMatch } from "@/lib/maps/live/types";

interface LiveProximityPanelProps {
  matches: InfrastructureProximityMatch[];
  eventName: string;
  onClose: () => void;
  onSelectFacility?: (match: InfrastructureProximityMatch) => void;
}

export function LiveProximityPanel({
  matches,
  eventName,
  onClose,
  onSelectFacility,
}: LiveProximityPanelProps) {
  return (
    <div className="w-84 bg-zinc-950/95 border border-zinc-800 rounded-lg shadow-2xl backdrop-blur-md p-4 flex flex-col gap-3 font-mono text-xs text-zinc-300">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-zinc-800 pb-2">
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-1.5">
            <Factory className="w-3.5 h-3.5 text-emerald-400" />
            <h4 className="font-bold text-zinc-100 text-xs tracking-wide uppercase">
              Infrastructure Proximity Correlation
            </h4>
          </div>
          <span className="text-[10px] text-zinc-500 truncate max-w-[240px]">
            Event: {eventName}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Mandatory Institutional Disclaimer Alert */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded p-2.5 flex items-start gap-2 text-[10px] text-amber-300">
        <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-amber-200">NON-PREDICTIVE DISCLAIMER: </strong>
          Spatial proximity does not constitute physical damage, structural failure, or operational outage.
          On-site telemetry or official engineering inspection required.
        </p>
      </div>

      {/* Matches List */}
      <div className="flex flex-col gap-2 max-h-60 overflow-y-auto pr-1">
        {matches.length === 0 ? (
          <div className="text-center py-4 text-zinc-500 text-[11px]">
            No verified infrastructure assets within search radius.
          </div>
        ) : (
          matches.map((m) => (
            <div
              key={m.facility_id}
              onClick={() => onSelectFacility?.(m)}
              className="bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700 rounded p-2.5 flex flex-col gap-1.5 cursor-pointer transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-zinc-100 text-[11px] truncate max-w-[170px]">
                  {m.facility_name}
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-emerald-400 font-bold">
                  {m.distance_km} km
                </span>
              </div>

              <div className="flex items-center justify-between text-[10px] text-zinc-400">
                <span className="text-zinc-500">Sector: {m.facility_sector}</span>
                <span className="text-[9px] px-1 py-0.5 bg-zinc-950 border border-zinc-800 rounded text-zinc-400">
                  {m.damage_assessment}
                </span>
              </div>

              {m.inside_alert_perimeter && (
                <div className="text-[9px] text-rose-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                  Inside Alert Perimeter
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Status Footer */}
      <div className="border-t border-zinc-900 pt-2 flex items-center justify-between text-[10px] text-zinc-500">
        <span>Damage Confirmed:</span>
        <span className="text-zinc-400 font-semibold">FALSE (Unverified)</span>
      </div>
    </div>
  );
}
