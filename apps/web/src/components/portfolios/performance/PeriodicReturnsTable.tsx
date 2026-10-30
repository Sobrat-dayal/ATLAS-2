"use client";

import React from "react";
import { formatRate } from "@/lib/portfolios/performance/formatting";
import { PeriodicReturnDTO } from "@/lib/portfolios/performance/types";

interface PeriodicReturnsTableProps {
  returns: PeriodicReturnDTO[];
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

export function PeriodicReturnsTable({ returns }: PeriodicReturnsTableProps) {
  if (!returns || returns.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 text-xs text-atlas-text-tertiary">
        No periodic monthly returns recorded yet.
      </div>
    );
  }

  // Group returns by year
  const yearsMap = new Map<number, { [month: number]: number; fullYear?: number }>();

  returns.forEach((r) => {
    const dt = new Date(r.start_date);
    const yr = dt.getFullYear();
    const m = dt.getMonth() + 1; // 1-indexed

    if (!yearsMap.has(yr)) {
      yearsMap.set(yr, {});
    }

    const yrEntry = yearsMap.get(yr)!;
    if (r.period_type === "MONTHLY" && r.return_value !== null && r.return_value !== undefined) {
      yrEntry[m] = parseFloat(r.return_value);
    } else if (r.period_type === "ANNUAL" && r.return_value !== null && r.return_value !== undefined) {
      yrEntry.fullYear = parseFloat(r.return_value);
    }
  });

  const sortedYears = Array.from(yearsMap.keys()).sort((a, b) => b - a);

  const getHeatmapColor = (val: number | undefined) => {
    if (val === undefined || val === null) return "text-atlas-text-tertiary";
    if (val > 0.05) return "bg-emerald-500/20 text-emerald-400 font-semibold";
    if (val > 0) return "bg-emerald-500/10 text-emerald-300";
    if (val < -0.05) return "bg-rose-500/20 text-rose-400 font-semibold";
    if (val < 0) return "bg-rose-500/10 text-rose-300";
    return "text-atlas-text-secondary";
  };

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs">
      <div className="border-b border-atlas-border-default/40 pb-2.5">
        <h4 className="text-xs font-semibold text-atlas-text-primary">
          Monthly & Annual Returns Matrix
        </h4>
        <p className="text-[11px] text-atlas-text-secondary">
          Calendar monthly returns and geometrically linked full-year performance.
        </p>
      </div>

      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-atlas-border-default/60 text-[11px] text-atlas-text-tertiary">
              <th className="py-2 pr-3 font-medium">Year</th>
              {MONTHS.map((m) => (
                <th key={m} className="px-2 py-2 text-right font-medium">
                  {m}
                </th>
              ))}
              <th className="py-2 pl-3 text-right font-semibold text-atlas-text-primary">
                Full Year
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/30">
            {sortedYears.map((yr) => {
              const row = yearsMap.get(yr)!;

              // Calculate compound full year if not explicitly provided
              let fullYearReturn = row.fullYear;
              if (fullYearReturn === undefined) {
                let compound = 1.0;
                let hasMonths = false;
                for (let m = 1; m <= 12; m++) {
                  if (row[m] !== undefined) {
                    compound *= 1.0 + row[m];
                    hasMonths = true;
                  }
                }
                if (hasMonths) {
                  fullYearReturn = compound - 1.0;
                }
              }

              return (
                <tr key={yr} className="hover:bg-atlas-surface-2/40 transition-colors">
                  <td className="py-2.5 pr-3 font-semibold text-atlas-text-primary">
                    {yr}
                  </td>
                  {MONTHS.map((_, mIdx) => {
                    const mNum = mIdx + 1;
                    const val = row[mNum];
                    return (
                      <td
                        key={mNum}
                        className={`px-2 py-2.5 text-right transition-colors ${getHeatmapColor(val)}`}
                      >
                        {val !== undefined ? formatRate(val) : "--"}
                      </td>
                    );
                  })}
                  <td
                    className={`py-2.5 pl-3 text-right font-bold border-l border-atlas-border-default/40 ${getHeatmapColor(
                      fullYearReturn
                    )}`}
                  >
                    {fullYearReturn !== undefined ? formatRate(fullYearReturn) : "--"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-atlas-border-default/40 pt-2 text-[11px] text-atlas-text-tertiary">
        <span>Geometric compounding: (1 + R_yr) = &prod;(1 + R_mo)</span>
        <span>Heatmap shaded by monthly variance</span>
      </div>
    </div>
  );
}

