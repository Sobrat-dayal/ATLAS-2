"use client";

import React from "react";
import { Users, Vote, AlertCircle, CheckCircle2 } from "lucide-react";
import {
  CommitteeVotingRecordDTO,
  MonetaryPolicyMeetingDTO,
} from "@/lib/economics/central-banks";

interface MeetingsPanelProps {
  meetings: MonetaryPolicyMeetingDTO[];
  selectedMeetingId: string | null;
  onSelectMeeting: (meetingId: string) => void;
  votingRecord: CommitteeVotingRecordDTO | null;
}

export function MeetingsPanel({
  meetings,
  selectedMeetingId,
  onSelectMeeting,
  votingRecord,
}: MeetingsPanelProps) {
  const selectedMeeting = meetings.find((m) => m.meeting_id === selectedMeetingId) || meetings[0];

  return (
    <div className="space-y-5">
      {/* 1. Meetings Master Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Policy Committee Deliberation Meetings
            </h3>
          </div>
          <span className="text-xs font-mono text-atlas-text-muted">
            {meetings.length} Documented Meetings
          </span>
        </div>

        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 font-mono text-[11px] text-atlas-text-muted uppercase">
                <th className="py-2.5 px-3">Meeting Identifier</th>
                <th className="py-2.5 px-3">Date Range</th>
                <th className="py-2.5 px-3">Meeting Kind</th>
                <th className="py-2.5 px-3">Minutes Published</th>
                <th className="py-2.5 px-3">Associated Decision</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle/50 font-mono">
              {meetings.map((meet) => {
                const isSelected = meet.meeting_id === selectedMeeting?.meeting_id;
                return (
                  <tr
                    key={meet.meeting_id}
                    onClick={() => onSelectMeeting(meet.meeting_id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-atlas-accent/10 border-l-2 border-atlas-accent"
                        : "hover:bg-atlas-surface-elevated/40"
                    }`}
                  >
                    <td className="py-3 px-3 font-semibold text-atlas-text-primary">
                      {meet.official_identifier}
                    </td>
                    <td className="py-3 px-3 text-atlas-text-muted">
                      {meet.start_date === meet.end_date
                        ? meet.start_date
                        : `${meet.start_date} to ${meet.end_date}`}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-atlas-background text-atlas-text-primary border border-atlas-border-subtle">
                        {meet.meeting_kind}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-atlas-text-muted text-[11px]">
                      {meet.minutes_published_at
                        ? new Date(meet.minutes_published_at).toLocaleString()
                        : "Same day / Immediate"}
                    </td>
                    <td className="py-3 px-3 text-atlas-accent text-[11px]">
                      {meet.decision_ids.join(", ") || "No rate change"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 2. Committee Voting Record Inspector */}
      {selectedMeeting && (
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <Vote className="w-4 h-4 text-atlas-accent" />
              <h4 className="text-sm font-semibold text-atlas-text-primary">
                Official Committee Voting Record — {selectedMeeting.official_identifier}
              </h4>
            </div>

            {votingRecord && votingRecord.is_publicly_disclosed && (
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-emerald-400">For: {votingRecord.votes_for}</span>
                <span className="text-atlas-text-muted">•</span>
                <span className={votingRecord.votes_against > 0 ? "text-rose-400 font-bold" : "text-atlas-text-muted"}>
                  Against: {votingRecord.votes_against}
                </span>
                <span className="text-atlas-text-muted">•</span>
                <span className="text-atlas-text-muted">Abstain: {votingRecord.votes_abstain}</span>
              </div>
            )}
          </div>

          <div className="mt-4">
            {votingRecord && votingRecord.is_publicly_disclosed ? (
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse font-mono">
                    <thead>
                      <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 text-[10px] uppercase text-atlas-text-muted">
                        <th className="py-2 px-3">Member Name</th>
                        <th className="py-2 px-3">Committee Role</th>
                        <th className="py-2 px-3">Vote</th>
                        <th className="py-2 px-3">Recorded Dissent Rationale</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-atlas-border-subtle/50">
                      {votingRecord.individual_votes.map((v, i) => (
                        <tr key={i} className="hover:bg-atlas-surface-elevated/30">
                          <td className="py-2.5 px-3 font-semibold text-atlas-text-primary font-sans">
                            {v.member_name}
                          </td>
                          <td className="py-2.5 px-3 text-atlas-text-muted text-[11px]">
                            {v.role_title}
                          </td>
                          <td className="py-2.5 px-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                v.vote === "FOR"
                                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                  : v.vote === "AGAINST"
                                  ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                  : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              }`}
                            >
                              {v.vote}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-atlas-text-muted font-sans text-xs">
                            {v.dissent_rationale ? (
                              <span className="text-rose-300 font-medium bg-rose-500/5 px-2 py-1 rounded border border-rose-500/15 block">
                                {v.dissent_rationale}
                              </span>
                            ) : (
                              <span className="text-atlas-text-muted/60">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="text-[11px] text-atlas-text-muted font-mono pt-2 border-t border-atlas-border-subtle flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Source Reference: {votingRecord.source_reference}</span>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-atlas-background rounded border border-atlas-border-subtle flex items-start gap-3">
                <AlertCircle className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div className="text-xs text-atlas-text-muted">
                  <span className="font-semibold text-atlas-text-primary block mb-1">
                    Individual Member Voting Not Published by Statute
                  </span>
                  <p className="leading-relaxed">
                    {votingRecord?.source_reference ||
                      "This central bank operates on a collegial consensus decision-making model and does not disclose individual member voting ballots by institutional convention."}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
