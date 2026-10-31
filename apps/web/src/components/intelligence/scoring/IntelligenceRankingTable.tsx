"use client";

import React from "react";
import { RankedItem, AtlasIntelligenceScore } from "@/lib/intelligence/scoring/types";
import { Radio, AlertCircle, CheckCircle2, ChevronRight, Sliders } from "lucide-react";

interface IntelligenceRankingTableProps {
  rankedItems: RankedItem[];
  selectedScoreId?: string | null;
  onSelectScore: (score: AtlasIntelligenceScore) => void;
  loading?: boolean;
}

export function IntelligenceRankingTable({
  rankedItems,
  selectedScoreId,
  onSelectScore,
  loading = false,
}: IntelligenceRankingTableProps) {
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-zinc-500 font-mono text-xs">
        <Sliders className="w-5 h-5 animate-spin mr-2 text-emerald-400" />
        <span>Executing Point-in-Time Scoring Model & Deterministic Ranking...</span>
      </div>
    );
  }

  if (!rankedItems || rankedItems.length === 0) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center text-zinc-500 font-mono text-xs border border-dashed border-zinc-800 rounded m-4">
        <div>
          <AlertCircle className="w-8 h-8 mx-auto text-zinc-600 mb-2" />
          <p>No eligible events found for current ranking criteria and temporal horizon.</p>
          <p className="text-[10px] text-zinc-600 mt-1">Adjust candidate filters or expand time window.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto font-mono text-xs select-none">
      <table className="w-full text-left border-collapse">
        <thead className="sticky top-0 bg-zinc-950 border-b border-zinc-800 text-[10px] uppercase text-zinc-500 z-10">
          <tr>
            <th className="py-2.5 px-3 w-12 text-center">RANK</th>
            <th className="py-2.5 px-3">EVENT / CANDIDATE SUBJECT</th>
            <th className="py-2.5 px-3 w-36">OBJECTIVE</th>
            <th className="py-2.5 px-3 w-28 text-center">SCORE</th>
            <th className="py-2.5 px-3 w-24 text-center">COVERAGE</th>
            <th className="py-2.5 px-3 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-900">
          {rankedItems.map((item) => {
            const score = item.score;
            const scoreVal = score.score_value;
            const isSelected = selectedScoreId === score.score_id;

            return (
              <tr
                key={score.score_id}
                onClick={() => onSelectScore(score)}
                className={`cursor-pointer transition-colors ${
                  isSelected ? "bg-zinc-900 border-l-2 border-emerald-500" : "hover:bg-zinc-900/60"
                }`}
              >
                {/* Rank Badge */}
                <td className="py-3 px-3 text-center">
                  <span
                    className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      item.rank === 1
                        ? "bg-amber-950 text-amber-400 border border-amber-800"
                        : item.rank <= 3
                        ? "bg-zinc-800 text-zinc-200"
                        : "text-zinc-500"
                    }`}
                  >
                    #{item.rank}
                  </span>
                </td>

                {/* Event Details */}
                <td className="py-3 px-3">
                  <div className="space-y-0.5">
                    <div className="font-semibold text-zinc-200 text-xs hover:text-emerald-400 transition-colors line-clamp-1">
                      {(score.subject_reference?.title as string) || score.event_id}
                    </div>
                    <div className="text-[10px] text-zinc-500 flex items-center gap-2">
                      <span>ID: {score.event_id}</span>
                      <span>•</span>
                      <span>Valid: {score.valid_at ? score.valid_at.split("T")[0] : "N/A"}</span>
                      {score.uncertainty.has_source_conflicts && (
                        <span className="text-rose-400 font-semibold">• Conflicting Sources</span>
                      )}
                    </div>
                  </div>
                </td>

                {/* Objective */}
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] text-zinc-400">
                    {score.scoring_objective}
                  </span>
                </td>

                {/* Score Value Pill */}
                <td className="py-3 px-3 text-center">
                  {scoreVal !== null && scoreVal !== undefined ? (
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded font-bold text-xs ${
                        scoreVal >= 80
                          ? "bg-emerald-950/80 border border-emerald-800/80 text-emerald-400"
                          : scoreVal >= 60
                          ? "bg-sky-950/80 border border-sky-800/80 text-sky-400"
                          : scoreVal >= 35
                          ? "bg-amber-950/80 border border-amber-800/80 text-amber-400"
                          : "bg-zinc-800 border border-zinc-700 text-zinc-400"
                      }`}
                    >
                      {scoreVal.toFixed(1)}
                    </span>
                  ) : (
                    <span className="text-[10px] text-zinc-500 italic">{score.score_status}</span>
                  )}
                </td>

                {/* Coverage % */}
                <td className="py-3 px-3 text-center">
                  <span className="text-[10px] text-zinc-400">
                    {(score.uncertainty.coverage_ratio * 100).toFixed(0)}%
                  </span>
                </td>

                {/* Arrow */}
                <td className="py-3 px-3 text-right">
                  <ChevronRight className="w-4 h-4 text-zinc-600" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
