/**
 * Financial Coordinate to Screen Mapping Engine for ATLAS Charts (Stage 71).
 *
 * Implements:
 * - Accurate bidirectional conversion between financial { time, price } and screen { x, y }.
 * - Direct integration with Lightweight Charts ITimeScaleApi and ISeriesApi.
 * - Interpolation fallback for off-bar or right-offset time coordinates.
 * - Non-fatal handling of off-screen or out-of-range coordinates.
 */

import { IChartApi, ISeriesApi, Time } from "lightweight-charts";
import { ChartBarDTO } from "../types";
import { DrawingAnchor, ScreenPoint } from "./types";

export interface CoordinateMapperOptions {
  chart: IChartApi;
  series: ISeriesApi<any>;
  bars?: ChartBarDTO[];
}

export class CoordinateMapper {
  private chart: IChartApi;
  private series: ISeriesApi<any>;
  private bars: ChartBarDTO[];

  constructor(options: CoordinateMapperOptions) {
    this.chart = options.chart;
    this.series = options.series;
    this.bars = options.bars || [];
  }

  public updateBars(bars: ChartBarDTO[]): void {
    this.bars = bars;
  }

  public updateSeries(series: ISeriesApi<any>): void {
    this.series = series;
  }

  /**
   * Converts a financial anchor { time, price } to chart-relative screen coordinates { x, y }.
   * Returns null if either coordinate cannot be mapped.
   */
  public financialToScreen(anchor: DrawingAnchor): ScreenPoint | null {
    if (typeof anchor.time !== "number" || typeof anchor.price !== "number") {
      return null;
    }
    if (isNaN(anchor.time) || isNaN(anchor.price) || !isFinite(anchor.price)) {
      return null;
    }

    const timeScale = this.chart.timeScale();
    let x: number | null = timeScale.timeToCoordinate(anchor.time as unknown as Time) as number | null;

    // Fallback: If timeToCoordinate is null (e.g. between bars or rightward),
    // interpolate or project using nearest loaded bar spacing
    if (x === null && this.bars.length > 0) {
      x = this.interpolateTimeToScreen(anchor.time);
    }

    const y: number | null = this.series.priceToCoordinate(anchor.price) as number | null;

    if (x === null || y === null || isNaN(x) || isNaN(y)) {
      return null;
    }

    return { x: Number(x), y: Number(y) };
  }

  /**
   * Converts chart-relative screen coordinates { x, y } to a financial anchor { time, price }.
   */
  public screenToFinancial(point: ScreenPoint): DrawingAnchor | null {
    if (typeof point.x !== "number" || typeof point.y !== "number") {
      return null;
    }

    const timeScale = this.chart.timeScale();
    let time = timeScale.coordinateToTime(point.x);

    // Fallback for coordinateToTime if pointing in right margin or between bars
    let timeUnix: number | null = null;
    if (time !== null && time !== undefined) {
      if (typeof time === "number") {
        timeUnix = time;
      } else if (typeof time === "object" && "year" in time) {
        // BusinessDay object: convert to unix timestamp
        const bd = time as { year: number; month: number; day: number };
        timeUnix = Math.floor(Date.UTC(bd.year, bd.month - 1, bd.day) / 1000);
      } else {
        timeUnix = Number(time);
      }
    }

    if (timeUnix === null && this.bars.length > 0) {
      timeUnix = this.interpolateScreenToTime(point.x);
    }

    const price = this.series.coordinateToPrice(point.y);

    if (timeUnix === null || price === null || isNaN(timeUnix) || isNaN(price)) {
      return null;
    }

    return {
      time: timeUnix,
      price: Number(price),
    };
  }

  /**
   * Approximate screen X for a timestamp when exact bar is not mapped.
   */
  private interpolateTimeToScreen(targetTime: number): number | null {
    if (!this.bars || this.bars.length === 0) return null;

    const timeScale = this.chart.timeScale();
    const firstBar = this.bars[0];
    const lastBar = this.bars[this.bars.length - 1];

    const firstX = timeScale.timeToCoordinate(firstBar.time_unix as unknown as Time) as number | null;
    const lastX = timeScale.timeToCoordinate(lastBar.time_unix as unknown as Time) as number | null;

    if (firstX === null || lastX === null) return null;

    if (this.bars.length === 1) return firstX;

    // Linear projection across the loaded bar time span
    const timeSpan = lastBar.time_unix - firstBar.time_unix;
    if (timeSpan <= 0) return lastX;

    const xSpan = lastX - firstX;
    const progress = (targetTime - firstBar.time_unix) / timeSpan;

    return firstX + progress * xSpan;
  }

  /**
   * Approximate timestamp for screen X when exact bar is not mapped.
   */
  private interpolateScreenToTime(screenX: number): number | null {
    if (!this.bars || this.bars.length === 0) return null;

    const timeScale = this.chart.timeScale();
    const firstBar = this.bars[0];
    const lastBar = this.bars[this.bars.length - 1];

    const firstX = timeScale.timeToCoordinate(firstBar.time_unix as unknown as Time) as number | null;
    const lastX = timeScale.timeToCoordinate(lastBar.time_unix as unknown as Time) as number | null;

    if (firstX === null || lastX === null) {
      return lastBar.time_unix;
    }

    const xSpan = lastX - firstX;
    if (Math.abs(xSpan) < 1) return lastBar.time_unix;

    const progress = (screenX - firstX) / xSpan;
    const timeSpan = lastBar.time_unix - firstBar.time_unix;

    return Math.floor(firstBar.time_unix + progress * timeSpan);
  }
}
