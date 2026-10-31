"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import { AtlasMapToolbar } from "./AtlasMapToolbar";
import { AtlasMapCanvas } from "./AtlasMapCanvas";
import { AtlasMapLayerPanel } from "./AtlasMapLayerPanel";
import { AtlasMapFeatureInspector } from "./AtlasMapFeatureInspector";
import { AtlasMapSaveViewDialog } from "./AtlasMapSaveViewDialog";
import { AtlasMapViewListModal } from "./AtlasMapViewListModal";
import { SpatialAnalyticsPanel } from "./analytics/SpatialAnalyticsPanel";
import { SpatialLegend } from "./analytics/SpatialLegend";
import { SpatialCellInspector } from "./analytics/SpatialCellInspector";
import { SpatialRegionComparison } from "./analytics/SpatialRegionComparison";
import { SpatialTimeline } from "./analytics/SpatialTimeline";
import { useMapLayers } from "@/hooks/maps/useMapLayers";
import { useMapSearch } from "@/hooks/maps/useMapSearch";
import { useMapSelection } from "@/hooks/maps/useMapSelection";
import { useSpatialAnalytics } from "@/hooks/maps/analytics/useSpatialAnalytics";
import { AtlasDeckOverlayController } from "@/lib/maps/analytics/deckOverlay";
import {
  buildH3HexagonLayer,
  buildScatterplotLayer,
  buildHeatmapLayer,
  buildHexagonGridLayer,
} from "@/lib/maps/analytics/deckLayers";
import { cellToLatLng } from "@/lib/maps/analytics/h3";
import { PRESET_BASEMAP_STYLES, DEFAULT_CAMERA } from "@/lib/maps/styles";
import {
  GeographicSearchResult,
  MapBasemapStyle,
  MapCameraState,
  UserMapView,
} from "@/lib/maps/types";
import { saveMapView } from "@/lib/maps/api";
import { AtlasGlobe } from "./globe/AtlasGlobe";
import { useSearchParams } from "next/navigation";
import { ScatterplotLayer } from "@deck.gl/layers";
import { CorporateMapMode } from "./corporate/CorporateMapMode";
import { CorporateFacility } from "@/lib/maps/corporate/types";
import { InfrastructureMapMode } from "./infrastructure/InfrastructureMapMode";
import { LiveWorldMode } from "./live/LiveWorldMode";
import {
  maplibreToCesiumCamera,
  cesiumToMaplibreCamera,
} from "@/lib/maps/globe/cameraInteroperability";
import { RendererMode, AtlasGlobeCamera } from "@/lib/maps/globe/types";

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

  // 2D / 3D Renderer Mode
  const [rendererMode, setRendererMode] = useState<RendererMode>(
    ((initialView as any)?.renderer_mode as RendererMode) || "2D"
  );

  // 3D Globe camera state
  const [globeCamera, setGlobeCamera] = useState<AtlasGlobeCamera>(() =>
    maplibreToCesiumCamera(
      camera.longitude,
      camera.latitude,
      camera.zoom,
      camera.bearing,
      camera.pitch
    )
  );

  // Interoperable Mode Switching
  const handleModeChange = useCallback(
    (newMode: RendererMode) => {
      if (newMode === rendererMode) return;
      if (newMode === "3D") {
        const c3d = maplibreToCesiumCamera(
          camera.longitude,
          camera.latitude,
          camera.zoom,
          camera.bearing,
          camera.pitch
        );
        setGlobeCamera(c3d);
        setRendererMode("3D");
      } else {
        const c2d = cesiumToMaplibreCamera(globeCamera);
        setCamera({
          longitude: c2d.center[0],
          latitude: c2d.center[1],
          zoom: c2d.zoom,
          bearing: c2d.bearing,
          pitch: c2d.pitch,
          projection: "mercator",
          revision: camera.revision ?? 1,
        });
        setRendererMode("2D");
      }
    },
    [camera, globeCamera, rendererMode]
  );

  // Panels visibility
  const [isLayerPanelOpen, setIsLayerPanelOpen] = useState(true);
  const [isInspectorOpen, setIsInspectorOpen] = useState(true);

  // Dialogs
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [isViewsModalOpen, setIsViewsModalOpen] = useState(false);

  // Corporate Geography Mode (Stage 132)
  const searchParams = useSearchParams();
  const companyParam = searchParams?.get("company") || null;
  const [isCorporateModeOpen, setIsCorporateModeOpen] = useState<boolean>(() => Boolean(companyParam));
  const [selectedCorporateFacility, setSelectedCorporateFacility] = useState<CorporateFacility | null>(null);
  const [corporateFacilities, setCorporateFacilities] = useState<CorporateFacility[]>([]);

  // Physical Infrastructure Intelligence Mode (Stage 133)
  const [isInfrastructureModeOpen, setIsInfrastructureModeOpen] = useState<boolean>(false);
  const [selectedInfrastructureAssetId, setSelectedInfrastructureAssetId] = useState<string | null>(null);

  // Live Physical-World Intelligence Mode (Stage 134)
  const [isLiveWorldOpen, setIsLiveWorldOpen] = useState<boolean>(false);

  // Spatial Analytics (Stage 131 deck.gl + H3)
  const analytics = useSpatialAnalytics();
  const overlayControllerRef = useRef<AtlasDeckOverlayController | null>(null);

  if (!overlayControllerRef.current) {
    overlayControllerRef.current = new AtlasDeckOverlayController();
  }

  // Ref to canvas map methods
  const mapControlsRef = useRef<any>(null);

  // Synchronize deck.gl layers with MapLibre instance
  useEffect(() => {
    const mapInstance = mapControlsRef.current?.map;
    if (!mapInstance || rendererMode !== "2D" || !overlayControllerRef.current) return;

    if (!overlayControllerRef.current.getAttached()) {
      overlayControllerRef.current.attach(mapInstance);
    }

    if (!analytics.isOpen || !analytics.result || analytics.result.aggregates.length === 0) {
      overlayControllerRef.current.setLayers([]);
      return;
    }

    let deckLayer: any = null;
    const summary = analytics.result.summary;

    if (analytics.visualizationType === "h3_hexagon") {
      deckLayer = buildH3HexagonLayer(analytics.result.aggregates, {
        palette: analytics.palette,
        minVal: summary.min_value,
        maxVal: summary.max_value,
        extruded: analytics.isExtruded,
        opacity: analytics.opacity,
        onClick: (info: any) => {
          if (info?.object) {
            analytics.setSelectedCell(info.object);
          }
        },
      });
    } else if (analytics.visualizationType === "scatterplot") {
      const pts = analytics.result.aggregates.map((a) => {
        const [lat, lon] = cellToLatLng(a.h3_cell_id);
        return {
          id: a.h3_cell_id,
          longitude: lon,
          latitude: lat,
          value: a.value ?? 0,
        };
      });
      deckLayer = buildScatterplotLayer(pts, {
        palette: analytics.palette,
        minVal: summary.min_value,
        maxVal: summary.max_value,
        opacity: analytics.opacity,
        onClick: (info: any) => {
          if (info?.object) {
            const match = analytics.result?.aggregates.find((x) => x.h3_cell_id === info.object.id);
            if (match) analytics.setSelectedCell(match);
          }
        },
      });
    } else if (analytics.visualizationType === "heatmap") {
      const pts = analytics.result.aggregates.map((a) => {
        const [lat, lon] = cellToLatLng(a.h3_cell_id);
        return { longitude: lon, latitude: lat, value: a.value ?? 1 };
      });
      deckLayer = buildHeatmapLayer(pts);
    } else if (analytics.visualizationType === "hexagon_grid") {
      const pts = analytics.result.aggregates.map((a) => {
        const [lat, lon] = cellToLatLng(a.h3_cell_id);
        return { longitude: lon, latitude: lat, value: a.value ?? 1 };
      });
      deckLayer = buildHexagonGridLayer(pts, {
        extruded: analytics.isExtruded,
        onClick: (info: any) => {
          if (info?.object) {
            // HexagonLayer object points
          }
        },
      });
    }

    const activeDeckLayers: any[] = [];
    if (deckLayer) activeDeckLayers.push(deckLayer);

    // Corporate Facilities Layer (Stage 132)
    if (isCorporateModeOpen && corporateFacilities.length > 0) {
      const corpPts = corporateFacilities
        .filter((f) => f.longitude != null && f.latitude != null)
        .map((f) => ({
          id: f.facility_id,
          longitude: f.longitude!,
          latitude: f.latitude!,
          facility: f,
        }));

      const corpDeckLayer = new ScatterplotLayer({
        id: "deck-corporate-facilities",
        data: corpPts,
        getPosition: (d: any) => [d.longitude, d.latitude],
        getRadius: 180,
        radiusMinPixels: 6,
        radiusMaxPixels: 18,
        getFillColor: (d: any) => {
          const t = d.facility.facility_type;
          if (t === "CORPORATE_HEADQUARTERS") return [56, 189, 248, 240];
          if (t === "MANUFACTURING_FACILITY") return [245, 158, 11, 240];
          if (t === "RESEARCH_AND_DEVELOPMENT") return [16, 185, 129, 240];
          return [96, 165, 250, 240];
        },
        getLineColor: [255, 255, 255, 255],
        getLineWidth: 2,
        stroked: true,
        pickable: true,
        onClick: ((info: any) => {
          if (info?.object?.facility) {
            setSelectedCorporateFacility(info.object.facility);
          }
        }) as any,
      });
      activeDeckLayers.push(corpDeckLayer);
    }

    overlayControllerRef.current.setLayers(activeDeckLayers);
  }, [
    mapControlsRef,
    rendererMode,
    isCorporateModeOpen,
    corporateFacilities,
    analytics.isOpen,
    analytics.result,
    analytics.visualizationType,
    analytics.palette,
    analytics.isExtruded,
    analytics.opacity,
  ]);

  // Clean up overlay on unmount
  useEffect(() => {
    return () => {
      overlayControllerRef.current?.detach();
    };
  }, []);

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

  if (rendererMode === "3D") {
    return (
      <div className={`relative h-full w-full ${className}`}>
        <AtlasGlobe
          initialCamera={globeCamera}
          onModeChange={handleModeChange}
          onCameraChange={setGlobeCamera}
          selectedFeatureId={selectedFeatureId}
          onSelectFeature={(id) => (id ? selectFeature(id) : clearSelection())}
          h3Aggregates={analytics.isOpen ? analytics.result?.aggregates : undefined}
          analyticsPalette={analytics.palette}
          analyticsExtruded={analytics.isExtruded}
          onSelectH3Cell={(agg) => analytics.setSelectedCell(agg)}
          corporateFacilities={isCorporateModeOpen ? corporateFacilities : undefined}
          onSelectCorporateFacility={setSelectedCorporateFacility}
          className="w-full h-full"
        />
        {isCorporateModeOpen && (
          <div className="absolute top-10 left-0 bottom-0 z-30 pointer-events-none">
            <div className="pointer-events-auto h-full">
              <CorporateMapMode
                initialCompanyId={companyParam}
                selectedFacility={selectedCorporateFacility}
                onSelectFacility={setSelectedCorporateFacility}
                onFacilitiesLoaded={setCorporateFacilities}
              />
            </div>
          </div>
        )}
        {isInfrastructureModeOpen && (
          <div className="absolute top-10 left-0 bottom-0 z-30 pointer-events-none">
            <div className="pointer-events-auto h-full">
              <InfrastructureMapMode
                selectedAssetId={selectedInfrastructureAssetId}
                onSelectAsset={setSelectedInfrastructureAssetId}
              />
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full w-full bg-atlas-surface-0 overflow-hidden ${className}`}>
      {/* Top Toolbar */}
      <AtlasMapToolbar
        currentStyleId={currentStyle.style_id}
        onStyleSelect={setCurrentStyle}
        rendererMode={rendererMode}
        onModeChange={handleModeChange}
        isAnalyticsOpen={analytics.isOpen}
        onToggleAnalytics={() => analytics.setIsOpen((open) => !open)}
        isCorporateModeOpen={isCorporateModeOpen}
        onToggleCorporateMode={() => setIsCorporateModeOpen((prev) => !prev)}
        isInfrastructureModeOpen={isInfrastructureModeOpen}
        onToggleInfrastructureMode={() => setIsInfrastructureModeOpen((prev) => !prev)}
        isLiveWorldOpen={isLiveWorldOpen}
        onToggleLiveWorld={() => setIsLiveWorldOpen((prev) => !prev)}
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
        {/* Left Corporate Intelligence Drawer (Stage 132) */}
        {isCorporateModeOpen && (
          <div className="absolute top-0 left-0 bottom-0 z-30 pointer-events-none">
            <div className="pointer-events-auto h-full">
              <CorporateMapMode
                initialCompanyId={companyParam}
                selectedFacility={selectedCorporateFacility}
                onSelectFacility={(fac) => {
                  setSelectedCorporateFacility(fac);
                  if (fac && fac.longitude != null && fac.latitude != null && mapControlsRef.current) {
                    mapControlsRef.current.flyTo(fac.longitude, fac.latitude, 11);
                  }
                }}
                onFacilitiesLoaded={setCorporateFacilities}
              />
            </div>
          </div>
        )}

        {/* Global Physical Infrastructure Intelligence (Stage 133) */}
        {isInfrastructureModeOpen && (
          <div className="absolute top-0 left-0 bottom-0 z-30 pointer-events-none">
            <div className="pointer-events-auto h-full">
              <InfrastructureMapMode
                selectedAssetId={selectedInfrastructureAssetId}
                onSelectAsset={(aid) => {
                  setSelectedInfrastructureAssetId(aid);
                }}
              />
            </div>
          </div>
        )}

        {/* Live Physical-World Intelligence (Stage 134) */}
        {isLiveWorldOpen && (
          <LiveWorldMode
            onNavigateToCoordinates={(lon, lat, zoom) => {
              mapControlsRef.current?.flyTo(lon, lat, zoom || 11);
            }}
          />
        )}

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

          {/* Floating Spatial Analytics Drawer (deck.gl + H3) */}
          <SpatialAnalyticsPanel
            isOpen={analytics.isOpen}
            onClose={() => analytics.setIsOpen(false)}
            datasetId={analytics.datasetId}
            onDatasetChange={analytics.setDatasetId}
            metricId={analytics.metricId}
            onMetricChange={analytics.setMetricId}
            metrics={analytics.metrics}
            visualizationType={analytics.visualizationType}
            onVisualizationChange={analytics.setVisualizationType}
            aggregation={analytics.aggregation}
            onAggregationChange={analytics.setAggregation}
            h3Resolution={analytics.h3Resolution}
            onH3ResolutionChange={analytics.setH3Resolution}
            palette={analytics.palette}
            onPaletteChange={analytics.setPalette}
            isExtruded={analytics.isExtruded}
            onExtrudedChange={analytics.setIsExtruded}
            opacity={analytics.opacity}
            onOpacityChange={analytics.setOpacity}
            onOpenComparison={() => analytics.setIsComparingRegions(true)}
            isLoading={analytics.isLoading}
            error={analytics.error}
            className="absolute top-3 left-3 z-30"
          />

          {/* Floating Spatial Legend */}
          {analytics.isOpen && analytics.result && (
            <SpatialLegend
              result={analytics.result}
              palette={analytics.palette}
              className="absolute bottom-6 right-3 z-20"
            />
          )}

          {/* Floating Timeline Controls (Historical exploration) */}
          {analytics.isOpen && (
            <SpatialTimeline
              timeBucket={analytics.timeBucket}
              onTimeBucketChange={analytics.setTimeBucket}
              className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20"
            />
          )}

          {/* Floating Cell Inspector */}
          {analytics.selectedCell && (
            <SpatialCellInspector
              cell={analytics.selectedCell}
              onClose={() => analytics.setSelectedCell(null)}
              className="absolute top-3 right-3 z-30"
            />
          )}

          {/* Regional Comparison Modal */}
          {analytics.isComparingRegions && (
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-40 flex items-center justify-center p-4">
              <SpatialRegionComparison
                datasetId={analytics.datasetId}
                metricId={analytics.metricId}
                aggregation={analytics.aggregation}
                h3Resolution={analytics.h3Resolution}
                onClose={() => analytics.setIsComparingRegions(false)}
              />
            </div>
          )}
        </div>

        {/* Right Feature Inspector */}
        {isInspectorOpen && !analytics.selectedCell && (
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

