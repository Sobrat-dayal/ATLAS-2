/**
 * CesiumJS Viewer Lifecycle and WebGL Context Hook (Stage 130).
 *
 * Manages client-only mounting, base URL configuration, imagery and terrain setup,
 * resize observation, picking events, and leak-free destruction.
 */

"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { AtlasGlobeCamera, GlobeStatus } from "@/lib/maps/globe/types";
import { radiansToDegrees, degreesToRadians } from "@/lib/maps/globe/coordinates";

interface UseCesiumViewerOptions {
  containerRef: React.RefObject<HTMLDivElement | null>;
  initialCamera?: AtlasGlobeCamera;
  onCameraChange?: (camera: AtlasGlobeCamera) => void;
  onFeaturePick?: (featureId: string | null, position?: { lon: number; lat: number; height: number }) => void;
  imageryUrl?: string;
  imageryAttribution?: string;
}

export function useCesiumViewer({
  containerRef,
  initialCamera,
  onCameraChange,
  onFeaturePick,
  imageryUrl = "https://naturalearth.cesium.com/tiles/{z}/{x}/{y}.png",
  imageryAttribution = "© Natural Earth (Public Domain)",
}: UseCesiumViewerOptions) {
  const viewerRef = useRef<any>(null);
  const [status, setStatus] = useState<GlobeStatus>("INITIALIZING");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cesiumModule, setCesiumModule] = useState<any>(null);

  // Initialize Cesium on client
  useEffect(() => {
    let isMounted = true;

    async function initCesium() {
      if (typeof window === "undefined" || !containerRef.current) return;

      try {
        // Set Cesium base URL before loading scripts/workers
        (window as any).CESIUM_BASE_URL = "/cesium";

        // Dynamically import Cesium ES module
        const Cesium = await import("cesium");
        if (!isMounted) return;
        setCesiumModule(Cesium);

        // Check WebGL availability
        const canvas = document.createElement("canvas");
        const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
        if (!gl) {
          setStatus("WEBGL_UNAVAILABLE");
          setErrorMessage("WebGL is not supported or hardware acceleration is disabled in your browser.");
          return;
        }

        // Initialize Cesium Viewer with minimal institutional chrome
        const viewer = new Cesium.Viewer(containerRef.current, {
          animation: false,
          timeline: false,
          geocoder: false,
          homeButton: false,
          sceneModePicker: false,
          baseLayerPicker: false,
          navigationHelpButton: false,
          infoBox: false,
          fullscreenButton: false,
          selectionIndicator: false,
          orderIndependentTranslucency: false,
          contextOptions: {
            webgl: {
              preserveDrawingBuffer: false,
              failIfMajorPerformanceCaveat: false,
            },
          },
        });

        viewerRef.current = viewer;

        // Configure base imagery layer
        const baseLayer = new Cesium.UrlTemplateImageryProvider({
          url: imageryUrl,
          credit: new Cesium.Credit(imageryAttribution),
          maximumLevel: 9,
        });
        viewer.imageryLayers.removeAll();
        viewer.imageryLayers.addImageryProvider(baseLayer);

        // Standard WGS84 Ellipsoid (Ellipsoid Terrain)
        viewer.terrainProvider = new Cesium.EllipsoidTerrainProvider();

        // Initial camera position
        const cam = initialCamera || {
          longitude: 0.0,
          latitude: 20.0,
          height_meters: 20000000.0,
          heading_radians: 0.0,
          pitch_radians: -Math.PI / 2,
          roll_radians: 0.0,
        };

        viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(
            cam.longitude,
            cam.latitude,
            cam.height_meters
          ),
          orientation: {
            heading: cam.heading_radians,
            pitch: cam.pitch_radians,
            roll: cam.roll_radians,
          },
        });

        // Camera move end listener
        viewer.camera.moveEnd.addEventListener(() => {
          if (!onCameraChange || !viewer.camera) return;
          const cartographic = Cesium.Cartographic.fromCartesian(viewer.camera.position);
          const currentCam: AtlasGlobeCamera = {
            longitude: radiansToDegrees(cartographic.longitude),
            latitude: radiansToDegrees(cartographic.latitude),
            height_meters: cartographic.height,
            heading_radians: viewer.camera.heading,
            pitch_radians: viewer.camera.pitch,
            roll_radians: viewer.camera.roll,
            scene_mode: "SCENE3D",
            camera_schema_version: "1.0",
          };
          onCameraChange(currentCam);
        });

        // Screen space picking handler
        const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
        handler.setInputAction((click: any) => {
          if (!onFeaturePick) return;
          const pickedObject = viewer.scene.pick(click.position);
          const ray = viewer.camera.getPickRay(click.position);

          let groundPos = undefined;
          if (ray) {
            const groundCartesian = viewer.scene.globe.pick(ray, viewer.scene);
            if (groundCartesian) {
              const carto = Cesium.Cartographic.fromCartesian(groundCartesian);
              groundPos = {
                lon: radiansToDegrees(carto.longitude),
                lat: radiansToDegrees(carto.latitude),
                height: carto.height,
              };
            }
          }

          if (Cesium.defined(pickedObject) && pickedObject.id) {
            const featureId = typeof pickedObject.id === "string" ? pickedObject.id : pickedObject.id.id;
            onFeaturePick(featureId, groundPos);
          } else {
            onFeaturePick(null, groundPos);
          }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        // WebGL Context Lost handler
        const canvasEl = viewer.canvas;
        const handleContextLost = (e: Event) => {
          e.preventDefault();
          setStatus("ERROR");
          setErrorMessage("WebGL context was lost. GPU resources reset.");
        };
        canvasEl.addEventListener("webglcontextlost", handleContextLost, false);

        setStatus("READY");
      } catch (err: any) {
        if (!isMounted) return;
        setStatus("ERROR");
        setErrorMessage(err?.message || "Failed to initialize 3D Globe.");
      }
    }

    initCesium();

    return () => {
      isMounted = false;
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, [containerRef]);

  // ResizeObserver handling
  useEffect(() => {
    if (!containerRef.current || !viewerRef.current) return;

    const observer = new ResizeObserver(() => {
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.resize();
      }
    });

    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [containerRef, status]);

  // Camera FlyTo helper
  const flyTo = useCallback(
    (lon: number, lat: number, heightMeters: number = 5000.0, headingRad: number = 0.0) => {
      if (!viewerRef.current || !cesiumModule) return;
      viewerRef.current.camera.flyTo({
        destination: cesiumModule.Cartesian3.fromDegrees(lon, lat, heightMeters),
        orientation: {
          heading: headingRad,
          pitch: -Math.PI / 4, // 45 deg angle
          roll: 0.0,
        },
        duration: 2.0,
      });
    },
    [cesiumModule]
  );

  // Switch Imagery helper
  const switchImagery = useCallback(
    (url: string, creditText: string) => {
      if (!viewerRef.current || !cesiumModule) return;
      const layers = viewerRef.current.imageryLayers;
      layers.removeAll();
      const provider = new cesiumModule.UrlTemplateImageryProvider({
        url,
        credit: new cesiumModule.Credit(creditText),
      });
      layers.addImageryProvider(provider);
    },
    [cesiumModule]
  );

  return {
    viewer: viewerRef.current,
    cesium: cesiumModule,
    status,
    errorMessage,
    flyTo,
    switchImagery,
  };
}
