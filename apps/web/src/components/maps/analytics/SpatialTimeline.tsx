/**
 * Spatial Timeline and Temporal Exploration Scrubber (Stage 131).
 *
 * Provides historical observation time filtering, discrete bucket playback,
 * and reduced-motion accessibility support.
 */

import React, { useEffect, useState } from 'react';
import { Pause, Play, RotateCcw, SkipBack, SkipForward } from 'lucide-react';

import { TimeBucketInterval } from '@/lib/maps/analytics/types';

interface SpatialTimelineProps {
  timeBucket?: TimeBucketInterval;
  onTimeBucketChange: (bucket: TimeBucketInterval | undefined) => void;
  activePeriod?: string;
  onPeriodChange?: (period: string) => void;
  availablePeriods?: string[];
  className?: string;
}

export function SpatialTimeline({
  timeBucket = '1m',
  onTimeBucketChange,
  activePeriod,
  onPeriodChange,
  availablePeriods = ['2025-Q1', '2025-Q2', '2025-Q3', '2025-Q4', '2026-Q1'],
  className = '',
}: SpatialTimelineProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const currentPeriod = activePeriod || availablePeriods[currentIndex] || '';

  // Auto-advance when playing
  useEffect(() => {
    if (!isPlaying) return;

    // Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const intervalMs = prefersReducedMotion ? 3000 : 1500;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => {
        const next = (prev + 1) % availablePeriods.length;
        if (onPeriodChange) onPeriodChange(availablePeriods[next]);
        return next;
      });
    }, intervalMs);

    return () => clearInterval(timer);
  }, [isPlaying, availablePeriods, onPeriodChange]);

  const handleStepPrev = () => {
    const next = currentIndex > 0 ? currentIndex - 1 : availablePeriods.length - 1;
    setCurrentIndex(next);
    if (onPeriodChange) onPeriodChange(availablePeriods[next]);
  };

  const handleStepNext = () => {
    const next = (currentIndex + 1) % availablePeriods.length;
    setCurrentIndex(next);
    if (onPeriodChange) onPeriodChange(availablePeriods[next]);
  };

  return (
    <div
      className={`bg-zinc-950/90 border border-zinc-800 backdrop-blur-md rounded-md px-3 py-2 text-xs text-zinc-300 shadow-xl pointer-events-auto flex items-center gap-3 ${className}`}
      role="region"
      aria-label="Spatial Timeline Controls"
    >
      <div className="flex items-center gap-1">
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-1 text-zinc-300 hover:text-zinc-100 hover:bg-zinc-800 rounded transition-colors"
          title={isPlaying ? 'Pause timeline' : 'Play timeline'}
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
        </button>

        <button
          onClick={handleStepPrev}
          className="p-1 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition-colors"
          title="Previous period"
          aria-label="Previous period"
        >
          <SkipBack className="w-3 h-3" />
        </button>

        <button
          onClick={handleStepNext}
          className="p-1 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition-colors"
          title="Next period"
          aria-label="Next period"
        >
          <SkipForward className="w-3 h-3" />
        </button>
      </div>

      <div className="h-4 w-px bg-zinc-800" />

      <div className="flex items-center gap-2">
        <span className="text-[10px] text-zinc-500 uppercase font-mono">Period:</span>
        <span className="font-mono text-zinc-100 font-semibold text-[11px] min-w-[70px]">
          {currentPeriod}
        </span>
      </div>

      <div className="h-4 w-px bg-zinc-800" />

      <div className="flex items-center gap-1 text-[10px]">
        {(['1m', '1q', '1y'] as TimeBucketInterval[]).map((interval) => (
          <button
            key={interval}
            onClick={() => onTimeBucketChange(interval)}
            className={`px-1.5 py-0.5 rounded uppercase font-mono transition-colors ${
              timeBucket === interval
                ? 'bg-zinc-800 text-zinc-100 font-medium'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            {interval}
          </button>
        ))}
      </div>
    </div>
  );
}

