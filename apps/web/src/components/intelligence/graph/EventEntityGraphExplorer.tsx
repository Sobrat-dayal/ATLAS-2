'use client';

import React, { useEffect, useState } from 'react';
import {
  AtlasEventEntityRelationship,
  CanonicalGraphNodeRef,
  GraphNodeType,
  GraphPath,
  PredicateType,
  RelationshipVerificationStatus,
} from '@/lib/intelligence/graph/types';
import {
  evaluateAsOf,
  findGraphPaths,
  getEventNeighbors,
  getGraphNeighborhood,
  getKnowledgeGraphCapabilities,
  getReviewQueue,
  revokeRelationship,
} from '@/lib/intelligence/graph/api';
import { GraphCanvas } from './GraphCanvas';
import { GraphTableView } from './GraphTableView';
import { GraphRelationshipInspector } from './GraphRelationshipInspector';
import { GraphPathInspector } from './GraphPathInspector';
import { GraphHistoricalControls } from './GraphHistoricalControls';

const REFERENCE_CHIPS = [
  { label: 'Apple Q3 Earnings', eventId: 'EVT-EARNINGS-AAPL-2024Q3' },
  { label: 'Alphabet Governance', eventId: 'EVT-CORP-GOOGL-GOV' },
  { label: 'Volga Sanctions (Exact)', eventId: 'EVT-SANCTION-VOLGA-PETRO' },
  { label: 'FOMC Rate Decision', eventId: 'EVT-FOMC-20230726' },
  { label: 'US CPI Release', eventId: 'EVT-CPI-US-202406' },
  { label: 'MSFT/ATVI Merger', eventId: 'EVT-MERGER-MSFT-ATVI' },
  { label: 'DeepMind Gemini (Multi-hop)', eventId: 'EVT-PRODUCT-DEEPMIND-GEMINI' },
  { label: 'Sendai Earthquake (Spatial)', eventId: 'EVT-QUAKE-SENDAI-2024' },
  { label: 'Colonial Pipeline Outage', eventId: 'EVT-PIPELINE-OUTAGE-COLONIAL' },
  { label: 'TSMC Arizona Fab', eventId: 'EVT-TSMC-AZ-FAB' },
];

export function EventEntityGraphExplorer() {
  // State
  const [activeView, setActiveView] = useState<'canvas' | 'table'>('canvas');
  const [nodes, setNodes] = useState<CanonicalGraphNodeRef[]>([]);
  const [relationships, setRelationships] = useState<AtlasEventEntityRelationship[]>([]);
  const [selectedNode, setSelectedNode] = useState<CanonicalGraphNodeRef | null>(null);
  const [selectedRelationship, setSelectedRelationship] = useState<AtlasEventEntityRelationship | null>(null);
  const [discoveredPaths, setDiscoveredPaths] = useState<GraphPath[] | null>(null);
  const [asOfTime, setAsOfTime] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [reviewQueue, setReviewQueue] = useState<any[]>([]);
  const [isReviewQueueOpen, setIsReviewQueueOpen] = useState(false);

  // Path discovery inputs
  const [isPathDiscoveryOpen, setIsPathDiscoveryOpen] = useState(false);
  const [pathSourceType, setPathSourceType] = useState<GraphNodeType>('EVENT');
  const [pathSourceId, setPathSourceId] = useState('EVT-PRODUCT-DEEPMIND-GEMINI');
  const [pathTargetType, setPathTargetType] = useState<GraphNodeType>('COMPANY');
  const [pathTargetId, setPathTargetId] = useState('COMP-GOOGL');
  const [pathMaxDepth, setPathMaxDepth] = useState(3);

  // Initial load
  useEffect(() => {
    loadEventGraph('EVT-EARNINGS-AAPL-2024Q3');
    loadReviewQueue();
  }, []);

  const loadEventGraph = async (eventId: string, horizon?: string | null) => {
    setIsLoading(true);
    setErrorMessage(null);
    setSelectedRelationship(null);
    setDiscoveredPaths(null);

    try {
      const rels = await getEventNeighbors(eventId, { asOf: horizon || undefined });
      setRelationships(rels);

      // Collect all distinct nodes (source + targets)
      const nodeMap = new Map<string, CanonicalGraphNodeRef>();
      rels.forEach((r) => {
        nodeMap.set(`${r.source_node.node_type}:${r.source_node.entity_id}`, r.source_node);
        nodeMap.set(`${r.target_node.node_type}:${r.target_node.entity_id}`, r.target_node);
      });
      const collected = Array.from(nodeMap.values());
      setNodes(collected);

      // Default select center or first node
      if (collected.length > 0) {
        setSelectedNode(collected[0]);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load knowledge graph relationships.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadReviewQueue = async () => {
    try {
      const queue = await getReviewQueue();
      setReviewQueue(queue);
    } catch {
      // Ignore
    }
  };

  const handleApplyAsOf = async (horizon: string | null) => {
    setAsOfTime(horizon);
    if (!horizon) {
      loadEventGraph('EVT-EARNINGS-AAPL-2024Q3', null);
      return;
    }

    setIsLoading(true);
    try {
      const asOfRels = await evaluateAsOf(horizon);
      setRelationships(asOfRels);
      const nodeMap = new Map<string, CanonicalGraphNodeRef>();
      asOfRels.forEach((r) => {
        nodeMap.set(`${r.source_node.node_type}:${r.source_node.entity_id}`, r.source_node);
        nodeMap.set(`${r.target_node.node_type}:${r.target_node.entity_id}`, r.target_node);
      });
      setNodes(Array.from(nodeMap.values()));
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to evaluate historical as-of horizon.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunPathDiscovery = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const paths = await findGraphPaths(
        pathSourceType,
        pathSourceId.trim(),
        pathTargetType,
        pathTargetId.trim(),
        pathMaxDepth,
        asOfTime || undefined
      );
      setDiscoveredPaths(paths);
      setIsPathDiscoveryOpen(false);

      // If paths found, expand nodes and relationships to include all hops
      const pathNodeMap = new Map<string, CanonicalGraphNodeRef>();
      const pathRels: AtlasEventEntityRelationship[] = [];

      paths.forEach((p) => {
        pathNodeMap.set(`${p.source_node.node_type}:${p.source_node.entity_id}`, p.source_node);
        pathNodeMap.set(`${p.target_node.node_type}:${p.target_node.entity_id}`, p.target_node);
        p.hops.forEach((h) => {
          pathNodeMap.set(`${h.from_node.node_type}:${h.from_node.entity_id}`, h.from_node);
          pathNodeMap.set(`${h.to_node.node_type}:${h.to_node.entity_id}`, h.to_node);
        });
      });

      if (pathNodeMap.size > 0) {
        setNodes(Array.from(pathNodeMap.values()));
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Path discovery failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevokeRelationship = async (relationshipId: string, reason: string) => {
    try {
      await revokeRelationship(relationshipId, reason);
      // Update local state
      setRelationships((prev) =>
        prev.map((r) =>
          r.relationship_id === relationshipId
            ? { ...r, is_revoked: true, revocation_reason: reason, verification_status: 'REVOKED' }
            : r
        )
      );
      if (selectedRelationship?.relationship_id === relationshipId) {
        setSelectedRelationship((prev) =>
          prev ? { ...prev, is_revoked: true, revocation_reason: reason, verification_status: 'REVOKED' } : null
        );
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Revocation failed.');
    }
  };

  const selectedNodeKey = selectedNode ? `${selectedNode.node_type}:${selectedNode.entity_id}` : null;

  return (
    <div className="w-full flex flex-col h-[calc(100vh-6rem)] min-h-[650px] p-4 bg-slate-950 text-slate-100 gap-3">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-900/80 border border-slate-800 rounded-xl backdrop-blur">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 font-bold text-sm">
            KG
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-wide">
              Event-to-Entity Knowledge Graph
            </h1>
            <p className="text-[11px] text-slate-400">
              Institutional typed relationships, zero-speculation multi-hop traversal & bitemporal validities
            </p>
          </div>
        </div>

        {/* Right Toolbar */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* As-Of Historical Controls */}
          <GraphHistoricalControls asOfTime={asOfTime} onApplyAsOf={handleApplyAsOf} />

          {/* Path Discovery Button */}
          <button
            onClick={() => setIsPathDiscoveryOpen(!isPathDiscoveryOpen)}
            className="px-2.5 py-1 text-xs bg-slate-900 border border-slate-700 hover:border-sky-500 hover:text-white text-slate-300 rounded-lg transition"
          >
            Find Path
          </button>

          {/* Review Queue Badge */}
          {reviewQueue.length > 0 && (
            <button
              onClick={() => setIsReviewQueueOpen(true)}
              className="px-2 py-1 text-xs bg-amber-950/40 border border-amber-700/50 text-amber-300 rounded-lg transition hover:bg-amber-900/40 flex items-center gap-1.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
              <span>Review Queue ({reviewQueue.length})</span>
            </button>
          )}

          {/* View Toggle */}
          <div className="flex items-center p-0.5 bg-slate-950 border border-slate-800 rounded-lg text-xs">
            <button
              onClick={() => setActiveView('canvas')}
              className={`px-2.5 py-1 rounded-md transition ${
                activeView === 'canvas' ? 'bg-sky-600 text-white font-medium' : 'text-slate-400 hover:text-white'
              }`}
            >
              Canvas
            </button>
            <button
              onClick={() => setActiveView('table')}
              className={`px-2.5 py-1 rounded-md transition ${
                activeView === 'table' ? 'bg-sky-600 text-white font-medium' : 'text-slate-400 hover:text-white'
              }`}
            >
              Table
            </button>
          </div>
        </div>
      </div>

      {/* Reference Chips Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs scrollbar-none">
        <span className="text-slate-500 font-mono text-[10px] uppercase shrink-0">Fixtures:</span>
        {REFERENCE_CHIPS.map((chip) => (
          <button
            key={chip.eventId}
            onClick={() => loadEventGraph(chip.eventId, asOfTime)}
            className="px-2.5 py-1 rounded-lg bg-slate-900/70 border border-slate-800 hover:border-sky-500/50 hover:bg-slate-800 text-slate-300 text-xs shrink-0 transition"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Historical Alert Banner */}
      {asOfTime && (
        <div className="p-2 bg-amber-950/30 border border-amber-800/50 rounded-lg text-amber-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-semibold uppercase tracking-wider text-[10px]">Historical As-Of Mode:</span>
            <span>Evaluating knowledge graph strictly known as-of {new Date(asOfTime).toUTCString()} (Zero Look-Ahead Bias enforced)</span>
          </div>
          <button
            onClick={() => handleApplyAsOf(null)}
            className="underline text-amber-200 hover:text-white"
          >
            Return to live
          </button>
        </div>
      )}

      {/* Error Banner */}
      {errorMessage && (
        <div className="p-2.5 bg-rose-950/40 border border-rose-800/60 rounded-lg text-rose-300 text-xs flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Main Workspace: Left Canvas/Table & Right Inspector */}
      <div className="flex-1 flex gap-3 min-h-0">
        {/* Left: Canvas or Table */}
        <div className="flex-1 min-w-0 h-full relative">
          {isLoading && (
            <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm z-30 flex items-center justify-center">
              <div className="text-sky-400 text-xs font-mono animate-pulse">Loading Knowledge Graph...</div>
            </div>
          )}

          {activeView === 'canvas' ? (
            <GraphCanvas
              nodes={nodes}
              relationships={relationships}
              selectedNodeKey={selectedNodeKey}
              selectedRelationshipId={selectedRelationship?.relationship_id}
              onSelectNode={(node) => {
                setSelectedNode(node);
                setSelectedRelationship(null);
              }}
              onSelectRelationship={(rel) => {
                setSelectedRelationship(rel);
                setDiscoveredPaths(null);
              }}
            />
          ) : (
            <GraphTableView
              relationships={relationships}
              selectedRelationshipId={selectedRelationship?.relationship_id}
              onSelectRelationship={(rel) => {
                setSelectedRelationship(rel);
                setDiscoveredPaths(null);
              }}
            />
          )}
        </div>

        {/* Right Pane: Inspector or Path Breakdown */}
        <div className="w-80 md:w-96 shrink-0 h-full flex flex-col">
          {discoveredPaths ? (
            <GraphPathInspector
              paths={discoveredPaths}
              onClose={() => setDiscoveredPaths(null)}
            />
          ) : selectedRelationship ? (
            <GraphRelationshipInspector
              relationship={selectedRelationship}
              onClose={() => setSelectedRelationship(null)}
              onRevoke={handleRevokeRelationship}
            />
          ) : selectedNode ? (
            <div className="w-full flex flex-col h-full bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden backdrop-blur p-4 space-y-4 text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-[10px] uppercase font-mono text-slate-500">Node Overview</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300">
                  {selectedNode.node_type}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-100">
                  {selectedNode.canonical_name}
                </h3>
                <span className="text-slate-400 font-mono text-[11px] block mt-0.5">
                  ID: {selectedNode.entity_id}
                </span>
              </div>

              {/* Identifiers */}
              {selectedNode.identifier_map && Object.keys(selectedNode.identifier_map).length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-[10px] uppercase font-semibold text-slate-500">Identifiers</span>
                  <div className="grid grid-cols-2 gap-1.5 font-mono text-[10px]">
                    {Object.entries(selectedNode.identifier_map).map(([k, v]) => (
                      <div key={k} className="p-1.5 bg-slate-950 border border-slate-800 rounded">
                        <span className="text-slate-500 block text-[9px]">{k}</span>
                        <span className="text-slate-300 font-medium truncate block">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Connected edges summary */}
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg space-y-1 text-slate-400 text-[11px]">
                <div className="flex justify-between">
                  <span>Connected Edges:</span>
                  <span className="text-slate-200 font-mono font-medium">
                    {relationships.filter(
                      (r) =>
                        r.source_node.entity_id === selectedNode.entity_id ||
                        r.target_node.entity_id === selectedNode.entity_id
                    ).length}
                  </span>
                </div>
              </div>

              <div className="mt-auto pt-4 border-t border-slate-800">
                <p className="text-[10px] text-slate-500 leading-relaxed italic">
                  Select an edge connecting this node to inspect supporting evidence records, assertions, and bitemporal audit horizons.
                </p>
              </div>
            </div>
          ) : (
            <div className="w-full flex flex-col h-full bg-slate-900/60 border border-slate-800 rounded-xl items-center justify-center p-6 text-center text-slate-500 text-xs">
              Select any node or relationship edge on the canvas to inspect its verified details.
            </div>
          )}
        </div>
      </div>

      {/* Path Discovery Modal */}
      {isPathDiscoveryOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                Discover Multi-Hop Knowledge Path
              </h3>
              <button
                onClick={() => setIsPathDiscoveryOpen(false)}
                className="text-slate-400 hover:text-white text-xs"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 text-[11px]">Source Node</label>
                <div className="flex gap-2">
                  <select
                    value={pathSourceType}
                    onChange={(e) => setPathSourceType(e.target.value as GraphNodeType)}
                    className="p-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs"
                  >
                    <option value="EVENT">EVENT</option>
                    <option value="COMPANY">COMPANY</option>
                    <option value="LEGAL_ENTITY">LEGAL_ENTITY</option>
                    <option value="FINANCIAL_INSTRUMENT">FINANCIAL_INSTRUMENT</option>
                  </select>
                  <input
                    type="text"
                    value={pathSourceId}
                    onChange={(e) => setPathSourceId(e.target.value)}
                    placeholder="Source Entity ID..."
                    className="flex-1 p-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 text-[11px]">Target Node</label>
                <div className="flex gap-2">
                  <select
                    value={pathTargetType}
                    onChange={(e) => setPathTargetType(e.target.value as GraphNodeType)}
                    className="p-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs"
                  >
                    <option value="COMPANY">COMPANY</option>
                    <option value="EVENT">EVENT</option>
                    <option value="LEGAL_ENTITY">LEGAL_ENTITY</option>
                    <option value="FINANCIAL_INSTRUMENT">FINANCIAL_INSTRUMENT</option>
                  </select>
                  <input
                    type="text"
                    value={pathTargetId}
                    onChange={(e) => setPathTargetId(e.target.value)}
                    placeholder="Target Entity ID..."
                    className="flex-1 p-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 text-[11px]">
                  Max Traversal Depth (1 - 5 hops)
                </label>
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={pathMaxDepth}
                  onChange={(e) => setPathMaxDepth(Math.min(5, Math.max(1, parseInt(e.target.value) || 1)))}
                  className="w-full p-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setIsPathDiscoveryOpen(false)}
                className="px-3 py-1 text-slate-400 hover:text-white rounded text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleRunPathDiscovery}
                disabled={isLoading}
                className="px-3 py-1 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-medium"
              >
                {isLoading ? 'Traversing...' : 'Discover Paths'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Review Queue Modal */}
      {isReviewQueueOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                Uncorroborated & Candidate Review Queue ({reviewQueue.length})
              </h3>
              <button
                onClick={() => setIsReviewQueueOpen(false)}
                className="text-slate-400 hover:text-white text-xs"
              >
                ✕
              </button>
            </div>

            <div className="max-h-80 overflow-y-auto space-y-2 text-xs">
              {reviewQueue.length === 0 ? (
                <p className="text-slate-500 text-center py-4">No relationships pending review.</p>
              ) : (
                reviewQueue.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-sky-400 font-semibold">{item.relationship_id}</span>
                      <span className="px-1.5 py-0.2 rounded border border-amber-800 bg-amber-950 text-amber-300 text-[10px]">
                        {item.status}
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px]">{item.reason}</p>
                    <span className="text-[10px] text-slate-500 font-mono block">Event: {item.event_id}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
