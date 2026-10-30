"use client";

import { useState } from "react";
import { Bot, Check, Copy, RefreshCw } from "lucide-react";
import { parseMarkdownBlocks } from "@/lib/ai/markdown";
import { AiMessage } from "@/lib/ai/types";
import { AiToolCallCard } from "./tools/AiToolCallCard";

interface AtlasAiAssistantMessageProps {
  message?: AiMessage;
  contentOverride?: string;
  isStreaming?: boolean;
  onRegenerate?: () => void;
}

export function AtlasAiAssistantMessage({
  message,
  contentOverride,
  isStreaming = false,
  onRegenerate,
}: AtlasAiAssistantMessageProps) {
  const [copied, setCopied] = useState(false);
  const [copiedCodeIdx, setCopiedCodeIdx] = useState<number | null>(null);

  const rawText = contentOverride !== undefined ? contentOverride : message?.content || "";
  const blocks = parseMarkdownBlocks(rawText);
  const toolCalls = Array.isArray(message?.metadata?.tool_calls)
    ? (message.metadata.tool_calls as Array<Record<string, any>>)
    : null;

  const handleCopyAll = async () => {
    try {
      await navigator.clipboard.writeText(rawText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Ignore
    }
  };

  const handleCopyCode = async (code: string, idx: number) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCodeIdx(idx);
      setTimeout(() => setCopiedCodeIdx(null), 2000);
    } catch {
      // Ignore
    }
  };

  return (
    <div className="flex gap-2.5 px-3 py-2 group">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-atlas-surface-2 border border-atlas-border-default text-atlas-accent shadow-sm">
        <Bot className="h-4 w-4" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="rounded-lg bg-atlas-surface-1 border border-atlas-border-default px-4 py-3 text-xs text-atlas-text-primary shadow-sm leading-relaxed space-y-2.5 select-text">
          {/* Tool Calls Activity (Stage 126) */}
          {toolCalls && toolCalls.length > 0 && (
            <div className="space-y-1 mb-2">
              {toolCalls.map((tc, i) => (
                <AiToolCallCard
                  key={tc.id || tc.tool_call_id || i}
                  toolId={tc.tool_id || "atlas.tool"}
                  status={tc.status || "COMPLETED"}
                  argumentsPayload={tc.arguments}
                  result={tc.result}
                  error={tc.error_message}
                  executionTimeMs={tc.execution_time_ms}
                  approvalRequestId={tc.approval_request_id}
                />
              ))}
            </div>
          )}

          {blocks.length === 0 && isStreaming && (
            <div className="flex items-center gap-1.5 text-atlas-text-muted italic">
              <span className="inline-block h-2 w-2 animate-ping rounded-full bg-atlas-accent" />
              ATLAS AI is computing response...
            </div>
          )}

          {blocks.map((block, idx) => {
            if (block.type === "heading") {
              const Tag = block.level === 1 ? "h2" : block.level === 2 ? "h3" : "h4";
              return (
                <Tag
                  key={idx}
                  className="font-bold text-atlas-text-primary tracking-wide text-xs pt-1 border-b border-atlas-border-default/40 pb-1"
                >
                  {block.content}
                </Tag>
              );
            }

            if (block.type === "code") {
              return (
                <div
                  key={idx}
                  className="relative my-2 rounded border border-atlas-border-strong bg-black/40 font-mono text-[11px] overflow-hidden"
                >
                  <div className="flex items-center justify-between border-b border-atlas-border-default/40 bg-atlas-surface-2/60 px-3 py-1 text-[10px] text-atlas-text-muted">
                    <span>{block.language || "text"}</span>
                    <button
                      onClick={() => handleCopyCode(block.content || "", idx)}
                      className="flex items-center gap-1 text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
                      title="Copy code snippet"
                    >
                      {copiedCodeIdx === idx ? (
                        <>
                          <Check className="h-3 w-3 text-emerald-400" />
                          <span className="text-[10px]">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" />
                          <span className="text-[10px]">Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="p-3 overflow-x-auto text-atlas-text-primary leading-normal whitespace-pre">
                    <code>{block.content}</code>
                  </pre>
                </div>
              );
            }

            if (block.type === "math") {
              return (
                <div
                  key={idx}
                  className="my-2 rounded bg-atlas-surface-2/50 border border-atlas-accent/20 px-3 py-2 text-center font-mono text-xs text-atlas-accent overflow-x-auto"
                >
                  {block.content}
                </div>
              );
            }

            if (block.type === "table") {
              return (
                <div key={idx} className="my-2 overflow-x-auto rounded border border-atlas-border-default">
                  <table className="w-full text-left border-collapse text-[11px]">
                    {block.headers && (
                      <thead>
                        <tr className="bg-atlas-surface-2 border-b border-atlas-border-default">
                          {block.headers.map((h, hIdx) => (
                            <th key={hIdx} className="px-2.5 py-1.5 font-semibold text-atlas-text-primary">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                    )}
                    <tbody>
                      {block.rows?.map((row, rIdx) => (
                        <tr
                          key={rIdx}
                          className="border-b border-atlas-border-default/40 last:border-0 hover:bg-atlas-surface-hover/50"
                        >
                          {row.map((cell, cIdx) => (
                            <td key={cIdx} className="px-2.5 py-1.5 text-atlas-text-secondary">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            }

            if (block.type === "list") {
              return (
                <ul key={idx} className="list-disc list-inside space-y-1 pl-1 text-atlas-text-secondary">
                  {block.items?.map((item, iIdx) => (
                    <li key={iIdx} className="leading-relaxed">
                      {item}
                    </li>
                  ))}
                </ul>
              );
            }

            // Paragraph
            return (
              <p key={idx} className="text-atlas-text-primary leading-relaxed whitespace-pre-wrap">
                {block.content}
              </p>
            );
          })}

          {isStreaming && (
            <span className="inline-block h-3.5 w-1.5 animate-pulse bg-atlas-accent align-middle ml-1" />
          )}
        </div>

        {/* Message utilities (Copy, Regenerate, Metrics) */}
        {!isStreaming && rawText && (
          <div className="mt-1 flex items-center justify-between text-[10px] text-atlas-text-muted px-1">
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyAll}
                className="flex items-center gap-1 hover:text-atlas-text-primary transition-colors"
                title="Copy entire response"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? "Copied" : "Copy"}</span>
              </button>

              {onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="flex items-center gap-1 hover:text-atlas-text-primary transition-colors ml-2"
                  title="Regenerate this response"
                >
                  <RefreshCw className="h-3 w-3" />
                  <span>Regenerate</span>
                </button>
              )}
            </div>

            {message?.token_count ? (
              <span>{message.token_count} tokens</span>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

