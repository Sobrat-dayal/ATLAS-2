'use client';

import React from 'react';
import { InfrastructureAsset } from '@/lib/maps/infrastructure/types';
import { SECTOR_VISUALS, STATUS_STYLES, PRECISION_STYLES } from '@/lib/maps/infrastructure/sectorStyles';
import { formatCapacityDisplay } from '@/lib/maps/infrastructure/capacityUnits';
import { X, ExternalLink, ShieldCheck, MapPin, Building, History, Activity } from 'lucide-react';

interface InfrastructureAssetInspectorProps {
  asset: InfrastructureAsset | null;
  onClose: () => void;
  onSelectRelatedAsset?: (assetId: string) => void;
}

export const InfrastructureAssetInspector: React.FC<InfrastructureAssetInspectorProps> = ({
  asset,
  onClose,
  onSelectRelatedAsset,
}) => {
  if (!asset) return null;

  const sectorMeta = SECTOR_VISUALS[asset.sector as keyof typeof SECTOR_VISUALS] || {
    label: asset.sector,
    color: '#38bdf8',
    borderColor: '#38bdf8',
  };
  const statusMeta = STATUS_STYLES[asset.status] || STATUS_STYLES.unknown;
  const precisionMeta = PRECISION_STYLES[asset.precision] || PRECISION_STYLES.approximate;

  return (
    <div className="absolute right-4 top-16 bottom-4 w-96 max-w-[calc(100vw-32px)] bg-zinc-950/95 border border-zinc-800 rounded-xl shadow-2xl backdrop-blur-xl flex flex-col z-30 overflow-hidden text-xs">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800/80 bg-zinc-900/50 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span
              style={{ color: sectorMeta.color, borderColor: sectorMeta.borderColor }}
              className="px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider uppercase border bg-zinc-900/80"
            >
              {sectorMeta.label}
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${statusMeta.badgeClass}`}>
              {statusMeta.label}
            </span>
          </div>
          <h3 className="font-semibold text-sm text-zinc-100 truncate" title={asset.name}>
            {asset.name}
          </h3>
          <div className="flex items-center gap-2 mt-1 text-zinc-400 font-mono text-[11px]">
            <span>{asset.country}</span>
            <span>•</span>
            <span>{asset.asset_id}</span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-zinc-400 hover:text-zinc-100 bg-zinc-800/40 hover:bg-zinc-800 rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content scroll area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Precision & Geographic Coordinates */}
        <div className="p-3 bg-zinc-900/60 border border-zinc-800/80 rounded-lg space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 font-medium flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-zinc-500" />
              Geographic Resolution
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${precisionMeta.badgeClass}`}>
              {precisionMeta.label}
            </span>
          </div>
          <div className="flex items-center justify-between text-zinc-300 font-mono text-[11px]">
            <span>Lat: {asset.latitude.toFixed(4)}°</span>
            <span>Lng: {asset.longitude.toFixed(4)}°</span>
          </div>
          {asset.is_approximate_route && (
            <p className="text-[10px] text-amber-400/90 leading-tight">
              Route geometry is generalized for regional analysis. Surveyed centerline alignment is not claimed.
            </p>
          )}
        </div>

        {/* Official Identifiers (UN/LOCODE, ICAO, IATA, GEM, etc.) */}
        {asset.identifiers && Object.keys(asset.identifiers).length > 0 && (
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              Authoritative Identifiers
            </span>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(asset.identifiers).map(([key, val]) => (
                <div key={key} className="p-2 bg-zinc-900/60 border border-zinc-800/80 rounded">
                  <div className="text-[10px] text-zinc-500 font-mono">{key}</div>
                  <div className="text-[11px] text-zinc-200 font-semibold font-mono truncate">{val}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Capacity & Throughput Records */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-zinc-500" />
            Verified Capacity & Output
          </span>
          {asset.capacity_records && asset.capacity_records.length > 0 ? (
            <div className="space-y-2">
              {asset.capacity_records.map((rec, idx) => (
                <div key={idx} className="p-2.5 bg-zinc-900/60 border border-zinc-800/80 rounded flex items-center justify-between">
                  <div>
                    <div className="font-medium text-zinc-200">
                      {formatCapacityDisplay(rec.value, rec.metric, rec.basis, rec.unit_str)}
                    </div>
                    {rec.reporting_year && (
                      <div className="text-[10px] text-zinc-500 font-mono">
                        Reporting Year: {rec.reporting_year}
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-zinc-400 font-mono uppercase bg-zinc-800/60 px-2 py-0.5 rounded">
                    {rec.basis}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-2.5 bg-zinc-900/40 border border-zinc-800/50 rounded text-zinc-400 text-center">
              Throughput / Capacity: <span className="font-mono text-zinc-300">Not available</span>
            </div>
          )}
        </div>

        {/* Corporate Entity Links (Owners, Operators) */}
        {asset.entity_links && asset.entity_links.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5 text-zinc-500" />
              Corporate Linkages
            </span>
            <div className="space-y-2">
              {asset.entity_links.map((link, idx) => (
                <div key={idx} className="p-2.5 bg-zinc-900/60 border border-zinc-800/80 rounded">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-zinc-200 truncate">{link.entity_name}</span>
                    <span className="text-[10px] font-semibold text-cyan-400 uppercase px-1.5 py-0.5 bg-cyan-950/40 border border-cyan-800/40 rounded">
                      {link.role}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-zinc-400 font-mono">
                    <span>Entity: {link.entity_id}</span>
                    {link.ownership_pct !== null && link.ownership_pct !== undefined && (
                      <span>Share: {link.ownership_pct}%</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Historical Status Timeline */}
        {asset.status_history && asset.status_history.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
              <History className="w-3.5 h-3.5 text-zinc-500" />
              Status History
            </span>
            <div className="p-2.5 bg-zinc-900/60 border border-zinc-800/80 rounded space-y-2">
              {asset.status_history.map((h, idx) => (
                <div key={idx} className="flex items-center justify-between text-[11px] border-b border-zinc-800/40 last:border-0 pb-1">
                  <span className="font-mono text-zinc-400">{h.effective_date}</span>
                  <span className="font-medium text-zinc-200 capitalize">{h.status}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Source Provenance & Licensing */}
        <div className="p-3 bg-zinc-900/40 border border-zinc-800/50 rounded-lg space-y-1 text-[11px]">
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Source Registry:</span>
            <span className="font-mono text-zinc-300">{asset.source_id}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Licensing Class:</span>
            <span className="font-mono text-zinc-300 capitalize">{asset.source_license}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
