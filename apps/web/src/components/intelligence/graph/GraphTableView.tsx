'use client';

import React, { useState } from 'react';
import { AtlasEventEntityRelationship } from '@/lib/intelligence/graph/types';
import { PREDICATE_REGISTRY, VERIFICATION_STATUS_META } from '@/lib/intelligence/graph/predicates';
import { NODE_TYPE_CONFIGS } from '@/lib/intelligence/graph/nodeTypes';

interface GraphTableViewProps {
  relationships: AtlasEventEntityRelationship[];
  selectedRelationshipId?: string | null;
  onSelectRelationship: (rel: AtlasEventEntityRelationship) => void;
}

export function GraphTableView({
  relationships,
  selectedRelationshipId,
  onSelectRelationship,
}: GraphTableViewProps) {
  const [filterQuery, setFilterQuery] = useState('');

  const filtered = relationships.filter((rel) => {
    const q = filterQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      rel.source_node.canonical_name.toLowerCase().includes(q) ||
      rel.target_node.canonical_name.toLowerCase().includes(q) ||
      rel.predicate.toLowerCase().includes(q) ||
      (rel.relationship_role && rel.relationship_role.toLowerCase().includes(q))
    );
  });

  return (
    <div className="w-full flex flex-col h-full bg-slate-950/70 border border-slate-800/80 rounded-xl overflow-hidden">
      {/* Table Header Filter */}
      <div className="p-3 border-b border-slate-800/80 flex items-center justify-between gap-4 bg-slate-900/60">
        <input
          type="text"
          value={filterQuery}
          onChange={(e) => setFilterQuery(e.target.value)}
          placeholder="Filter relationships by source, target, or predicate..."
          className="w-full max-w-sm px-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
          aria-label="Filter relationships"
        />
        <span className="text-xs text-slate-400">
          Showing {filtered.length} of {relationships.length} edges
        </span>
      </div>

      {/* Accessible Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left text-xs text-slate-300 border-collapse">
          <thead className="sticky top-0 bg-slate-900/90 backdrop-blur z-10 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
            <tr>
              <th className="py-2.5 px-3">Source Node</th>
              <th className="py-2.5 px-3">Predicate</th>
              <th className="py-2.5 px-3">Target Node</th>
              <th className="py-2.5 px-3">Role</th>
              <th className="py-2.5 px-3">Verification</th>
              <th className="py-2.5 px-3">Evidence</th>
              <th className="py-2.5 px-3">As Of Available</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No relationships matching filter.
                </td>
              </tr>
            ) : (
              filtered.map((rel) => {
                const isSelected = selectedRelationshipId === rel.relationship_id;
                const predMeta = PREDICATE_REGISTRY[rel.predicate];
                const verMeta = VERIFICATION_STATUS_META[rel.verification_status];
                const sCfg = NODE_TYPE_CONFIGS[rel.source_node.node_type];
                const tCfg = NODE_TYPE_CONFIGS[rel.target_node.node_type];

                return (
                  <tr
                    key={rel.relationship_id}
                    onClick={() => onSelectRelationship(rel)}
                    className={`cursor-pointer transition hover:bg-slate-800/40 ${
                      isSelected ? 'bg-sky-950/40 border-l-2 border-sky-400' : ''
                    }`}
                  >
                    <td className="py-2 px-3 font-medium text-slate-200">
                      <div className="flex items-center gap-1.5">
                        <span
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: sCfg?.color || '#94a3b8' }}
                        />
                        <span className="truncate max-w-[180px]">
                          {rel.source_node.canonical_name}
                        </span>
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded border text-[11px] font-mono ${
                          predMeta?.badgeColor || 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {predMeta?.label || rel.predicate}
                      </span>
                    </td>
                    <td className="py-2 px-3 font-medium text-slate-200">
                      <div className="flex items-center gap-1.5">
                        <span
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: tCfg?.color || '#94a3b8' }}
                        />
                        <span className="truncate max-w-[180px]">
                          {rel.target_node.canonical_name}
                        </span>
                      </div>
                    </td>
                    <td className="py-2 px-3 text-slate-400 font-mono text-[11px]">
                      {rel.relationship_role || '—'}
                    </td>
                    <td className="py-2 px-3">
                      <span
                        className={`inline-block px-1.5 py-0.5 rounded border text-[10px] ${
                          verMeta?.badgeColor || 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {verMeta?.label || rel.verification_status}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-400">
                      <span className="px-1.5 py-0.5 bg-slate-900 border border-slate-800 rounded text-[10px] font-mono">
                        {rel.evidence_ids.length} doc{rel.evidence_ids.length === 1 ? '' : 's'}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-400 font-mono text-[10px]">
                      {rel.knowledge_available_at ? rel.knowledge_available_at.slice(0, 10) : '—'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

