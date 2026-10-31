"use client";

import React, { useState, useEffect } from "react";
import { ScoringModelDefinition, ScoringEvaluationManifest, ScoringTelemetrySummary } from "@/lib/intelligence/scoring/types";
import { fetchScoringModels, fetchScoringEvaluations, fetchScoringTelemetry } from "@/lib/intelligence/scoring/api";
import { ShieldCheck, Activity, Award, CheckCircle2, RotateCcw, AlertTriangle } from "lucide-react";

export function IntelligenceModelDetails() {
  const [models, setModels] = useState<ScoringModelDefinition[]>([]);
  const [evaluations, setEvaluations] = useState<ScoringEvaluationManifest[]>([]);
  const [telemetry, setTelemetry] = useState<ScoringTelemetrySummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchScoringModels().catch(() => []),
      fetchScoringEvaluations().catch(() => []),
      fetchScoringTelemetry().catch(() => null),
    ])
      .then(([m, ev, tel]) => {
        setModels(m);
        setEvaluations(ev);
        setTelemetry(tel);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 font-mono text-xs select-none bg-black text-zinc-100">
      {/* Title & Governance Badge */}
      <div className="p-3 bg-zinc-950 border border-zinc-800 rounded flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-zinc-100 uppercase tracking-wider">
            SCORING MODEL REGISTRY & GOVERNANCE
          </h2>
          <p className="text-[11px] text-zinc-400 mt-0.5">
            Institutional model specifications, version rollback controls, and historical benchmark evaluations.
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-950/80 border border-emerald-800 text-emerald-400 text-[10px] font-bold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>GOVERNANCE STATUS: ACTIVE</span>
        </div>
      </div>

      {/* Real-Time Telemetry and Drift Status */}
      {telemetry && (
        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded space-y-2">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
            <span className="text-zinc-400 font-semibold uppercase text-[10px] tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-sky-400" />
              OPERATIONAL HEALTH & DRIFT TELEMETRY
            </span>
            <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 text-[10px] font-bold">
              {telemetry.drift_status}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
            <div className="p-2 bg-zinc-900 border border-zinc-800 rounded">
              <span className="text-zinc-500 block text-[10px]">TOTAL SCORES COMPUTED</span>
              <span className="text-zinc-100 font-bold text-sm">{telemetry.total_scores_computed}</span>
            </div>
            <div className="p-2 bg-zinc-900 border border-zinc-800 rounded">
              <span className="text-zinc-500 block text-[10px]">MEAN SCORE INDEX</span>
              <span className="text-zinc-100 font-bold text-sm">{telemetry.mean_score_value.toFixed(1)}</span>
            </div>
            <div className="p-2 bg-zinc-900 border border-zinc-800 rounded">
              <span className="text-zinc-500 block text-[10px]">HIGH PRIORITY FRACTION (&ge;80)</span>
              <span className="text-emerald-400 font-bold text-sm">
                {(telemetry.high_priority_fraction * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-2 bg-zinc-900 border border-zinc-800 rounded">
              <span className="text-zinc-500 block text-[10px]">AVG FEATURE COVERAGE</span>
              <span className="text-sky-400 font-bold text-sm">
                {(telemetry.average_coverage_ratio * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Model Registry Cards */}
      <div className="space-y-3">
        <span className="text-zinc-400 font-semibold uppercase text-[10px] tracking-wider block">
          REGISTERED SCORING MODELS ({models.length})
        </span>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {models.map((mod) => (
            <div key={mod.model_id} className="p-3 bg-zinc-950 border border-zinc-800 rounded space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-zinc-200 text-xs">{mod.model_name}</span>
                <span className="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 text-[10px] font-mono">
                  {mod.active_version}
                </span>
              </div>

              <div className="text-[11px] text-zinc-400 space-y-1">
                <div>Objective: <span className="text-zinc-300">{mod.objective_id}</span></div>
                <div>Family: <span className="text-zinc-300">{mod.model_family}</span></div>
                <div>Scale: <span className="text-zinc-300">{mod.score_scale}</span></div>
                <div>Approved By: <span className="text-zinc-300">{mod.approved_by || "Risk Governance Board"}</span></div>
              </div>

              <div className="pt-2 border-t border-zinc-800 flex items-center justify-between text-[10px] text-zinc-500">
                <span>Supported: {mod.supported_versions.join(", ")}</span>
                <span className="text-emerald-400 font-semibold">{mod.governance_status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Historical Evaluation Benchmarks */}
      {evaluations.length > 0 && (
        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded space-y-3">
          <span className="text-zinc-400 font-semibold uppercase text-[10px] tracking-wider block flex items-center gap-1.5">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            HISTORICAL VALIDATION BENCHMARKS
          </span>

          <div className="space-y-2">
            {evaluations.map((ev) => (
              <div key={ev.evaluation_id} className="p-3 bg-zinc-900 border border-zinc-800 rounded space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-zinc-200">{ev.evaluation_dataset}</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400 font-bold text-[10px]">
                    {ev.validation_status}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[10px]">
                  <div>
                    <span className="text-zinc-500 block">NDCG@10</span>
                    <span className="text-emerald-400 font-bold text-xs">
                      {ev.ndcg_at_10 !== null && ev.ndcg_at_10 !== undefined ? ev.ndcg_at_10.toFixed(4) : "N/A"}
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-500 block">PRECISION@5</span>
                    <span className="text-sky-400 font-bold text-xs">
                      {ev.precision_at_5 !== null && ev.precision_at_5 !== undefined ? ev.precision_at_5.toFixed(4) : "N/A"}
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-500 block">EVALUATION WINDOW</span>
                    <span className="text-zinc-300">
                      {ev.time_window_start.split("T")[0]} to {ev.time_window_end.split("T")[0]}
                    </span>
                  </div>
                  <div>
                    <span className="text-zinc-500 block">SAMPLE SIZE</span>
                    <span className="text-zinc-300 font-bold">{ev.sample_size} events</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
