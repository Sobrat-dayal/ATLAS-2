"use client";

import React, { useState } from "react";
import { Briefcase, Building2, Globe, Layout, LineChart, Plus, ShieldAlert, X } from "lucide-react";
import { Button } from "@/design-system";
import { WorkspaceTemplate } from "@/lib/workspaces/types";

interface WorkspaceCreateDialogProps {
  isOpen: boolean;
  templates: WorkspaceTemplate[];
  onClose: () => void;
  onCreate: (name: string, description?: string, templateId?: string) => Promise<any>;
}

export function WorkspaceCreateDialog({
  isOpen,
  templates,
  onClose,
  onCreate,
}: WorkspaceCreateDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("EQUITY_RESEARCH_DESK");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      await onCreate(
        name.trim(),
        description.trim() || undefined,
        selectedTemplateId === "BLANK_DESK" ? undefined : selectedTemplateId
      );
      onClose();
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTemplateIcon = (id: string) => {
    switch (id) {
      case "EQUITY_RESEARCH_DESK":
        return <Building2 className="w-4 h-4 text-blue-400" />;
      case "MARKET_MONITORING_DESK":
        return <Globe className="w-4 h-4 text-emerald-400" />;
      case "MACRO_DESK":
        return <LineChart className="w-4 h-4 text-purple-400" />;
      case "PORTFOLIO_DESK":
        return <Briefcase className="w-4 h-4 text-amber-400" />;
      case "RISK_DESK":
        return <ShieldAlert className="w-4 h-4 text-rose-400" />;
      default:
        return <Layout className="w-4 h-4 text-atlas-text-muted" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-xl bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">Create New Workspace Desk</h3>
          </div>
          <button type="button" onClick={onClose} className="text-atlas-text-muted hover:text-atlas-text-primary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-bold text-atlas-text-muted">Desk Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Technology Quantitative Alpha Desk"
              required
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[10px] uppercase font-bold text-atlas-text-muted">Description (Optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Analytical objective or focus universe..."
              className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus font-sans"
            />
          </div>

          <div className="pt-2 border-t border-atlas-border-subtle">
            <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1.5">
              Select Starting Template
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-56 overflow-auto custom-scrollbar p-0.5">
              {templates.map((tmpl) => {
                const isSelected = selectedTemplateId === tmpl.template_id;
                return (
                  <div
                    key={tmpl.template_id}
                    onClick={() => {
                      setSelectedTemplateId(tmpl.template_id);
                      if (!name) {
                        setName(tmpl.name);
                      }
                    }}
                    className={`p-2.5 rounded-sm border cursor-pointer transition-colors flex flex-col justify-between ${
                      isSelected
                        ? "border-blue-500 bg-blue-500/10 text-atlas-text-primary"
                        : "border-atlas-border-default bg-atlas-surface-0 hover:bg-atlas-surface-hover text-atlas-text-muted"
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-1.5 font-bold text-xs text-atlas-text-primary mb-1">
                        {getTemplateIcon(tmpl.template_id)}
                        <span>{tmpl.name}</span>
                      </div>
                      <p className="text-[10px] font-sans text-atlas-text-muted leading-tight line-clamp-2">
                        {tmpl.description}
                      </p>
                    </div>
                    <span className="text-[9px] uppercase font-mono text-blue-400 mt-2">
                      {tmpl.panel_definitions.length} Panels
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-atlas-border-default mt-4">
            <Button variant="ghost" size="xs" type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button variant="primary" size="xs" type="submit" disabled={!name.trim() || isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Desk"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

