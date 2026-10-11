"use client";

import React from "react";
import { Activity, CheckCircle2, HelpCircle, Info } from "lucide-react";

export function SystemHealthPanel() {
  const healthDimensions = [
    {
      name: "Market Data WebSocket (Stage 43)",
      status: "Connected",
      badgeColor: "text-atlas-positive border-atlas-positive/30 bg-atlas-positive/10",
      description: "WebSocket connection established in AppShell",
      verified: true,
    },
    {
      name: "FastAPI Backend API (Stage 11)",
      status: "Reachable",
      badgeColor: "text-atlas-positive border-atlas-positive/30 bg-atlas-positive/10",
      description: "Authenticated REST endpoints available",
      verified: true,
    },
    {
      name: "PostgreSQL / Supabase (Stage 12)",
      status: "Status unavailable",
      badgeColor: "text-atlas-text-muted border-atlas-border-subtle bg-atlas-surface-2",
      description: "Detailed database telemetry not connected",
      verified: false,
    },
    {
      name: "ClickHouse Ingestion (Stage 37)",
      status: "Status unavailable",
      badgeColor: "text-atlas-text-muted border-atlas-border-subtle bg-atlas-surface-2",
      description: "Analytical database telemetry not connected",
      verified: false,
    },
    {
      name: "Redis / Valkey Cache (Stage 38)",
      status: "Status unavailable",
      badgeColor: "text-atlas-text-muted border-atlas-border-subtle bg-atlas-surface-2",
      description: "In-memory cache telemetry not connected",
      verified: false,
    },
    {
      name: "Market Data Workers (Stage 40)",
      status: "Status unavailable",
      badgeColor: "text-atlas-text-muted border-atlas-border-subtle bg-atlas-surface-2",
      description: "Worker process telemetry not connected",
      verified: false,
    },
  ];

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4 select-none">
      <div className="flex items-center justify-between mb-3 border-b border-atlas-border-default pb-2">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-atlas-accent" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            System Connectivity &amp; Health
          </h4>
        </div>
        <span className="text-[11px] text-atlas-text-muted font-mono">
          Stage 50 Read-Only Shell
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
        {healthDimensions.map((dim) => (
          <div
            key={dim.name}
            className="flex items-start justify-between p-2.5 rounded border border-atlas-border-default bg-atlas-surface-2/40"
          >
            <div className="flex flex-col pr-2">
              <span className="text-xs font-medium text-atlas-text-primary">
                {dim.name}
              </span>
              <span className="text-[11px] text-atlas-text-muted mt-0.5">
                {dim.description}
              </span>
            </div>
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium border shrink-0 ${dim.badgeColor}`}
            >
              {dim.verified ? (
                <CheckCircle2 className="h-2.5 w-2.5" />
              ) : (
                <HelpCircle className="h-2.5 w-2.5" />
              )}
              {dim.status}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-auto border-t border-atlas-border-subtle pt-2 flex items-center gap-2 text-[11px] text-atlas-text-muted">
        <Info className="h-3.5 w-3.5 shrink-0 text-atlas-accent/80" />
        <span>
          Grounded reporting: Connectivity != service health. Detailed Prometheus/Grafana monitoring will be integrated in future observability stages. No internal credentials, secrets, or IP addresses are exposed.
        </span>
      </div>
    </div>
  );
}
