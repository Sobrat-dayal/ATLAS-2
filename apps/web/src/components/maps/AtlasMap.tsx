"use client";

import React, { useState, useRef, useCallback } from "react";
import { AtlasMapToolbar } from "./AtlasMapToolbar";
import { AtlasMapCanvas } from "./AtlasMapCanvas";
import { AtlasMapLayerPanel } from "./AtlasMapLayerPanel";
import { AtlasMapFeatureInspector } from "./AtlasMapFeatureInspector";
import { AtlasMapSaveViewDialog } from "./AtlasMapSaveViewDialog";
import { AtlasMapViewListModal } from "./AtlasMapViewListModal";
import { useMapLayers } from "@/hooks/maps/useMapLayers";
import { useMapSearch } from "@/hooks/maps/useMapSearch";
import { useMapSelection } from "@/hooks/maps/useMapSelection";
import { PRESET_BASEMAP_STYLES, DEFAULT_CAMERA } from "@/lib/maps/styles";
import {
  GeographicSearchResult,
  MapBasemapStyle,
  MapCameraState,
  UserMapView,
} from "@/lib/maps/types";
import { saveMapView } from "@/lib/maps/api";

interface AtlasMapProps {
  initialView?: UserMapView;
  workspaceId?: string;
  className?: string;
}

export function AtlasMap({
  initialView,
  workspaceId,
  className = "",
}: AtlasMapProps) {
  // Basemap style
  const [currentStyle, setCurrentStyle] = useState<MapBasemapStyle>(() => {
    if (initialView?.basemap_style_id) {
      const match = PRESET_BASEMAP_STYLES.find(
        (s) => s.style_id === initialView.basemap_style_id
      );
      if (match) return match;
    }
    return PRESET_BASEMAP_STYLES[0];
  });

  // Camera state
  const [camera, setCamera] = useState<MapCameraState>(
    initialView?.camera ?? (DEFAULT_CAMERA as MapCameraState)
  );

  // Panels visibility
  const [isLayerPanelOpen, setIsLayerPanelOpen] = useState(true);
  const [isInspectorOpen, setIsInspectorOpen] = useState(true);

  // Dialogs
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [isViewsModalOpen, setIsViewsModalOpen] = useState(false);

  // Ref to canvas map methods
  const mapControlsRef = useRef<any>(null);

  // Custom hooks
  const {
    layers,
    toggleLayerVisibility,
    setLayerOpacity,
  } = useMapLayers();

  const {
    query: searchQuery,
    setQuery: setSearchQuery,
    results: searchResults,
    isSearching,
    isOpen: isSearchOpen,
    setIsOpen: setIsSearchOpen,
    clearSearch,
  } = useMapSearch();

  const {
    selectedFeatureId,
    featureDetail,
    isLoading: isFeatureLoading,
    selectFeature,
    clearSelection,
  } = useMapSelection();

  // Search result click
  const handleSelectSearchResult = (result: GeographicSearchResult) => {
    clearSearch();
    if (result.coordinates && mapControlsRef.current) {
      if (result.bounding_box) {
        mapControlsRef.current.fitBounds(
          result.bounding_box[0],
          result.bounding_box[1],
          result.bounding_box[2],
          result.bounding_box[3]
        );
      } else {
        const zoom = result.place_type === "coordinates" ? 12 : 9;
        mapControlsRef.current.flyTo(
          result.coordinates[0],
          result.coordinates[1],
          zoom
        );
      }
    }
    if (result.result_id && !result.result_id.startsWith("coord_")) {
      selectFeature(result.result_id);
      setIsInspectorOpen(true);
    }
  };

  // Feature click on canvas
  const handleFeatureClick = useCallback(
    (featureId: string) => {
      selectFeature(featureId);
      setIsInspectorOpen(true);
    },
    [selectFeature]
  );

  // Save view
  const handleSaveView = async (name: string) => {
    const visibleLayers = layers.filter((l) => l.visible !== false).map((l) => l.layer_id);
    const layerConfigs = layers.reduce((acc, l) => {
      acc[l.layer_id] = { opacity: l.opacity ?? 1.0 };
      return acc;
    }, {} as Record<string, any>);

    await saveMapView({
      name,
      camera,
      basemap_style_id: currentStyle.style_id,
      visible_layers: visibleLayers,
      layer_configurations: layerConfigs,
      selected_feature_id: selectedFeatureId,
      workspace_id: workspaceId,
    });
  };

  // Restore view
  const handleRestoreView = (view: UserMapView) => {
    setCamera(view.camera);
    const styleMatch = PRESET_BASEMAP_STYLES.find(
      (s) => s.style_id === view.basemap_style_id
    );
    if (styleMatch) {
      setCurrentStyle(styleMatch);
    }
    if (view.camera && mapControlsRef.current) {
      mapControlsRef.current.flyTo(
        view.camera.longitude,
        view.camera.latitude,
        view.camera.zoom
      );
    }
    if (view.selected_feature_id) {
      selectFeature(view.selected_feature_id);
      setIsInspectorOpen(true);
    }
  };

  return (
    <div className={`flex flex-col h-full w-full bg-atlas-surface-0 overflow-hidden ${className}`}>
      {/* Top Toolbar */}
      <AtlasMapToolbar
        currentStyleId={currentStyle.style_id}
        onStyleSelect={setCurrentStyle}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchResults={searchResults}
        isSearching={isSearching}
        isSearchOpen={isSearchOpen}
        onSelectSearchResult={handleSelectSearchResult}
        onClearSearch={clearSearch}
        onCloseSearch={() => setIsSearchOpen(false)}
        currentZoom={camera.zoom}
        onZoomIn={() => mapControlsRef.current?.zoomIn()}
        onZoomOut={() => mapControlsRef.current?.zoomOut()}
        onResetOrientation={() => mapControlsRef.current?.resetBearing()}
        onFitGlobal={() => mapControlsRef.current?.flyTo(DEFAULT_CAMERA.longitude, DEFAULT_CAMERA.latitude, DEFAULT_CAMERA.zoom)}
        onOpenSaveDialog={() => setIsSaveDialogOpen(true)}
        onOpenViewsModal={() => setIsViewsModalOpen(true)}
        isLayerPanelOpen={isLayerPanelOpen}
        onToggleLayerPanel={() => setIsLayerPanelOpen((p) => !p)}
        isInspectorOpen={isInspectorOpen}
        onToggleInspector={() => setIsInspectorOpen((p) => !p)}
      />

      {/* Main Workspace: Left Panel, Center Canvas, Right Inspector */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Layer Panel */}
        {isLayerPanelOpen && (
          <div className="w-64 border-r border-atlas-border-default shrink-0 z-10 transition-all">
            <AtlasMapLayerPanel
              layers={layers}
              onToggleVisibility={toggleLayerVisibility}
              onSetOpacity={setLayerOpacity}
            />
          </div>
        )}

        {/* Center Canvas */}
        <div className="flex-1 h-full relative overflow-hidden">
          <AtlasMapCanvas
            styleUrl={currentStyle.style_url}
            attribution={currentStyle.attribution}
            layers={layers}
            initialCamera={camera}
            onCameraChange={setCamera}
            onFeatureClick={handleFeatureClick}
            mapInstanceRef={mapControlsRef}
          />
        </div>

        {/* Right Feature Inspector */}
        {isInspectorOpen && (
          <div className="w-72 border-l border-atlas-border-default shrink-0 z-10 transition-all">
            <AtlasMapFeatureInspector
              featureDetail={featureDetail}
              isLoading={isFeatureLoading}
              onClose={() => setIsInspectorOpen(false)}
            />
          </div>
        )}
      </div>

      {/* Modals & Dialogs */}
      <AtlasMapSaveViewDialog
        isOpen={isSaveDialogOpen}
        onClose={() => setIsSaveDialogOpen(false)}
        onSave={handleSaveView}
      />

      <AtlasMapViewListModal
        isOpen={isViewsModalOpen}
        onClose={() => setIsViewsModalOpen(false)}
        onRestoreView={handleRestoreView}
        workspaceId={workspaceId}
      />
    </div>
  );
}

