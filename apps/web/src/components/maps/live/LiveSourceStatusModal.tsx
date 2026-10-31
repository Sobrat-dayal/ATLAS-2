"use client";

import React from "react";
import { X, ExternalLink, Activity, ShieldCheck, AlertCircle } from "lucide-react";
import { LiveGeoProvider } from "@/lib/maps/live/types";
import { getProviderStatusBadge } from "@/lib/maps/live/freshness";

interface LiveSourceStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  providers: LiveGeoProvider[];
}

export function LiveSourceStatusModal({
  isOpen,
  onClose,
  providers,
}: LiveSourceStatusModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-xl shadow-2xl overflow-hidden font-mono text-zinc-300">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 bg-zinc-900/60">
          <div className="flex items-center gap-2.5">
            <Activity className="w-4 h-4 text-emerald-400" />
            <h3 className="font-semibold text-zinc-100 text-sm tracking-wide uppercase">
              Live Geospatial Source Registry & Provider Status
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 flex flex-col gap-3.5 max-h-[70vh] overflow-y-auto">
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-3 text-[11px] text-zinc-400 flex items-start gap-2.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
            <p>
              ATLAS strictly enforces institutional data authenticity. When external
              provider API credentials are not configured or access is restricted, feeds
              report authentic unconfigured or degraded states. Simulated records are
              never injected into production.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-2.5">
            {providers.map((p) => {
              const statusBadge = getProviderStatusBadge(p.status);

              return (
                <div
                  key={p.provider_id}
                  className="bg-zinc-900/50 border border-zinc-800/70 rounded-lg p-3.5 flex flex-col gap-2 hover:border-zinc-700/80 transition-all text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${statusBadge.dotColor}`} />
                      <span className="font-medium text-zinc-200">{p.name}</span>
                      <span className="text-[10px] text-zinc-500">[{p.provider_id}]</span>
                    </div>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded border border-zinc-800 bg-zinc-950/80 ${statusBadge.color}`}
                    >
                      {statusBadge.label}
                    </span>
                  </div>

                  {p.status_reason && (
                    <div className="flex items-center gap-2 text-[11px] text-amber-400/90 bg-amber-500/10 border border-amber-500/20 px-2 py-1 rounded">
                      <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                      <span>{p.status_reason}</span>
                    </div>
                  )}

                  <div className="grid grid-cols-3 gap-2 text-[11px] text-zinc-400 pt-1 border-t border-zinc-800/50">
                    <div>
                      <span className="text-zinc-500">Nominal Latency: </span>
                      <span className="text-zinc-300">{p.nominal_latency_seconds}s</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">TTL Window: </span>
                      <span className="text-zinc-300">{p.ttl_seconds}s</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Auth Required: </span>
                      <span className="text-zinc-300">{p.requires_auth ? "Yes (API Key)" : "Public Domain"}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-1">
                    <span className="truncate max-w-[80%]">{p.attribution}</span>
                    {p.endpoint_url && (
                      <a
                        href={p.endpoint_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-zinc-400 hover:text-emerald-400 flex items-center gap-1 transition-colors"
                      >
                        Docs <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-zinc-800 bg-zinc-900/40 flex items-center justify-between text-xs text-zinc-500">
          <span>Clock Baseline: UTC Physical (observed_at)</span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded transition-colors text-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

