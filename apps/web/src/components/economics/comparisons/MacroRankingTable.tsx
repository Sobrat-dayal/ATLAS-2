"use client";

import React from "react";
import {
  ComparableIndicatorDTO,
  EconomicRankingsResponseDTO,
  RankingDirection,
  TieBreakerPolicy,
} from "@/lib/economics/comparisons";
import { ArrowDownAZ, ArrowUpZA, Award, Info, Scale } from "lucide-react";

interface MacroRankingTableProps {
  rankingsData: EconomicRankingsResponseDTO | null;
  indicators: ComparableIndicatorDTO[];
  direction: RankingDirection;
  onChangeDirection: (dir: RankingDirection) => void;
  tiePolicy: TieBreakerPolicy;
  onChangeTiePolicy: (policy: TieBreakerPolicy) => void;
  isLoading: boolean;
}

export function MacroRankingTable({
  rankingsData,
  indicators,
  direction,
  onChangeDirection,
  tiePolicy,
  onChangeTiePolicy,
  isLoading,
}: MacroRankingTableProps) {
  if (isLoading && !rankingsData) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Computing Sovereign Economic Rankings...</span>
      </div>
    );
  }

  if (!rankingsData || rankingsData.rankings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-atlas-text-muted gap-2 border border-dashed border-atlas-border-subtle rounded m-4">
        <Info className="w-8 h-8 text-atlas-text-muted/60" />
        <p className="text-sm font-medium text-atlas-text-primary">No Ranking Observations Available</p>
        <p className="text-xs text-atlas-text-muted">
          Selected indicator has insufficient eligible observations in the requested cohort.
        </p>
      </div>
    );
  }

  const indicatorDef = indicators.find((i) => i.metric_kind === rankingsData.metric_kind);

  return (
    <div className="flex flex-col flex-1 h-full min-h-0 bg-atlas-background overflow-hidden p-4 gap-4">
      {/* Ranking Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded bg-atlas-surface/60 border border-atlas-border-subtle text-xs">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-indigo-500/15 text-indigo-400">
            <Award className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-atlas-text-primary text-sm tracking-tight">
              {indicatorDef?.name || rankingsData.metric_kind}
            </h2>
            <div className="flex items-center gap-2 text-atlas-text-muted text-[11px] font-mono">
              <span>Period: {rankingsData.reference_period}</span>
              <span>•</span>
              <span>
                Eligible: {rankingsData.total_eligible} | Excluded: {rankingsData.total_excluded}
              </span>
            </div>
          </div>
        </div>

        {/* Sort & Tie-Breaking Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-atlas-background border border-atlas-border-subtle rounded p-0.5">
            <button
              onClick={() => onChangeDirection("descending")}
              className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 transition-colors ${
                direction === "descending"
                  ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <ArrowDownAZ className="w-3.5 h-3.5 text-indigo-400" />
              <span>Highest First</span>
            </button>
            <button
              onClick={() => onChangeDirection("ascending")}
              className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 transition-colors ${
                direction === "ascending"
                  ? "bg-atlas-surface text-atlas-text-primary shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <ArrowUpZA className="w-3.5 h-3.5 text-indigo-400" />
              <span>Lowest First</span>
            </button>
          </div>

          <select
            value={tiePolicy}
            onChange={(e) => onChangeTiePolicy(e.target.value as TieBreakerPolicy)}
            className="bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1 text-xs text-atlas-text-primary focus:outline-hidden"
          >
            <option value="standard_competition">Standard Competition Tie (1, 2, 2, 4)</option>
            <option value="dense_rank">Dense Tie (1, 2, 2, 3)</option>
          </select>
        </div>
      </div>

      {/* Rankings Table */}
      <div className="flex-1 overflow-auto border border-atlas-border-subtle rounded bg-atlas-surface/20">
        <table className="w-full border-collapse text-left text-xs font-mono">
          <thead className="sticky top-0 bg-atlas-surface border-b border-atlas-border-subtle z-10 shadow-xs">
            <tr>
              <th className="p-2.5 font-bold text-atlas-text-primary w-16 text-center">Rank</th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary">Country / Area</th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary text-right">Value</th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary w-28">Unit</th>
              <th className="p-2.5 font-semibold text-atlas-text-secondary w-28">Period</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/40">
            {rankingsData.rankings.map((row) => {
              const isFirst = row.rank === 1;
              const isArea = row.geography_id === "geo-ea";
              return (
                <tr key={row.geography_id} className="hover:bg-atlas-surface/50 transition-colors">
                  <td className="p-2.5 text-center font-bold">
                    <span
                      className={`inline-flex items-center justify-center w-6 h-6 rounded text-xs ${
                        isFirst
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                          : "bg-atlas-surface border border-atlas-border-subtle text-atlas-text-primary"
                      }`}
                    >
                      {row.rank}
                    </span>
                  </td>
                  <td className="p-2.5 font-semibold text-atlas-text-primary">
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-atlas-surface border border-atlas-border-subtle text-atlas-accent font-bold">
                        {row.iso_code}
                      </span>
                      <span>{row.country_name}</span>
                      {isArea && (
                        <span className="text-[9px] uppercase px-1 py-0.2 rounded bg-amber-500/15 text-amber-300 font-normal">
                          ECONOMIC AREA
                        </span>
                      )}
                      {row.is_tied && (
                        <span className="text-[9px] uppercase px-1 py-0.2 rounded bg-blue-500/15 text-blue-300">
                          TIED
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="p-2.5 text-right font-bold text-atlas-text-primary text-[13px]">
                    {row.formatted_value}
                  </td>
                  <td className="p-2.5 text-atlas-text-muted">{row.unit}</td>
                  <td className="p-2.5 text-atlas-text-muted">{row.reference_period}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Methodological Caveat / Disclaimer */}
      <div className="p-2.5 rounded bg-atlas-surface/40 border border-atlas-border-subtle/60 text-[11px] text-atlas-text-muted flex items-start gap-2">
        <Scale className="w-4 h-4 text-atlas-accent shrink-0 mt-0.5" />
        <div className="flex flex-col gap-0.5">
          <span className="font-semibold text-atlas-text-primary">Institutional Methodological Qualification</span>
          <p>
            Rankings reflect strict statistical comparability across eligible official reporting periods. ATLAS does not assign normative qualitative scores (e.g. &ldquo;best&rdquo; or &ldquo;worst&rdquo; economy) and excludes countries with missing observations from the ranked population without assuming zero.
          </p>
        </div>
      </div>
    </div>
  );
}
