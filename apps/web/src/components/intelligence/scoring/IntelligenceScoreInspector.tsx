"use client";

import React from "react";
import { AtlasIntelligenceScore } from "@/lib/intelligence/scoring/types";
import { IntelligenceFactorBreakdown } from "./IntelligenceFactorBreakdown";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  History,
  Database,
  Sliders,
  Layers,
  X,
  Lock,
} from "lucide-react";

interface IntelligenceScoreInspectorProps {
  score: AtlasIntelligenceScore | null;
  onClose: () => void;
}

export function IntelligenceScoreInspector({ score, onClose }: IntelligenceScoreInspectorProps) {
  if (!score) return null;

  const scoreVal = score.score_value;
  const isAvailable = score.score_status === "AVAILABLE" || score.score_status === "PARTIAL";

  return (
    <div className="h-full flex flex-col bg-zinc-950 border-l border-zinc-800 text-zinc-100 font-mono text-xs select-none overflow-y-auto">
      {/* Inspector Header */}
      <div className="p-3 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-zinc-200 uppercase tracking-wider text-[11px]">
            SCORE INSPECTOR (STAGE 139)
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 space-y-4 flex-1">
        {/* Primary Subject & Score Banner */}
        <div className="p-3 bg-black border border-zinc-800 rounded space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider">SCORING OBJECTIVE</span>
            <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 text-[10px] font-semibold">
              {score.scoring_objective}
            </span>
          </div>

          <h3 className="text-sm font-bold text-zinc-100 line-clamp-2">
            {(score.subject_reference?.title as string) || score.event_id || "Scored Event"}
          </h3>

          <div className="pt-2 border-t border-zinc-800 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-zinc-500 block">FINAL PRIORITY INDEX</span>
              <span
                className={`text-2xl font-bold font-mono ${
                  scoreVal !== null && scoreVal !== undefined && scoreVal >= 80
                    ? "text-emerald-400"
                    : scoreVal !== null && scoreVal !== undefined && scoreVal >= 60
                    ? "text-sky-400"
                    : "text-amber-400"
                }`}
              >
                {scoreVal !== null && scoreVal !== undefined ? scoreVal.toFixed(1) : "N/A"}
                <span className="text-xs text-zinc-500 font-normal ml-1">/ 100</span>
              </span>
            </div>

            <div className="text-right">
              <span className="text-[10px] text-zinc-500 block">STATUS</span>
              <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 text-[10px] font-bold">
                {score.score_status}
              </span>
            </div>
          </div>
        </div>

        {/* Semantic Interpretation Banner */}
        <div className="p-3 bg-zinc-900 border border-zinc-800 rounded space-y-1">
          <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider block">
            INTERPRETATION
          </span>
          <p className="text-zinc-200 text-xs leading-relaxed">{score.score_interpretation}</p>
        </div>

        {/* Factor Breakdown Waterfall */}
        <IntelligenceFactorBreakdown
          contributions={score.factor_contributions}
          scoreValue={score.score_value}
        />

        {/* Coverage & Uncertainty Disclosures */}
        <div className="p-3 bg-zinc-900 border border-zinc-800 rounded space-y-2">
          <span className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wider block">
            DATA COVERAGE & UNCERTAINTY
          </span>
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2 bg-black border border-zinc-800 rounded">
              <span className="text-zinc-500 block text-[10px]">COVERAGE RATIO</span>
              <span className="text-zinc-200 font-bold">
                {(score.uncertainty.coverage_ratio * 100).toFixed(0)}%
              </span>
            </div>
            <div className="p-2 bg-black border border-zinc-800 rounded">
              <span className="text-zinc-500 block text-[10px]">AVAILABLE FEATURES</span>
              <span className="text-zinc-200 font-bold">
                {score.uncertainty.available_feature_count} / {score.uncertainty.required_feature_count}
              </span>
            </div>
          </div>

          {score.uncertainty.missing_features.length > 0 && (
            <div className="p-2 bg-amber-950/30 border border-amber-900/50 rounded text-amber-300 text-[10px]">
              Missing features: {score.uncertainty.missing_features.join(", ")}
            </div>
          )}

          {score.uncertainty.has_source_conflicts && (
            <div className="p-2 bg-rose-950/30 border border-rose-900/50 rounded text-rose-300 text-[10px] flex items-start gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
              <span>Conflicting source reports detected. Evidence conflict penalty applied.</span>
            </div>
          )}

          <div className="space-y-1 pt-1 border-t border-zinc-800">
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider">KNOWN LIMITATIONS</span>
            {score.uncertainty.limitations.map((lim, idx) => (
              <p key={idx} className="text-[10px] text-zinc-400 leading-normal">
                • {lim}
              </p>
            ))}
          </div>
        </div>

        {/* Reproducibility & Lineage Audit */}
        <div className="p-3 bg-zinc-900 border border-zinc-800 rounded space-y-1.5 text-[10px] text-zinc-400">
          <span className="text-zinc-500 font-semibold uppercase tracking-wider block">
            AUDIT LINEAGE & REPRODUCIBILITY
          </span>
          <div>
            <span className="text-zinc-500">Model ID / Version: </span>
            <span className="text-zinc-300 font-mono">{score.model_id} ({score.model_version})</span>
          </div>
          <div>
            <span className="text-zinc-500">Policy: </span>
            <span className="text-zinc-300 font-mono">{score.lineage.policy_id}</span>
          </div>
          <div>
            <span className="text-zinc-500">Feature Snapshot: </span>
            <span className="text-zinc-300 font-mono">{score.lineage.feature_snapshot_id}</span>
          </div>
          <div>
            <span className="text-zinc-500">Evaluation As-Of: </span>
            <span className="text-zinc-300 font-mono">{score.known_as_of}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
