"use client";

/**
 * Institutional Technical Indicator Subpane & Oscillator Component (Stage 70).
 *
 * Implements independent vertical scale chart panes for momentum oscillators,
 * trend strength indicators, volatility distance metrics, and volume studies:
 * - RSI (0-100 scale, 30/70 reference bands)
 * - MACD (MACD line, Signal line, zero-centered positive/negative histogram)
 * - Stochastic Oscillator (%K and %D lines, 20/80 reference bands)
 * - ATR, ADX, CCI, ROC, MOM, OBV, MFI
 * - HTML5 Canvas rendering via Lightweight Charts with responsive resizing
 * - Synchronized time scale, live legend, crosshair values, and status badges
 */

import React, { useEffect, useRef, useState } from "react";
import {
  ColorType,
  CrosshairMode,
  HistogramData,
  HistogramSeries,
  IChartApi,
  ISeriesApi,
  LineData,
  LineSeries,
  LineStyle,
  Time,
  WhitespaceData,
  createChart,
} from "lightweight-charts";
import { Eye, EyeOff, Settings, X } from "lucide-react";
import {
  HoveredBarData,
  IndicatorCalculationResult,
  IndicatorDefinition,
  IndicatorInstanceConfig,
} from "@/lib/charts";

export interface IndicatorSubpaneProps {
  instance: IndicatorInstanceConfig;
  definition?: IndicatorDefinition | null;
  result?: IndicatorCalculationResult;
  hoveredBar?: HoveredBarData | null;
  height?: number;
  onConfigure?: () => void;
  onRemove?: () => void;
  onToggleVisibility?: () => void;
}

export function IndicatorSubpane({
  instance,
  definition,
  result,
  hoveredBar,
  height = 140,
  onConfigure,
  onRemove,
  onToggleVisibility,
}: IndicatorSubpaneProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesMapRef = useRef<Map<string, ISeriesApi<"Line" | "Histogram">>>(new Map());
  const [hoveredValues, setHoveredValues] = useState<Record<string, number | null>>({});

  const isVisible = instance.visible !== false;

  // Format label from parameters
  const formatLabel = () => {
    const name = definition?.display_name || instance.indicator_id.replace("atlas.", "").toUpperCase();
    const p = instance.parameters;
    if (instance.indicator_id === "atlas.macd") {
      return `${name} (${p["fast_period"] ?? 12}, ${p["slow_period"] ?? 26}, ${p["signal_period"] ?? 9})`;
    }
    if (instance.indicator_id === "atlas.stoch") {
      return `${name} (${p["fastk_period"] ?? 5}, ${p["slowk_period"] ?? 3}, ${p["slowd_period"] ?? 3})`;
    }
    if (instance.indicator_id === "atlas.bbands") {
      return `${name} (${p["period"] ?? 20}, ${p["nbdevup"] ?? 2}, ${p["nbdevdn"] ?? 2})`;
    }
    if (p["period"] != null) {
      return `${name} (${p["period"]})`;
    }
    return name;
  };

  // Initialize and mount Lightweight Charts for the subpane
  useEffect(() => {
    if (!containerRef.current || !isVisible) return;

    const container = containerRef.current;
    const isDark = document.documentElement.classList.contains("dark") || true;

    const chart = createChart(container, {
      width: container.clientWidth || 800,
      height: height - 28, // Leave room for subpane header
      layout: {
        background: {
          type: ColorType.Solid,
          color: isDark ? "#09090b" : "#ffffff",
        },
        textColor: isDark ? "#a1a1aa" : "#3f3f46",
        fontSize: 10,
        fontFamily: "var(--font-geist-mono), monospace",
      },
      grid: {
        vertLines: { color: isDark ? "#18181b" : "#f4f4f5" },
        horzLines: { color: isDark ? "#18181b" : "#f4f4f5" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: isDark ? "#71717a" : "#a1a1aa",
          width: 1,
          style: 1,
        },
        horzLine: {
          color: isDark ? "#71717a" : "#a1a1aa",
          width: 1,
          style: 1,
        },
      },
      timeScale: {
        borderColor: isDark ? "#27272a" : "#e4e4e7",
        visible: false, // Hide secondary time axis to keep chart clean
      },
      rightPriceScale: {
        borderColor: isDark ? "#27272a" : "#e4e4e7",
        autoScale: true,
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
    });

    chartRef.current = chart;

    const resizeObserver = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0 || !chartRef.current) return;
      const { width, height: h } = entries[0].contentRect;
      if (width > 0 && h > 0) {
        chartRef.current.applyOptions({ width, height: h });
      }
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      seriesMapRef.current.forEach((s) => {
        try {
          chart.removeSeries(s);
        } catch {
          // ignore
        }
      });
      seriesMapRef.current.clear();
      chart.remove();
      chartRef.current = null;
    };
  }, [isVisible, height]);

  // Synchronize data series into the subpane chart
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || !result || !result.series || !isVisible) return;

    const currentMap = seriesMapRef.current;
    const activeSeriesIds = new Set<string>();

    for (const s of result.series) {
      if (!s.points || s.points.length === 0) continue;
      activeSeriesIds.add(s.series_id);

      if (s.rendering_type === "HISTOGRAM") {
        let histSeries = currentMap.get(s.series_id) as ISeriesApi<"Histogram"> | undefined;
        if (!histSeries) {
          histSeries = chart.addSeries(HistogramSeries, {
            color: "#10b981",
            priceFormat: { type: "price", precision: 2, minMove: 0.01 },
            priceLineVisible: false,
            lastValueVisible: true,
          });
          currentMap.set(s.series_id, histSeries);

          // Add zero line for zero-centered histograms like MACD
          histSeries.createPriceLine({
            price: 0,
            color: "rgba(255, 255, 255, 0.2)",
            lineWidth: 1,
            lineStyle: LineStyle.Dotted,
            axisLabelVisible: false,
            title: "",
          });
        }

        const histData: HistogramData[] = s.points.map((pt) => {
          const val = pt.value != null ? Number(pt.value) : 0;
          return {
            time: pt.time_unix as Time,
            value: val,
            color: val >= 0 ? "rgba(16, 185, 129, 0.7)" : "rgba(239, 68, 68, 0.7)",
          };
        });

        histSeries.setData(histData);
      } else {
        // Line Series (RSI, MACD line, Signal line, %K, %D, ATR, ADX, etc.)
        let lineSeries = currentMap.get(s.series_id) as ISeriesApi<"Line"> | undefined;

        let lineColor = s.color || instance.color || "#38bdf8";
        if (s.series_id === "signal_line" || s.series_id === "slowd") {
          lineColor = "#f59e0b"; // Amber for signal / %D line
        }

        if (!lineSeries) {
          lineSeries = chart.addSeries(LineSeries, {
            color: lineColor,
            lineWidth: (s.line_width || instance.line_width || 2) as 1 | 2 | 3 | 4,
            priceLineVisible: false,
            lastValueVisible: true,
            crosshairMarkerVisible: true,
            crosshairMarkerRadius: 3,
            crosshairMarkerBorderColor: lineColor,
            crosshairMarkerBackgroundColor: "#09090b",
          });
          currentMap.set(s.series_id, lineSeries);

          // Add conventional reference lines
          if (instance.indicator_id === "atlas.rsi") {
            lineSeries.createPriceLine({
              price: 70,
              color: "rgba(239, 68, 68, 0.4)",
              lineWidth: 1,
              lineStyle: LineStyle.Dashed,
              axisLabelVisible: true,
              title: "70",
            });
            lineSeries.createPriceLine({
              price: 30,
              color: "rgba(16, 185, 129, 0.4)",
              lineWidth: 1,
              lineStyle: LineStyle.Dashed,
              axisLabelVisible: true,
              title: "30",
            });
          } else if (instance.indicator_id === "atlas.stoch" || instance.indicator_id === "atlas.mfi") {
            lineSeries.createPriceLine({
              price: 80,
              color: "rgba(239, 68, 68, 0.4)",
              lineWidth: 1,
              lineStyle: LineStyle.Dashed,
              axisLabelVisible: true,
              title: "80",
            });
            lineSeries.createPriceLine({
              price: 20,
              color: "rgba(16, 185, 129, 0.4)",
              lineWidth: 1,
              lineStyle: LineStyle.Dashed,
              axisLabelVisible: true,
              title: "20",
            });
          } else if (instance.indicator_id === "atlas.adx") {
            lineSeries.createPriceLine({
              price: 25,
              color: "rgba(255, 255, 255, 0.3)",
              lineWidth: 1,
              lineStyle: LineStyle.Dotted,
              axisLabelVisible: true,
              title: "25",
            });
          } else if (instance.indicator_id === "atlas.cci") {
            lineSeries.createPriceLine({
              price: 100,
              color: "rgba(239, 68, 68, 0.4)",
              lineWidth: 1,
              lineStyle: LineStyle.Dashed,
              axisLabelVisible: true,
              title: "+100",
            });
            lineSeries.createPriceLine({
              price: -100,
              color: "rgba(16, 185, 129, 0.4)",
              lineWidth: 1,
              lineStyle: LineStyle.Dashed,
              axisLabelVisible: true,
              title: "-100",
            });
          }
        }

        const lineData: (LineData | WhitespaceData)[] = s.points.map((pt) => {
          if (pt.value !== null && pt.value !== undefined && !isNaN(Number(pt.value))) {
            return {
              time: pt.time_unix as Time,
              value: Number(pt.value),
            };
          }
          return {
            time: pt.time_unix as Time,
          };
        });

        lineSeries.setData(lineData);
      }
    }

    // Clean up removed series
    currentMap.forEach((s, sid) => {
      if (!activeSeriesIds.has(sid)) {
        try {
          chart.removeSeries(s);
        } catch {
          // ignore
        }
        currentMap.delete(sid);
      }
    });

    chart.timeScale().fitContent();
  }, [result, isVisible, instance]);

  // Compute values for header legend based on hover or latest point
  useEffect(() => {
    if (!result || !result.series || result.series.length === 0) return;

    const values: Record<string, number | null> = {};
    for (const s of result.series) {
      if (!s.points || s.points.length === 0) continue;

      let matchedPoint = null;
      if (hoveredBar?.time_unix) {
        matchedPoint = s.points.find((p) => Math.abs(p.time_unix - hoveredBar.time_unix) <= 1);
      }

      if (!matchedPoint) {
        // Fallback to latest valid point
        for (let i = s.points.length - 1; i >= 0; i--) {
          if (s.points[i].value != null) {
            matchedPoint = s.points[i];
            break;
          }
        }
      }

      values[s.series_id] = matchedPoint?.value != null ? Number(matchedPoint.value) : null;
    }

    setHoveredValues(values);
  }, [hoveredBar, result]);

  if (!isVisible) return null;

  return (
    <div
      style={{ height: `${height}px` }}
      className="w-full relative border-t border-zinc-800/80 bg-zinc-950 flex flex-col justify-between overflow-hidden text-xs font-mono select-none"
    >
      {/* Subpane Header Bar */}
      <div className="flex items-center justify-between px-3 py-1 bg-zinc-900/60 border-b border-zinc-800/60 text-[11px]">
        {/* Left: Indicator title and output series values */}
        <div className="flex items-center gap-3 overflow-x-auto">
          <div className="flex items-center gap-1.5 shrink-0">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: instance.color || "#38bdf8" }}
            />
            <span className="font-semibold text-zinc-100">{formatLabel()}</span>
          </div>

          {/* Series Values */}
          <div className="flex items-center gap-2.5 text-[10px]">
            {result?.series?.map((s) => {
              const val = hoveredValues[s.series_id];
              let color = s.color || instance.color || "#38bdf8";
              if (s.series_id === "signal_line" || s.series_id === "slowd") {
                color = "#f59e0b";
              } else if (s.series_id === "histogram") {
                color = val != null && val >= 0 ? "#10b981" : "#ef4444";
              }

              return (
                <div key={s.series_id} className="flex items-center gap-1">
                  <span className="text-zinc-500">{s.name}:</span>
                  <span className="font-semibold font-mono" style={{ color }}>
                    {val != null ? (val >= 0 && s.series_id === "histogram" ? `+${val.toFixed(2)}` : val.toFixed(2)) : "—"}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Status Badges */}
          {result?.status === "WARMUP" && (
            <span className="px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 text-[9px] uppercase">
              Warmup Period
            </span>
          )}
          {result?.status === "MISSING_VOLUME" && (
            <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[9px] uppercase">
              Traded Volume Required
            </span>
          )}
          {result?.status === "INSUFFICIENT_HISTORY" && (
            <span className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[9px] uppercase">
              Insufficient History
            </span>
          )}
        </div>

        {/* Right: Controls (Visibility, Configure, Remove) */}
        <div className="flex items-center gap-1 shrink-0 ml-2">
          {onToggleVisibility && (
            <button
              type="button"
              onClick={onToggleVisibility}
              className="text-zinc-400 hover:text-zinc-100 p-0.5 rounded hover:bg-zinc-800 transition-colors"
              title="Toggle visibility"
              aria-label="Toggle visibility"
            >
              <Eye className="w-3 h-3" />
            </button>
          )}
          {onConfigure && (
            <button
              type="button"
              onClick={onConfigure}
              className="text-zinc-400 hover:text-zinc-100 p-0.5 rounded hover:bg-zinc-800 transition-colors"
              title="Configure parameters"
              aria-label="Configure parameters"
            >
              <Settings className="w-3 h-3" />
            </button>
          )}
          {onRemove && (
            <button
              type="button"
              onClick={onRemove}
              className="text-zinc-400 hover:text-rose-400 p-0.5 rounded hover:bg-zinc-800 transition-colors"
              title="Remove subpane"
              aria-label="Remove subpane"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div ref={containerRef} className="w-full flex-1" />
    </div>
  );
}
