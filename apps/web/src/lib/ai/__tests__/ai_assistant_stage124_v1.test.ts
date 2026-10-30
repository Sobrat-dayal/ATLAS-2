import { describe, it } from "node:test";
import assert from "node:assert";

import { CANONICAL_ROUTES_MAP, getRouteContext } from "../routeRegistry";
import { parseMarkdownBlocks, stripMarkdown } from "../markdown";

describe("Stage 124 - AI Assistant V1 & Universal Overlay Web Tests", () => {
  it("Fixture A: validates all 20 canonical ATLAS platform modules are registered", () => {
    const expectedRoutes = [
      "/home",
      "/markets",
      "/charts",
      "/watchlists",
      "/screeners",
      "/companies",
      "/economics",
      "/news",
      "/research",
      "/maps",
      "/intelligence",
      "/options",
      "/trading",
      "/portfolios",
      "/risk",
      "/ai",
      "/data",
      "/saved",
      "/workspaces",
      "/agents",
    ];

    assert.strictEqual(
      expectedRoutes.length,
      20,
      "Must have exactly 20 canonical top-level routes"
    );

    for (const r of expectedRoutes) {
      assert.ok(
        CANONICAL_ROUTES_MAP[r],
        `Route ${r} must be defined in CANONICAL_ROUTES_MAP`
      );
      assert.ok(
        CANONICAL_ROUTES_MAP[r].module_name.length > 0,
        `Route ${r} must have a non-empty module_name`
      );
      assert.ok(
        CANONICAL_ROUTES_MAP[r].summary.length > 0,
        `Route ${r} must have an institutional summary description`
      );
    }
  });

  it("Fixture B: validates getRouteContext resolves exact and nested paths", () => {
    // Exact match
    const riskCtx = getRouteContext("/risk");
    assert.strictEqual(riskCtx.route, "/risk");
    assert.strictEqual(riskCtx.module_name, "Risk Engine");

    // Nested match
    const companyNested = getRouteContext("/companies/AAPL/statements");
    assert.strictEqual(companyNested.route, "/companies");
    assert.strictEqual(companyNested.module_name, "Companies");

    // Unknown fallback
    const unknown = getRouteContext("/custom-beta-feature");
    assert.strictEqual(unknown.module_name, "ATLAS Operating System");
  });

  it("Fixture C: verifies markdown parser tokenizes fenced code blocks", () => {
    const text = "Here is the code:\n```python\nimport numpy as np\nx = np.mean([1, 2, 3])\n```\nDone.";
    const blocks = parseMarkdownBlocks(text);

    const codeBlock = blocks.find((b) => b.type === "code");
    assert.ok(codeBlock, "Must detect code block");
    assert.strictEqual(codeBlock.language, "python");
    assert.ok(codeBlock.content?.includes("np.mean"));
  });

  it("Fixture D: verifies markdown parser extracts KaTeX math blocks", () => {
    const text = "Sharpe ratio formula:\n$$\\text{Sharpe} = \\frac{R_p - R_f}{\\sigma_p}$$\nEnd of formula.";
    const blocks = parseMarkdownBlocks(text);

    const mathBlock = blocks.find((b) => b.type === "math");
    assert.ok(mathBlock, "Must detect math block");
    assert.ok(mathBlock.content?.includes("Sharpe"));
  });

  it("Fixture E: verifies markdown parser handles tables and lists", () => {
    const text = `
### Model Summary
| Metric | Value |
| :--- | :--- |
| Beta | 1.15 |
| Alpha | 2.4% |

Key takeaways:
- Strong market correlation
- Positive risk-adjusted return
`;
    const blocks = parseMarkdownBlocks(text);

    const heading = blocks.find((b) => b.type === "heading");
    assert.ok(heading);
    assert.strictEqual(heading.content, "Model Summary");

    const table = blocks.find((b) => b.type === "table");
    assert.ok(table);
    assert.strictEqual(table.headers?.length, 2);
    assert.strictEqual(table.rows?.length, 2);

    const list = blocks.find((b) => b.type === "list");
    assert.ok(list);
    assert.strictEqual(list.items?.length, 2);
  });

  it("Fixture F: verifies plain text markdown stripping", () => {
    const formatted = "Calculate **Duration** using `mod_duration()` function with [link](https://atlas.finance).";
    const stripped = stripMarkdown(formatted);
    assert.strictEqual(
      stripped,
      "Calculate Duration using mod_duration() function with link."
    );
  });
});

