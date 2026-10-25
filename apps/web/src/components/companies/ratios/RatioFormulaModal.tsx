"use client";

import React from "react";
import {
  RatioDefinitionDTO,
  RatioValueDTO,
  RatioMethodologyResponse,
  RatioLineageResponse,
  RatioInputFactDTO,
} from "@/lib/companies/ratios/types";
import { Badge, Button } from "@/design-system";
import {
  Calculator,
  CheckCircle2,
  FileText,
  Scale,
  ShieldCheck,
  X,
  Clock,
} from "lucide-react";

export interface RatioFormulaModalProps {
  companyId: string;
  ratioDef: RatioDefinitionDTO;
  calculatedValue?: RatioValueDTO | null;
  methodologyData?: RatioMethodologyResponse | null;
  lineageData?: RatioLineageResponse | null;
  isLoading?: boolean;
  onClose: () => void;
}

export function RatioFormulaModal({
  ratioDef,
  calculatedValue,
  methodologyData,
  lineageData,
  isLoading,
  onClose,
}: RatioFormulaModalProps) {
  const inputLineage = calculatedValue?.input_lineage || lineageData?.ratio_value?.input_lineage || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden text-xs">
        {/* Modal Header */}
        <div className="px-5 py-3.5 border-b border-atlas-border-subtle flex items-center justify-between bg-atlas-surface-2 shrink-0">
          <div className="flex items-center gap-2.5">
            <Calculator className="w-4 h-4 text-atlas-accent" />
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-atlas-text-primary tracking-wide">
                  {ratioDef.name}
                </h3>
                <Badge variant="outline" className="text-[10px] uppercase font-mono">
                  {ratioDef.category}
                </Badge>
                <Badge variant="default" className="text-[10px] font-mono">
                  v{ratioDef.methodology_version}
                </Badge>
              </div>
              <div className="text-[11px] text-atlas-text-muted font-mono mt-0.5">
                Canonical ID: {ratioDef.id}
              </div>
            </div>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={onClose}
            className="h-7 w-7 p-0"
            title="Close inspection"
          >
            <X className="w-3.5 h-3.5" />
          </Button>
        </div>

        {/* Modal Body */}
        <div className="p-5 overflow-y-auto space-y-4 flex-1">
          {/* Description */}
          <div className="text-atlas-text-secondary leading-relaxed">
            {ratioDef.description}
          </div>

          {/* Formula Display Box */}
          <div className="bg-atlas-surface-2 border border-atlas-border-default rounded-sm p-3.5 space-y-2">
            <div className="text-[11px] font-bold text-atlas-text-muted uppercase tracking-wider flex items-center gap-1.5">
              <Calculator className="w-3.5 h-3.5 text-atlas-accent" />
              <span>Standard Canonical Formula</span>
            </div>
            <div className="font-mono text-sm font-bold text-atlas-text-primary bg-atlas-bg-0 px-3 py-2 rounded-xs border border-atlas-border-subtle">
              {ratioDef.formula_display}
            </div>
          </div>

          {/* Numerator & Denominator Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="border border-atlas-border-subtle rounded-sm p-3 space-y-1.5 bg-atlas-surface-0">
              <div className="text-[11px] font-bold text-atlas-accent uppercase flex items-center gap-1">
                <span>Numerator Definition</span>
              </div>
              <div className="text-atlas-text-secondary text-[11px] leading-relaxed">
                {ratioDef.numerator_definition || "Standard reporting metric"}
              </div>
            </div>

            <div className="border border-atlas-border-subtle rounded-sm p-3 space-y-1.5 bg-atlas-surface-0">
              <div className="text-[11px] font-bold text-atlas-accent uppercase flex items-center gap-1">
                <span>Denominator Definition</span>
              </div>
              <div className="text-atlas-text-secondary text-[11px] leading-relaxed">
                {ratioDef.denominator_definition || "Standard reporting metric"}
              </div>
            </div>
          </div>

          {/* Institutional Policies */}
          <div className="border border-atlas-border-subtle rounded-sm p-3.5 space-y-2.5 bg-atlas-surface-0">
            <div className="text-[11px] font-bold text-atlas-text-muted uppercase tracking-wider flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-atlas-text-muted" />
              <span>Institutional Calculation Policies</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-[11px] font-mono">
              <div>
                <span className="text-atlas-text-muted block text-[10px]">Zero Denominator:</span>
                <span className="text-atlas-text-primary font-medium">
                  {ratioDef.denominator_policy}
                </span>
              </div>
              <div>
                <span className="text-atlas-text-muted block text-[10px]">Negative Denominator:</span>
                <span className="text-atlas-text-primary font-medium">
                  {ratioDef.negative_policy}
                </span>
              </div>
              <div>
                <span className="text-atlas-text-muted block text-[10px]">Output Unit Kind:</span>
                <span className="text-atlas-text-primary font-medium">
                  {ratioDef.unit_kind}
                </span>
              </div>
              <div>
                <span className="text-atlas-text-muted block text-[10px]">Supported Periods:</span>
                <span className="text-atlas-text-primary font-medium">
                  {ratioDef.supported_periods.join(", ")}
                </span>
              </div>
              <div>
                <span className="text-atlas-text-muted block text-[10px]">Industry Scope:</span>
                <span className="text-atlas-text-primary font-medium">
                  {ratioDef.supported_industries.join(", ")}
                </span>
              </div>
              <div>
                <span className="text-atlas-text-muted block text-[10px]">Requires Market Data:</span>
                <span className="text-atlas-text-primary font-medium">
                  {ratioDef.requires_market_data ? "Yes (Stage 33)" : "No"}
                </span>
              </div>
            </div>
          </div>

          {/* Methodology Notes if available */}
          {methodologyData && methodologyData.calculation_notes && (
            <div className="border border-atlas-border-subtle rounded-sm p-3.5 space-y-1.5 bg-atlas-surface-0">
              <div className="text-[11px] font-bold text-atlas-text-muted uppercase tracking-wider">
                Methodology Notes
              </div>
              <div className="text-atlas-text-secondary text-[11px] leading-relaxed">
                {methodologyData.calculation_notes}
              </div>
            </div>
          )}

          {/* Current Observation Lineage Facts (if available) */}
          {calculatedValue && (
            <div className="border border-atlas-border-subtle rounded-sm p-3.5 space-y-2.5 bg-atlas-surface-0">
              <div className="text-[11px] font-bold text-atlas-text-muted uppercase tracking-wider flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-atlas-text-muted" />
                  <span>Observation Input Lineage ({calculatedValue.period_id})</span>
                </span>
                <Badge
                  variant={calculatedValue.status === "AVAILABLE" ? "positive" : "default"}
                  className="font-mono text-[9px]"
                >
                  {calculatedValue.status}
                </Badge>
              </div>

              {isLoading ? (
                <div className="text-atlas-text-muted font-mono text-[11px] py-2">
                  Resolving canonical source fact lineage...
                </div>
              ) : inputLineage.length > 0 ? (
                <div className="space-y-1.5">
                  <div className="text-[10px] text-atlas-text-muted font-mono">
                    Underlying Financial Statement Facts (Stage 82 / Stage 34):
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-[11px]">
                      <thead>
                        <tr className="text-atlas-text-muted border-b border-atlas-border-subtle">
                          <th className="py-1 font-semibold">Concept</th>
                          <th className="py-1 font-semibold">Statement</th>
                          <th className="py-1 font-semibold text-right">Fact Amount</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-atlas-border-subtle">
                        {inputLineage.map((inp: RatioInputFactDTO, idx: number) => (
                          <tr key={idx} className="text-atlas-text-secondary">
                            <td className="py-1 text-atlas-text-primary font-medium">
                              {inp.concept_name}
                              {inp.is_average && (
                                <span className="ml-1 text-[9px] text-atlas-text-muted italic">
                                  (avg)
                                </span>
                              )}
                            </td>
                            <td className="py-1 text-atlas-text-muted">
                              {inp.statement_type || "statement"}
                            </td>
                            <td className="py-1 text-right font-bold text-atlas-text-primary">
                              {inp.formatted_value || String(inp.value || "—")}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="text-[11px] font-mono text-atlas-text-muted">
                  Required Inputs: {ratioDef.required_inputs.join(", ")}
                </div>
              )}

              {/* Provenance Footer */}
              <div className="pt-2 border-t border-atlas-border-subtle flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-atlas-text-muted">
                <span className="flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-atlas-positive" />
                  Canonical Provenance Verified (Stage 24)
                </span>
                {calculatedValue.calculated_at && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Calculated: {calculatedValue.calculated_at}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-5 py-3 border-t border-atlas-border-subtle flex items-center justify-between bg-atlas-surface-2 shrink-0">
          <div className="text-[11px] text-atlas-text-muted font-mono flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-atlas-positive" />
            <span>Lossless Decimal Calculation • Zero Nan/Infinity Guarantee</span>
          </div>

          <Button variant="secondary" size="sm" onClick={onClose} className="text-xs">
            Done
          </Button>
        </div>
      </div>
    </div>
  );
}
