"use client";

import React from "react";
import {
  Globe,
  ExternalLink,
  ShieldCheck,
  TrendingUp,
  Percent,
  Users,
  Landmark,
  Clock,
} from "lucide-react";
import { MajorEconomyMacroSummaryDTO } from "@/lib/economics";

interface MajorEconomiesTableProps {
  economies: MajorEconomyMacroSummaryDTO[];
  onSelectSeries?: (seriesId: string) => void;
}

export function MajorEconomiesTable({ economies, onSelectSeries }: MajorEconomiesTableProps) {
  if (!economies || economies.length === 0) {
    return (
      <div className="p-6 bg-atlas-surface border border-atlas-border-subtle rounded text-center text-atlas-text-muted text-sm">
        No major economy data available.
      </div>
    );
  }

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded overflow-hidden mb-6">
      <div className="px-4 py-3 border-b border-atlas-border-subtle flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-atlas-accent" />
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Major Economies Macroeconomic Matrix (G6)
          </h3>
          <span className="text-[11px] font-mono bg-atlas-border-subtle/50 text-atlas-text-muted px-2 py-0.5 rounded">
            Canonical Statistical Releases
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-atlas-text-muted">
          <Clock className="w-3.5 h-3.5 text-atlas-text-muted" />
          <span>Independent Sovereign Reference Periods</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 text-atlas-text-muted font-medium">
              <th className="py-2.5 px-3">Economy / Area</th>
              <th className="py-2.5 px-3">
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-emerald-400" />
                  Real GDP Growth
                </div>
              </th>
              <th className="py-2.5 px-3">
                <div className="flex items-center gap-1">
                  <Percent className="w-3 h-3 text-blue-400" />
                  Inflation (CPI YoY)
                </div>
              </th>
              <th className="py-2.5 px-3">
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3 text-amber-400" />
                  Unemployment Rate
                </div>
              </th>
              <th className="py-2.5 px-3">
                <div className="flex items-center gap-1">
                  <Landmark className="w-3 h-3 text-purple-400" />
                  Policy Interest Rate
                </div>
              </th>
              <th className="py-2.5 px-3">Statistical Authority</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/50">
            {economies.map((item) => {
              const geo = item.geography;
              const gdp = item.gdp_growth_qoq;
              const cpi = item.cpi_inflation_yoy;
              const unemp = item.unemployment_rate;
              const rate = item.policy_rate;

              return (
                <tr
                  key={geo.geography_id}
                  className="hover:bg-atlas-surface-hover transition-colors"
                >
                  {/* Economy Column */}
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold px-1.5 py-0.5 rounded bg-atlas-border-subtle/60 text-atlas-text-primary">
                        {geo.iso_code}
                      </span>
                      <div>
                        <div className="font-medium text-atlas-text-primary flex items-center gap-1.5">
                          {geo.name}
                        </div>
                        <div className="text-[10px] text-atlas-text-muted font-mono">
                          {geo.currency_code} &bull; {geo.central_bank_name}
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Real GDP Growth Column */}
                  <td className="py-3 px-3">
                    {gdp ? (
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`font-mono font-semibold ${
                              gdp.value >= 0 ? "text-emerald-400" : "text-rose-400"
                            }`}
                          >
                            {gdp.value >= 0 ? `+${gdp.value.toFixed(1)}%` : `${gdp.value.toFixed(1)}%`}
                          </span>
                          <span className="text-[10px] font-mono bg-atlas-border-subtle/40 px-1 rounded text-atlas-text-muted">
                            {gdp.reference_period}
                          </span>
                        </div>
                        <div className="text-[10px] text-atlas-text-muted flex items-center gap-1 mt-0.5">
                          <span>{gdp.frequency}</span>
                          {item.gdp_growth_series_id && onSelectSeries && (
                            <button
                              onClick={() => onSelectSeries(item.gdp_growth_series_id!)}
                              className="text-emerald-400 hover:text-emerald-300 font-mono text-[9px] underline ml-1"
                            >
                              chart
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <span className="text-atlas-text-muted font-mono text-[11px]">&mdash;</span>
                    )}
                  </td>

                  {/* CPI Inflation Column */}
                  <td className="py-3 px-3">
                    {cpi ? (
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-semibold text-blue-400">
                            {cpi.value.toFixed(1)}%
                          </span>
                          <span className="text-[10px] font-mono bg-atlas-border-subtle/40 px-1 rounded text-atlas-text-muted">
                            {cpi.reference_period}
                          </span>
                        </div>
                        <div className="text-[10px] text-atlas-text-muted flex items-center gap-1 mt-0.5">
                          <span>YoY Headline</span>
                          {item.cpi_series_id && onSelectSeries && (
                            <button
                              onClick={() => onSelectSeries(item.cpi_series_id!)}
                              className="text-blue-400 hover:text-blue-300 font-mono text-[9px] underline ml-1"
                            >
                              chart
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <span className="text-atlas-text-muted font-mono text-[11px]">&mdash;</span>
                    )}
                  </td>

                  {/* Unemployment Column */}
                  <td className="py-3 px-3">
                    {unemp ? (
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-semibold text-amber-400">
                            {unemp.value.toFixed(1)}%
                          </span>
                          <span className="text-[10px] font-mono bg-atlas-border-subtle/40 px-1 rounded text-atlas-text-muted">
                            {unemp.reference_period}
                          </span>
                        </div>
                        <div className="text-[10px] text-atlas-text-muted flex items-center gap-1 mt-0.5">
                          <span>{unemp.seasonal_adjustment === "SEASONALLY_ADJUSTED" ? "SA" : "NSA"}</span>
                          {item.unemployment_series_id && onSelectSeries && (
                            <button
                              onClick={() => onSelectSeries(item.unemployment_series_id!)}
                              className="text-amber-400 hover:text-amber-300 font-mono text-[9px] underline ml-1"
                            >
                              chart
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <span className="text-atlas-text-muted font-mono text-[11px]">&mdash;</span>
                    )}
                  </td>

                  {/* Policy Interest Rate Column */}
                  <td className="py-3 px-3">
                    {rate ? (
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-semibold text-purple-400">
                            {rate.value.toFixed(2)}%
                          </span>
                          <span className="text-[10px] font-mono bg-atlas-border-subtle/40 px-1 rounded text-atlas-text-muted">
                            {rate.reference_period}
                          </span>
                        </div>
                        <div className="text-[10px] text-atlas-text-muted flex items-center gap-1 mt-0.5">
                          <span>{geo.central_bank_name}</span>
                          {item.policy_rate_series_id && onSelectSeries && (
                            <button
                              onClick={() => onSelectSeries(item.policy_rate_series_id!)}
                              className="text-purple-400 hover:text-purple-300 font-mono text-[9px] underline ml-1"
                            >
                              chart
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <span className="text-atlas-text-muted font-mono text-[11px]">&mdash;</span>
                    )}
                  </td>

                  {/* Statistical Authority Column */}
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-1.5 text-atlas-text-secondary text-[11px]">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{geo.statistical_agency}</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="p-3 bg-atlas-background/40 border-t border-atlas-border-subtle text-[11px] text-atlas-text-muted flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span>
            Critical Qualification: Observations represent official published series per jurisdiction. Independent
            reporting periods prevent false temporal alignment. No synthetic world averages are constructed.
          </span>
        </div>
      </div>
    </div>
  );
}
