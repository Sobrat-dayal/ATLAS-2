/**
 * Lightweight and safe markdown tokenizer and renderer for financial AI text.
 * Handles headings, bold, italics, code blocks, tables, lists, and LaTeX math formulas.
 */

export interface MarkdownBlock {
  type: "paragraph" | "heading" | "code" | "table" | "list" | "math";
  content?: string;
  level?: number;
  language?: string;
  items?: string[];
  headers?: string[];
  rows?: string[][];
}

export function parseMarkdownBlocks(text: string): MarkdownBlock[] {
  if (!text) return [];

  const lines = text.split("\n");
  const blocks: MarkdownBlock[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced Code Block
    if (line.trim().startsWith("```")) {
      const language = line.trim().slice(3).trim() || "text";
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      blocks.push({
        type: "code",
        language,
        content: codeLines.join("\n"),
      });
      i++;
      continue;
    }

    // Display Math Block $$ ... $$
    if (line.trim().startsWith("$$")) {
      const mathLines: string[] = [];
      const trimmed = line.trim();
      if (trimmed.endsWith("$$") && trimmed.length > 2 && trimmed.indexOf("$$", 2) !== -1) {
        // Single line math block
        const mathContent = trimmed.slice(2, -2).trim();
        blocks.push({ type: "math", content: mathContent });
        i++;
        continue;
      }
      i++;
      while (i < lines.length && !lines[i].trim().endsWith("$$")) {
        mathLines.push(lines[i]);
        i++;
      }
      if (i < lines.length) {
        mathLines.push(lines[i].replace(/\$\$$/, ""));
        i++;
      }
      blocks.push({
        type: "math",
        content: mathLines.join("\n").trim(),
      });
      continue;
    }

    // Headings: #, ##, ###, ####
    if (line.startsWith("#")) {
      const match = line.match(/^(#{1,4})\s+(.+)$/);
      if (match) {
        blocks.push({
          type: "heading",
          level: match[1].length,
          content: match[2].trim(),
        });
        i++;
        continue;
      }
    }

    // Markdown Table (starts with |)
    if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|") && lines[i].trim().endsWith("|")) {
        tableLines.push(lines[i].trim());
        i++;
      }
      if (tableLines.length >= 2) {
        const headerRow = tableLines[0]
          .slice(1, -1)
          .split("|")
          .map((c) => c.trim());
        // line 1 is usually separator |:---|:---|
        const contentRows = tableLines.slice(2).map((row) =>
          row
            .slice(1, -1)
            .split("|")
            .map((c) => c.trim())
        );
        blocks.push({
          type: "table",
          headers: headerRow,
          rows: contentRows,
        });
        continue;
      }
    }

    // Unordered List (- or *)
    if (line.trim().match(/^[-*]\s+/)) {
      const listItems: string[] = [];
      while (i < lines.length && lines[i].trim().match(/^[-*]\s+/)) {
        listItems.push(lines[i].trim().replace(/^[-*]\s+/, ""));
        i++;
      }
      blocks.push({
        type: "list",
        items: listItems,
      });
      continue;
    }

    // Ordered List (1., 2.)
    if (line.trim().match(/^\d+\.\s+/)) {
      const listItems: string[] = [];
      while (i < lines.length && lines[i].trim().match(/^\d+\.\s+/)) {
        listItems.push(lines[i].trim().replace(/^\d+\.\s+/, ""));
        i++;
      }
      blocks.push({
        type: "list",
        items: listItems,
      });
      continue;
    }

    // Empty lines
    if (!line.trim()) {
      i++;
      continue;
    }

    // Regular Paragraph
    const paraLines: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].trim().startsWith("```") &&
      !lines[i].trim().startsWith("$$") &&
      !lines[i].startsWith("#") &&
      !(lines[i].trim().startsWith("|") && lines[i].trim().endsWith("|")) &&
      !lines[i].trim().match(/^[-*]\s+/) &&
      !lines[i].trim().match(/^\d+\.\s+/)
    ) {
      paraLines.push(lines[i]);
      i++;
    }

    if (paraLines.length > 0) {
      blocks.push({
        type: "paragraph",
        content: paraLines.join(" "),
      });
    }
  }

  return blocks;
}

/**
 * Strips basic markdown markers for plain text preview.
 */
export function stripMarkdown(markdown: string): string {
  if (!markdown) return "";
  return markdown
    .replace(/```[\s\S]*?```/g, "[Code]")
    .replace(/\$\$[\s\S]*?\$\$/g, "[Formula]")
    .replace(/\$([^$]+)\$/g, "$1")
    .replace(/#{1,6}\s+/g, "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1")
    .trim();
}

