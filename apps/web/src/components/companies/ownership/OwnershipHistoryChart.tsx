"use client";

import React from "react";
import { HistoricalOwnershipSnapshotDTO } from "@/lib/companies/ownership";
import {
  History,
  Calendar,
  Layers,
  ShieldCheck,
  TrendingUp,
  Info,
} from "lucide-react";

interface OwnershipHistoryChartProps {
  snapshots: HistoricalOwnershipSnapshotDTO[];
  onSelectPeriod?: (period: string) => void;
  selectedPeriod?: string;
}

export const OwnershipHistoryChart: React.FC<OwnershipHistoryChartProps> = ({
  snapshots,
  onSelectPeriod,
  selectedPeriod,
}) => {
  if (snapshots.length === 0) {
    return (
      <div className="p-8 text-center border border-border/60 rounded-lg bg-card/40 text-muted-foreground text-xs">
        No historical ownership snapshots available for this security.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Visual Timeline Comparison Bar */}
      <div className="rounded-lg border border-border/60 bg-card/60 p-4 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <div className="font-semibold text-foreground flex items-center gap-1.5">
            <TrendingUp className="h-4 w-4 text-primary" />
            <span>Top 5 Disclosed Stake Trajectory Across Reporting Periods</span>
          </div>
          <span className="text-[11px] font-mono text-muted-foreground">
            {snapshots.length} Historical Vintages
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          {snapshots.map((snap) => {
            const isSelected = selectedPeriod === snap.reporting_period;
            return (
              <div
                key={snap.reporting_period}
                onClick={() => onSelectPeriod && onSelectPeriod(snap.reporting_period)}
                className={`p-3 rounded-lg border transition-all cursor-pointer ${
                  isSelected
                    ? "border-primary bg-primary/10 shadow-sm"
                    : "border-border/60 bg-muted/20 hover:border-border hover:bg-muted/30"
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-foreground font-mono">{snap.reporting_period}</span>
                  <span className="text-[10px] text-muted-foreground font-mono">{snap.reporting_date}</span>
                </div>

                <div className="mt-2">
                  <div className="text-[11px] text-muted-foreground">Top 5 Concentration</div>
                  <div className="text-lg font-extrabold font-mono text-primary">
                    {snap.top_5_percentage.toFixed(2)}%
                  </div>
                </div>

                {/* Progress bar visual */}
                <div className="mt-2 h-1.5 w-full bg-muted/60 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${snap.top_5_percentage}%` }}
                  />
                </div>

                <div className="mt-2 pt-2 border-t border-border/30 text-[10px] text-muted-foreground font-mono flex justify-between">
                  <span>Disclosed:</span>
                  <span className="text-foreground font-medium">{snap.formatted_disclosed_shares}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Historical Table */}
      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 border-b border-border/60 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <tr>
              <th className="py-2.5 px-3">Period</th>
              <th className="py-2.5 px-3">Reporting Date</th>
              <th className="py-2.5 px-3">Filing Date</th>
              <th className="py-2.5 px-3 text-right">Shares Outstanding</th>
              <th className="py-2.5 px-3 text-right">Disclosed Shares</th>
              <th className="py-2.5 px-3 text-right">Top 5 Stake %</th>
              <th className="py-2.5 px-3 text-right">Disclosed Stake %</th>
              <th className="py-2.5 px-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {snapshots.map((snap) => {
              const isSelected = selectedPeriod === snap.reporting_period;

              return (
                <tr
                  key={snap.reporting_period}
                  onClick={() => onSelectPeriod && onSelectPeriod(snap.reporting_period)}
                  className={`cursor-pointer transition-colors ${
                    isSelected ? "bg-primary/10 hover:bg-primary/15" : "hover:bg-muted/20"
                  }`}
                >
                  <td className="py-2.5 px-3 font-mono font-bold text-foreground">
                    {snap.reporting_period}
                  </td>

                  <td className="py-2.5 px-3 font-mono text-muted-foreground">
                    {snap.reporting_date}
                  </td>

                  <td className="py-2.5 px-3 font-mono text-muted-foreground">
                    {snap.filing_date}
                  </td>

                  <td className="py-2.5 px-3 text-right font-mono font-medium text-foreground">
                    {snap.formatted_shares_outstanding}
                  </td>

                  <td className="py-2.5 px-3 text-right font-mono text-muted-foreground">
                    {snap.formatted_disclosed_shares}
                  </td>

                  <td className="py-2.5 px-3 text-right font-mono font-bold text-primary">
                    {snap.top_5_percentage.toFixed(2)}%
                  </td>

                  <td className="py-2.5 px-3 text-right font-mono font-semibold text-foreground">
                    {snap.total_disclosed_percentage.toFixed(2)}%
                  </td>

                  <td className="py-2.5 px-3 text-center font-mono">
                    <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Point-in-Time
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Point-in-time disclosure note */}
      <div className="flex items-start gap-2 p-3 rounded-lg border border-border/40 bg-muted/20 text-xs text-muted-foreground">
        <Info className="h-4 w-4 text-sky-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-foreground">Point-in-Time Temporal Discipline: </span>
          Historical snapshots record disclosures as of each specific reporting period end, with actual filing dates preserved. Historical ownership percentages use the shares outstanding denominator certified at that historical date, preventing retrospective distortion from later buybacks or stock issuances.
        </div>
      </div>
    </div>
  );
};
