/**
 * Output security, ANSI sanitization, and XSS protection for the Stage 122 Terminal.
 */

import React from "react";

/**
 * Escapes unsafe characters for HTML rendering.
 */
export function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Strips dangerous OSC escape sequences:
 * - OSC 8: Hyperlinks
 * - OSC 52: Arbitrary clipboard manipulation
 * - OSC 0/2: Window title modification
 * - Device status reports (DSR)
 */
export function stripUnsafeAnsi(text: string): string {
  return text
    // Strip OSC sequences (OSC ... ST / BEL)
    .replace(/\x1b\][^\x07\x1b]*(\x07|\x1b\\)/g, "")
    // Strip DCS (Device Control String)
    .replace(/\x1bP[^\x1b]*\x1b\\/g, "")
    // Strip Cursor Positioning & Device Status
    .replace(/\x1b\[[0-9;]*[HFABCDJKsuhln]/g, "");
}

export interface AnsiSpan {
  text: string;
  className?: string;
  color?: string;
  bold?: boolean;
}

const ANSI_COLOR_MAP: Record<number, string> = {
  30: "text-zinc-500", // Black / Dark gray
  31: "text-rose-400", // Red
  32: "text-emerald-400", // Green
  33: "text-amber-400", // Yellow
  34: "text-sky-400", // Blue
  35: "text-purple-400", // Magenta
  36: "text-cyan-400", // Cyan
  37: "text-zinc-200", // White
  90: "text-zinc-500", // Bright Black
  91: "text-rose-300",
  92: "text-emerald-300",
  93: "text-amber-300",
  94: "text-sky-300",
  95: "text-purple-300",
  96: "text-cyan-300",
  97: "text-white",
};

/**
 * Parses safe SGR (Select Graphic Rendition) color codes and returns structured text spans.
 */
export function parseAnsiToSpans(rawText: string): AnsiSpan[] {
  const sanitized = stripUnsafeAnsi(rawText);
  const parts = sanitized.split(/(\x1b\[[0-9;]*m)/g);

  const spans: AnsiSpan[] = [];
  let currentColorClass: string | undefined = undefined;
  let isBold = false;

  for (const part of parts) {
    if (!part) continue;

    if (part.startsWith("\x1b[")) {
      const codes = part
        .replace("\x1b[", "")
        .replace("m", "")
        .split(";")
        .map(Number);

      for (const code of codes) {
        if (code === 0) {
          currentColorClass = undefined;
          isBold = false;
        } else if (code === 1) {
          isBold = true;
        } else if (ANSI_COLOR_MAP[code]) {
          currentColorClass = ANSI_COLOR_MAP[code];
        }
      }
    } else {
      spans.push({
        text: part,
        className: [currentColorClass, isBold ? "font-bold" : ""].filter(Boolean).join(" "),
        bold: isBold,
      });
    }
  }

  return spans.length > 0 ? spans : [{ text: sanitized }];
}

/**
 * Validates that an untrusted link begins with safe HTTP/HTTPS schemes.
 */
export function isSafeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

