'use client';

import React, { useState } from 'react';
import { AtlasEventEntityRelationship } from '@/lib/intelligence/graph/types';
import { PREDICATE_REGISTRY, VERIFICATION_STATUS_META } from '@/lib/intelligence/graph/predicates';
import { NODE_TYPE_CONFIGS } from '@/lib/intelligence/graph/nodeTypes';

interface GraphRelationshipInspectorProps {
  relationship: AtlasEventEntityRelationship;
  onClose: () => void;
  onRevoke?: (relationshipId: string, reason: string) => Promise<void>;
}

export function GraphRelationshipInspector({
  relationship,
  onClose,
  onRevoke,
}: GraphRelationshipInspectorProps) {
  const [isRevoking, setIsRevoking] = useState(false);
  const [revokeReason, setRevokeReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const predMeta = PREDICATE_REGISTRY[relationship.predicate];
  const verMeta = VERIFICATION_STATUS_META[relationship.verification_status];
  const sourceCfg = NODE_TYPE_CONFIGS[relationship.source_node.node_type];
  const targetCfg = NODE_TYPE_CONFIGS[relationship.target_node.node_type];

  const handleRevokeSubmit = async () => {
    if (!revokeReason.trim() || !onRevoke) return;
    setIsSubmitting(true);
    try {
      await onRevoke(relationship.relationship_id, revokeReason.trim());
      setIsRevoking(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full flex flex-col h-full bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden backdrop-blur">
      {/* Header */}
      <div className="p-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Relationship Inspector
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white text-xs px-2 py-0.5 rounded hover:bg-slate-800 transition"
          aria-label="Close relationship inspector"
        >
          ✕
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs text-slate-300">
        {/* Predicate Banner */}
        <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 space-y-1.5">
          <div className="flex items-center justify-between">
            <span
              className={`px-2 py-0.5 rounded border text-[11px] font-mono font-semibold ${
                predMeta?.badgeColor || 'bg-slate-800 text-slate-200'
              }`}
            >
              {predMeta?.label || relationship.predicate}
            </span>
            <span
              className={`px-2 py-0.5 rounded border text-[10px] ${
                verMeta?.badgeColor || 'bg-slate-800 text-slate-300'
              }`}
            >
              {verMeta?.label || relationship.verification_status}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            {predMeta?.description || 'Directed knowledge graph assertion.'}
          </p>
        </div>

        {/* Directed Nodes Connection */}
        <div className="space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Connected Topology
          </div>
          <div className="flex items-center gap-2 p-2.5 bg-slate-950/60 border border-slate-800/60 rounded-lg">
            <div className="flex-1 min-w-0">
              <span className="text-[9px] uppercase font-mono block text-slate-500">
                Source ({relationship.source_node.node_type})
              </span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: sourceCfg?.color || '#94a3b8' }}
                />
                <span className="font-medium text-slate-200 truncate">
                  {relationship.source_node.canonical_name}
                </span>
              </div>
            </div>
            <span className="text-slate-600 font-bold">→</span>
            <div className="flex-1 min-w-0">
              <span className="text-[9px] uppercase font-mono block text-slate-500">
                Target ({relationship.target_node.node_type})
              </span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: targetCfg?.color || '#94a3b8' }}
                />
                <span className="font-medium text-slate-200 truncate">
                  {relationship.target_node.canonical_name}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Role & Derivation */}
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="p-2 bg-slate-950/60 border border-slate-800/60 rounded-lg">
            <span className="text-[9px] uppercase font-mono text-slate-500 block">Assigned Role</span>
            <span className="font-medium text-slate-200 font-mono">
              {relationship.relationship_role || 'DIRECT_SUBJECT'}
            </span>
          </div>
          <div className="p-2 bg-slate-950/60 border border-slate-800/60 rounded-lg">
            <span className="text-[9px] uppercase font-mono text-slate-500 block">Derivation Method</span>
            <span className="font-medium text-slate-200 font-mono truncate block">
              {relationship.derivation_method}
            </span>
          </div>
        </div>

        {/* Proximity Metadata (If Spatial) */}
        {relationship.proximity_metadata && (
          <div className="p-3 bg-amber-950/20 border border-amber-800/40 rounded-lg space-y-1.5">
            <div className="flex items-center justify-between text-amber-300 font-medium">
              <span>Geospatial Proximity Calculation</span>
              <span className="font-mono text-xs">
                {relationship.proximity_metadata.distance_km} km
              </span>
            </div>
            <p className="text-[10px] text-amber-400/80 leading-relaxed">
              {relationship.proximity_metadata.disclaimer ||
                'Proximity calculation indicates spatial distance only; no physical damage or economic impairment asserted.'}
            </p>
          </div>
        )}

        {/* Supporting Evidence Records */}
        <div className="space-y-1.5">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Grounding Evidence ({relationship.evidence_ids.length})
          </div>
          {relationship.evidence_ids.length === 0 ? (
            <p className="text-slate-500 text-[11px] italic">No evidence links attached.</p>
          ) : (
            <div className="space-y-1">
              {relationship.evidence_ids.map((id) => (
                <div
                  key={id}
                  className="px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded font-mono text-[11px] text-slate-300 flex items-center justify-between"
                >
                  <span>{id}</span>
                  <span className="text-[9px] px-1 bg-slate-800 rounded text-slate-400">VERIFIED</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Temporal Validity & System Time */}
        <div className="p-2.5 bg-slate-950/60 border border-slate-800/60 rounded-lg space-y-1 text-[10px] font-mono text-slate-400">
          <div>
            <span className="text-slate-500">Knowledge Horizon:</span>{' '}
            <span className="text-slate-300">
              {relationship.knowledge_available_at ? new Date(relationship.knowledge_available_at).toUTCString() : '—'}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Valid From:</span>{' '}
            <span className="text-slate-300">
              {relationship.temporal_valid_from ? new Date(relationship.temporal_valid_from).toUTCString() : 'Permanent / Inception'}
            </span>
          </div>
          <div>
            <span className="text-slate-500">Valid To:</span>{' '}
            <span className="text-slate-300">
              {relationship.temporal_valid_to ? new Date(relationship.temporal_valid_to).toUTCString() : 'Open / Indefinite'}
            </span>
          </div>
        </div>

        {/* Revocation Section */}
        {relationship.is_revoked ? (
          <div className="p-2.5 bg-rose-950/30 border border-rose-800/50 rounded-lg text-rose-300 text-xs">
            <span className="font-semibold block">Relationship Revoked</span>
            <span className="text-[10px] text-rose-400/80">
              Reason: {relationship.revocation_reason || 'De-authorized or contradicted.'}
            </span>
          </div>
        ) : (
          onRevoke && (
            <div className="pt-2 border-t border-slate-800/80">
              {isRevoking ? (
                <div className="space-y-2">
                  <textarea
                    value={revokeReason}
                    onChange={(e) => setRevokeReason(e.target.value)}
                    placeholder="Enter reason for institutional revocation (e.g. source debunked, license expired)..."
                    rows={2}
                    className="w-full p-2 bg-slate-950 border border-slate-800 rounded text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500"
                  />
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => setIsRevoking(false)}
                      className="px-2 py-1 text-slate-400 hover:text-white rounded transition"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleRevokeSubmit}
                      disabled={!revokeReason.trim() || isSubmitting}
                      className="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white font-medium rounded transition disabled:opacity-50"
                    >
                      {isSubmitting ? 'Revoking...' : 'Confirm Revocation'}
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setIsRevoking(true)}
                  className="w-full py-1.5 text-xs text-rose-400 hover:text-rose-300 border border-rose-900/40 hover:bg-rose-950/20 rounded transition"
                >
                  Revoke Relationship Edge
                </button>
              )}
            </div>
          )
        )}
      </div>
    </div>
  );
}

