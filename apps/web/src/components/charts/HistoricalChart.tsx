"use client";

/**
 * Institutional Financial Chart Canvas Component for ATLAS Charts V1 (Stage 66).
 *
 * Implements:
 * - HTML5 Canvas rendering via TradingView Lightweight Charts (v5.2.1).
 * - Real candlestick rendering with true High/Low wicks and Open/Close bodies.
 * - Basic historical Close Line rendering mode.
 * - Volume histogram overlay when volume data is present.
 * - Mouse and touch pan & zoom.
 * - Interactive crosshair with exact OHLC hover emission.
 * - Bounded older-history backfill on scrolling left.
 * - Full theme awareness (dark/light mode).
 * - Strict resource cleanup and memory leak prevention.
 */

import React, { useEffect, useRef } from "react";
import {
  AreaData,
  AreaSeries,
  BarData,
  BarSeries,
  CandlestickData,
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  HistogramData,
  HistogramSeries,
  IChartApi,
  IPriceLine,
  ISeriesApi,
  LineData,
  LineSeries,
  LineStyle,
  Time,
  createChart,
} from "lightweight-charts";
import {
  ChartBarDTO,
  ChartInstrumentMetadata,
  ChartRenderMode,
  HoveredBarData,
  LiveQuoteDTO,
} from "@/lib/charts";

export interface HistoricalChartProps {
  bars: ChartBarDTO[];
  renderMode: ChartRenderMode;
  instrument: ChartInstrumentMetadata | null;
  liveQuote?: LiveQuoteDTO | null;
  onHoverBar?: (data: HoveredBarData | null) => void;
  onBackfill?: () => void;
  hasMore?: boolean;
  isBackfilling?: boolean;
  onUserPan?: () => void;
  onAtLatest?: () => void;
  chartActionsRef?: React.MutableRefObject<{ goToLatest: () => void } | null>;
}

export function HistoricalChart({
  bars,
  renderMode,
  instrument,
  liveQuote,
  onHoverBar,
  onBackfill,
  hasMore,
  isBackfilling,
  onUserPan,
  onAtLatest,
  chartActionsRef,
}: HistoricalChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const mainSeriesRef = useRef<
    | ISeriesApi<"Candlestick">
    | ISeriesApi<"Bar">
    | ISeriesApi<"Line">
    | ISeriesApi<"Area">
    | null
  >(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const priceLineRef = useRef<IPriceLine | null>(null);
  const lastBarsLengthRef = useRef<number>(0);
  const isBackfillingRef = useRef<boolean>(false);
  const barsCountRef = useRef<number>(0);

  useEffect(() => {
    isBackfillingRef.current = !!isBackfilling;
  }, [isBackfilling]);

  // Initialize and mount chart
  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const isDark = document.documentElement.classList.contains("dark") || true;

    const chart = createChart(container, {
      width: container.clientWidth || 800,
      height: container.clientHeight || 520,
      layout: {
        background: {
          type: ColorType.Solid,
          color: isDark ? "#09090b" : "#ffffff",
        },
        textColor: isDark ? "#a1a1aa" : "#3f3f46",
        fontSize: 12,
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
          labelBackgroundColor: isDark ? "#27272a" : "#e4e4e7",
        },
        horzLine: {
          color: isDark ? "#71717a" : "#a1a1aa",
          width: 1,
          style: 1,
          labelBackgroundColor: isDark ? "#27272a" : "#e4e4e7",
        },
      },
      timeScale: {
        borderColor: isDark ? "#27272a" : "#e4e4e7",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 5,
        barSpacing: 8,
        minBarSpacing: 3,
      },
      rightPriceScale: {
        borderColor: isDark ? "#27272a" : "#e4e4e7",
        autoScale: true,
        scaleMargins: {
          top: 0.1,
          bottom: 0.2, // Leave room for volume histogram
        },
      },
    });

    chartRef.current = chart;

    // Handle responsive resize with ResizeObserver
    const resizeObserver = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0 || !chartRef.current) return;
      const { width, height } = entries[0].contentRect;
      if (width > 0 && height > 0) {
        chartRef.current.applyOptions({ width, height });
      }
    });
    resizeObserver.observe(container);

    // Crosshair movement subscription
    chart.subscribeCrosshairMove((param) => {
      if (!param || !param.time || !mainSeriesRef.current || !onHoverBar) {
        return;
      }

      const seriesData = param.seriesData.get(mainSeriesRef.current);
      if (!seriesData) return;

      const timeUnix = typeof param.time === "number" ? param.time : 0;
      const isoTime = new Date(timeUnix * 1000).toISOString();

      if ("open" in seriesData && "close" in seriesData) {
        const cData = seriesData as CandlestickData | BarData;
        const openVal = Number(cData.open);
        const closeVal = Number(cData.close);
        const highVal = Number(cData.high);
        const lowVal = Number(cData.low);
        const pct = openVal !== 0 ? ((closeVal - openVal) / openVal) * 100 : 0;

        let volVal: number | null = null;
        if (volumeSeriesRef.current) {
          const volData = param.seriesData.get(volumeSeriesRef.current) as HistogramData | undefined;
          if (volData && typeof volData.value === "number") {
            volVal = volData.value;
          }
        }

        onHoverBar({
          time_unix: timeUnix,
          timestamp: isoTime,
          open: openVal,
          high: highVal,
          low: lowVal,
          close: closeVal,
          volume: volVal,
          changePercent: pct,
        });
      } else if ("value" in seriesData) {
        const lData = seriesData as LineData | AreaData;
        const closeVal = Number(lData.value);
        let volVal: number | null = null;
        if (volumeSeriesRef.current) {
          const volData = param.seriesData.get(volumeSeriesRef.current) as HistogramData | undefined;
          if (volData && typeof volData.value === "number") {
            volVal = volData.value;
          }
        }
        onHoverBar({
          time_unix: timeUnix,
          timestamp: isoTime,
          open: closeVal,
          high: closeVal,
          low: closeVal,
          close: closeVal,
          volume: volVal,
          changePercent: 0,
        });
      }
    });

    // Viewport range subscription to detect scrolling left for backfill and user pan
    chart.timeScale().subscribeVisibleLogicalRangeChange((logicalRange) => {
      if (!logicalRange) return;
      if (logicalRange.from <= 2 && hasMore && onBackfill && !isBackfillingRef.current) {
        onBackfill();
      }
      const totalBars = barsCountRef.current;
      if (totalBars > 0) {
        if (logicalRange.to < totalBars - 3) {
          onUserPan?.();
        } else if (logicalRange.to >= totalBars - 1) {
          onAtLatest?.();
        }
      }
    });

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      mainSeriesRef.current = null;
      volumeSeriesRef.current = null;
      priceLineRef.current = null;
    };
  }, [hasMore, onBackfill, onHoverBar, onUserPan, onAtLatest]);

  // Imperative handle for Go to Latest action
  useEffect(() => {
    if (chartActionsRef) {
      chartActionsRef.current = {
        goToLatest: () => {
          if (chartRef.current) {
            chartRef.current.timeScale().scrollToRealTime();
            onAtLatest?.();
          }
        },
      };
    }
    return () => {
      if (chartActionsRef) {
        chartActionsRef.current = null;
      }
    };
  }, [chartActionsRef, onAtLatest]);

  // Update series and data when bars or renderMode changes
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    // Reset price line reference since series is being recreated
    priceLineRef.current = null;

    // Remove existing main series if render mode changed
    if (mainSeriesRef.current) {
      chart.removeSeries(mainSeriesRef.current);
      mainSeriesRef.current = null;
    }

    // Remove existing volume series if present
    if (volumeSeriesRef.current) {
      chart.removeSeries(volumeSeriesRef.current);
      volumeSeriesRef.current = null;
    }

    barsCountRef.current = bars.length;
    if (bars.length === 0) return;

    // 1. Create main series (Candlestick, Bar, Line, or Area)
    if (renderMode === "candlestick") {
      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor: "#10b981", // Emerald 500
        downColor: "#ef4444", // Red 500
        borderVisible: true,
        borderUpColor: "#10b981",
        borderDownColor: "#ef4444",
        wickVisible: true,
        wickUpColor: "#10b981",
        wickDownColor: "#ef4444",
      });

      const formattedCandles: CandlestickData[] = bars.map((b) => ({
        time: b.time_unix as Time,
        open: typeof b.open === "string" ? parseFloat(b.open) : Number(b.open),
        high: typeof b.high === "string" ? parseFloat(b.high) : Number(b.high),
        low: typeof b.low === "string" ? parseFloat(b.low) : Number(b.low),
        close: typeof b.close === "string" ? parseFloat(b.close) : Number(b.close),
      }));

      candleSeries.setData(formattedCandles);
      mainSeriesRef.current = candleSeries;
    } else if (renderMode === "bar") {
      const barSeries = chart.addSeries(BarSeries, {
        upColor: "#10b981",
        downColor: "#ef4444",
        openVisible: true,
        thinBars: false,
      });

      const formattedBars: BarData[] = bars.map((b) => ({
        time: b.time_unix as Time,
        open: typeof b.open === "string" ? parseFloat(b.open) : Number(b.open),
        high: typeof b.high === "string" ? parseFloat(b.high) : Number(b.high),
        low: typeof b.low === "string" ? parseFloat(b.low) : Number(b.low),
        close: typeof b.close === "string" ? parseFloat(b.close) : Number(b.close),
      }));

      barSeries.setData(formattedBars);
      mainSeriesRef.current = barSeries;
    } else if (renderMode === "line") {
      const lineSeries = chart.addSeries(LineSeries, {
        color: "#38bdf8", // Sky 400
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        crosshairMarkerBorderColor: "#38bdf8",
        crosshairMarkerBackgroundColor: "#09090b",
      });

      const formattedLine: LineData[] = bars.map((b) => ({
        time: b.time_unix as Time,
        value: typeof b.close === "string" ? parseFloat(b.close) : Number(b.close),
      }));

      lineSeries.setData(formattedLine);
      mainSeriesRef.current = lineSeries;
    } else {
      // Area Series
      const areaSeries = chart.addSeries(AreaSeries, {
        topColor: "rgba(56, 189, 248, 0.35)", // Sky 400 translucent gradient
        bottomColor: "rgba(56, 189, 248, 0.0)",
        lineColor: "#38bdf8",
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 4,
        crosshairMarkerBorderColor: "#38bdf8",
        crosshairMarkerBackgroundColor: "#09090b",
      });

      const formattedArea: AreaData[] = bars.map((b) => ({
        time: b.time_unix as Time,
        value: typeof b.close === "string" ? parseFloat(b.close) : Number(b.close),
      }));

      areaSeries.setData(formattedArea);
      mainSeriesRef.current = areaSeries;
    }

    // 2. Add volume histogram if instrument has volume
    const hasAnyVolume = bars.some((b) => b.volume !== null);
    if (hasAnyVolume && instrument?.has_volume !== false) {
      const volSeries = chart.addSeries(HistogramSeries, {
        color: "#27272a",
        priceFormat: { type: "volume" },
        priceScaleId: "volume_overlay",
      });

      volSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.82,
          bottom: 0,
        },
      });

      const formattedVol: HistogramData[] = bars
        .filter((b) => b.volume !== null)
        .map((b) => {
          const openVal = typeof b.open === "string" ? parseFloat(b.open) : Number(b.open);
          const closeVal = typeof b.close === "string" ? parseFloat(b.close) : Number(b.close);
          const volVal = typeof b.volume === "string" ? parseFloat(b.volume) : Number(b.volume);
          const isUp = closeVal >= openVal;

          return {
            time: b.time_unix as Time,
            value: volVal,
            color: isUp ? "rgba(16, 185, 129, 0.35)" : "rgba(239, 68, 68, 0.35)",
          };
        });

      volSeries.setData(formattedVol);
      volumeSeriesRef.current = volSeries;
    }

    // Only fit content on initial load, not during prepend backfill
    if (lastBarsLengthRef.current === 0) {
      chart.timeScale().fitContent();
    }
    lastBarsLengthRef.current = bars.length;
  }, [bars, renderMode, instrument]);

  // Manage Stage 67 Live Last-Price Overlay on chart canvas
  useEffect(() => {
    const series = mainSeriesRef.current;
    if (!series) return;

    if (
      liveQuote &&
      liveQuote.has_genuine_last &&
      liveQuote.last_price !== null &&
      liveQuote.last_price !== undefined
    ) {
      const priceNum =
        typeof liveQuote.last_price === "string"
          ? parseFloat(liveQuote.last_price)
          : Number(liveQuote.last_price);

      if (!isNaN(priceNum)) {
        if (!priceLineRef.current) {
          priceLineRef.current = series.createPriceLine({
            price: priceNum,
            color: "#10b981", // Emerald 500 for active live quote
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: "LAST",
          });
        } else {
          priceLineRef.current.applyOptions({
            price: priceNum,
          });
        }
        return;
      }
    }

    // If no genuine last price (e.g. OTC FX / bonds / feed missing last), remove price line
    if (priceLineRef.current) {
      try {
        series.removePriceLine(priceLineRef.current);
      } catch {
        // ignore
      }
      priceLineRef.current = null;
    }
  }, [liveQuote]);

  return (
    <div className="relative w-full h-full min-h-[460px] flex flex-col bg-zinc-950 rounded border border-zinc-800/80 overflow-hidden">
      {/* Canvas container */}
      <div ref={containerRef} className="w-full flex-1" />

      {/* Backfill progress pill */}
      {isBackfilling && (
        <div className="absolute top-3 right-3 bg-zinc-900/90 border border-zinc-700/60 px-2.5 py-1 rounded text-xs text-zinc-300 flex items-center gap-2 backdrop-blur shadow-md pointer-events-none">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>Loading historical bars...</span>
        </div>
      )}
    </div>
  );
}
