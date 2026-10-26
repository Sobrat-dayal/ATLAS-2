"use client";

import React from "react";
import {
  AlertTriangle,
  Building2,
  Calendar,
  Clock,
  Cpu,
  FileText,
  History,
  Layers,
  Link2,
  Network,
  PieChart,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  Truck,
} from "lucide-react";
import {
  SupplyChainSubTab,
  useCompanySupplyChain,
} from "@/hooks/companies/useCompanySupplyChain";
import { CustomerConcentrationPanel } from "./CustomerConcentrationPanel";
import { CustomersTable } from "./CustomersTable";
import { RelationshipTimeline } from "./RelationshipTimeline";
import { SuppliersTable } from "./SuppliersTable";
import { SupplyChainCoveragePanel } from "./SupplyChainCoveragePanel";
import { SupplyChainEdgeInspector } from "./SupplyChainEdgeInspector";
import { SupplyChainNetworkGraph } from "./SupplyChainNetworkGraph";
import { SupplyChainOverviewCards } from "./SupplyChainOverviewCards";

interface SupplyChainWorkspaceProps {
  companyId: string;
  companyName: string;
  ticker?: string;
  className?: string;
}

export function SupplyChainWorkspace({
  companyId,
  companyName,
  ticker,
  className = "",
}: SupplyChainWorkspaceProps) {
  const {
    activeSubTab,
    setActiveSubTab,
    overview,
    suppliers,
    customers,
    network,
    networkDepth,
    setNetworkDepth,
    networkDirection,
    setNetworkDirection,
    concentration,
    history,
    coverage,
    tierFilter,
    setTierFilter,
    relationshipTypeFilter,
    setRelationshipTypeFilter,
    countryFilter,
    setCountryFilter,
    searchQuery,
    setSearchQuery,
    selectedRelationship,
    selectedEvidence,
    isEvidenceLoading,
    inspectRelationship,
    closeInspector,
    isLoading,
    error,
    refresh,
  } = useCompanySupplyChain(companyId);

  const subTabs: { id: SupplyChainSubTab; label: string; icon: React.ReactNode; count?: number }[] = [
    { id: "overview", label: "Overview", icon: <Building2 className="w-3.5 h-3.5" /> },
    {
      id: "suppliers",
      label: "Suppliers",
      icon: <Cpu className="w-3.5 h-3.5 text-blue-400" />,
      count: overview?.verified_tier_1_suppliers_count,
    },
    {
      id: "customers",
      label: "Customers & Channels",
      icon: <Truck className="w-3.5 h-3.5 text-emerald-400" />,
      count: overview?.verified_tier_1_customers_count,
    },
    { id: "network", label: "Network Explorer", icon: <Network className="w-3.5 h-3.5 text-purple-400" /> },
    {
      id: "concentration",
      label: "Dependency Analysis",
      icon: <PieChart className="w-3.5 h-3.5 text-amber-400" />,
    },
    {
      id: "history",
      label: "Historical Changes",
      icon: <History className="w-3.5 h-3.5 text-indigo-400" />,
      count: history?.total_events,
    },
    {
      id: "coverage",
      label: "Evidence & Coverage",
      icon: <ShieldCheck className="w-3.5 h-3.5 text-atlas-accent" />,
    },
  ];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Workspace Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-atlas-surface border border-atlas-border-subtle rounded-md">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-atlas-text-primary flex items-center gap-1.5">
              <Network className="w-4 h-4 text-atlas-accent" />
              Corporate Supply Chain Intelligence
            </h2>
            <span className="font-mono text-xs text-atlas-text-muted">
              {ticker ? `${ticker} • ` : ""}
              {companyName}
            </span>
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            Verified corporate network topology, multi-tier supplier precursors, customer revenue concentration, and regulatory filing citations.
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={refresh}
            disabled={isLoading}
            className="flex items-center gap-1 px-2.5 py-1 text-xs bg-atlas-surface-subtle hover:bg-atlas-accent hover:text-white text-atlas-text-secondary rounded border border-atlas-border-subtle transition-colors disabled:opacity-50"
            title="Refresh supply chain data"
          >
            <RefreshCw className={`w-3 h-3 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Subtab Navigation Bar */}
      <div className="flex items-center gap-1 border-b border-atlas-border-subtle overflow-x-auto pb-1 text-xs">
        {subTabs.map((tab) => {
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t font-medium transition-colors border-b-2 whitespace-nowrap ${
                isActive
                  ? "border-atlas-accent text-atlas-text-primary bg-atlas-surface"
                  : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-subtle/50"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className="font-mono text-[10px] bg-atlas-surface-subtle px-1.5 py-0.2 rounded text-atlas-text-muted">
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Loading & Error States */}
      {isLoading && !overview && (
        <div className="py-16 text-center text-xs text-atlas-text-muted">
          <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-atlas-accent" />
          Loading institutional supply chain intelligence...
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-md text-xs text-red-400 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>Error loading supply chain data: {error}</span>
        </div>
      )}

      {/* Subtab Content */}
      {!isLoading && (
        <div>
          {/* 1. Overview */}
          {activeSubTab === "overview" && (
            <div className="space-y-4">
              <SupplyChainOverviewCards
                overview={overview}
                onSelectTab={(tab) => setActiveSubTab(tab as SupplyChainSubTab)}
              />

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Direct Suppliers Summary */}
                <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md p-3">
                  <div className="flex items-center justify-between pb-2 border-b border-atlas-border-subtle mb-3">
                    <span className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5">
                      <Cpu className="w-3.5 h-3.5 text-blue-400" />
                      Key Direct Upstream Partners
                    </span>
                    <button
                      onClick={() => setActiveSubTab("suppliers")}
                      className="text-[11px] text-blue-400 hover:text-blue-300 font-medium"
                    >
                      View All ({suppliers.length}) →
                    </button>
                  </div>
                  <div className="space-y-2">
                    {suppliers.slice(0, 4).map((s) => (
                      <div
                        key={s.relationship_id}
                        className="p-2 bg-atlas-surface-subtle/50 rounded border border-atlas-border-subtle/50 text-xs flex items-center justify-between cursor-pointer hover:border-atlas-accent/40"
                        onClick={() => inspectRelationship(s.relationship_id)}
                      >
                        <div>
                          <div className="font-semibold text-atlas-text-primary">{s.supplier_name}</div>
                          <div className="text-[10px] text-atlas-text-muted font-mono">{s.supplied_item_type}</div>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded">
                            Tier {s.tier_level}
                          </span>
                          <div className="text-[10px] text-atlas-text-muted mt-0.5 font-mono">
                            {s.verification_status}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Direct Customers Summary */}
                <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md p-3">
                  <div className="flex items-center justify-between pb-2 border-b border-atlas-border-subtle mb-3">
                    <span className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5">
                      <Truck className="w-3.5 h-3.5 text-emerald-400" />
                      Key Downstream Commercial Channels
                    </span>
                    <button
                      onClick={() => setActiveSubTab("customers")}
                      className="text-[11px] text-emerald-400 hover:text-emerald-300 font-medium"
                    >
                      View All ({customers.length}) →
                    </button>
                  </div>
                  <div className="space-y-2">
                    {customers.slice(0, 4).map((c) => (
                      <div
                        key={c.relationship_id}
                        className="p-2 bg-atlas-surface-subtle/50 rounded border border-atlas-border-subtle/50 text-xs flex items-center justify-between cursor-pointer hover:border-atlas-accent/40"
                        onClick={() => inspectRelationship(c.relationship_id)}
                      >
                        <div>
                          <div className="font-semibold text-atlas-text-primary">{c.customer_name}</div>
                          <div className="text-[10px] text-atlas-text-muted font-mono">{c.supplied_item_type}</div>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                            Channel
                          </span>
                          <div className="text-[10px] text-atlas-text-muted mt-0.5 font-mono">
                            {c.reported_revenue_percentage
                              ? `${c.reported_revenue_percentage}% Rev`
                              : "Commercial Partner"}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Quick Network Preview Button */}
              <div className="p-3 bg-atlas-surface-subtle border border-atlas-border-subtle rounded-md flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Network className="w-4 h-4 text-purple-400" />
                  <span className="text-atlas-text-secondary">
                    Explore multi-tier directed material flows and precursor dependencies in the interactive graph.
                  </span>
                </div>
                <button
                  onClick={() => setActiveSubTab("network")}
                  className="px-3 py-1 bg-atlas-accent text-white rounded font-medium hover:bg-atlas-accent/90 transition-colors"
                >
                  Open Network Explorer →
                </button>
              </div>
            </div>
          )}

          {/* 2. Suppliers Table */}
          {activeSubTab === "suppliers" && (
            <SuppliersTable
              suppliers={suppliers}
              onInspect={inspectRelationship}
              selectedRelationshipId={selectedRelationship?.relationship_id}
            />
          )}

          {/* 3. Customers Table */}
          {activeSubTab === "customers" && (
            <CustomersTable
              customers={customers}
              onInspect={inspectRelationship}
              selectedRelationshipId={selectedRelationship?.relationship_id}
            />
          )}

          {/* 4. Network Explorer */}
          {activeSubTab === "network" && (
            <SupplyChainNetworkGraph
              network={network}
              onInspectEdge={inspectRelationship}
              depth={networkDepth}
              setDepth={setNetworkDepth}
              direction={networkDirection}
              setDirection={setNetworkDirection}
            />
          )}

          {/* 5. Concentration & Dependency Analysis */}
          {activeSubTab === "concentration" && (
            <CustomerConcentrationPanel concentration={concentration} />
          )}

          {/* 6. Historical Changes Timeline */}
          {activeSubTab === "history" && (
            <RelationshipTimeline history={history} />
          )}

          {/* 7. Evidence & Coverage */}
          {activeSubTab === "coverage" && (
            <SupplyChainCoveragePanel coverage={coverage} />
          )}
        </div>
      )}

      {/* Edge & Evidence Inspector Modal */}
      {selectedRelationship && (
        <SupplyChainEdgeInspector
          relationship={selectedRelationship}
          evidenceList={selectedEvidence}
          isLoading={isEvidenceLoading}
          onClose={closeInspector}
        />
      )}
    </div>
  );
}
