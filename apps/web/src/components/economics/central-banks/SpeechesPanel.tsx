"use client";

import React from "react";
import { Mic, ExternalLink, MapPin, Calendar, Quote } from "lucide-react";
import { OfficialSpeechDTO } from "@/lib/economics/central-banks";

interface SpeechesPanelProps {
  speeches: OfficialSpeechDTO[];
}

export function SpeechesPanel({ speeches }: SpeechesPanelProps) {
  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
        <div className="flex items-center gap-2">
          <Mic className="w-4 h-4 text-atlas-accent" />
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Official Policymaker Speeches & Transcripts
          </h3>
        </div>
        <span className="text-xs font-mono text-atlas-text-muted">
          {speeches.length} Recorded Transcripts
        </span>
      </div>

      <div className="space-y-4">
        {speeches.map((sp) => (
          <div
            key={sp.speech_id}
            className="p-4 rounded-lg bg-atlas-background border border-atlas-border-subtle space-y-3"
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
              <div>
                <h4 className="text-sm font-bold text-atlas-text-primary">
                  {sp.title}
                </h4>
                <div className="flex items-center gap-2 mt-1 text-xs">
                  <span className="font-semibold text-atlas-accent">
                    {sp.speaker_name}
                  </span>
                  <span className="text-atlas-text-muted">•</span>
                  <span className="text-atlas-text-muted">{sp.speaker_role}</span>
                </div>
              </div>

              <a
                href={sp.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-atlas-accent hover:underline flex items-center gap-1 font-mono text-xs shrink-0 self-start sm:self-auto"
              >
                Official Transcript <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            {/* Key Takeaway Callout */}
            <div className="flex items-start gap-2 bg-atlas-surface/60 p-3 rounded border border-atlas-border-subtle/60 text-xs italic text-atlas-text-primary leading-relaxed font-serif">
              <Quote className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <span>{sp.key_takeaway}</span>
            </div>

            <div className="flex items-center gap-4 text-[10px] text-atlas-text-muted font-mono pt-1">
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3 text-atlas-text-muted" />
                {sp.location}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3 text-atlas-text-muted" />
                Delivered: {new Date(sp.delivered_at).toLocaleString()}
              </span>
              <span>•</span>
              <span>Published: {new Date(sp.published_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
