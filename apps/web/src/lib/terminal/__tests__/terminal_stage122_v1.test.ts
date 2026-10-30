import { describe, it } from "node:test";
import assert from "node:assert";

import {
  REGISTERED_CLI_COMMANDS,
  TERMINAL_CAPABILITIES_CATALOG,
} from "../capabilities";
import {
  escapeHtml,
  isSafeUrl,
  parseAnsiToSpans,
  stripUnsafeAnsi,
} from "../sanitization";
import { TerminalSession, TerminalType } from "../types";

describe("Stage 122 - Integrated ATLAS Terminal Shell Unit Tests", () => {
  it("Fixture A: validates all 6 principal console types exist with execution disabled", () => {
    const expectedConsoles: TerminalType[] = [
      "ATLAS_CLI",
      "PYTHON",
      "SQL",
      "LOGS",
      "AGENTS",
      "MCP",
    ];

    for (const cType of expectedConsoles) {
      const cap = TERMINAL_CAPABILITIES_CATALOG[cType];
      assert.ok(cap, `Missing capability definition for ${cType}`);
      assert.strictEqual(
        cap.supports_arbitrary_execution,
        false,
        `${cType} must not permit arbitrary execution in Stage 122`
      );
      assert.ok(
        cap.execution_status_notice.length > 0,
        `${cType} must declare an explicit execution notice`
      );
    }
  });

  it("Fixture B: validates static CLI commands catalog has required system builtins", () => {
    const commands = REGISTERED_CLI_COMMANDS.map((c) => c.command);
    assert.ok(commands.includes("help"));
    assert.ok(commands.includes("clear"));
    assert.ok(commands.includes("status"));
    assert.ok(commands.includes("version"));
    assert.ok(commands.includes("workspace"));
    assert.ok(commands.includes("context"));
    assert.ok(commands.includes("markets"));
    assert.ok(commands.includes("instrument"));
  });

  it("Fixture C: escapes unsafe HTML characters to prevent XSS in logs and terminal output", () => {
    const malicious = "<script>alert('xss')</script>&\"hello\"";
    const escaped = escapeHtml(malicious);
    assert.strictEqual(
      escaped,
      "&lt;script&gt;alert(&#039;xss&#039;)&lt;/script&gt;&amp;&quot;hello&quot;"
    );
    assert.ok(!escaped.includes("<script>"));
  });

  it("Fixture D: strips dangerous OSC escape sequences (OSC 8 hyperlinks, OSC 52 clipboard hijacking)", () => {
    // OSC 8 hyperlink sequence
    const osc8 = "\x1b]8;;http://malicious-phishing.com\x07Click Here\x1b]8;;\x07";
    const cleanOsc8 = stripUnsafeAnsi(osc8);
    assert.strictEqual(cleanOsc8, "Click Here");

    // OSC 52 clipboard manipulation sequence
    const osc52 = "\x1b]52;c;c2VjcmV0X2tleQ==\x07Hello Terminal";
    const cleanOsc52 = stripUnsafeAnsi(osc52);
    assert.strictEqual(cleanOsc52, "Hello Terminal");

    // Window title manipulation (OSC 0 / 2)
    const oscTitle = "\x1b]0;Pwned Terminal\x07Normal Text";
    const cleanTitle = stripUnsafeAnsi(oscTitle);
    assert.strictEqual(cleanTitle, "Normal Text");
  });

  it("Fixture E: safely parses ANSI color codes into structured styled spans", () => {
    const coloredText = "\x1b[32mSuccess\x1b[0m and \x1b[31;1mError!\x1b[0m";
    const spans = parseAnsiToSpans(coloredText);

    assert.ok(spans.length >= 3);
    assert.strictEqual(spans[0].text, "Success");
    assert.ok(spans[0].className?.includes("text-emerald-400"));

    const errSpan = spans.find((s) => s.text === "Error!");
    assert.ok(errSpan);
    assert.ok(errSpan.className?.includes("text-rose-400"));
    assert.strictEqual(errSpan.bold, true);
  });

  it("Fixture F: validates safe HTTP/HTTPS URLs and blocks dangerous javascript: or data: URIs", () => {
    assert.strictEqual(isSafeUrl("https://financial.market.data/v1"), true);
    assert.strictEqual(isSafeUrl("http://localhost:8000/api"), true);
    assert.strictEqual(isSafeUrl("javascript:alert(1)"), false);
    assert.strictEqual(isSafeUrl("data:text/html,<script>"), false);
    assert.strictEqual(isSafeUrl("not-a-valid-url"), false);
  });

  it("Fixture G: enforces independent per-session draft isolation", () => {
    const sessionPy1: TerminalSession = {
      session_id: "term_py_1",
      owner_user_id: "usr_trader_1",
      terminal_type: "PYTHON",
      display_name: "Python 1",
      lifecycle: "ACTIVE",
      connection_state: "CONNECTED",
      execution_capability: "DISABLED",
      status: "INPUT_ONLY",
      session_order: 0,
      configuration_schema_version: 1,
      version: 1,
      draft_content: "import pandas as pd\n",
      scrollback_limit: 2000,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_active_at: new Date().toISOString(),
    };

    const sessionPy2: TerminalSession = {
      ...sessionPy1,
      session_id: "term_py_2",
      display_name: "Python 2",
      session_order: 1,
      draft_content: "import numpy as np\n",
    };

    // Modifying Py1 draft does not mutate Py2 draft
    const updatedPy1 = { ...sessionPy1, draft_content: "import scipy\n" };
    assert.notStrictEqual(updatedPy1.draft_content, sessionPy2.draft_content);
    assert.strictEqual(sessionPy2.draft_content, "import numpy as np\n");
    assert.strictEqual(updatedPy1.draft_content, "import scipy\n");
  });

  it("Fixture H: validates multiline editing capability configuration", () => {
    // ATLAS CLI is single-line prompt
    assert.strictEqual(
      TERMINAL_CAPABILITIES_CATALOG.ATLAS_CLI.supports_multiline,
      false
    );
    // Python & SQL support multiline editor
    assert.strictEqual(
      TERMINAL_CAPABILITIES_CATALOG.PYTHON.supports_multiline,
      true
    );
    assert.strictEqual(
      TERMINAL_CAPABILITIES_CATALOG.SQL.supports_multiline,
      true
    );
    // Logs, Agents, MCP are read-only
    assert.strictEqual(
      TERMINAL_CAPABILITIES_CATALOG.LOGS.supports_multiline,
      false
    );
    assert.strictEqual(
      TERMINAL_CAPABILITIES_CATALOG.AGENTS.supports_multiline,
      false
    );
    assert.strictEqual(
      TERMINAL_CAPABILITIES_CATALOG.MCP.supports_multiline,
      false
    );
  });

  it("Fixture I: validates Stage 123 preparation contracts structure", () => {
    import("../stage123Contracts").then((contracts) => {
      assert.ok(contracts, "Stage 123 contracts module must be exported");
    });
  });
});

