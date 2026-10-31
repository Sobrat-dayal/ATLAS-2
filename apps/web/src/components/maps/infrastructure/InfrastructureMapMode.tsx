'use client';

import React, { useState } from 'react';
import { useInfrastructureAssets } from '@/hooks/maps/infrastructure/useInfrastructureAssets';
import { useInfrastructureNetworks } from '@/hooks/maps/infrastructure/useInfrastructureNetworks';
import { useInfrastructureFilters } from '@/hooks/maps/infrastructure/useInfrastructureFilters';
import { InfrastructureSectorPanel } from './InfrastructureSectorPanel';
import { InfrastructureFilters } from './InfrastructureFilters';
import { InfrastructureAssetInspector } from './InfrastructureAssetInspector';
import { InfrastructureNetworkInspector } from './InfrastructureNetworkInspector';
import { InfrastructureRegionalSummary } from './InfrastructureRegionalSummary';
import { InfrastructureAssetComparison } from './InfrastructureAssetComparison';
import { InfrastructureNetworkLegend } from './InfrastructureNetworkLegend';
import { compareInfrastructureAssets, fetchRegionalSummary } from '@/lib/maps/infrastructure/api';
import { RegionalSummary } from '@/lib/maps/infrastructure/types';
import {
  Network,
  BarChart3,
  Layers,
  ArrowLeftRight,
  Filter,
} from 'lucide-react';

interface InfrastructureMapModeProps {
  onSelectAsset?: (assetId: string) => void;
  selectedAssetId?: string | null;
  onCloseMode?: () => void;
}

export const InfrastructureMapMode: React.FC<InfrastructureMapModeProps> = ({
  onSelectAsset,
  selectedAssetId,
  onCloseMode,
}) => {
  const {
    filters,
    toggleSector,
    selectAllSectors,
    clearSectors,
    setStatus,
    setCountry,
    setSearch,
    setHistoricalAsOf,
    resetFilters,
  } = useInfrastructureFilters();

  const {
    assets,
    selectedAsset,
    selectAsset,
    setSelectedAsset,
  } = useInfrastructureAssets();

  const {
    networks,
    activeNetwork,
    subgraph,
    pathResult,
    selectNetwork,
    traverseSubgraph,
    findPath,
    isLoading: isNetworkLoading,
  } = useInfrastructureNetworks();

  const [activeSubMode, setActiveSubMode] = useState<'assets' | 'networks' | 'analytics'>('assets');
  const [showSectorPanel, setShowSectorPanel] = useState<boolean>(true);
  const [regionalSummary, setRegionalSummary] = useState<RegionalSummary | null>(null);
  const [comparisonData, setComparisonData] = useState<any | null>(null);

  // Sync external selection
  React.useEffect(() => {
    if (selectedAssetId && (!selectedAsset || selectedAsset.asset_id !== selectedAssetId)) {
      selectAsset(selectedAssetId);
    }
  }, [selectedAssetId, selectAsset, selectedAsset]);

  // Count assets by sector
  const sectorCounts: Record<string, number> = {};
  assets.forEach((a) => {
    sectorCounts[a.sector] = (sectorCounts[a.sector] || 0) + 1;
  });

  const handleOpenRegionalSummary = async () => {
    try {
      const summary = await fetchRegionalSummary('Global Infrastructure Overview');
      setRegionalSummary(summary);
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenComparison = async () => {
    if (assets.length < 2) return;
    try {
      const sampleIds = assets.slice(0, 3).map((a) => a.asset_id);
      const comp = await compareInfrastructureAssets(sampleIds);
      setComparisonData(comp);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      {/* Top Floating Infrastructure Bar */}
      <div className="absolute top-16 left-4 z-20 flex flex-col gap-2 max-w-xl">
        {/* Navigation tabs & Action toggles */}
        <div className="flex items-center gap-1.5 p-1.5 bg-zinc-950/90 border border-zinc-800 rounded-lg shadow-xl backdrop-blur-md text-xs">
          <button
            onClick={() => setActiveSubMode('assets')}
            className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
              activeSubMode === 'assets'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            Assets ({assets.length})
          </button>

          <button
            onClick={() => {
              setActiveSubMode('networks');
              if (networks.length > 0 && !activeNetwork) {
                selectNetwork(networks[0].network_id);
              }
            }}
            className={`px-3 py-1.5 rounded font-medium transition-colors flex items-center gap-1.5 ${
              activeSubMode === 'networks'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Network className="w-3.5 h-3.5 text-purple-400" />
            Topology ({networks.length})
          </button>

          <span className="text-zinc-700">|</span>

          <button
            onClick={handleOpenRegionalSummary}
            className="px-2.5 py-1.5 text-zinc-400 hover:text-zinc-100 rounded transition-colors flex items-center gap-1"
            title="Regional Profile Summary"
          >
            <BarChart3 className="w-3.5 h-3.5 text-amber-400" />
            Analytics
          </button>

          <button
            onClick={handleOpenComparison}
            className="px-2.5 py-1.5 text-zinc-400 hover:text-zinc-100 rounded transition-colors flex items-center gap-1"
            title="Side-by-Side Comparison"
          >
            <ArrowLeftRight className="w-3.5 h-3.5 text-emerald-400" />
            Compare
          </button>

          <button
            onClick={() => setShowSectorPanel(!showSectorPanel)}
            className={`p-1.5 rounded transition-colors ml-auto ${
              showSectorPanel ? 'bg-zinc-800 text-zinc-200' : 'text-zinc-400 hover:text-zinc-200'
            }`}
            title="Toggle Sector Panel"
          >
            <Filter className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Filters */}
        <InfrastructureFilters
          filters={filters}
          onSearchChange={setSearch}
          onCountryChange={setCountry}
          onStatusChange={setStatus}
          onHistoricalDateChange={setHistoricalAsOf}
          onReset={resetFilters}
        />

        {/* Collapsible Sector Panel */}
        {showSectorPanel && (
          <InfrastructureSectorPanel
            selectedSectors={filters.selectedSectors}
            onToggleSector={toggleSector}
            onSelectAll={selectAllSectors}
            onClearAll={clearSectors}
            sectorCounts={sectorCounts}
          />
        )}
      </div>

      {/* Bottom Left Legend */}
      <div className="absolute bottom-6 left-4 z-20">
        <InfrastructureNetworkLegend />
      </div>

      {/* Right Drawer: Asset Inspector */}
      {selectedAsset && (
        <InfrastructureAssetInspector
          asset={selectedAsset}
          onClose={() => {
            setSelectedAsset(null);
            if (onSelectAsset) onSelectAsset('');
          }}
        />
      )}

      {/* Right Drawer: Network Inspector */}
      {activeSubMode === 'networks' && activeNetwork && (
        <InfrastructureNetworkInspector
          network={activeNetwork}
          onClose={() => setActiveSubMode('assets')}
          onTraverse={traverseSubgraph}
          onFindPath={findPath}
          subgraphResult={subgraph}
          pathResult={pathResult}
          isLoading={isNetworkLoading}
        />
      )}

      {/* Left Modal: Regional Summary */}
      {regionalSummary && (
        <InfrastructureRegionalSummary
          summary={regionalSummary}
          onClose={() => setRegionalSummary(null)}
        />
      )}

      {/* Center Modal: Asset Comparison */}
      {comparisonData && (
        <InfrastructureAssetComparison
          comparisonData={comparisonData}
          onClose={() => setComparisonData(null)}
        />
      )}
    </>
  );
};
