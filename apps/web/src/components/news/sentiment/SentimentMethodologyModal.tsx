"use client";

import React from "react";
import { SentimentEvaluationResultDTO } from "@/lib/news/types";
import { X, ShieldCheck, CheckCircle2, AlertCircle, Cpu } from "lucide-react";

interface SentimentMethodologyModalProps {
  isOpen: boolean;
  onClose: () => void;
  evaluation: SentimentEvaluationResultDTO | null;
  isLoading?: boolean;
}

export function SentimentMethodologyModal({
  isOpen,
  onClose,
  evaluation,
  isLoading,
}: SentimentMethodologyModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm font-mono">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-cyan-500" />
            <div>
              <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
                Sentiment Model Methodology & Golden Benchmark
              </h2>
              <p className="text-[10px] text-zinc-500">
                Evaluation Version: {evaluation?.evaluation_version || "v1.0.0-institutional"}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-5 text-xs">
          {/* Institutional Principles */}
          <div className="p-3 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-500 text-[11px] space-y-1">
            <div className="font-bold uppercase tracking-wider flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>Institutional Analytics Standards</span>
            </div>
            <p className="text-zinc-600 dark:text-zinc-400">
              ATLAS Stage 102 classifies financial tone and entity relevance strictly as descriptive text annotations.
              Tone is never converted into Buy/Sell trade signals, and observed price reactions are never claimed to be caused by news headlines.
            </p>
          </div>

          {/* Golden Benchmark Summary */}
          {isLoading ? (
            <div className="h-32 bg-zinc-100 dark:bg-zinc-800/40 rounded animate-pulse" />
          ) : evaluation ? (
            <div>
              <h3 className="text-xs font-bold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <Cpu className="w-4 h-4 text-cyan-500" />
                <span>Golden Test Corpus Evaluation ({evaluation.total_samples} Scenarios)</span>
              </h3>

              <div className="grid grid-cols-4 gap-2 mb-4">
                <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-center">
                  <div className="text-[10px] text-zinc-500 uppercase">Macro-F1</div>
                  <div className="text-base font-bold text-emerald-500 tabular-nums">
                    {evaluation.macro_f1.toFixed(2)}
                  </div>
                </div>
                <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-center">
                  <div className="text-[10px] text-zinc-500 uppercase">Accuracy</div>
                  <div className="text-base font-bold text-zinc-900 dark:text-zinc-100 tabular-nums">
                    {(evaluation.accuracy * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-center">
                  <div className="text-[10px] text-zinc-500 uppercase">Target Acc</div>
                  <div className="text-base font-bold text-zinc-900 dark:text-zinc-100 tabular-nums">
                    {(evaluation.target_resolution_accuracy * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-center">
                  <div className="text-[10px] text-zinc-500 uppercase">Abstention</div>
                  <div className="text-base font-bold text-zinc-900 dark:text-zinc-100 tabular-nums">
                    {(evaluation.abstention_rate * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Per-Class Metrics Table */}
              <div className="border border-zinc-200 dark:border-zinc-800 rounded overflow-hidden">
                <table className="w-full text-left text-[11px]">
                  <thead>
                    <tr className="bg-zinc-50 dark:bg-zinc-950 border-b border-zinc-200 dark:border-zinc-800 text-[10px] text-zinc-500 uppercase">
                      <th className="py-1.5 px-3">Sentiment Class</th>
                      <th className="py-1.5 px-3">Precision</th>
                      <th className="py-1.5 px-3">Recall</th>
                      <th className="py-1.5 px-3">F1 Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                    {Object.keys(evaluation.per_class_f1).map((cls) => (
                      <tr key={cls}>
                        <td className="py-1.5 px-3 font-semibold text-zinc-900 dark:text-zinc-100">
                          {cls}
                        </td>
                        <td className="py-1.5 px-3 tabular-nums text-zinc-600 dark:text-zinc-400">
                          {(evaluation.per_class_precision[cls] ?? 1.0).toFixed(2)}
                        </td>
                        <td className="py-1.5 px-3 tabular-nums text-zinc-600 dark:text-zinc-400">
                          {(evaluation.per_class_recall[cls] ?? 1.0).toFixed(2)}
                        </td>
                        <td className="py-1.5 px-3 tabular-nums font-bold text-emerald-500">
                          {(evaluation.per_class_f1[cls] ?? 1.0).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 text-center text-zinc-500">
              No evaluation data available.
            </div>
          )}

          {/* Boundaries List */}
          <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-[11px] space-y-2">
            <div className="font-bold text-zinc-900 dark:text-zinc-200 uppercase">
              Strict Implementation Boundaries:
            </div>
            <ul className="list-disc list-inside space-y-1 text-zinc-600 dark:text-zinc-400">
              <li>Neutral reporting of facts is strictly differentiated from insufficient evidence.</li>
              <li>Negation handling recognizes explicit corporate denials without negative false-positives.</li>
              <li>Syndicated duplicate reports do not multiply sentiment confidence or aggregate counts.</li>
              <li>Multi-target articles isolate sentiment independently for each participating company.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded bg-zinc-200 dark:bg-zinc-800 hover:bg-zinc-300 dark:hover:bg-zinc-700 text-zinc-900 dark:text-zinc-100 text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
