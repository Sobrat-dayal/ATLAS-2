/**
 * Master ATLAS 3D God's Eye Globe Component (Stage 130).
 *
 * Integrates CesiumJS WebGL globe canvas, navigation toolbar,
 * layer management, feature inspector, and legal attribution.
 */

"use client";

import React, { useRef, useState, useEffect } from "react";
import {
  AtlasGlobeCamera,
  GlobeImageryProvider,
  GlobeTerrainProvider,
  Atlas3DTilesetSource,
  RendererMode,
} from "@/lib/maps/globe/types";
import { useCesiumViewer } from "@/hooks/maps/globe/useCesiumViewer";
import {
  fetchGlobeConfig,
  fetchImageryProviders,
  fetchTerrainProviders,
  fetchTilesets,
} from "@/lib/maps/globe/api";
import { CesiumGlobeCanvas } from "./CesiumGlobeCanvas";
import { GlobeToolbar } from "./GlobeToolbar";
import { GlobeLayerPanel } from "./GlobeLayerPanel";
import { GlobeFeatureInspector } from "./GlobeFeatureInspector";
import { GlobeSourceAttribution } from "./GlobeSourceAttribution";
import { GlobeSaveViewDialog } from "./GlobeSaveViewDialog";

interface AtlasGlobeProps {
  initialCamera?: AtlasGlobeCamera;
  onModeChange: (mode: RendererMode) => void;
  onCameraChange?: (camera: AtlasGlobeCamera) => void;
  selectedFeatureId?: string | null;
  onSelectFeature?: (featureId: string | null) => void;
  className?: string;
}

export function AtlasGlobe({
  initialCamera,
  onModeChange,
  onCameraChange,
  selectedFeatureId,
  onSelectFeature,
  className = "w-full h-full relative",
}: AtlasGlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Catalogs
  const [imageryProviders, setImageryProviders] = useState<GlobeImageryProvider[]>([]);
  const [activeImageryId, setActiveImageryId] = useState<string>("natural-earth");
  const [terrainProviders, setTerrainProviders] = useState<GlobeTerrainProvider[]>([]);
  const [activeTerrainId, setActiveTerrainId] = useState<string>("ellipsoid");
  const [tilesets, setTilesets] = useState<Atlas3DTilesetSource[]>([]);
  const [activeTilesetIds, setActiveTilesetIds] = useState<string[]>([]);

  // Panels
  const [isLayersOpen, setIsLayersOpen] = useState(false);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [isTiltActive, setIsTiltActive] = useState(false);

  // Selected feature & surface click position
  const [surfacePosition, setSurfacePosition] = useState<{
    lon: number;
    lat: number;
    height: number;
  } | null>(null);
  const [selectedFeatureData, setSelectedFeatureData] = useState<any | null>(null);

  // Current camera tracking
  const [currentCamera, setCurrentCamera] = useState<AtlasGlobeCamera>(
    initialCamera || {
      longitude: 0.0,
      latitude: 20.0,
      height_meters: 20000000.0,
      heading_radians: 0.0,
      pitch_radians: -Math.PI / 2,
      roll_radians: 0.0,
    }
  );

  // Load catalogs on mount
  useEffect(() => {
    async function loadData() {
      const [imgs, terrs, tsets] = await Promise.all([
        fetchImageryProviders(),
        fetchTerrainProviders(),
        fetchTilesets(),
      ]);
      setImageryProviders(imgs);
      setTerrainProviders(terrs);
      setTilesets(tsets);
    }
    loadData();
  }, []);

  // Cesium viewer hook
  const { viewer, cesium, status, errorMessage, flyTo, switchImagery } = useCesiumViewer({
    containerRef,
    initialCamera: currentCamera,
    onCameraChange: (cam) => {
      setCurrentCamera(cam);
      if (onCameraChange) onCameraChange(cam);
    },
    onFeaturePick: (featId, pos) => {
      if (pos) setSurfacePosition(pos);
      if (featId) {
        if (onSelectFeature) onSelectFeature(featId);
        setSelectedFeatureData({
          feature_id: featId,
          label: featId,
          dataset_id: "atlas.reference.financial_centers",
          data_quality: "Verified",
          properties: {
            picked_id: featId,
            inspection_mode: "3D Globe Scene Pick",
          },
        });
        setIsInspectorOpen(true);
      } else {
        setSelectedFeatureData(null);
      }
    },
  });

  // Current Attribution string
  const activeImagery = imageryProviders.find((p) => p.provider_id === activeImageryId);
  const attributionText = activeImagery
    ? activeImagery.attribution
    : "© OpenStreetMap contributors, © CARTO, © Natural Earth";

  // Navigation handlers
  const handleZoomIn = () => {
    if (!viewer) return;
    viewer.camera.zoomIn(viewer.camera.positionCartographic.height * 0.4);
  };

  const handleZoomOut = () => {
    if (!viewer) return;
    viewer.camera.zoomOut(viewer.camera.positionCartographic.height * 0.6);
  };

  const handleResetOrientation = () => {
    if (!viewer || !cesium) return;
    viewer.camera.flyTo({
      destination: viewer.camera.position,
      orientation: {
        heading: 0.0,
        pitch: viewer.camera.pitch,
        roll: 0.0,
      },
      duration: 1.0,
    });
  };

  const handleResetGlobalView = () => {
    flyTo(0.0, 20.0, 20000000.0, 0.0);
    setIsTiltActive(false);
  };

  const handleToggleTilt = () => {
    if (!viewer || !cesium) return;
    const nextTilt = !isTiltActive;
    setIsTiltActive(nextTilt);
    viewer.camera.flyTo({
      destination: viewer.camera.position,
      orientation: {
        heading: viewer.camera.heading,
        pitch: nextTilt ? -Math.PI / 4 : -Math.PI / 2,
        roll: 0.0,
      },
      duration: 1.0,
    });
  };

  const handleSelectImagery = (providerId: string) => {
    const prov = imageryProviders.find((p) => p.provider_id === providerId);
    if (!prov) return;
    setActiveImageryId(providerId);
    switchImagery(prov.source_url, prov.attribution);
  };

  const handleSelectTerrain = (providerId: string) => {
    if (!viewer || !cesium) return;
    setActiveTerrainId(providerId);
    if (providerId === "ellipsoid") {
      viewer.terrainProvider = new cesium.EllipsoidTerrainProvider();
    }
  };

  const handleToggleTileset = (tilesetId: string) => {
    setActiveTilesetIds((prev) =>
      prev.includes(tilesetId) ? prev.filter((id) => id !== tilesetId) : [...prev, tilesetId]
    );
  };

  const handleSearchSelect = (item: { lon: number; lat: number; label: string }) => {
    flyTo(item.lon, item.lat, 4000.0, 0.0);
    setSurfacePosition({ lon: item.lon, lat: item.lat, height: 0.0 });
    setSelectedFeatureData({
      feature_id: item.label.toLowerCase().replace(/\s+/g, "-"),
      label: item.label,
      dataset_id: "atlas.reference.financial_centers",
      data_quality: "Verified",
      properties: {
        coordinates: `${item.lat.toFixed(4)}, ${item.lon.toFixed(4)}`,
        classification: "Major Financial Hub",
      },
    });
    setIsInspectorOpen(true);
  };

  return (
    <div className={className}>
      {/* 3D Toolbar */}
      <GlobeToolbar
        mode="3D"
        onModeChange={onModeChange}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onResetOrientation={handleResetOrientation}
        onResetGlobalView={handleResetGlobalView}
        onToggleTilt={handleToggleTilt}
        isTiltActive={isTiltActive}
        onToggleLayers={() => setIsLayersOpen((v) => !v)}
        isLayersOpen={isLayersOpen}
        onToggleInspector={() => setIsInspectorOpen((v) => !v)}
        isInspectorOpen={isInspectorOpen}
        onOpenSaveDialog={() => setIsSaveDialogOpen(true)}
        onSearchSelect={handleSearchSelect}
      />

      {/* Cesium WebGL Canvas Container */}
      <CesiumGlobeCanvas
        status={status}
        errorMessage={errorMessage}
        containerRef={containerRef}
        onFallback2D={() => onModeChange("2D")}
      />

      {/* Layer Panel Drawer */}
      <GlobeLayerPanel
        isOpen={isLayersOpen}
        onClose={() => setIsLayersOpen(false)}
        imageryProviders={imageryProviders}
        activeImageryId={activeImageryId}
        onSelectImagery={handleSelectImagery}
        terrainProviders={terrainProviders}
        activeTerrainId={activeTerrainId}
        onSelectTerrain={handleSelectTerrain}
        tilesets={tilesets}
        activeTilesetIds={activeTilesetIds}
        onToggleTileset={handleToggleTileset}
      />

      {/* Feature Inspector Drawer */}
      <GlobeFeatureInspector
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
        selectedFeature={selectedFeatureData}
        surfacePosition={surfacePosition}
        terrainActive={activeTerrainId !== "ellipsoid"}
      />

      {/* Visible Legal Attribution Overlay */}
      <GlobeSourceAttribution attributionText={attributionText} />

      {/* Save View Modal Dialog */}
      <GlobeSaveViewDialog
        isOpen={isSaveDialogOpen}
        onClose={() => setIsSaveDialogOpen(false)}
        currentCamera={currentCamera}
        activeImageryId={activeImageryId}
        activeTerrainId={activeTerrainId}
        activeLayerIds={activeTilesetIds}
        selectedFeatureId={selectedFeatureId}
      />
    </div>
  );
}

