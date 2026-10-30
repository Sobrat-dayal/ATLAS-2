"use client";

import React, { useEffect, useState } from "react";
import { AtlasMap } from "@/components/maps/AtlasMap";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";
import { MapCameraState, UserMapView } from "@/lib/maps/types";
import { DEFAULT_CAMERA } from "@/lib/maps/styles";

interface MapPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

export function MapPanelAdapter({
  panel,
  context,
  onUpdateContext,
  onUpdateConfig,
}: MapPanelAdapterProps) {
  // Panel configuration or fallback
  const initialCamera: MapCameraState = (panel.configuration?.camera as MapCameraState) || {
    ...DEFAULT_CAMERA,
    revision: 1,
  };

  const initialStyleId = (panel.configuration?.basemap_style_id as string) || "atlas-dark";

  const [panelView] = useState<UserMapView>({
    map_view_id: `ws_panel_${panel.panel_instance_id}`,
    owner_user_id: "workspace_user",
    name: panel.title_override || "Workspace Map Panel",
    camera: initialCamera,
    basemap_style_id: initialStyleId,
    visible_layers: (panel.configuration?.visible_layers as string[]) || [
      "atlas.layer.financial_centers",
      "atlas.layer.world_boundaries",
    ],
    layer_configurations: {},
    selected_feature_id: null,
    workspace_id: panel.panel_instance_id,
    revision: 1,
    map_schema_version: "1.0.0",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  });

  // Handle global linking if not in independent mode
  useEffect(() => {
    if (!panel.independent_mode) {
      if (context.REGION && typeof context.REGION === "string") {
        // e.g. Region or Financial Center linked
      }
    }
  }, [context.REGION, panel.independent_mode]);

  return (
    <div className="h-full w-full overflow-hidden">
      <AtlasMap
        initialView={panelView}
        workspaceId={panel.panel_instance_id}
      />
    </div>
  );
}

