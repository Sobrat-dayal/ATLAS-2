'use client';

import React, { useEffect, useState } from 'react';
import { ReviewItem } from '@/lib/events/types';
import { fetchReviewQueue, resolveReviewQueueItem } from '@/lib/events/api';
import { ShieldAlert, Check, Split, X, RefreshCw } from 'lucide-react';

interface EventReviewQueueModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EventReviewQueueModal: React.FC<EventReviewQueueModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const loadQueue = async () => {
    setIsLoading(true);
    try {
      const data = await fetchReviewQueue();
      setItems(data);
    } catch {
      // fallback
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadQueue();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleResolve = async (
    reviewId: string,
    resolution: 'CONFIRMED_MERGE' | 'CONFIRMED_SEPARATE'
  ) => {
    try {
      await resolveReviewQueueItem(reviewId, resolution);
      setActionMessage(`Resolved item as ${resolution}`);
      setTimeout(() => setActionMessage(null), 3000);
      loadQueue();
    } catch (err: unknown) {
      setActionMessage(err instanceof Error ? err.message : 'Resolution failed');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl shadow-2xl max-w-2xl w-full p-6 text-zinc-100 font-sans space-y-4">
        <div className="flex items-start justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <div>
              <h3 className="text-base font-bold">Ambiguous Candidate Match Review Queue</h3>
              <p className="text-xs text-zinc-400 font-mono">
                Preserves Distinct Entities Against False Collisions (Fixture K & Review Protocol)
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

        {actionMessage && (
          <div className="p-2.5 rounded bg-blue-950/60 border border-blue-800 text-blue-300 text-xs font-mono">
            {actionMessage}
          </div>
        )}

        <div className="space-y-3 max-h-80 overflow-y-auto">
          {items.length === 0 ? (
            <div className="text-center py-8 text-zinc-500 font-mono text-xs">
              Review queue is clear. No ambiguous candidate matches pending resolution.
            </div>
          ) : (
            items.map((item) => (
              <div
                key={item.review_id}
                className="p-3.5 rounded-lg border border-zinc-800 bg-zinc-900/60 space-y-2 font-mono text-xs"
              >
                <div className="flex items-center justify-between text-zinc-400">
                  <span className="text-zinc-200 font-semibold">{item.review_id}</span>
                  <span className="text-[10px] text-amber-400 border border-amber-900/80 px-1.5 py-0.5 rounded">
                    {item.status}
                  </span>
                </div>

                <p className="text-zinc-300 font-sans text-xs leading-relaxed">
                  Reason: {item.reason}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-zinc-800 text-[11px]">
                  <span className="text-zinc-500">
                    A: {item.event_a_id} | B: {item.event_b_id}
                  </span>
                  {item.status === 'PENDING' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleResolve(item.review_id, 'CONFIRMED_SEPARATE')}
                        className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 flex items-center gap-1 border border-zinc-700 transition-colors"
                        title="Confirm events represent distinct real-world events"
                      >
                        <Split className="w-3 h-3 text-cyan-400" />
                        <span>Keep Distinct</span>
                      </button>
                      <button
                        onClick={() => handleResolve(item.review_id, 'CONFIRMED_MERGE')}
                        className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1 transition-colors"
                        title="Merge events into a single canonical event"
                      >
                        <Check className="w-3 h-3" />
                        <span>Merge</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

