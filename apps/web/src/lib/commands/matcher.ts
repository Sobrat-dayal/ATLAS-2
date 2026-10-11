import type {
  CommandDefinition,
  CommandContext,
  CommandCategory,
  CommandMatch,
} from "./types";
import { COMMAND_REGISTRY } from "./registry";

const CATEGORY_ORDER: Record<CommandCategory, number> = {
  navigation: 1,
  search: 2,
  selection: 3,
  settings: 4,
  shell: 5,
};

/**
 * Normalizes query string: trims, collapses whitespace, converts to lowercase.
 */
export function normalizeQuery(query: string): string {
  return query.trim().toLowerCase().replace(/\s+/g, " ");
}

function editDistance(a: string, b: string): number {
  if (Math.abs(a.length - b.length) > 2) return 99;
  const d: number[][] = [];
  for (let i = 0; i <= a.length; i++) {
    d[i] = [i];
  }
  for (let j = 0; j <= b.length; j++) {
    d[0][j] = j;
  }
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(
        d[i - 1][j] + 1,
        d[i][j - 1] + 1,
        d[i - 1][j - 1] + cost
      );
    }
  }
  return d[a.length][b.length];
}

/**
 * Checks if a candidate string contains query as a character subsequence (deterministic fuzzy match).
 */
function isSubsequence(query: string, text: string): boolean {
  if (query.length > text.length) return false;
  let qIdx = 0;
  for (let tIdx = 0; tIdx < text.length && qIdx < query.length; tIdx++) {
    if (query[qIdx] === text[tIdx]) {
      qIdx++;
    }
  }
  return qIdx === query.length;
}

/**
 * Evaluates a single command against a normalized query and returns a match if found.
 */
function matchCommand(
  command: CommandDefinition,
  query: string
): CommandMatch | null {
  const normLabel = command.label.toLowerCase();
  const normDesc = (command.description || "").toLowerCase();
  const aliases = (command.aliases || []).map((a) => a.toLowerCase());
  const keywords = (command.keywords || []).map((k) => k.toLowerCase());

  // Tier 1: Exact label match
  if (normLabel === query) {
    return { command, tier: 1, score: 100, matchedField: "label" };
  }

  // Tier 2: Exact alias match
  if (aliases.includes(query)) {
    return { command, tier: 2, score: 95, matchedField: "alias" };
  }

  // Tier 3: Label prefix match (either entire label starts with query, or word starts with query)
  if (normLabel.startsWith(query)) {
    return { command, tier: 3, score: 90, matchedField: "label" };
  }
  const labelWords = normLabel.split(" ");
  if (labelWords.some((word) => word.startsWith(query))) {
    return { command, tier: 3, score: 85, matchedField: "label" };
  }

  // Tier 4: Alias prefix match
  if (aliases.some((alias) => alias.startsWith(query))) {
    return { command, tier: 4, score: 80, matchedField: "alias" };
  }

  // Tier 5: Keyword exact or prefix match
  if (keywords.includes(query)) {
    return { command, tier: 5, score: 75, matchedField: "keyword" };
  }
  if (keywords.some((k) => k.startsWith(query))) {
    return { command, tier: 5, score: 70, matchedField: "keyword" };
  }

  // Tier 6: Label substring match
  if (normLabel.includes(query)) {
    return { command, tier: 6, score: 60, matchedField: "label" };
  }

  // Tier 7: Description substring match
  if (normDesc.includes(query)) {
    return { command, tier: 7, score: 50, matchedField: "description" };
  }

  // Tier 8: Lightweight deterministic fuzzy match (subsequence or bounded edit distance)
  if (query.length >= 2) {
    if (isSubsequence(query, normLabel)) {
      return { command, tier: 8, score: 40, matchedField: "label" };
    }

    const words = [...labelWords, ...aliases];
    const maxEdits = query.length >= 5 ? 2 : 1;
    for (const word of words) {
      if (editDistance(query, word) <= maxEdits) {
        return { command, tier: 8, score: 35, matchedField: "label" };
      }
    }
  }

  return null;
}

/**
 * Filters and ranks commands deterministically based on query and context.
 */
export function filterCommands(
  rawQuery: string,
  context: CommandContext,
  commands: readonly CommandDefinition[] = COMMAND_REGISTRY
): CommandDefinition[] {
  const query = normalizeQuery(rawQuery);

  // Filter out hidden commands based on current context
  const eligibleCommands = commands.filter((cmd) => {
    if (cmd.availability) {
      const status = cmd.availability(context);
      return status !== "hidden";
    }
    return true;
  });

  // If query is empty, return curated default ordering
  if (!query) {
    return [...eligibleCommands].sort((a, b) => {
      const catA = CATEGORY_ORDER[a.category] ?? 99;
      const catB = CATEGORY_ORDER[b.category] ?? 99;
      if (catA !== catB) return catA - catB;
      return 0; // maintain registration order within same category
    });
  }

  // Match and rank
  const matches: CommandMatch[] = [];
  for (const cmd of eligibleCommands) {
    const match = matchCommand(cmd, query);
    if (match) {
      matches.push(match);
    }
  }

  // Deterministic tie-breaking:
  // 1. Tier (ascending, 1 is best)
  // 2. Category order
  // 3. Shorter label length
  // 4. Alphabetical label
  // 5. Command ID
  matches.sort((a, b) => {
    if (a.tier !== b.tier) return a.tier - b.tier;

    const catA = CATEGORY_ORDER[a.command.category] ?? 99;
    const catB = CATEGORY_ORDER[b.command.category] ?? 99;
    if (catA !== catB) return catA - catB;

    if (a.command.label.length !== b.command.label.length) {
      return a.command.label.length - b.command.label.length;
    }

    const labelCmp = a.command.label.localeCompare(b.command.label);
    if (labelCmp !== 0) return labelCmp;

    return a.command.id.localeCompare(b.command.id);
  });

  return matches.map((m) => m.command);
}
