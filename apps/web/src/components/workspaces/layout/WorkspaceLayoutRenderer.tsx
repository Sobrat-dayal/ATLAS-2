"use client";

import React from "react";
import { AtlasPanel, AtlasResizeHandle, AtlasSplit } from "@/design-system";
import {
  LayoutNode,
  PanelNode,
  SplitNode,
  TabStackNode,
  WorkspaceLinkGroup,
  WorkspacePanelInstance,
} from "@/lib/workspaces/types";
import { WorkspacePanelHost } from "../panels/WorkspacePanelHost";

interface WorkspaceLayoutRendererProps {
  node: LayoutNode;
  panelInstances: Record<string, WorkspacePanelInstance>;
  linkGroups: WorkspaceLinkGroup[];
  maximizedPanelId: string | null;
  onToggleMaximize: (panelId: string) => void;
  onSplitRight: (panelId: string) => void;
  onSplitBottom: (panelId: string) => void;
  onClosePanel: (panelId: string) => void;
  onSetActiveTab: (tabStackId: string, panelId: string) => void;
  onUpdateSplitRatios: (splitNodeId: string, newRatios: number[]) => void;
  onUpdateContext: (linkGroupId: string, updates: Record<string, unknown>) => void;
  onUpdateConfig: (panelId: string, updates: Partial<WorkspacePanelInstance>) => void;
  onOpenSettings?: (panelId: string) => void;
}

export function WorkspaceLayoutRenderer({
  node,
  panelInstances,
  linkGroups,
  maximizedPanelId,
  onToggleMaximize,
  onSplitRight,
  onSplitBottom,
  onClosePanel,
  onSetActiveTab,
  onUpdateSplitRatios,
  onUpdateContext,
  onUpdateConfig,
  onOpenSettings,
}: WorkspaceLayoutRendererProps) {
  // If maximized panel exists, render only that panel
  if (maximizedPanelId && panelInstances[maximizedPanelId]) {
    const panel = panelInstances[maximizedPanelId];
    return (
      <div className="w-full h-full p-1 bg-atlas-surface-0">
        <WorkspacePanelHost
          panel={panel}
          linkGroups={linkGroups}
          isMaximized={true}
          onToggleMaximize={() => onToggleMaximize(maximizedPanelId)}
          onClose={() => onClosePanel(maximizedPanelId)}
          onUpdateContext={(updates) => {
            if (panel.link_group_id) {
              onUpdateContext(panel.link_group_id, updates);
            }
          }}
          onUpdateConfig={(cfg) => onUpdateConfig(panel.panel_instance_id, { configuration: cfg })}
          onOpenSettings={onOpenSettings ? () => onOpenSettings(maximizedPanelId) : undefined}
        />
      </div>
    );
  }

  // Render Panel Node
  if (node.node_type === "PANEL") {
    const panel = panelInstances[node.panel_instance_id];
    if (!panel) {
      return (
        <div className="flex items-center justify-center h-full p-4 border border-atlas-border-subtle text-atlas-text-muted text-xs font-mono">
          Panel not found ({node.panel_instance_id})
        </div>
      );
    }

    return (
      <WorkspacePanelHost
        panel={panel}
        linkGroups={linkGroups}
        isMaximized={false}
        onToggleMaximize={() => onToggleMaximize(panel.panel_instance_id)}
        onSplitRight={() => onSplitRight(panel.panel_instance_id)}
        onSplitBottom={() => onSplitBottom(panel.panel_instance_id)}
        onClose={() => onClosePanel(panel.panel_instance_id)}
        onUpdateContext={(updates) => {
          if (panel.link_group_id) {
            onUpdateContext(panel.link_group_id, updates);
          }
        }}
        onUpdateConfig={(cfg) => onUpdateConfig(panel.panel_instance_id, { configuration: cfg })}
        onOpenSettings={onOpenSettings ? () => onOpenSettings(panel.panel_instance_id) : undefined}
      />
    );
  }

  // Render Tab Stack Node
  if (node.node_type === "TAB_STACK") {
    const activeId = node.active_panel_instance_id || node.panel_instance_ids[0];
    const activePanel = panelInstances[activeId];

    return (
      <div className="flex flex-col w-full h-full border border-atlas-border-default bg-atlas-surface-0 overflow-hidden rounded-sm">
        {/* Tab strip */}
        <div className="flex items-center px-1 bg-atlas-surface-2 border-b border-atlas-border-default shrink-0 overflow-x-auto gap-0.5 custom-scrollbar">
          {node.panel_instance_ids.map((pid) => {
            const p = panelInstances[pid];
            const isActive = pid === activeId;
            return (
              <button
                key={pid}
                type="button"
                onClick={() => onSetActiveTab(node.node_id, pid)}
                className={`px-3 py-1.5 text-xs font-mono border-b-2 transition-colors flex items-center gap-1.5 ${
                  isActive
                    ? "border-blue-500 text-atlas-text-primary bg-atlas-surface-0 font-semibold"
                    : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-1"
                }`}
              >
                <span>{p?.title_override || p?.panel_type_id || pid}</span>
              </button>
            );
          })}
        </div>

        {/* Tab active panel body */}
        <div className="flex-1 w-full h-full overflow-hidden">
          {activePanel ? (
            <WorkspacePanelHost
              panel={activePanel}
              linkGroups={linkGroups}
              isMaximized={false}
              onToggleMaximize={() => onToggleMaximize(activePanel.panel_instance_id)}
              onSplitRight={() => onSplitRight(activePanel.panel_instance_id)}
              onSplitBottom={() => onSplitBottom(activePanel.panel_instance_id)}
              onClose={() => onClosePanel(activePanel.panel_instance_id)}
              onUpdateContext={(updates) => {
                if (activePanel.link_group_id) {
                  onUpdateContext(activePanel.link_group_id, updates);
                }
              }}
              onUpdateConfig={(cfg) =>
                onUpdateConfig(activePanel.panel_instance_id, { configuration: cfg })
              }
              onOpenSettings={
                onOpenSettings ? () => onOpenSettings(activePanel.panel_instance_id) : undefined
              }
            />
          ) : (
            <div className="flex items-center justify-center h-full text-atlas-text-muted text-xs">
              No active tab selected
            </div>
          )}
        </div>
      </div>
    );
  }

  // Render Split Node
  if (node.node_type === "SPLIT") {
    const direction = node.orientation === "VERTICAL" ? "vertical" : "horizontal";
    // Convert ratios to percent for react-resizable-panels
    const defaultPercents = node.size_ratios.map((r) => Math.round(r * 100));

    return (
      <AtlasSplit
        id={`split_${node.node_id}`}
        direction={direction}
        className="w-full h-full"
      >
        {node.children.map((child, index) => {
          const ratioPercent = defaultPercents[index] || Math.round(100 / node.children.length);
          const isLast = index === node.children.length - 1;

          return (
            <React.Fragment key={child.node_id}>
              <AtlasPanel
                id={`panel_container_${child.node_id}`}
                minSize={15}
                defaultSize={ratioPercent}
                className="w-full h-full overflow-hidden"
              >
                <WorkspaceLayoutRenderer
                  node={child}
                  panelInstances={panelInstances}
                  linkGroups={linkGroups}
                  maximizedPanelId={maximizedPanelId}
                  onToggleMaximize={onToggleMaximize}
                  onSplitRight={onSplitRight}
                  onSplitBottom={onSplitBottom}
                  onClosePanel={onClosePanel}
                  onSetActiveTab={onSetActiveTab}
                  onUpdateSplitRatios={onUpdateSplitRatios}
                  onUpdateContext={onUpdateContext}
                  onUpdateConfig={onUpdateConfig}
                  onOpenSettings={onOpenSettings}
                />
              </AtlasPanel>
              {!isLast && <AtlasResizeHandle />}
            </React.Fragment>
          );
        })}
      </AtlasSplit>
    );
  }

  return null;
}

