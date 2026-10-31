'use client';

import React, { useState } from 'react';
import { AtlasUniversalEvent } from '@/lib/events/types';
import { fetchAsOfHistoricalEvents } from '@/lib/events/api';
import { formatEventTimestamp } from '@/lib/events/temporal';
import { History, X, Clock, AlertCircle, CheckCircle, Database } from 'lucide-react';

interface EventAsOfModalProps {
  event?: AtlasUniversalEvent | null;
  isOpen: boolean;
  onClose: () => void;
  onSelectEvent?: (event: AtlasUniversalEvent) => void;
}

export const EventAsOfModal: React.FC<EventAsOfModalProps> = ({
  event,
  isOpen,
  onClose,
  onSelectEvent,
}) => {
  const [asOfDate, setAsOfDate] = useState<string>('2026-01-10T12:00');
  const [results, setResults] = useState<AtlasUniversalEvent[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleExecute = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const isoStr = new Date(asOfDate).toISOString();
      const data = await fetchAsOfHistoricalEvents(isoStr, event?.event_id);
      setResults(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query historical as-of state');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl shadow-2xl max-w-2xl w-full p-6 text-zinc-100 font-sans space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-amber-400" />
            <div>
              <h3 className="text-base font-bold">Historical Point-in-Time Knowledge Evaluation</h3>
              <p className="text-xs text-zinc-400 font-mono">
                Strict Zero Look-Ahead Bias Guarantee (Stage 135)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Target Context */}
        {event && (
          <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-mono">
            <span className="text-zinc-500 block mb-0.5">Target Canonical Event:</span>
            <span className="text-zinc-200 font-semibold">{event.title}</span>
            <div className="text-[11px] text-zinc-400 mt-1">
              Current Revision: #{event.current_revision_number} | Key: {event.canonical_event_key}
            </div>
          </div>
        )}

        {/* Input Parameters */}
        <div className="space-y-2">
          <label className="text-xs font-mono text-zinc-300 block">
            Select Knowledge As-Of Timestamp (UTC):
          </label>
          <div className="flex gap-2">
            <input
              type="datetime-local"
              value={asOfDate}
              onChange={(e) => setAsOfDate(e.target.value)}
              className="flex-1 bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-xs text-zinc-100 font-mono focus:outline-none focus:border-amber-500"
            />
            <button
              onClick={handleExecute}
              disabled={isLoading}
              className="px-4 py-1.5 rounded bg-amber-600 hover:bg-amber-500 text-zinc-950 font-semibold text-xs font-mono transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Rewinding...' : 'Evaluate As-Of'}
            </button>
          </div>
          <p className="text-[11px] text-zinc-500">
            Queries the historical system knowledge state. Any revisions, restatements, or retractions recorded after this moment will be strictly excluded.
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 rounded bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Results view */}
        {results !== null && (
          <div className="mt-4 border-t border-zinc-800 pt-3 space-y-2">
            <h4 className="text-xs font-mono text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-blue-400" />
              <span>Historical State ({results.length} record{results.length !== 1 ? 's' : ''})</span>
            </h4>

            {results.length === 0 ? (
              <div className="p-4 rounded bg-zinc-900 text-zinc-400 text-xs text-center font-mono">
                Event was NOT known to the system as of this historical moment (zero look-ahead bias).
              </div>
            ) : (
              <div className="max-h-60 overflow-y-auto space-y-2">
                {results.map((r) => (
                  <div
                    key={r.event_id}
                    onClick={() => onSelectEvent?.(r)}
                    className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800/80 cursor-pointer transition-colors space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="font-bold text-zinc-100">{r.title}</span>
                      <span className="text-cyan-400">Rev #{r.current_revision_number}</span>
                    </div>
                    <pre className="text-[11px] font-mono p-2 rounded bg-zinc-950 border border-zinc-800 text-zinc-300 overflow-x-auto">
                      {JSON.stringify(r.event_payload, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
