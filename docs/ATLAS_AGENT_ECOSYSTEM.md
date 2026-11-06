# ATLAS Stage 149: MCP, Plugin and Agent Ecosystem Platform

## Architectural Specification and Developer Guide

### Overview
Stage 149 establishes the extensible institutional foundation for ATLAS, transforming the platform into a secure, extensible operating environment supporting third-party integrations, Model Context Protocol (MCP) clients and servers, scoped plugin sandboxes, downloadable `.atlas-agent` packages, pre-configured starter templates, Git repository provenance, and an institutional developer SDK.

---

## 1. Core Ecosystem Modules & Routes

| Surface | Web Route | Backend API Path | Description |
|---|---|---|---|
| **Ecosystem Cockpit** | `/agents/ecosystem` | `/api/v1/ecosystem/overview` | Unified command center for extensions, governance metrics, and audit ledger. |
| **MCP Registry** | `/agents/mcp` | `/api/v1/ecosystem/mcp/...` | Registration, connection, capability discovery, and ping testing for MCP servers. |
| **Plugin Registry** | `/agents/plugins` | `/api/v1/ecosystem/plugins/...` | Scoped plugin manifests, tenant installations, and permission grant review. |
| **Package Platform** | `/agents/packages` | `/api/v1/ecosystem/packages/...` | Validation, export, and draft installation of `.atlas-agent` archive packages. |
| **Starter Templates** | `/agents/templates` | `/api/v1/ecosystem/templates/...` | Pre-built templates for agents, teams, and workflows instantiated into DRAFT state. |
| **Marketplace** | `/agents/marketplace` | `/api/v1/ecosystem/marketplace/...` | Truthful catalog of extensions with verified publisher badges and zero fake ratings. |
| **Developer Platform**| `/agents/developers`| `/api/v1/ecosystem/developers/...`| Custom Tool Testing Lab, Developer Apps, API keys, Git sync, and SDK documentation. |

---

## 2. Institutional Security Guardrails

### A. Financial Safety Firewall
- **Zero Live Execution:** All ecosystem extensions (MCP tools, plugins, custom tools, agent packages) are strictly prohibited from submitting live financial orders or mutating real-money brokerage ledgers.
- **Side-Effect Classification:** Every tool declares its side-effect class: `READ_ONLY`, `SIMULATED_WRITE`, or `SANDBOX_EXECUTE`. Any tool attempting unapproved mutations is rejected with `FinancialSafetyViolationError`.

### B. SSRF Protection on MCP Endpoints
- **Localhost and Private IP Rejection:** MCP server endpoints are inspected by `validate_endpoint_security` prior to registration.
- **Blocked Ranges:**
  - Loopback (`127.0.0.0/8`, `localhost`, `::1`)
  - RFC 1918 Private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Cloud Metadata services (`169.254.169.254`, `metadata.google.internal`)
  - Non-HTTP/HTTPS protocols (e.g., `file://`, `ftp://`, `gopher://`)
- Violations raise `MCPSSRFSecurityError`.

### C. `.atlas-agent` Archive Security (Zip-Slip & Secret Scanning)
- **Zip-Slip Defense:** All file paths within ingested zip packages are sanitized. Any path attempting relative traversal (`../`, `..\\`) or absolute root escapes is blocked with `PackageSecurityError`.
- **Decompression Bomb Protection:** Archives exceeding 100 files, uncompressed file size > 50 MB, or compression ratio > 20x are rejected.
- **Automated Secret Redaction:** Package validation actively scans for exposed credentials (OpenAI `sk-...`, AWS `AKIA...`, GitHub `ghp_...`, Bearer tokens). Any package with unredacted keys is rejected.
- **Draft-First Instantiation:** Agents and teams installed from packages or instantiated from templates ALWAYS start in `DRAFT` status with execution disabled until tenant administrator approval.

### D. Truthful Marketplace & Authenticity
- No fabricated reviews, synthetic star ratings, or simulated download metrics.
- Verified publisher badges: `OFFICIAL_ATLAS`, `VERIFIED_PARTNER`, and `COMMUNITY`.
- Transparent permission inspection before installation.

---

## 3. The `.atlas-agent` Package Specification

An `.atlas-agent` file is a standard ZIP archive containing:
1. `manifest.json`: Root package manifest complying with `AtlasAgentPackageManifest`:
   - `package_id`: Unique identifier (e.g. `pkg-equity-analyst-v1`)
   - `name`: Display name
   - `version`: Semantic version string
   - `kind`: `AGENT`, `TEAM`, `WORKFLOW`, or `TOOLSET`
   - `author`: Author or publisher identifier
   - `permissions`: Scoped permissions requested
   - `required_tools`: Tool names required by the package
   - `atlas_version_min`: Minimum compatible ATLAS runtime version
   - `checksum_sha256`: Cryptographic SHA-256 hash
2. `agent.json` / `agents/*.json`: Serialized agent configurations (with canonical models: `atlas-intelligence-v1`, `atlas-reasoning-v1`, `atlas-speed-v1`).
3. `tools/*.json`: Custom tool definitions with input/output JSON schemas.
4. `README.md`: Human-readable description, usage instructions, and licensing.

---

## 4. Custom Tool Testing Lab

Developers can create and test JSON Schema custom tools directly in the browser or via API:
- Inputs validated against standard JSON Schema Draft 7.
- Sandbox execution captures return outputs and execution duration in milliseconds (`duration_ms`).
- Immutable versioning on publish prevents runtime drift.

---

## 5. Developer Platform & External MCP Server

### Developer Apps & API Keys
- Issue scoped credentials (`client_id`, `client_secret`) hashed with SHA-256.
- Per-application rate limiting (120 RPM default) and token usage metering.
- Revocation lifecycle (`ACTIVE`, `REVOKED`).

### External ATLAS MCP Server
ATLAS exposes its own Model Context Protocol server for external AI tools:
- `atlas_research_search`: Search internal research and filing archives.
- `atlas_company_profile`: Retrieve fundamentals and sector classifications.
- `atlas_market_quote`: Fetch delayed market quotes (sandbox only).
- `atlas_workflow_status`: Query execution status of long-running workflows.

---

## 6. Verification and Testing

Stage 149 has been verified with comprehensive unit and integration test suites:
- **Backend Tests:** 15 / 15 tests passing in `apps/api/tests/test_ecosystem_stage149_suite.py` covering Demonstrations A through M, SSRF defense, Zip-Slip, secret scanning, tampered package rejection, and HTTP endpoints.
- **Backend Regression Tests:** 31 / 31 passing across Stages 146 through 148 (46 tests total).
- **Frontend Unit Tests:** 12 / 12 tests passing in `apps/web/src/lib/ecosystem/__tests__/ecosystem_stage149.test.ts`.
- **Frontend App Regression Tests:** 382 / 382 passing across the full web workspace.
- **Production Build:** Next.js / TypeScript production build compiles cleanly with zero type errors.

*Note: In compliance with the frozen canonical roadmap, Stage 149 is complete and stops cleanly before Stage 150.*
