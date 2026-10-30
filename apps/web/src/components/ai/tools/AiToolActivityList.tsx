"use client";

import React from "react";
import { AiToolCall } from "@/lib/ai/tools/types";
import { AiToolCallCard } from "./AiToolCallCard";

interface AiToolActivityListProps {
  calls: AiToolCall[];
  onOpenApproval?: (approvalId: string) => void;
}

export function AiToolActivityList({ calls, onOpenApproval }: AiToolActivityListProps) {
  if (!calls || calls.length === 0) return null;

  return (
    <div className="flex flex-col gap-1 my-2">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 px-1">
        Tool Invocations ({calls.length})
      </div>
      {calls.map((call) => (
        <AiToolCallCard
          key={call.id}
          toolId={call.tool_id}
          status={call.status}
          argumentsPayload={call.arguments}
          result={call.result}
          error={call.error_message}
          executionTimeMs={call.execution_time_ms}
          approvalRequestId={call.approval_request_id}
          onOpenApproval={onOpenApproval}
        />
      ))}
    </div>
  );
}

