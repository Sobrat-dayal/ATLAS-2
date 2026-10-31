"use client";

import React, { useState, useEffect } from "react";
import { SourceFreshnessRecord } from "@/lib/intelligence/v1/types";
import { fetchSourcesStatus } from "@/lib/intelligence/v1/api";
import {
  Database,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Power,
  RotateCcw
} from "lucide-react";

export function IntelligenceSourcesView() {
  const [sources, setSources] = useState<SourceFreshnessRecord[]>([]);
  const [loading, setLoading] = useState(false);

  const loadSources = () => {
    setLoading(true);
    fetchSourcesStatus()
      .then((data) => setSources(data))
      .catch((err) => console.error("Could not fetch sources:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadSources();
  }, []);

  const handleSimulateOutage = async (sourceId: string) => {
    try {
      await fetch(`/api/v1/intelligence/sources/${sourceId}/simulate-outage`, { method: "POST" });
      loadSources();
    } catch (err) {
      console.error("Outage simulation failed:", err);
    }
  };

  const handleRestoreSource = async (sourceId: string) => {
    try {
      await fetch(`/api/v1/intelligence/sources/${sourceId}/restore`, { method: "POST" });
      loadSources();
    } catch (err) {
      console.error("Restore failed:", err);
    }
  };

  return (
    <div className="h-full flex flex-col bg-black text-zinc-100 font-mono text-xs select-none p-4 space-y-4 overflow-y-auto">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-zinc-950 border border-zinc-800 rounded">
        <div>
          <div className="text-sm font-bold text-zinc-100 flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>DATA QUALITY, COVERAGE & SOURCE FRESHNESS TELEMETRY</span>
          </div>
          <div className="text-[11px] text-zinc-400 mt-0.5">
            Factual operational status of underlying regulatory, statistical, and sensor feeds.
          </div>
        </div>
        <button
          onClick={loadSources}
          disabled={loading}
          className="p-1.5 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
          title="Refresh source telemetry"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Telemetry Table */}
      <div className="overflow-x-auto border border-zinc-800 rounded bg-zinc-950">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-zinc-900 border-b border-zinc-800 text-zinc-400">
              <th className="p-3">DATASET & SOURCE</th>
              <th className="p-3">STATUS</th>
              <th className="p-3">EFFECTIVE DATE</th>
              <th className="p-3">COVERAGE</th>
              <th className="p-3">LICENSING</th>
              <th className="p-3 text-center">SIMULATE OUTAGE</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {sources.map((src) => {
              const isDegraded = src.status !== "READY";
              return (
                <tr key={src.source_id} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="p-3">
                    <div className="font-semibold text-zinc-200">{src.source_name}</div>
                    <div className="text-[10px] text-zinc-400 mt-0.5">{src.dataset}</div>
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        isDegraded
                          ? "bg-amber-950/40 border border-amber-800 text-amber-300"
                          : "bg-emerald-950/40 border border-emerald-800 text-emerald-400"
                      }`}
                    >
                      {src.status}
                    </span>
                  </td>
                  <td className="p-3 text-zinc-300">
                    {src.effective_data_date
                      ? new Date(src.effective_data_date).toLocaleTimeString()
                      : "Real-time stream"}
                  </td>
                  <td className="p-3 font-semibold text-zinc-200">
                    {src.coverage_percentage ? `${src.coverage_percentage}%` : "100.0%"}
                  </td>
                  <td className="p-3 text-zinc-400 text-[10px]">
                    {src.licensing_restriction || "STANDARD"}
                  </td>
                  <td className="p-3 text-center">
                    {isDegraded ? (
                      <button
                        onClick={() => handleRestoreSource(src.source_id)}
                        className="px-2.5 py-1 rounded bg-emerald-900/50 hover:bg-emerald-800 border border-emerald-700 text-emerald-200 text-[10px] flex items-center gap-1 mx-auto"
                      >
                        <RotateCcw className="w-3 h-3" />
                        <span>Restore Feed</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => handleSimulateOutage(src.source_id)}
                        className="px-2.5 py-1 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-400 hover:text-amber-400 text-[10px] flex items-center gap-1 mx-auto"
                        title="Simulate provider disconnection to verify partial failure handling"
                      >
                        <Power className="w-3 h-3" />
                        <span>Simulate Disconnect</span>
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
