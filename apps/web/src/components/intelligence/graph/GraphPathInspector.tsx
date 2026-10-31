'use client';

import React from 'react';
import { GraphPath } from '@/lib/intelligence/graph/types';
import { PREDICATE_REGISTRY, VERIFICATION_STATUS_META } from '@/lib/intelligence/graph/predicates';
import { NODE_TYPE_CONFIGS } from '@/lib/intelligence/graph/nodeTypes';

interface GraphPathInspectorProps {
  paths: GraphPath[];
  onClose: () => void;
}

export function GraphPathInspector({ paths, onClose }: GraphPathInspectorProps) {
  return (
    <div className="w-full flex flex-col h-full bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden backdrop-blur">
      {/* Header */}
      <div className="p-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Multi-Hop Path Discovery ({paths.length})
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white text-xs px-2 py-0.5 rounded hover:bg-slate-800 transition"
          aria-label="Close path inspector"
        >
          ✕
        </button>
      </div>

      {/* Path List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs text-slate-300">
        {paths.length === 0 ? (
          <div className="py-8 text-center text-slate-500">
            No verified paths found connecting selected nodes within allowable depth.
          </div>
        ) : (
          paths.map((path, idx) => (
            <div
              key={path.path_id}
              className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-3"
            >
              <div className="flex items-center justify-between border-b border-slate-800/50 pb-2">
                <span className="font-semibold text-slate-200 text-xs">
                  Path {idx + 1}: {path.total_hops} Hop{path.total_hops === 1 ? '' : 's'}
                </span>
                <span className="px-2 py-0.5 rounded bg-slate-900 text-[10px] font-mono text-slate-400 border border-slate-800">
                  {path.path_id}
                </span>
              </div>

              {/* Hop Breakdown */}
              <div className="space-y-2">
                {path.hops.map((hop) => {
                  const predMeta = PREDICATE_REGISTRY[hop.predicate];
                  const verMeta = VERIFICATION_STATUS_META[hop.verification_status];
                  const fromCfg = NODE_TYPE_CONFIGS[hop.from_node.node_type];
                  const toCfg = NODE_TYPE_CONFIGS[hop.to_node.node_type];

                  return (
                    <div
                      key={`${hop.hop_number}-${hop.relationship_id}`}
                      className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/60 space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="font-mono text-sky-400 font-semibold">
                          Hop #{hop.hop_number}
                        </span>
                        <span
                          className={`px-1.5 py-0.2 rounded border text-[9px] ${
                            verMeta?.badgeColor || 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {verMeta?.label || hop.verification_status}
                        </span>
                      </div>

                      {/* Connection */}
                      <div className="flex items-center gap-1.5 text-[11px]">
                        <div className="flex items-center gap-1 min-w-0">
                          <span
                            className="w-1.5 h-1.5 rounded-full shrink-0"
                            style={{ backgroundColor: fromCfg?.color || '#94a3b8' }}
                          />
                          <span className="font-medium text-slate-300 truncate">
                            {hop.from_node.canonical_name}
                          </span>
                        </div>

                        <span
                          className={`px-1.5 py-0.2 rounded border text-[10px] font-mono font-medium shrink-0 ${
                            predMeta?.badgeColor || 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {predMeta?.label || hop.predicate}
                        </span>

                        <div className="flex items-center gap-1 min-w-0">
                          <span
                            className="w-1.5 h-1.5 rounded-full shrink-0"
                            style={{ backgroundColor: toCfg?.color || '#94a3b8' }}
                          />
                          <span className="font-medium text-slate-300 truncate">
                            {hop.to_node.canonical_name}
                          </span>
                        </div>
                      </div>

                      {/* Hop explanation */}
                      <p className="text-[10px] text-slate-400 leading-normal">
                        {hop.explanation}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Path Explanation Notice */}
              <div className="p-2.5 rounded-lg bg-slate-900/40 border border-slate-800/40 text-[10px] text-slate-400 leading-relaxed font-mono">
                <span className="text-slate-300 font-semibold block mb-0.5">
                  Factual Summary:
                </span>
                {path.factual_explanation}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
