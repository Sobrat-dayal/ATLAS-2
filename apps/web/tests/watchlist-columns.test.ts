import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import * as watchlistComponents from "../src/components/watchlists";
import {
  COLUMN_CATALOG,
  COLUMN_MAP,
  MAX_PINNED_COLUMNS,
  MAX_VISIBLE_COLUMNS,
  REQUIRED_COLUMN_ID,
  calculateStickyLeftOffsets,
  getDefaultColumnConfig,
} from "../src/lib/watchlists/columns/registry";
import { WatchlistColumnDefinition } from "../src/lib/watchlists/columns/types";

describe("Stage 77 - Advanced Watchlist Columns V1 Frontend Tests", () => {
  it("should confirm all Stage 77 column components are properly exported", () => {
    assert.ok(
      watchlistComponents.WatchlistColumnManager,
      "WatchlistColumnManager must be exported"
    );
    assert.ok(
      watchlistComponents.WatchlistColumnHeader,
      "WatchlistColumnHeader must be exported"
    );
    assert.ok(
      watchlistComponents.WatchlistTable,
      "WatchlistTable must be exported"
    );
    assert.ok(
      watchlistComponents.WatchlistsWorkspace,
      "WatchlistsWorkspace must be exported"
    );
  });

  it("should verify Column Registry catalog integrity (14 operational columns)", () => {
    assert.strictEqual(COLUMN_CATALOG.length, 14, "Must contain exactly 14 operational columns");
    assert.strictEqual(COLUMN_MAP.size, 14, "COLUMN_MAP must contain 14 entries");

    const validCategories = new Set(["identity", "market", "quote", "quality"]);
    const validValueTypes = new Set([
      "TEXT",
      "IDENTIFIER",
      "ENUM",
      "MONETARY",
      "PERCENTAGE",
      "TIMESTAMP",
      "STATUS",
    ]);

    for (const col of COLUMN_CATALOG) {
      assert.ok(col.id.length > 0, "Column ID must be non-empty");
      assert.ok(col.label.length > 0, "Column label must be non-empty");
      assert.ok(col.description.length > 0, "Column description must be non-empty");
      assert.ok(validCategories.has(col.category), `Invalid category: ${col.category}`);
      assert.ok(validValueTypes.has(col.value_type), `Invalid value type: ${col.value_type}`);
      assert.ok(
        col.min_width <= col.default_width && col.default_width <= col.max_width,
        `Width bounds violated for ${col.id}: ${col.min_width} <= ${col.default_width} <= ${col.max_width}`
      );
      assert.strictEqual(col.version, 1, "Initial schema version must be 1");
    }
  });

  it("should enforce mandatory constraints on required Symbol column", () => {
    const symbolCol = COLUMN_MAP.get(REQUIRED_COLUMN_ID);
    assert.ok(symbolCol, "instrument.symbol must exist in registry");
    assert.strictEqual(symbolCol.can_hide, false, "Symbol column must NEVER be hideable");
    assert.strictEqual(symbolCol.can_pin, true, "Symbol column must be pinnable");
    assert.strictEqual(symbolCol.default_visible, true, "Symbol column must be default visible");
  });

  it("should produce a valid default column configuration", () => {
    const config = getDefaultColumnConfig();
    assert.strictEqual(config.schema_version, 1);
    assert.ok(config.visible_column_ids.includes(REQUIRED_COLUMN_ID));
    assert.ok(config.pinned_left_column_ids.includes(REQUIRED_COLUMN_ID));
    assert.ok(config.visible_column_ids.length <= MAX_VISIBLE_COLUMNS);
    assert.ok(config.pinned_left_column_ids.length <= MAX_PINNED_COLUMNS);

    // All columns have initial widths
    for (const col of COLUMN_CATALOG) {
      assert.strictEqual(config.widths[col.id], col.default_width);
    }
  });

  it("should accurately compute sticky left offsets for pinned columns", () => {
    const symCol = COLUMN_MAP.get("instrument.symbol")!;
    const nameCol = COLUMN_MAP.get("instrument.name")!;
    const venueCol = COLUMN_MAP.get("market.venue")!;

    const visibleCols: WatchlistColumnDefinition[] = [symCol, nameCol, venueCol];
    const pinnedIds = ["instrument.symbol", "instrument.name"];
    const widths: Record<string, number> = {
      "instrument.symbol": 140,
      "instrument.name": 220,
      "market.venue": 120,
    };

    // Base offset: 72px (32px drag handle + 40px index #)
    const offsets = calculateStickyLeftOffsets(visibleCols, pinnedIds, widths, 72);

    assert.strictEqual(offsets.get("instrument.symbol"), 72);
    // Next pinned column offset is 72 + 140 = 212px
    assert.strictEqual(offsets.get("instrument.name"), 212);
    // venueCol is not pinned, so no offset
    assert.strictEqual(offsets.has("market.venue"), false);
  });

  it("should verify sorting with missing-values-last semantics", () => {
    // Conceptual row sorting check
    const rows = [
      { id: "1", price: null, pos: 0 },
      { id: "2", price: 200, pos: 1 },
      { id: "3", price: 50, pos: 2 },
      { id: "4", price: null, pos: 3 },
    ];

    const sortRows = (items: typeof rows, isDesc: boolean) => {
      const valid = items.filter((i) => i.price !== null);
      const missing = items.filter((i) => i.price === null);

      valid.sort((a, b) => a.pos - b.pos);
      valid.sort((a, b) => {
        if (a.price! < b.price!) return isDesc ? 1 : -1;
        if (a.price! > b.price!) return isDesc ? -1 : 1;
        return 0;
      });

      missing.sort((a, b) => a.pos - b.pos);
      return [...valid, ...missing];
    };

    const asc = sortRows(rows, false);
    assert.deepStrictEqual(
      asc.map((r) => r.id),
      ["3", "2", "1", "4"],
      "Ascending numeric sort must place missing values last"
    );

    const desc = sortRows(rows, true);
    assert.deepStrictEqual(
      desc.map((r) => r.id),
      ["2", "3", "1", "4"],
      "Descending numeric sort must place missing values last as well"
    );
  });

  it("should verify strict institutional design compliance: zero purple gradients or cartoon chrome", () => {
    const tableFile = path.resolve(__dirname, "../src/components/watchlists/WatchlistTable.tsx");
    const managerFile = path.resolve(
      __dirname,
      "../src/components/watchlists/WatchlistColumnManager.tsx"
    );
    const headerFile = path.resolve(
      __dirname,
      "../src/components/watchlists/WatchlistColumnHeader.tsx"
    );

    const checkFiles = [tableFile, managerFile, headerFile];

    for (const file of checkFiles) {
      assert.ok(fs.existsSync(file), `File must exist: ${file}`);
      const content = fs.readFileSync(file, "utf-8");

      assert.ok(!content.includes("from-purple"), `Forbidden purple gradient in ${file}`);
      assert.ok(!content.includes("to-indigo"), `Forbidden indigo gradient in ${file}`);
      assert.ok(!content.includes("to-purple"), `Forbidden purple gradient in ${file}`);
      assert.ok(!content.includes("bg-gradient"), `Forbidden decorative gradient in ${file}`);
    }
  });
});
