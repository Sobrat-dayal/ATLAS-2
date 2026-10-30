"use client";

import React from "react";
import {
  Columns2,
  Maximize2,
  Minimize2,
  Rows2,
  Settings2,
  X,
} from "lucide-react";
import {
  WorkspaceLinkGroup,
  WorkspacePanelInstance,
} from "@/lib/workspaces/types";
import { ChartPanelAdapter } from "./adapters/ChartPanelAdapter";
import { CompanyPanelAdapter } from "./adapters/CompanyPanelAdapter";
import { EconomicsPanelAdapter } from "./adapters/EconomicsPanelAdapter";
import { GenericPanelAdapter } from "./adapters/GenericPanelAdapter";
import { MarketPanelAdapter } from "./adapters/MarketPanelAdapter";
import { NewsPanelAdapter } from "./adapters/NewsPanelAdapter";
import { PortfolioPanelAdapter } from "./adapters/PortfolioPanelAdapter";
import { RiskPanelAdapter } from "./adapters/RiskPanelAdapter";
import { WatchlistPanelAdapter } from "./adapters/WatchlistPanelAdapter";
import { WorkspacePanelErrorBoundary } from "./WorkspacePanelErrorBoundary";

interface WorkspacePanelHostProps {
  panel: WorkspacePanelInstance;
  linkGroups: WorkspaceLinkGroup[];
  isMaximized?: boolean;
  onToggleMaximize?: () => void;
  onSplitRight?: () => void;
  onSplitBottom?: () => void;
  onClose?: () => void;
  onUpdateContext?: (updates: Record<string, unknown>) => void;
  onUpdateConfig?: (cfg: Record<string, unknown>) => void;
  onOpenSettings?: () => void;
}

export function WorkspacePanelHost({
  panel,
  linkGroups,
  isMaximized = false,
  onToggleMaximize,
  onSplitRight,
  onSplitBottom,
  onClose,
  onUpdateContext,
  onUpdateConfig,
  onOpenSettings,
}: WorkspacePanelHostProps) {
  // Find associated link group
  const activeLinkGroup = linkGroups.find((g) => g.link_group_id === panel.link_group_id);
  const context = activeLinkGroup ? activeLinkGroup.context : {};

  const handleUpdateContext = (updates: Record<string, unknown>) => {
    if (activeLinkGroup && onUpdateContext) {
      onUpdateContext(updates);
    }
  };

  const handleUpdateConfig = (cfg: Record<string, unknown>) => {
    if (onUpdateConfig) {
      onUpdateConfig(cfg);
    }
  };

  const renderAdapter = () => {
    switch (panel.panel_type_id) {
      case "MARKET_OVERVIEW":
        return (
          <MarketPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "INSTRUMENT_CHART":
        return (
          <ChartPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "WATCHLIST":
        return (
          <WatchlistPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "COMPANY_OVERVIEW":
        return (
          <CompanyPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "NEWS_FEED":
        return (
          <NewsPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "ECONOMIC_SERIES":
        return (
          <EconomicsPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "PORTFOLIO_SUMMARY":
      case "PORTFOLIO_PERFORMANCE":
        return (
          <PortfolioPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      case "RISK_OVERVIEW":
      case "RISK_ANALYSIS":
        return (
          <RiskPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
      default:
        return (
          <GenericPanelAdapter
            panel={panel}
            context={context}
            onUpdateContext={handleUpdateContext}
            onUpdateConfig={handleUpdateConfig}
          />
        );
    }
  };

  return (
    <div className="flex flex-col w-full h-full border border-atlas-border-default bg-atlas-surface-0 overflow-hidden rounded-sm select-none">
      {/* Panel Top Titlebar */}
      <div className="flex items-center justify-between px-2.5 py-1 bg-atlas-surface-2 border-b border-atlas-border-default shrink-0">
        <div className="flex items-center gap-2 truncate">
          <span className="text-xs font-semibold text-atlas-text-primary truncate">
            {panel.title_override || panel.panel_type_id}
          </span>

          {/* Link Group Badge */}
          {activeLinkGroup && (
            <span
              className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-full text-[9px] font-mono border"
              style={{
                borderColor: `${activeLinkGroup.color}40`,
                backgroundColor: `${activeLinkGroup.color}15`,
                color: activeLinkGroup.color,
              }}
              title={`Linked to ${activeLinkGroup.name}: ${JSON.stringify(activeLinkGroup.context)}`}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: activeLinkGroup.color }}
              />
              <span>{activeLinkGroup.name}</span>
            </span>
          )}

          {panel.independent_mode && (
            <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-atlas-surface-3 text-atlas-text-muted">
              Independent
            </span>
          )}
        </div>

        {/* Toolbar Buttons */}
        <div className="flex items-center gap-1 shrink-0 text-atlas-text-muted">
          {onSplitRight && (
            <button
              type="button"
              onClick={onSplitRight}
              className="p-1 hover:text-atlas-text-primary rounded-sm hover:bg-atlas-surface-hover"
              title="Split Panel Right"
            >
              <Columns2 className="w-3.5 h-3.5" />
            </button>
          )}

          {onSplitBottom && (
            <button
              type="button"
              onClick={onSplitBottom}
              className="p-1 hover:text-atlas-text-primary rounded-sm hover:bg-atlas-surface-hover"
              title="Split Panel Down"
            >
              <Rows2 className="w-3.5 h-3.5" />
            </button>
          )}

          {onToggleMaximize && (
            <button
              type="button"
              onClick={onToggleMaximize}
              className="p-1 hover:text-atlas-text-primary rounded-sm hover:bg-atlas-surface-hover"
              title={isMaximized ? "Restore Layout" : "Maximize Panel"}
            >
              {isMaximized ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
            </button>
          )}

          {onOpenSettings && (
            <button
              type="button"
              onClick={onOpenSettings}
              className="p-1 hover:text-atlas-text-primary rounded-sm hover:bg-atlas-surface-hover"
              title="Panel Settings"
            >
              <Settings2 className="w-3.5 h-3.5" />
            </button>
          )}

          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="p-1 hover:text-rose-400 rounded-sm hover:bg-rose-500/10"
              title="Close Panel"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Panel Inner Content Body */}
      <div className="flex-1 w-full h-full overflow-hidden relative">
        <WorkspacePanelErrorBoundary
          panelId={panel.panel_instance_id}
          panelTitle={panel.title_override || panel.panel_type_id}
        >
          {renderAdapter()}
        </WorkspacePanelErrorBoundary>
      </div>
    </div>
  );
}

