'use client';

import React, { useState } from 'react';

interface GraphHistoricalControlsProps {
  asOfTime?: string | null;
  onApplyAsOf: (asOfTime: string | null) => void;
}

export function GraphHistoricalControls({
  asOfTime,
  onApplyAsOf,
}: GraphHistoricalControlsProps) {
  const [selectedDate, setSelectedDate] = useState<string>(
    asOfTime ? asOfTime.slice(0, 16) : ''
  );

  const handleApply = () => {
    if (!selectedDate) {
      onApplyAsOf(null);
      return;
    }
    const iso = new Date(selectedDate).toISOString();
    onApplyAsOf(iso);
  };

  const handleReset = () => {
    setSelectedDate('');
    onApplyAsOf(null);
  };

  return (
    <div className="flex items-center gap-2 text-xs">
      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-900 border border-slate-800 rounded-lg text-slate-300">
        <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
          As-Of Time:
        </span>
        <input
          type="datetime-local"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="bg-transparent text-slate-200 text-xs focus:outline-none"
          aria-label="Historical As-Of Horizon"
        />
      </div>

      <button
        onClick={handleApply}
        className="px-2.5 py-1 bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition font-medium text-xs"
      >
        Travel
      </button>

      {asOfTime && (
        <button
          onClick={handleReset}
          className="px-2 py-1 text-slate-400 hover:text-white border border-slate-800 rounded-lg transition text-xs hover:bg-slate-800"
          title="Return to Live State"
        >
          Reset to Live
        </button>
      )}
    </div>
  );
}

