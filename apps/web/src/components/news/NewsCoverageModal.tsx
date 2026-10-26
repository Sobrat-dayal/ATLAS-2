"use client";

import React from "react";
import { X, Database, ShieldCheck, Globe, CheckCircle2 } from "lucide-react";
import {
  NewsCoverageResponseDTO,
  NewsPublisherDTO,
  NewsSourceDTO,
} from "@/lib/news/types";

interface NewsCoverageModalProps {
  isOpen: boolean;
  onClose: () => void;
  coverage: NewsCoverageResponseDTO | null;
  sources: NewsSourceDTO[];
  publishers: NewsPublisherDTO[];
}

export function NewsCoverageModal({
  isOpen,
  onClose,
  coverage,
  sources,
  publishers,
}: NewsCoverageModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl max-h-[85vh] flex flex-col rounded-lg bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-zinc-500" />
            <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 font-mono">
              SOURCES & COVERAGE REPORT
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-5 text-xs text-zinc-700 dark:text-zinc-300">
          {/* Metrics summary */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200 dark:border-zinc-800">
              <span className="text-[10px] font-mono text-zinc-400 uppercase block">Total Articles</span>
              <span className="text-base font-bold font-mono text-zinc-900 dark:text-zinc-100">
                {coverage?.total_articles ?? 0}
              </span>
            </div>
            <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200 dark:border-zinc-800">
              <span className="text-[10px] font-mono text-zinc-400 uppercase block">Active Sources</span>
              <span className="text-base font-bold font-mono text-zinc-900 dark:text-zinc-100">
                {sources.length}
              </span>
            </div>
            <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200 dark:border-zinc-800">
              <span className="text-[10px] font-mono text-zinc-400 uppercase block">Verified Publishers</span>
              <span className="text-base font-bold font-mono text-zinc-900 dark:text-zinc-100">
                {publishers.length}
              </span>
            </div>
            <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200 dark:border-zinc-800">
              <span className="text-[10px] font-mono text-zinc-400 uppercase block">Geographies</span>
              <span className="text-base font-bold font-mono text-zinc-900 dark:text-zinc-100">
                {coverage?.geographic_coverage?.length ?? 6}
              </span>
            </div>
          </div>

          {/* Authorized Sources */}
          <div>
            <h4 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2 font-mono uppercase text-[11px] tracking-wider">
              Authorized Ingestion Sources
            </h4>
            <div className="space-y-2">
              {sources.map((s) => (
                <div
                  key={s.source_id}
                  className="flex items-center justify-between p-2.5 rounded bg-zinc-50 dark:bg-zinc-800/30 border border-zinc-100 dark:border-zinc-800"
                >
                  <div>
                    <span className="font-medium text-zinc-900 dark:text-zinc-100 block">
                      {s.provider_name}
                    </span>
                    <span className="text-[11px] text-zinc-400 font-mono">
                      Type: {s.provider_type} • Cadence: {s.update_cadence_seconds}s
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-mono text-[10px]">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{s.health_status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Verified Publishers */}
          <div>
            <h4 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-2 font-mono uppercase text-[11px] tracking-wider">
              Verified Financial Publishers
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {publishers.map((p) => (
                <div
                  key={p.publisher_id}
                  className="p-2 rounded bg-zinc-50 dark:bg-zinc-800/20 border border-zinc-100 dark:border-zinc-800 flex items-center justify-between"
                >
                  <div className="truncate pr-2">
                    <span className="font-medium text-zinc-800 dark:text-zinc-200 block truncate">
                      {p.canonical_name}
                    </span>
                    <span className="text-[10px] text-zinc-400 font-mono truncate block">
                      {p.verified_domain}
                    </span>
                  </div>
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                </div>
              ))}
            </div>
          </div>

          {/* Copyright & Licensing Policy */}
          <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-800/40 border border-zinc-200 dark:border-zinc-800 text-[11px] text-zinc-500 space-y-1">
            <span className="font-semibold font-mono text-zinc-700 dark:text-zinc-300 block uppercase">
              Publisher Licensing & Rights Policy
            </span>
            <p>
              ATLAS respects publisher intellectual property rights and data distribution agreements. All headlines and excerpts are source-attributed. Full article texts remain on verified publisher websites.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-zinc-200 dark:border-zinc-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
