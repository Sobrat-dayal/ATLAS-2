"use client";

import React, { useState } from "react";
import { formatNumber, formatStrike } from "@/lib/options/formatters";
import { Activity, BarChart2, Info } from "lucide-react";

interface StrikeActivity {
  strike_price: number;
  call_volume: number;
  put_volume: number;
  call_open_interest: number;
  put_open_interest: number;
  total_volume: number;
  total_open_interest: number;
}

interface OptionsActivityViewProps {
  activityData: StrikeActivity[];
  expirationDate: string;
  currency?: string;
  isLoading?: boolean;
}

export function OptionsActivityView({
  activityData,
  expirationDate,
  currency = "USD",
  isLoading,
}: OptionsActivityViewProps) {
  const [metric, setMetric] = useState<"VOLUME" | "OPEN_INTEREST">("OPEN_INTEREST");

  if (isLoading) {
    return (
      <div className="p-12 text-center text-zinc-500 text-xs">
        Loading trading activity and open interest distributions...
      </div>
    );
  }

  if (!activityData || activityData.length === 0) {
    return (
      <div className="p-12 text-center text-zinc-500 text-xs">
        No trading activity data available for this expiration.
      </div>
    );
  }

  const maxVal = Math.max(
    ...activityData.map((d) =>
      metric === "VOLUME"
        ? Math.max(d.call_volume, d.put_volume)
        : Math.max(d.call_open_interest, d.put_open_interest)
    ),
    1
  );

  return (
    <div className="p-4 space-y-4 bg-zinc-950 overflow-y-auto h-full">
      {/* Metric Selector & Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-zinc-900/60 border border-zinc-800 p-3 rounded-lg">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Strike Activity Distribution ({expirationDate})
          </h3>
          <p className="text-xs text-zinc-500 mt-0.5">
            Call vs. Put distribution across active strike prices
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setMetric("OPEN_INTEREST")}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              metric === "OPEN_INTEREST"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "bg-zinc-800 text-zinc-400 hover:text-white"
            }`}
          >
            Open Interest
          </button>
          <button
            onClick={() => setMetric("VOLUME")}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              metric === "VOLUME"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "bg-zinc-800 text-zinc-400 hover:text-white"
            }`}
          >
            Trading Volume
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 text-xs text-zinc-400">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-sm bg-emerald-500" />
          <span>Calls {metric === "VOLUME" ? "Volume" : "Open Interest"}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-sm bg-rose-500" />
          <span>Puts {metric === "VOLUME" ? "Volume" : "Open Interest"}</span>
        </div>
      </div>

      {/* Distribution Bars */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-4 space-y-2">
        {activityData.map((d) => {
          const callVal = metric === "VOLUME" ? d.call_volume : d.call_open_interest;
          const putVal = metric === "VOLUME" ? d.put_volume : d.put_open_interest;
          const callPct = (callVal / maxVal) * 100;
          const putPct = (putVal / maxVal) * 100;

          return (
            <div key={d.strike_price} className="flex items-center gap-3 text-xs font-mono">
              {/* Call Bar (Extends to left) */}
              <div className="w-1/2 flex items-center justify-end gap-2">
                <span className="text-[11px] text-zinc-400 font-semibold">{formatNumber(callVal)}</span>
                <div className="w-full max-w-[200px] h-4 bg-zinc-850 rounded-l overflow-hidden flex justify-end">
                  <div
                    style={{ width: `${callPct}%` }}
                    className="h-full bg-emerald-500/80 rounded-l transition-all"
                  />
                </div>
              </div>

              {/* Center Strike Label */}
              <div className="w-20 text-center font-bold text-white bg-zinc-800/80 py-1 rounded border border-zinc-750 shrink-0">
                {formatStrike(d.strike_price, currency)}
              </div>

              {/* Put Bar (Extends to right) */}
              <div className="w-1/2 flex items-center justify-start gap-2">
                <div className="w-full max-w-[200px] h-4 bg-zinc-850 rounded-r overflow-hidden flex justify-start">
                  <div
                    style={{ width: `${putPct}%` }}
                    className="h-full bg-rose-500/80 rounded-r transition-all"
                  />
                </div>
                <span className="text-[11px] text-zinc-400 font-semibold">{formatNumber(putVal)}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Disclaimers */}
      <div className="p-3 bg-zinc-900/40 rounded border border-zinc-850 text-[10px] text-zinc-500 flex items-center gap-2">
        <Info className="w-4 h-4 shrink-0 text-zinc-400" />
        <span>
          Open interest reflects settled contracts as reported by the clearing corporation (OCC / NSE Clearing) prior to the current trading session and does not update continuously intraday.
        </span>
      </div>
    </div>
  );
}
