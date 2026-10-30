"use client";

import React, { useState } from "react";
import {
  Briefcase,
  Building2,
  Check,
  CheckCircle2,
  Copy,
  ExternalLink,
  Globe,
  Grid,
  Layers,
  Layout,
  LineChart,
  Monitor,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  Star,
  Trash2,
} from "lucide-react";
import { Badge, Button, MetricCard, PageHeader } from "@/design-system";
import { Workspace, WorkspaceSortOption, WorkspaceTemplate } from "@/lib/workspaces/types";
import { WorkspaceCreateDialog } from "./WorkspaceCreateDialog";

interface WorkspaceHomeProps {
  workspaces: Workspace[];
  allWorkspaces: Workspace[];
  templates: WorkspaceTemplate[];
  isLoading: boolean;
  error: string | null;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  sortBy: WorkspaceSortOption;
  setSortBy: (sort: WorkspaceSortOption) => void;
  activeTab: "ALL" | "FAVORITES" | "RECENT" | "TEMPLATES";
  setActiveTab: (tab: "ALL" | "FAVORITES" | "RECENT" | "TEMPLATES") => void;
  onOpenWorkspace: (workspaceId: string) => void;
  onCreateWorkspace: (name: string, description?: string, templateId?: string) => Promise<any>;
  onDuplicateWorkspace: (workspaceId: string, newName?: string) => Promise<any>;
  onDeleteWorkspace: (workspaceId: string) => Promise<any>;
  onToggleFavorite: (workspace: Workspace) => Promise<any>;
  onSetDefault: (workspaceId: string) => Promise<any>;
  onRefresh: () => Promise<void>;
}

export function WorkspaceHome({
  workspaces,
  allWorkspaces,
  templates,
  isLoading,
  error,
  searchQuery,
  setSearchQuery,
  sortBy,
  setSortBy,
  activeTab,
  setActiveTab,
  onOpenWorkspace,
  onCreateWorkspace,
  onDuplicateWorkspace,
  onDeleteWorkspace,
  onToggleFavorite,
  onSetDefault,
  onRefresh,
}: WorkspaceHomeProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [duplicatingId, setDuplicatingId] = useState<string | null>(null);

  // Metrics
  const totalDesks = allWorkspaces.length;
  const favoriteDesks = allWorkspaces.filter((w) => w.is_favorite).length;
  const defaultDesk = allWorkspaces.find((w) => w.is_default);

  const getTemplateIcon = (id: string) => {
    switch (id) {
      case "EQUITY_RESEARCH_DESK":
        return <Building2 className="w-5 h-5 text-blue-400" />;
      case "MARKET_MONITORING_DESK":
        return <Globe className="w-5 h-5 text-emerald-400" />;
      case "MACRO_DESK":
        return <LineChart className="w-5 h-5 text-purple-400" />;
      case "PORTFOLIO_DESK":
        return <Briefcase className="w-5 h-5 text-amber-400" />;
      case "RISK_DESK":
        return <ShieldAlert className="w-5 h-5 text-rose-400" />;
      default:
        return <Layout className="w-5 h-5 text-cyan-400" />;
    }
  };

  const handleLaunchTemplate = async (tmpl: WorkspaceTemplate) => {
    try {
      const created = await onCreateWorkspace(
        tmpl.name,
        tmpl.description,
        tmpl.template_id === "BLANK_DESK" ? undefined : tmpl.template_id
      );
      if (created && created.workspace_id) {
        onOpenWorkspace(created.workspace_id);
      }
    } catch (err) {
      console.error("Failed to launch template:", err);
    }
  };

  const handleDelete = async (e: React.MouseEvent, wsId: string) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this analytical workspace?")) {
      setDeletingId(wsId);
      try {
        await onDeleteWorkspace(wsId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  const handleDuplicate = async (e: React.MouseEvent, wsId: string, name: string) => {
    e.stopPropagation();
    setDuplicatingId(wsId);
    try {
      await onDuplicateWorkspace(wsId, `${name} (Copy)`);
    } finally {
      setDuplicatingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-y-auto custom-scrollbar font-mono">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0 flex items-center justify-between">
        <PageHeader
          title="Analytical Workspaces & Multi-Panel Desktop"
          description="Bloomberg-grade dockable windowing, multi-panel layouts, and cross-panel context synchronization."
          className="mb-0 pb-0 border-b-0"
        />
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="xs"
            onClick={onRefresh}
            disabled={isLoading}
            className="text-atlas-text-muted hover:text-atlas-text-primary"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button variant="primary" size="xs" onClick={() => setIsCreateOpen(true)}>
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            New Workspace Desk
          </Button>
        </div>
      </div>

      <div className="p-6 space-y-6 flex-1">
        {/* Metric Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="TOTAL DESKS"
            value={totalDesks}
            format="number"
            className="bg-atlas-surface-1 border-atlas-border-default"
          />
          <MetricCard
            title="FAVORITE DESKS"
            value={favoriteDesks}
            format="number"
            className="bg-atlas-surface-1 border-atlas-border-default"
          />
          <MetricCard
            title="DEFAULT DESK"
            value={defaultDesk ? defaultDesk.name : "None Set"}
            format="raw"
            className="bg-atlas-surface-1 border-atlas-border-default"
          />
          <MetricCard
            title="INSTITUTIONAL TEMPLATES"
            value={templates.length}
            format="number"
            className="bg-atlas-surface-1 border-atlas-border-default"
          />
        </div>

        {/* Tab Navigation and Controls Bar */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-b border-atlas-border-default pb-3">
          {/* Tabs */}
          <div className="flex items-center gap-1 bg-atlas-surface-1 p-1 rounded-sm border border-atlas-border-default text-xs">
            <button
              type="button"
              onClick={() => setActiveTab("ALL")}
              className={`px-3 py-1.5 rounded-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "ALL"
                  ? "bg-atlas-surface-3 text-atlas-text-primary font-bold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <Layout className="w-3.5 h-3.5" />
              <span>All Desks ({allWorkspaces.length})</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("FAVORITES")}
              className={`px-3 py-1.5 rounded-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "FAVORITES"
                  ? "bg-atlas-surface-3 text-atlas-text-primary font-bold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <Star className="w-3.5 h-3.5 text-amber-400" />
              <span>Favorites ({favoriteDesks})</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("RECENT")}
              className={`px-3 py-1.5 rounded-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "RECENT"
                  ? "bg-atlas-surface-3 text-atlas-text-primary font-bold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <Monitor className="w-3.5 h-3.5 text-blue-400" />
              <span>Recent Desks</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("TEMPLATES")}
              className={`px-3 py-1.5 rounded-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "TEMPLATES"
                  ? "bg-atlas-surface-3 text-atlas-text-primary font-bold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              <span>Template Gallery ({templates.length})</span>
            </button>
          </div>

          {/* Search & Sort Controls */}
          {activeTab !== "TEMPLATES" && (
            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="relative flex-1 md:w-64">
                <Search className="w-3.5 h-3.5 text-atlas-text-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter workspaces..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-atlas-surface-1 border border-atlas-border-default rounded-sm pl-8 pr-3 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-atlas-border-focus"
                />
              </div>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as WorkspaceSortOption)}
                className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus"
              >
                <option value="RECENTLY_OPENED">Recently Opened</option>
                <option value="RECENTLY_MODIFIED">Recently Modified</option>
                <option value="NAME">Name (A-Z)</option>
                <option value="FAVORITES">Favorites</option>
              </select>
            </div>
          )}
        </div>

        {/* Workspace Cards Grid or Templates View */}
        {activeTab === "TEMPLATES" ? (
          <div className="space-y-4">
            <div className="text-xs text-atlas-text-muted">
              Select an institutional template to instantiate a ready-to-use analytical workspace with pre-configured
              docked panels, linked context dimensions, and financial data adapters.
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((tmpl) => (
                <div
                  key={tmpl.template_id}
                  className="flex flex-col justify-between p-4 bg-atlas-surface-1 border border-atlas-border-default rounded-sm hover:border-atlas-border-focus transition-all group"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <div className="p-2 bg-atlas-surface-2 rounded-sm border border-atlas-border-subtle">
                          {getTemplateIcon(tmpl.template_id)}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-atlas-text-primary group-hover:text-blue-400 transition-colors">
                            {tmpl.name}
                          </h4>
                          <span className="text-[10px] text-atlas-text-muted uppercase font-mono">
                            {tmpl.category || "INSTITUTIONAL"}
                          </span>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-[9px] font-mono">
                        {tmpl.panel_definitions.length} Panels
                      </Badge>
                    </div>

                    <p className="text-xs font-sans text-atlas-text-muted leading-relaxed mb-4">
                      {tmpl.description}
                    </p>

                    <div className="space-y-1.5 mb-4">
                      <span className="text-[10px] uppercase font-bold text-atlas-text-muted">Pre-docked Panels</span>
                      <div className="flex flex-wrap gap-1">
                        {tmpl.panel_definitions.map((p) => (
                          <span
                            key={p.panel_instance_id}
                            className="px-1.5 py-0.5 bg-atlas-surface-2 border border-atlas-border-subtle rounded-xs text-[10px] text-atlas-text-primary"
                          >
                            {p.title_override || p.panel_type_id}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Button
                    variant="primary"
                    size="xs"
                    onClick={() => handleLaunchTemplate(tmpl)}
                    className="w-full mt-2"
                  >
                    <Plus className="w-3.5 h-3.5 mr-1" />
                    Instantiate Workspace
                  </Button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            {workspaces.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 bg-atlas-surface-1 border border-dashed border-atlas-border-default rounded-sm text-center">
                <Layout className="w-10 h-10 text-atlas-text-muted mb-3 opacity-40" />
                <h4 className="text-sm font-bold text-atlas-text-primary mb-1">No Workspaces Found</h4>
                <p className="text-xs text-atlas-text-muted max-w-sm mb-4 font-sans">
                  {searchQuery
                    ? `No analytical desks matching "${searchQuery}".`
                    : "Create your first multi-panel desk or choose from our institutional templates."}
                </p>
                <div className="flex items-center gap-2">
                  {searchQuery && (
                    <Button variant="secondary" size="xs" onClick={() => setSearchQuery("")}>
                      Clear Filter
                    </Button>
                  )}
                  <Button variant="primary" size="xs" onClick={() => setIsCreateOpen(true)}>
                    <Plus className="w-3.5 h-3.5 mr-1" />
                    Create Desk
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {workspaces.map((ws) => {
                  const panelCount =
                    ws.panel_count ??
                    (ws.layout?.panel_instances ? Object.keys(ws.layout.panel_instances).length : 0);
                  return (
                    <div
                      key={ws.workspace_id}
                      onClick={() => onOpenWorkspace(ws.workspace_id)}
                      className="flex flex-col justify-between p-4 bg-atlas-surface-1 border border-atlas-border-default rounded-sm hover:border-atlas-border-focus hover:shadow-lg transition-all cursor-pointer group"
                    >
                      <div>
                        {/* Header bar of Card */}
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex items-center gap-2 min-w-0">
                            <h4 className="text-sm font-bold text-atlas-text-primary group-hover:text-blue-400 transition-colors truncate">
                              {ws.name}
                            </h4>
                          </div>

                          <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
                            <button
                              type="button"
                              title={ws.is_favorite ? "Remove from Favorites" : "Add to Favorites"}
                              onClick={() => onToggleFavorite(ws)}
                              className="p-1 rounded-xs text-atlas-text-muted hover:text-amber-400 hover:bg-atlas-surface-2 transition-colors"
                            >
                              <Star
                                className={`w-3.5 h-3.5 ${
                                  ws.is_favorite ? "text-amber-400 fill-amber-400" : ""
                                }`}
                              />
                            </button>
                            <button
                              type="button"
                              title="Duplicate Workspace"
                              disabled={duplicatingId === ws.workspace_id}
                              onClick={(e) => handleDuplicate(e, ws.workspace_id, ws.name)}
                              className="p-1 rounded-xs text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors"
                            >
                              <Copy className="w-3.5 h-3.5" />
                            </button>
                            <button
                              type="button"
                              title="Delete Workspace"
                              disabled={deletingId === ws.workspace_id}
                              onClick={(e) => handleDelete(e, ws.workspace_id)}
                              className="p-1 rounded-xs text-atlas-text-muted hover:text-rose-400 hover:bg-atlas-surface-2 transition-colors"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>

                        {/* Badges */}
                        <div className="flex flex-wrap items-center gap-1.5 mb-3">
                          {ws.is_default && (
                            <Badge variant="positive" className="text-[9px] font-mono px-1.5 py-0.2">
                              DEFAULT
                            </Badge>
                          )}
                          <Badge variant="outline" className="text-[9px] font-mono px-1.5 py-0.2">
                            {ws.workspace_type}
                          </Badge>
                          <Badge variant="default" className="text-[9px] font-mono px-1.5 py-0.2">
                            {panelCount} PANELS
                          </Badge>
                          <span className="text-[10px] text-atlas-text-muted font-mono ml-auto">
                            rev {ws.layout_revision}
                          </span>
                        </div>

                        {/* Description */}
                        <p className="text-xs font-sans text-atlas-text-muted line-clamp-2 leading-relaxed mb-4">
                          {ws.description || "Custom multi-panel financial analytical desktop layout."}
                        </p>
                      </div>

                      {/* Footer Actions */}
                      <div
                        className="pt-3 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <div className="flex items-center gap-2">
                          {!ws.is_default && (
                            <button
                              type="button"
                              onClick={() => onSetDefault(ws.workspace_id)}
                              className="text-blue-400 hover:underline flex items-center gap-1"
                            >
                              <CheckCircle2 className="w-3 h-3" />
                              Set as Default
                            </button>
                          )}
                        </div>

                        <Button
                          variant="secondary"
                          size="xs"
                          onClick={() => onOpenWorkspace(ws.workspace_id)}
                          className="group-hover:border-blue-500 group-hover:text-blue-400"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          Open Desk
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal Dialog */}
      <WorkspaceCreateDialog
        isOpen={isCreateOpen}
        templates={templates}
        onClose={() => setIsCreateOpen(false)}
        onCreate={async (name, desc, tmplId) => {
          const res = await onCreateWorkspace(name, desc, tmplId);
          if (res && res.workspace_id) {
            onOpenWorkspace(res.workspace_id);
          }
        }}
      />
    </div>
  );
}
