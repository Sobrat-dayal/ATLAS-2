"use client";

import React, { useState } from "react";
import { X, Copy, Check, ShieldCheck, Database, Calendar, MapPin, Compass } from "lucide-react";
import { GeoFeatureDetail } from "@/lib/maps/types";
import { formatCoordinates } from "@/lib/maps/coordinates";

interface AtlasMapFeatureInspectorProps {
  featureDetail: GeoFeatureDetail | null;
  isLoading: boolean;
  onClose: () => void;
  className?: string;
}

export function AtlasMapFeatureInspector({
  featureDetail,
  isLoading,
  onClose,
  className = "",
}: AtlasMapFeatureInspectorProps) {
  const [copied, setCopied] = useState(false);

  if (isLoading) {
    return (
      <div className={`h-full flex flex-col items-center justify-center p-6 bg-atlas-surface-0 font-mono text-xs text-atlas-text-muted ${className}`}>
        <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-3" />
        <p>Loading feature intelligence...</p>
      </div>
    );
  }

  if (!featureDetail) {
    return (
      <div className={`h-full flex flex-col items-center justify-center p-6 text-center bg-atlas-surface-0 font-mono text-xs text-atlas-text-muted ${className}`}>
        <Compass className="w-8 h-8 mb-3 text-atlas-border-strong opacity-60" />
        <p className="font-medium text-atlas-text-secondary">No Feature Selected</p>
        <p className="text-[11px] mt-1 text-atlas-text-muted max-w-[200px]">
          Click any point, boundary, or financial center on the map to inspect metadata and provenance.
        </p>
      </div>
    );
  }

  const lon = Array.isArray(featureDetail.coordinates)
    ? featureDetail.coordinates[0]
    : 0;
  const lat = Array.isArray(featureDetail.coordinates)
    ? featureDetail.coordinates[1]
    : 0;
  const coordsFormatted = formatCoordinates(lon, lat);

  const handleCopyCoords = () => {
    navigator.clipboard.writeText(`${lat}, ${lon}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`h-full flex flex-col bg-atlas-surface-0 font-mono text-xs ${className}`}>
      {/* Header */}
      <div className="px-3 py-2 border-b border-atlas-border-default bg-atlas-surface-1 flex items-center justify-between">
        <div className="flex items-center gap-1.5 truncate">
          <MapPin className="w-3.5 h-3.5 text-blue-400 shrink-0" />
          <span className="font-semibold text-atlas-text-primary uppercase tracking-wider text-[11px] truncate">
            {featureDetail.label}
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-atlas-text-muted hover:text-atlas-text-primary p-1"
          title="Close Inspector"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {/* Coordinates Card */}
        <div className="p-2.5 rounded bg-atlas-surface-1 border border-atlas-border-default/60 space-y-1.5">
          <div className="text-[10px] text-atlas-text-muted uppercase tracking-wider flex items-center justify-between">
            <span>Coordinates (WGS84)</span>
            <button
              type="button"
              onClick={handleCopyCoords}
              className="text-blue-400 hover:text-blue-300 flex items-center gap-1 text-[10px]"
              title="Copy Coordinates"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
          </div>
          <div className="font-mono text-xs text-atlas-text-primary font-medium">
            {coordsFormatted}
          </div>
          <div className="text-[10px] text-atlas-text-muted font-mono">
            Lon: {lon.toFixed(6)}, Lat: {lat.toFixed(6)}
          </div>
        </div>

        {/* Data Quality Status */}
        <div className="p-2.5 rounded bg-atlas-surface-1 border border-atlas-border-default/60 space-y-1.5">
          <div className="text-[10px] text-atlas-text-muted uppercase tracking-wider">
            Data Quality & Accuracy
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                featureDetail.data_quality === "verified"
                  ? "bg-emerald-900/30 text-emerald-400 border border-emerald-500/30"
                  : "bg-amber-900/30 text-amber-400 border border-amber-500/30"
              }`}
            >
              {featureDetail.data_quality}
            </span>
            <span className="text-[11px] text-atlas-text-secondary">
              EPSG:4326 Canonical Storage
            </span>
          </div>
        </div>

        {/* Properties */}
        {featureDetail.properties && Object.keys(featureDetail.properties).length > 0 && (
          <div className="p-2.5 rounded bg-atlas-surface-1 border border-atlas-border-default/60 space-y-2">
            <div className="text-[10px] text-atlas-text-muted uppercase tracking-wider">
              Geographic & Financial Attributes
            </div>
            <div className="space-y-1.5">
              {Object.entries(featureDetail.properties).map(([k, v]) => {
                if (k.startsWith("_") || typeof v === "object") return null;
                return (
                  <div key={k} className="flex justify-between items-start gap-2 text-[11px]">
                    <span className="text-atlas-text-muted capitalize">{k.replace(/_/g, " ")}:</span>
                    <span className="text-atlas-text-primary text-right font-medium max-w-[150px] truncate" title={String(v)}>
                      {String(v)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Source Provenance */}
        <div className="p-2.5 rounded bg-atlas-surface-1 border border-atlas-border-default/60 space-y-2">
          <div className="text-[10px] text-atlas-text-muted uppercase tracking-wider flex items-center gap-1">
            <Database className="w-3 h-3 text-blue-400" />
            <span>Source Provenance</span>
          </div>
          <div className="space-y-1 text-[11px]">
            <div className="text-atlas-text-primary font-medium">{featureDetail.dataset_name}</div>
            <div className="text-[10px] text-atlas-text-muted">{featureDetail.source_reference}</div>
            <div className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1">
              <ShieldCheck className="w-3 h-3" />
              <span>{featureDetail.licensing_policy}</span>
            </div>
            <div className="text-[10px] text-atlas-text-muted flex items-center gap-1 mt-1">
              <Calendar className="w-3 h-3" />
              <span>Updated: {featureDetail.source_updated_at?.split("T")[0] || "2026-10-30"}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

