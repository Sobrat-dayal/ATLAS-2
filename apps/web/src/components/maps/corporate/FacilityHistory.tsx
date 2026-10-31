"use client";

import React from "react";
import { X, Clock, Calendar, ShieldCheck } from "lucide-react";
import { CorporateFacility } from "@/lib/maps/corporate/types";
import { FACILITY_STATUS_STYLES } from "@/lib/maps/corporate/facilityStyles";

interface FacilityHistoryProps {
  facility: CorporateFacility;
  onClose: () => void;
}

export function FacilityHistory({ facility, onClose }: FacilityHistoryProps) {
  const history = facility.status_history || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg max-w-lg w-full max-h-[80vh] flex flex-col shadow-2xl text-xs text-zinc-300 overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-sky-400" />
            <div>
              <h3 className="font-bold text-zinc-100 text-sm">Operational Status Timeline</h3>
              <p className="text-[10px] text-zinc-500">{facility.canonical_name}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Timeline List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {history.length === 0 ? (
            <div className="p-8 text-center text-zinc-500">
              <Clock className="w-8 h-8 mx-auto text-zinc-700 mb-2 opacity-50" />
              <p>Current Status: {facility.facility_status}</p>
              <p className="text-[10px] mt-1 text-zinc-600">No prior historical revisions recorded.</p>
            </div>
          ) : (
            <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-zinc-800">
              {history.map((entry) => {
                const statusStyle = FACILITY_STATUS_STYLES[entry.status];
                return (
                  <div key={entry.history_id} className="relative">
                    {/* Timeline bullet */}
                    <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-sky-500 border-2 border-zinc-950" />

                    <div className="p-3 bg-zinc-900/70 border border-zinc-800 rounded-md space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border ${
                            statusStyle?.border || "border-zinc-700"
                          } ${statusStyle?.bg || "bg-zinc-900"} ${statusStyle?.text || "text-zinc-300"}`}
                        >
                          {statusStyle?.label || entry.status}
                        </span>

                        <span className="text-[10px] text-zinc-500 font-mono flex items-center gap-1">
                          <Calendar className="w-2.5 h-2.5" />
                          <span>
                            {entry.valid_from ? entry.valid_from.split("T")[0] : "Inception"} &rarr;{" "}
                            {entry.valid_to ? entry.valid_to.split("T")[0] : "Present"}
                          </span>
                        </span>
                      </div>

                      {entry.source_manifest_id && (
                        <div className="text-[10px] text-zinc-500 flex items-center justify-between pt-1 border-t border-zinc-800/60">
                          <span>Source Manifest:</span>
                          <span className="font-mono text-zinc-400">{entry.source_manifest_id}</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-zinc-800 bg-zinc-900/60 flex items-center justify-between text-[10px] text-zinc-500">
          <span>Bitemporal Point-In-Time Revisions</span>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

