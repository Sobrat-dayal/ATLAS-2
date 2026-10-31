'use client';

import React, { useState } from 'react';
import { InfrastructureNetwork } from '@/lib/maps/infrastructure/types';
import { X, Network, Share2, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface InfrastructureNetworkInspectorProps {
  network: InfrastructureNetwork | null;
  onClose: () => void;
  onTraverse: (startNodeId: string, maxHops: number) => void;
  onFindPath: (startNodeId: string, targetNodeId: string) => void;
  subgraphResult?: any;
  pathResult?: any;
  isLoading?: boolean;
}

export const InfrastructureNetworkInspector: React.FC<InfrastructureNetworkInspectorProps> = ({
  network,
  onClose,
  onTraverse,
  onFindPath,
  subgraphResult,
  pathResult,
  isLoading,
}) => {
  const [startNode, setStartNode] = useState<string>('');
  const [targetNode, setTargetNode] = useState<string>('');
  const [maxHops, setMaxHops] = useState<number>(3);

  if (!network) return null;

  const nodes = network.nodes || [];
  const edges = network.edges || [];

  return (
    <div className="absolute right-4 top-16 bottom-4 w-96 max-w-[calc(100vw-32px)] bg-zinc-950/95 border border-zinc-800 rounded-xl shadow-2xl backdrop-blur-xl flex flex-col z-30 overflow-hidden text-xs">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800/80 bg-zinc-900/50 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider uppercase border border-purple-500/40 bg-purple-950/30 text-purple-400">
              Verified Topology
            </span>
            <span className="text-zinc-500 font-mono text-[11px]">{network.country}</span>
          </div>
          <h3 className="font-semibold text-sm text-zinc-100 truncate" title={network.name}>
            {network.name}
          </h3>
          <div className="flex items-center gap-2 mt-1 text-zinc-400 font-mono text-[11px]">
            <span>{nodes.length} Nodes</span>
            <span>•</span>
            <span>{edges.length} Conduits/Edges</span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-zinc-400 hover:text-zinc-100 bg-zinc-800/40 hover:bg-zinc-800 rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Traversal Controls */}
      <div className="p-4 border-b border-zinc-800/80 space-y-3 bg-zinc-900/30">
        <div className="text-[11px] font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
          <Share2 className="w-3.5 h-3.5 text-purple-400" />
          Bounded Graph Query
        </div>

        <div className="space-y-2">
          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-mono">Origin Node</label>
            <select
              value={startNode}
              onChange={(e) => setStartNode(e.target.value)}
              className="w-full mt-1 px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 text-xs focus:outline-none focus:border-purple-500/50"
            >
              <option value="">Select Starting Node...</option>
              {nodes.map((n) => (
                <option key={n.node_id} value={n.node_id}>
                  {n.name} ({n.node_type})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex-1">
              <label className="text-[10px] text-zinc-400 uppercase font-mono">Target Node (Optional)</label>
              <select
                value={targetNode}
                onChange={(e) => setTargetNode(e.target.value)}
                className="w-full mt-1 px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 text-xs focus:outline-none focus:border-purple-500/50"
              >
                <option value="">None (Reachability mode)</option>
                {nodes.map((n) => (
                  <option key={n.node_id} value={n.node_id}>
                    {n.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="w-20">
              <label className="text-[10px] text-zinc-400 uppercase font-mono">Max Depth</label>
              <input
                type="number"
                min={1}
                max={5}
                value={maxHops}
                onChange={(e) => setMaxHops(Number(e.target.value))}
                className="w-full mt-1 px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 text-xs text-center font-mono focus:outline-none focus:border-purple-500/50"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <button
              disabled={!startNode || isLoading}
              onClick={() => {
                if (targetNode) {
                  onFindPath(startNode, targetNode);
                } else {
                  onTraverse(startNode, maxHops);
                }
              }}
              className="flex-1 py-1.5 px-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium rounded transition-colors flex items-center justify-center gap-1.5"
            >
              <Network className="w-3.5 h-3.5" />
              {targetNode ? 'Find Shortest Path' : 'Explore Subgraph'}
            </button>
          </div>
        </div>
      </div>

      {/* Results and Edge Details */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {/* Shortest Path Result */}
        {pathResult && (
          <div className="p-3 bg-purple-950/30 border border-purple-800/40 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-purple-300 font-semibold">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Verified Path Found
              </span>
              <span className="font-mono text-[11px]">{pathResult.total_length_km.toFixed(1)} km</span>
            </div>
            <div className="text-[11px] text-zinc-300 space-y-1">
              <div className="text-zinc-500 font-mono text-[10px]">Hops: {pathResult.hop_count}</div>
              <div className="flex items-center gap-1 flex-wrap font-mono">
                {pathResult.path_node_ids.map((nid: string, idx: number) => (
                  <React.Fragment key={nid}>
                    <span className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 rounded">{nid}</span>
                    {idx < pathResult.path_node_ids.length - 1 && <ArrowRight className="w-3 h-3 text-zinc-500" />}
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Reachable Subgraph Result */}
        {subgraphResult && (
          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-zinc-200 font-semibold">
              <span>Reachable Subgraph</span>
              <span className="font-mono text-purple-400 text-[11px]">
                {subgraphResult.node_count} nodes reachable
              </span>
            </div>
            <div className="text-[10px] text-zinc-400">
              Traversed {subgraphResult.depth_reached} levels (depth bound: {subgraphResult.max_authorized_depth}).
            </div>
          </div>
        )}

        {/* Crossing Separation Invariant Banner */}
        <div className="p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-lg flex items-start gap-2.5 text-[10px] text-zinc-400 leading-relaxed">
          <ShieldAlert className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          <div>
            <strong className="text-zinc-300 font-semibold">Topology Invariant:</strong> Geometric
            crossings (pipelines or rail overpasses) do not establish connectivity without an explicit
            junction switch in source records.
          </div>
        </div>

        {/* Conduits List */}
        <div className="space-y-1.5 pt-2">
          <span className="text-[10px] font-semibold text-zinc-500 uppercase font-mono tracking-wider">
            Verified Physical Segments
          </span>
          <div className="space-y-1.5">
            {edges.map((e) => (
              <div key={e.edge_id} className="p-2 bg-zinc-900/40 border border-zinc-800/60 rounded text-[11px]">
                <div className="flex items-center justify-between text-zinc-300 font-medium">
                  <span>{e.edge_id}</span>
                  <span className="text-[10px] text-zinc-500 capitalize">{e.edge_type.replace('_', ' ')}</span>
                </div>
                <div className="flex items-center justify-between text-[10px] text-zinc-500 font-mono mt-1">
                  <span>{e.from_node_id} ➔ {e.to_node_id}</span>
                  {e.length_km && <span>{e.length_km.toFixed(1)} km</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
