"use client";

import React, { useState, useEffect } from "react";
import {
  AtlasExposureResult,
  ExposureAnalysisRun,
  ExposureCoverageSummary,
  ExposureDomain
} from "@/lib/intelligence/exposure/types";
import { ExposureSummary } from "./ExposureSummary";
import { ExposureTable } from "./ExposureTable";
import { ExposureInspector } from "./ExposureInspector";
import { ExposureScenarioWorkbench } from "./ExposureScenarioWorkbench";
import { ExposureCoverageView } from "./ExposureCoverageView";
import {
  Layers,
  PieChart,
  Sliders,
  ShieldCheck,
  RefreshCw,
  Search,
  Filter,
  Building2,
  Briefcase,
  AlertOctagon,
  ChevronRight
} from "lucide-react";

// Canonical Seed Datasets for Instant Interactive Inspection
const PRESET_RUNS: Record<string, { label: string; type: string; run: ExposureAnalysisRun }> = {
  acme_corp: {
    label: "Acme Global Corp (Geographic Revenue & Facility Presence)",
    type: "COMPANY",
    run: {
      run_id: "run_preset_acme",
      subject_ref: { node_type: "COMPANY", entity_id: "COMP_ACME", canonical_name: "Acme Global Corporation", country_code: "US" },
      exposure_domains: ["COMPANY", "GEOGRAPHIC", "INFRASTRUCTURE"],
      status: "COMPLETED",
      valid_at: "2024-12-31T00:00:00Z",
      known_as_of: new Date().toISOString(),
      calculation_versions: { v1: "1.0.0" },
      warnings: [],
      started_at: new Date().toISOString(),
      coverage_summary: {
        total_relevant_denominator: 10000000.0,
        eligible_covered_denominator: 8500000.0,
        coverage_ratio: 0.85,
        covered_dimensions: ["North America", "Europe"],
        uncovered_dimensions: ["Rest of World / Unallocated Residual"],
        unallocated_residual_amount: 1500000.0,
        unallocated_residual_percentage: 15.0,
        coverage_status: "PARTIAL",
        notes: [
          "Reported geographic segments account for 85.0% of total consolidated revenue.",
          "An unallocated residual of $1,500,000.00 (15.00%) remains unassigned."
        ]
      },
      results: [
        {
          exposure_id: "exp_acme_na",
          analysis_run_id: "run_preset_acme",
          subject_entity_ref: { node_type: "COMPANY", entity_id: "COMP_ACME", canonical_name: "Acme Global Corporation" },
          target_entity_ref: { node_type: "ADMINISTRATIVE_REGION", entity_id: "REG_NA", canonical_name: "North America" },
          exposure_domain: "GEOGRAPHIC",
          exposure_type: "REVENUE_GEOGRAPHIC_EXPOSURE",
          exposure_measure_id: "REV_GEO_SHARE_V1",
          evidence_class: "DETERMINISTICALLY_CALCULATED",
          relationship_strength: "DIRECT_REPORTED",
          amount: 5000000.0,
          currency: "USD",
          unit: "PERCENT",
          percentage: 50.0,
          numerator_value: 5000000.0,
          denominator_value: 10000000.0,
          denominator_reference: "Total Reported Consolidated Revenue (FY2024)",
          reporting_period: "FY2024",
          calculation_method_id: "RATIO_CALCULATION",
          calculation_version: "v1.0",
          input_lineage_ids: ["lin_acme_1"],
          graph_path_ids: [],
          coverage_status: "PARTIAL",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Acme Global Corporation reported $5,000,000.00 (50.00%) revenue from North America in FY2024.",
          limitations_disclaimer: "Calculated exposure represents verified financial relationship topology. It does not constitute a prediction of future market outcomes.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        },
        {
          exposure_id: "exp_acme_eu",
          analysis_run_id: "run_preset_acme",
          subject_entity_ref: { node_type: "COMPANY", entity_id: "COMP_ACME", canonical_name: "Acme Global Corporation" },
          target_entity_ref: { node_type: "ADMINISTRATIVE_REGION", entity_id: "REG_EU", canonical_name: "Europe" },
          exposure_domain: "GEOGRAPHIC",
          exposure_type: "REVENUE_GEOGRAPHIC_EXPOSURE",
          exposure_measure_id: "REV_GEO_SHARE_V1",
          evidence_class: "DETERMINISTICALLY_CALCULATED",
          relationship_strength: "DIRECT_REPORTED",
          amount: 3500000.0,
          currency: "USD",
          unit: "PERCENT",
          percentage: 35.0,
          numerator_value: 3500000.0,
          denominator_value: 10000000.0,
          denominator_reference: "Total Reported Consolidated Revenue (FY2024)",
          reporting_period: "FY2024",
          calculation_method_id: "RATIO_CALCULATION",
          calculation_version: "v1.0",
          input_lineage_ids: ["lin_acme_2"],
          graph_path_ids: [],
          coverage_status: "PARTIAL",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Acme Global Corporation reported $3,500,000.00 (35.00%) revenue from Europe in FY2024.",
          limitations_disclaimer: "Calculated exposure represents verified financial relationship topology. It does not constitute a prediction of future market outcomes.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        },
        {
          exposure_id: "exp_acme_fac",
          analysis_run_id: "run_preset_acme",
          subject_entity_ref: { node_type: "COMPANY", entity_id: "COMP_ACME", canonical_name: "Acme Global Corporation" },
          target_entity_ref: { node_type: "ADMINISTRATIVE_REGION", entity_id: "REG_EU", canonical_name: "Europe" },
          exposure_domain: "INFRASTRUCTURE",
          exposure_type: "FACILITY_GEOGRAPHIC_PRESENCE",
          exposure_measure_id: "FACILITY_COUNT_V1",
          evidence_class: "REPORTED",
          relationship_strength: "DIRECT_MEASURED",
          amount: 10,
          unit: "COUNT",
          percentage: 20.0,
          numerator_value: 10,
          denominator_value: 50,
          denominator_reference: "Total Facilities Globally (50)",
          calculation_method_id: "SPATIAL_COUNT",
          calculation_version: "v1.0",
          input_lineage_ids: ["lin_acme_fac"],
          graph_path_ids: [],
          coverage_status: "COMPLETE",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Acme Global operates 10 physical facilities in Europe (20.00% of global network). Prohibited from being used as a revenue proxy.",
          limitations_disclaimer: "Facility counts indicate operational presence only, never revenue or financial loss.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        }
      ]
    }
  },
  flagship_portfolio: {
    label: "Alpha Flagship Fund (Long/Short, Net vs Gross, Look-Through)",
    type: "PORTFOLIO",
    run: {
      run_id: "run_preset_port",
      subject_ref: { node_type: "OTHER_SUPPORTED_CANONICAL_ENTITY", entity_id: "PORT_ALPHA", canonical_name: "Alpha Flagship Fund", tenant_id: "TENANT_1" },
      exposure_domains: ["PORTFOLIO", "SECTOR", "DERIVATIVES"],
      status: "COMPLETED",
      known_as_of: new Date().toISOString(),
      calculation_versions: { v1: "1.0.0" },
      warnings: [],
      started_at: new Date().toISOString(),
      coverage_summary: {
        total_relevant_denominator: 1000000.0,
        eligible_covered_denominator: 900000.0,
        coverage_ratio: 0.90,
        covered_dimensions: ["Information Technology", "Financials"],
        uncovered_dimensions: ["UNCLASSIFIED_HOLDINGS"],
        unallocated_residual_amount: 100000.0,
        unallocated_residual_percentage: 10.0,
        coverage_status: "PARTIAL",
        notes: ["Unclassified holdings retained as uncovered; no guessed sector labels."]
      },
      results: [
        {
          exposure_id: "exp_port_spy",
          analysis_run_id: "run_preset_port",
          subject_entity_ref: { node_type: "OTHER_SUPPORTED_CANONICAL_ENTITY", entity_id: "PORT_ALPHA", canonical_name: "Alpha Flagship Fund" },
          target_entity_ref: { node_type: "FINANCIAL_INSTRUMENT", entity_id: "INSTR_SPY", canonical_name: "SPDR S&P 500 ETF Trust" },
          exposure_domain: "PORTFOLIO",
          exposure_type: "PORTFOLIO_WEIGHT_EXPOSURE",
          exposure_measure_id: "PORTFOLIO_NAV_WEIGHT_V1",
          evidence_class: "DETERMINISTICALLY_CALCULATED",
          relationship_strength: "DIRECT_MEASURED",
          amount: 500000.0,
          currency: "USD",
          unit: "PERCENT",
          percentage: 50.0,
          numerator_value: 500000.0,
          denominator_value: 1000000.0,
          denominator_reference: "Portfolio NAV ($1,000,000.00)",
          calculation_method_id: "DETERMINISTIC_VALUATION_RATIO",
          calculation_version: "v1.0",
          input_lineage_ids: [],
          graph_path_ids: [],
          coverage_status: "COMPLETE",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Long position in SPY valued at $500,000.00 represents 50.00% of portfolio NAV.",
          limitations_disclaimer: "Verified holding valuation as of close.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        },
        {
          exposure_id: "exp_port_short",
          analysis_run_id: "run_preset_port",
          subject_entity_ref: { node_type: "OTHER_SUPPORTED_CANONICAL_ENTITY", entity_id: "PORT_ALPHA", canonical_name: "Alpha Flagship Fund" },
          target_entity_ref: { node_type: "FINANCIAL_INSTRUMENT", entity_id: "INSTR_QQQ", canonical_name: "Invesco QQQ Trust" },
          exposure_domain: "PORTFOLIO",
          exposure_type: "PORTFOLIO_WEIGHT_EXPOSURE",
          exposure_measure_id: "PORTFOLIO_NAV_WEIGHT_V1",
          evidence_class: "DETERMINISTICALLY_CALCULATED",
          relationship_strength: "DIRECT_MEASURED",
          amount: -300000.0,
          currency: "USD",
          unit: "PERCENT",
          percentage: -30.0,
          numerator_value: -300000.0,
          denominator_value: 1000000.0,
          denominator_reference: "Portfolio NAV ($1,000,000.00)",
          calculation_method_id: "DETERMINISTIC_VALUATION_RATIO",
          calculation_version: "v1.0",
          input_lineage_ids: [],
          graph_path_ids: [],
          coverage_status: "COMPLETE",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Short position in QQQ valued at -$300,000.00 represents -30.00% Net / 30.00% Gross.",
          limitations_disclaimer: "Signed directional exposure.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        },
        {
          exposure_id: "exp_port_lookthrough",
          analysis_run_id: "run_preset_port",
          subject_entity_ref: { node_type: "OTHER_SUPPORTED_CANONICAL_ENTITY", entity_id: "PORT_ALPHA", canonical_name: "Alpha Flagship Fund" },
          target_entity_ref: { node_type: "COMPANY", entity_id: "COMP_AAPL", canonical_name: "Apple Inc." },
          exposure_domain: "PORTFOLIO",
          exposure_type: "PORTFOLIO_WEIGHT_EXPOSURE",
          exposure_measure_id: "FUND_LOOKTHROUGH_WEIGHT_V1",
          evidence_class: "DETERMINISTICALLY_CALCULATED",
          relationship_strength: "DERIVED_FROM_VERIFIED_DATA",
          amount: 60000.0,
          currency: "USD",
          unit: "PERCENT",
          percentage: 6.0,
          numerator_value: 60000.0,
          denominator_value: 1000000.0,
          denominator_reference: "Compound Traversal (20% in Fund * 30% holding)",
          calculation_method_id: "BOUNDED_CYCLE_PROTECTED_TRAVERSAL",
          calculation_version: "v1.0",
          input_lineage_ids: [],
          graph_path_ids: ["PORT_ALPHA -> FUND_F -> COMP_AAPL"],
          coverage_status: "COMPLETE",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Indirect look-through holding in Apple Inc. via intermediate fund holdings (6.00% effective weight). Cycle protected.",
          limitations_disclaimer: "Look-through traversal with cycle detection.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        }
      ]
    }
  },
  quake_event: {
    label: "Magnitude 7.1 Offshore Earthquake (Physical Proximity vs Loss)",
    type: "EVENT",
    run: {
      run_id: "run_preset_quake",
      subject_ref: { node_type: "EVENT", entity_id: "EVT_EQ_2025_001", canonical_name: "Magnitude 7.1 Offshore Earthquake" },
      exposure_domains: ["INFRASTRUCTURE", "COMPANY"],
      status: "COMPLETED",
      known_as_of: new Date().toISOString(),
      calculation_versions: { v1: "1.0.0" },
      warnings: [],
      started_at: new Date().toISOString(),
      results: [
        {
          exposure_id: "exp_quake_fac_1",
          analysis_run_id: "run_preset_quake",
          subject_entity_ref: { node_type: "COMPANY", entity_id: "COMP_ACME", canonical_name: "Acme Precision Components" },
          target_entity_ref: { node_type: "CORPORATE_FACILITY", entity_id: "FAC_PLANT_1", canonical_name: "Miyagi Precision Assembly Plant", country_code: "JP" },
          related_event_id: "EVT_EQ_2025_001",
          exposure_domain: "INFRASTRUCTURE",
          exposure_type: "INFRASTRUCTURE_ASSET_ASSOCIATION",
          exposure_measure_id: "EARTHQUAKE_PROXIMITY_PRESENCE_V1",
          evidence_class: "DETERMINISTICALLY_CALCULATED",
          relationship_strength: "DIRECT_MEASURED",
          amount: 25.0,
          unit: "KM",
          percentage: null,
          numerator_value: 25.0,
          denominator_value: 50.0,
          denominator_reference: "Proximity Threshold (50.0 km)",
          calculation_method_id: "HAVERSINE_SPATIAL_DISTANCE",
          calculation_version: "v1.0",
          input_lineage_ids: [],
          graph_path_ids: [],
          coverage_status: "COMPLETE",
          uncertainty_class: "VERIFIED_DETERMINISTIC",
          explanation: "Facility is located 25.0 km from earthquake epicenter (threshold: 50.0 km). Physical proximity confirmed. Damage status and financial loss are UNKNOWN.",
          limitations_disclaimer: "Geographic proximity confirms co-location only. It does not measure or imply asset impairment, disruption, or insurance recovery.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        }
      ]
    }
  }
};

export function ExposureExplorer() {
  const [activePreset, setActivePreset] = useState<string>("acme_corp");
  const [activeTab, setActiveTab] = useState<"table" | "scenarios" | "coverage">("table");
  const [selectedDomain, setSelectedDomain] = useState<string>("ALL");
  const [selectedExposure, setSelectedExposure] = useState<AtlasExposureResult | null>(null);

  const currentRun = PRESET_RUNS[activePreset]?.run;
  const results = currentRun?.results || [];

  // Filter results by domain
  const filteredResults = results.filter((r) => {
    if (selectedDomain === "ALL") return true;
    return r.exposure_domain === selectedDomain;
  });

  return (
    <div className="flex flex-col h-full bg-black text-zinc-100 font-mono text-xs select-none">
      {/* Subject Preset Bar & Mode Selector */}
      <div className="p-3 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3">
        {/* Preset Selector */}
        <div className="flex items-center gap-2">
          <span className="text-zinc-500 uppercase text-[10px] font-semibold tracking-wider">
            ANALYSIS SUBJECT:
          </span>
          <select
            value={activePreset}
            onChange={(e) => {
              setActivePreset(e.target.value);
              setSelectedExposure(null);
            }}
            className="bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-zinc-200 font-medium focus:outline-none focus:border-sky-500"
          >
            {Object.entries(PRESET_RUNS).map(([key, item]) => (
              <option key={key} value={key}>
                {item.label}
              </option>
            ))}
          </select>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 rounded p-0.5 text-xs">
          <button
            onClick={() => setActiveTab("table")}
            className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
              activeTab === "table"
                ? "bg-sky-600 text-white font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Exposure Matrix</span>
          </button>

          <button
            onClick={() => setActiveTab("scenarios")}
            className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
              activeTab === "scenarios"
                ? "bg-sky-600 text-white font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Scenario Workbench</span>
          </button>

          <button
            onClick={() => setActiveTab("coverage")}
            className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
              activeTab === "coverage"
                ? "bg-sky-600 text-white font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Coverage & Residuals</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Banner */}
      <ExposureSummary
        results={filteredResults}
        coverageSummary={currentRun?.coverage_summary}
      />

      {/* Sub-Header & Domain Filter Bar */}
      {activeTab === "table" && (
        <div className="px-3 py-2 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between text-zinc-400 text-[11px]">
          <div className="flex items-center gap-2 overflow-x-auto">
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider">DOMAIN:</span>
            {["ALL", "GEOGRAPHIC", "PORTFOLIO", "INFRASTRUCTURE", "SECTOR", "CORPORATE_GROUP"].map((d) => (
              <button
                key={d}
                onClick={() => setSelectedDomain(d)}
                className={`px-2 py-0.5 rounded transition-colors ${
                  selectedDomain === d
                    ? "bg-zinc-800 text-sky-400 font-bold border border-zinc-700"
                    : "hover:bg-zinc-900 text-zinc-400"
                }`}
              >
                {d}
              </button>
            ))}
          </div>
          <div className="text-zinc-500 text-[10px]">
            Showing {filteredResults.length} of {results.length} relations
          </div>
        </div>
      )}

      {/* Main Workspace Area (Split Pane when Inspector is Open) */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-auto">
          {activeTab === "table" ? (
            <ExposureTable
              results={filteredResults}
              selectedExposureId={selectedExposure?.exposure_id}
              onSelectExposure={(exp) => setSelectedExposure(exp)}
            />
          ) : activeTab === "scenarios" ? (
            <ExposureScenarioWorkbench />
          ) : (
            <ExposureCoverageView coverageSummary={currentRun?.coverage_summary} />
          )}
        </div>

        {/* Deep Inspector Drawer */}
        {selectedExposure && (
          <div className="w-[380px] shrink-0 border-l border-zinc-800">
            <ExposureInspector
              exposure={selectedExposure}
              onClose={() => setSelectedExposure(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
