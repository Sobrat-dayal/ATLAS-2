/**
 * Hook for Managing Spatial Analytics State, Queries, and Selections (Stage 131).
 */

import { useCallback, useEffect, useState } from 'react';

import { executeSpatialQuery, fetchAnalyticsMetrics } from '@/lib/maps/analytics/api';
import {
  AtlasH3Aggregate,
  ColorPalette,
  SpatialAggregationMethod,
  SpatialAnalyticsQuery,
  SpatialAnalyticsResult,
  SpatialMetricDefinition,
  SpatialVisualizationType,
  TimeBucketInterval,
} from '@/lib/maps/analytics/types';

export interface UseSpatialAnalyticsOptions {
  initialDatasetId?: string;
  initialMetricId?: string;
  initialVisualization?: SpatialVisualizationType;
  initialResolution?: number;
}

export function useSpatialAnalytics(options: UseSpatialAnalyticsOptions = {}) {
  const [isOpen, setIsOpen] = useState(false);
  const [datasetId, setDatasetId] = useState(options.initialDatasetId || 'financial_centers_global');
  const [metricId, setMetricId] = useState(options.initialMetricId || 'market_capital_intensity');
  const [visualizationType, setVisualizationType] = useState<SpatialVisualizationType>(
    options.initialVisualization || 'h3_hexagon'
  );
  const [aggregation, setAggregation] = useState<SpatialAggregationMethod>('sum');
  const [h3Resolution, setH3Resolution] = useState<number>(options.initialResolution ?? 5);
  const [palette, setPalette] = useState<ColorPalette>('viridis');
  const [isExtruded, setIsExtruded] = useState(false);
  const [opacity, setOpacity] = useState(0.85);

  // Temporal analysis
  const [timeBucket, setTimeBucket] = useState<TimeBucketInterval | undefined>(undefined);
  const [timeRangeStart, setTimeRangeStart] = useState<string | undefined>(undefined);
  const [timeRangeEnd, setTimeRangeEnd] = useState<string | undefined>(undefined);
  const [historicalAsOf, setHistoricalAsOf] = useState<string | undefined>(undefined);

  // Data & execution state
  const [metrics, setMetrics] = useState<SpatialMetricDefinition[]>([]);
  const [result, setResult] = useState<SpatialAnalyticsResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Selected cell for Inspector
  const [selectedCell, setSelectedCell] = useState<AtlasH3Aggregate | null>(null);

  // Region comparison toggle
  const [isComparingRegions, setIsComparingRegions] = useState(false);

  // Load metrics when dataset changes
  useEffect(() => {
    let isCurrent = true;
    fetchAnalyticsMetrics(datasetId)
      .then((data) => {
        if (!isCurrent) return;
        setMetrics(data);
        if (data.length > 0) {
          const match = data.find((m) => m.metric_id === metricId);
          if (!match) {
            setMetricId(data[0].metric_id);
            setAggregation(data[0].default_aggregation);
          }
        }
      })
      .catch((err) => {
        if (isCurrent) console.warn('[useSpatialAnalytics] Metrics load error:', err);
      });

    return () => {
      isCurrent = false;
    };
  }, [datasetId]);

  // Execute query
  const runQuery = useCallback(
    async (bounds?: [number, number, number, number]) => {
      setIsLoading(true);
      setError(null);

      const querySpec: SpatialAnalyticsQuery = {
        dataset_id: datasetId,
        metric_id: metricId,
        aggregation,
        visualization_type: visualizationType,
        h3_resolution: h3Resolution,
        bounds,
        time_range_start: timeRangeStart,
        time_range_end: timeRangeEnd,
        time_bucket: timeBucket,
        historical_as_of: historicalAsOf,
        min_contributors: 1, // Dev / demo default
        result_limit: 5000,
      };

      try {
        const queryRes = await executeSpatialQuery(querySpec);
        setResult(queryRes);
      } catch (err: any) {
        setError(err.message || 'Spatial query failed.');
      } finally {
        setIsLoading(false);
      }
    },
    [datasetId, metricId, aggregation, visualizationType, h3Resolution, timeRangeStart, timeRangeEnd, timeBucket, historicalAsOf]
  );

  // Automatically execute query when parameters change
  useEffect(() => {
    runQuery();
  }, [runQuery]);

  return {
    isOpen,
    setIsOpen,
    datasetId,
    setDatasetId,
    metricId,
    setMetricId,
    visualizationType,
    setVisualizationType,
    aggregation,
    setAggregation,
    h3Resolution,
    setH3Resolution,
    palette,
    setPalette,
    isExtruded,
    setIsExtruded,
    opacity,
    setOpacity,
    timeBucket,
    setTimeBucket,
    timeRangeStart,
    setTimeRangeStart,
    timeRangeEnd,
    setTimeRangeEnd,
    historicalAsOf,
    setHistoricalAsOf,
    metrics,
    result,
    isLoading,
    error,
    selectedCell,
    setSelectedCell,
    isComparingRegions,
    setIsComparingRegions,
    runQuery,
  };
}

