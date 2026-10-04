"use client";

import { useShellState } from "@/hooks/shell/useShellState";
import { Terminal, CheckSquare, Activity, AlertTriangle, Cpu, ActivitySquare, Server } from "lucide-react";

export function BottomTaskbar() {
  const { activeBottomPanel, setActiveBottomPanel } = useShellState();

  const togglePanel = (panelId: string) => {
    setActiveBottomPanel(activeBottomPanel === panelId ? null : panelId);
  };

  const panels = [
    { id: "tasks", label: "Tasks", icon: CheckSquare },
    { id: "agents", label: "Agents", icon: Cpu },
    { id: "jobs", label: "Jobs", icon: ActivitySquare },
    { id: "alerts", label: "Alerts", icon: AlertTriangle },
    { id: "system", label: "System", icon: Server },
  ];

  return (
    <div className="flex h-8 shrink-0 flex-col border-t border-atlas-border-default bg-atlas-surface-1">
      {/* Optional: Future Bottom Panel Area (Rendered here when activeBottomPanel is set) */}
      {activeBottomPanel && (
        <div className="absolute bottom-8 left-[var(--atlas-sidebar-width,160px)] right-0 h-[260px] border-t border-atlas-border-default bg-atlas-surface-1 z-20 flex flex-col shadow-lg">
          <div className="flex h-8 items-center justify-between border-b border-atlas-border-default px-3 bg-atlas-surface-2">
            <span className="text-xs font-semibold uppercase text-atlas-text-primary">{activeBottomPanel}</span>
            <button onClick={() => setActiveBottomPanel(null)} className="text-atlas-text-muted hover:text-atlas-text-primary">✕</button>
          </div>
          <div className="flex-1 p-3 text-sm text-atlas-text-muted overflow-y-auto">
            {activeBottomPanel} panel placeholder. Logic deferred.
          </div>
        </div>
      )}

      {/* Taskbar */}
      <div className="flex h-full items-center justify-between px-2 text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">
        <div className="flex h-full items-center">
          {panels.map((panel) => (
            <button
              key={panel.id}
              onClick={() => togglePanel(panel.id)}
              className={`flex h-full items-center px-3 transition-colors hover:bg-atlas-surface-hover hover:text-atlas-text-primary ${
                activeBottomPanel === panel.id ? "bg-atlas-surface-selected text-atlas-accent" : ""
              }`}
            >
              <panel.icon className="mr-1.5 h-3.5 w-3.5" />
              {panel.label}
            </button>
          ))}
        </div>

        <div className="flex h-full items-center">
          <button
            onClick={() => togglePanel("terminal")}
            className={`flex h-full items-center px-3 transition-colors hover:bg-atlas-surface-hover hover:text-atlas-text-primary ${
              activeBottomPanel === "terminal" ? "bg-atlas-surface-selected text-atlas-accent" : ""
            }`}
          >
            <Terminal className="mr-1.5 h-3.5 w-3.5" />
            Terminal
          </button>
        </div>
      </div>
    </div>
  );
}
