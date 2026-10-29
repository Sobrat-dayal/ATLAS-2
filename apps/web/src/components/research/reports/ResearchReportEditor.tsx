"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchReportSection,
  ResearchReportContentBlock,
  ReportBlockType,
} from "@/lib/research/types";

interface ResearchReportEditorProps {
  section: ResearchReportSection | null;
  onUpdateSection: (sectionId: string, title: string, blocks: ResearchReportContentBlock[], expectedRev: number) => Promise<void>;
  isFinalized?: boolean;
}

export function ResearchReportEditor({
  section,
  onUpdateSection,
  isFinalized = false,
}: ResearchReportEditorProps) {
  const [prevSectionId, setPrevSectionId] = useState(section?.section_id);
  const [title, setTitle] = useState(section?.title || "");
  const [blocks, setBlocks] = useState<ResearchReportContentBlock[]>(section?.blocks || []);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (section && section.section_id !== prevSectionId) {
    setPrevSectionId(section.section_id);
    setTitle(section.title);
    setBlocks(section.blocks || []);
    setIsDirty(false);
    setError(null);
  }

  if (!section) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-atlas-text-muted bg-atlas-surface-0 flex-1">
        Select a section from the outline to begin writing.
      </div>
    );
  }

  const handleBlockChange = (blockId: string, updatedFields: Partial<ResearchReportContentBlock>) => {
    setBlocks((prev) =>
      prev.map((b) => (b.block_id === blockId ? { ...b, ...updatedFields } : b))
    );
    setIsDirty(true);
  };

  const handleAddBlock = (blockType: ReportBlockType) => {
    const newBlock: ResearchReportContentBlock = {
      block_id: `blk-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`,
      block_type: blockType,
      text_content:
        blockType === "HEADING_2"
          ? "Subheading Title"
          : blockType === "PARAGRAPH"
          ? "Enter institutional narrative analysis, thesis reasoning, and evidence synthesis..."
          : blockType === "QUOTE"
          ? "Management or expert quote excerpt..."
          : "",
      table_content:
        blockType === "FINANCIAL_TABLE"
          ? {
              columns: ["Metric / Period", "FY2023", "FY2024", "YoY Change"],
              rows: [
                ["Revenue ($M)", "383,285", "391,035", "+2.0%"],
                ["Operating Margin", "29.8%", "31.2%", "+140 bps"],
                ["Free Cash Flow ($M)", "99,584", "108,810", "+9.3%"],
              ],
            }
          : undefined,
      chart_spec:
        blockType === "CHART"
          ? {
              chart_type: "FINANCIAL_TREND",
              series_name: "Operating Margin Trend",
              data_points: [
                { period: "2021", value: 29.8 },
                { period: "2022", value: 30.3 },
                { period: "2023", value: 29.8 },
                { period: "2024", value: 31.2 },
              ],
            }
          : undefined,
      citation_ids: [],
    };
    setBlocks((prev) => [...prev, newBlock]);
    setIsDirty(true);
  };

  const handleDeleteBlock = (blockId: string) => {
    setBlocks((prev) => prev.filter((b) => b.block_id !== blockId));
    setIsDirty(true);
  };

  const handleSave = async () => {
    if (!section) return;
    setIsSaving(true);
    setError(null);
    try {
      await onUpdateSection(section.section_id, title, blocks, section.revision);
      setIsDirty(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save section edits.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0 flex-1">
      {/* Editor Header Bar */}
      <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2.5">
        <div className="flex items-center gap-2 flex-1 mr-4">
          <input
            type="text"
            value={title}
            disabled={isFinalized}
            onChange={(e) => {
              setTitle(e.target.value);
              setIsDirty(true);
            }}
            className="w-full text-sm font-bold text-atlas-text-primary bg-transparent focus:outline-hidden border-b border-transparent focus:border-atlas-accent"
          />
          <Badge variant="outline" className="text-[10px] shrink-0 font-mono">
            {section.section_type}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {isDirty && (
            <span className="text-[11px] font-mono text-atlas-warning">Unsaved Changes</span>
          )}
          {!isFinalized && (
            <Button
              variant="primary"
              size="sm"
              disabled={!isDirty || isSaving}
              onClick={handleSave}
            >
              {isSaving ? "Saving..." : "Save Section"}
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="border-b border-atlas-negative/30 bg-atlas-negative/10 px-4 py-2 text-xs text-atlas-negative">
          {error}
        </div>
      )}

      {/* Editor Workspace */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 max-w-4xl mx-auto w-full">
        {blocks.map((block) => (
          <div
            key={block.block_id}
            className="rounded-xs border border-atlas-border-default bg-atlas-surface-1/40 p-3 relative group transition-colors hover:border-atlas-border-strong"
          >
            {/* Block Action Controls */}
            {!isFinalized && (
              <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity z-10 bg-atlas-surface-1/90 rounded-xs px-1 border border-atlas-border-default">
                <span className="text-[9px] font-mono text-atlas-text-muted mr-1">
                  {block.block_type}
                </span>
                <button
                  onClick={() => handleDeleteBlock(block.block_id)}
                  className="p-1 text-atlas-negative hover:text-atlas-negative/80 text-xs"
                  title="Delete Block"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Render block according to type */}
            {block.block_type === "HEADING_2" ? (
              <input
                type="text"
                disabled={isFinalized}
                value={block.text_content || ""}
                onChange={(e) => handleBlockChange(block.block_id, { text_content: e.target.value })}
                className="w-full text-base font-bold text-atlas-text-primary bg-transparent focus:outline-hidden border-b border-atlas-border-default/50 pb-1"
                placeholder="Section Heading..."
              />
            ) : block.block_type === "HEADING_3" ? (
              <input
                type="text"
                disabled={isFinalized}
                value={block.text_content || ""}
                onChange={(e) => handleBlockChange(block.block_id, { text_content: e.target.value })}
                className="w-full text-sm font-semibold text-atlas-text-secondary bg-transparent focus:outline-hidden border-b border-atlas-border-default/50 pb-1"
                placeholder="Subsection Heading..."
              />
            ) : block.block_type === "PARAGRAPH" ? (
              <div className="space-y-1.5">
                <textarea
                  disabled={isFinalized}
                  value={block.text_content || ""}
                  rows={4}
                  onChange={(e) => handleBlockChange(block.block_id, { text_content: e.target.value })}
                  className="w-full text-xs text-atlas-text-primary leading-relaxed bg-transparent focus:outline-hidden resize-y font-sans"
                  placeholder="Enter institutional narrative, empirical commentary, and synthesis..."
                />
                <div className="flex items-center gap-2 pt-1 border-t border-atlas-border-default/40">
                  <span className="text-[10px] text-atlas-text-muted font-mono">Citations:</span>
                  <input
                    type="text"
                    disabled={isFinalized}
                    placeholder="Comma-separated citation IDs (e.g. cit-10k-q4-2024)"
                    value={(block.citation_ids || []).join(", ")}
                    onChange={(e) =>
                      handleBlockChange(block.block_id, {
                        citation_ids: e.target.value
                          .split(",")
                          .map((s) => s.trim())
                          .filter(Boolean),
                      })
                    }
                    className="flex-1 bg-atlas-surface-0 px-2 py-0.5 text-[10px] text-atlas-text-secondary rounded-xs border border-atlas-border-default focus:border-atlas-accent focus:outline-hidden font-mono"
                  />
                </div>
              </div>
            ) : block.block_type === "FINANCIAL_TABLE" ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
                    Financial Performance Data
                  </span>
                  <Badge variant="outline" className="text-[9px]">
                    Table Block
                  </Badge>
                </div>
                {block.table_content && (
                  <div className="overflow-x-auto border border-atlas-border-default rounded-xs bg-atlas-surface-0">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-atlas-surface-1 border-b border-atlas-border-default font-mono text-[11px] text-atlas-text-secondary">
                        <tr>
                          {block.table_content.columns.map((c, i) => (
                            <th key={i} className="py-1.5 px-3">
                              {c}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-atlas-border-default font-mono text-[11px]">
                        {block.table_content.rows.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-atlas-surface-1/40">
                            {row.map((cell, cIdx) => (
                              <td key={cIdx} className="py-1.5 px-3">
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : block.block_type === "CHART" ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
                    Stage 106 Analysis Chart Embed: {block.chart_spec?.series_name || "Trend Series"}
                  </span>
                  <Badge variant="primary" className="text-[9px]">
                    Reproducible Run Embed
                  </Badge>
                </div>
                <div className="h-36 rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-3 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-[11px] text-atlas-text-muted font-mono">
                    <span>{block.chart_spec?.chart_type || "LINE_CHART"}</span>
                    <span>Verified Point-in-Time Run</span>
                  </div>
                  <div className="flex items-end justify-around h-20 gap-2 px-4">
                    {(block.chart_spec?.data_points || []).map((dp: { period?: string; value?: number }, i: number) => (
                      <div key={i} className="flex flex-col items-center gap-1 flex-1">
                        <div
                          className="w-full bg-atlas-accent/80 rounded-t-xs transition-all"
                          style={{ height: `${Math.min(100, Math.max(15, (dp.value ?? 0) * 2.5))}%` }}
                        />
                        <span className="font-mono text-[9px] text-atlas-text-muted">{dp.period}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : block.block_type === "QUOTE" ? (
              <blockquote className="border-l-2 border-atlas-accent pl-3 py-1 space-y-1">
                <textarea
                  disabled={isFinalized}
                  value={block.text_content || ""}
                  rows={2}
                  onChange={(e) => handleBlockChange(block.block_id, { text_content: e.target.value })}
                  className="w-full text-xs italic text-atlas-text-primary bg-transparent focus:outline-hidden resize-none"
                  placeholder="Direct citation quotation..."
                />
              </blockquote>
            ) : null}
          </div>
        ))}

        {/* Add Block Toolbar */}
        {!isFinalized && (
          <div className="rounded-xs border border-dashed border-atlas-border-default p-3 bg-atlas-surface-1/20 flex flex-wrap items-center justify-center gap-2">
            <span className="text-xs font-medium text-atlas-text-muted mr-2">
              + Append Content Block:
            </span>
            <Button variant="ghost" size="xs" onClick={() => handleAddBlock("PARAGRAPH")}>
              Paragraph
            </Button>
            <Button variant="ghost" size="xs" onClick={() => handleAddBlock("HEADING_2")}>
              Heading
            </Button>
            <Button variant="ghost" size="xs" onClick={() => handleAddBlock("FINANCIAL_TABLE")}>
              Financial Table
            </Button>
            <Button variant="ghost" size="xs" onClick={() => handleAddBlock("CHART")}>
              Chart Embed
            </Button>
            <Button variant="ghost" size="xs" onClick={() => handleAddBlock("QUOTE")}>
              Quote
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
