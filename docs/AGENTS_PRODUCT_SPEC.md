# ATLAS Agents Product Specification

ATLAS Agents represents an autonomous workforce and workflow development environment. It is a core pillar of the platform.

## Agent Types

1. **Built-in ATLAS Agents:** Pre-configured agents for specific domains (e.g., Market Agent, Research Agent, Maps Agent, Trading Agent, Quant Agent, Data Agent).
2. **User-Created Agents:** Configured via the UI.
3. **Code-Defined Agents:** Written in code within ATLAS.
4. **Installable Agents:** Downloaded via local package, Git repo, URL, marketplace, or ATLAS package.

## Workforce Concept

Agents act conceptually as employees. Every agent will possess:
- Name, Role, Mission, System instructions
- Model configuration
- Tools & MCP access
- Memory & Knowledge
- Permissions & Autonomy level
- Schedule, Budget, and Cost tracking
- Status, Active task, Task history, and Logs

Agents can operate manually, on-demand, scheduled, event-triggered, or 24/7 (only when server infrastructure is active, not when ATLAS infrastructure is offline).

## Agent Teams and Departments

Agents can be organized into departments (e.g., Executive, Financial Research, Trading, Engineering, AI Safety). Manager agents can delegate tasks to worker agents.

## N8N-Style Visual Agent/Workflow Builder

ATLAS must include a visual node-based automation environment tailored for finance, research, and software development.

### Node Categories
Triggers, Agents, ATLAS tools, AI/LLM, MCP, Data, Logic (Conditions, Loops, Merge, Split, Wait, Retry, Approval, Policy), Code (Python, JS, SQL), External APIs, Files, Sub-workflows.

### Triggers
- **Finance-specific:** Market open/close, price conditions, volume spikes, earnings, filings, rate decisions, news events, portfolio drawdown.
- **Geospatial:** Earthquake, wildfire, ship entering an area, facility disruption.
- **Agent events:** Task completed, failed, approval required, message received.

## Advanced Workflow Concepts

### Agent as a Node
An entire agent can serve as a workflow node with specific inputs (task, context, entity) and outputs (answer, report, structured data).

### Internal & Nested Workflows
An agent can possess an internal workflow (e.g., Receive Task -> Search Sources -> Analyze -> Critic -> Revise -> Return).
ATLAS supports deep nesting: `Workflow -> Sub-workflow -> Agent -> Agent internal workflow -> Tools/MCP/Code`.

## MCP (Model Context Protocol)

MCP is a first-class citizen. Users can:
- Add servers, configure credentials securely, and inspect tools.
- Assign MCP tools to agents and use them as workflow nodes.
- Restrict access via permissions and monitor tool calls.
*Security Principle:* Agents never receive unrestricted access merely because a server is connected.

## Agent Tool Gateway & Safety

Agents must not manipulate production databases, infrastructure, or brokers directly. 
All interactions follow: `Agent -> Capability Gateway -> Permission Engine -> Approved Tool -> ATLAS Service`.

### Autonomy Levels
- **Level 0:** Observe
- **Level 1:** Recommend
- **Level 2:** Perform approved internal actions
- **Level 3:** Perform approved external low-risk actions
- **Level 4:** Autonomous within configured policy

### Human Approval
Approval is a first-class workflow concept (approve, reject, modify, request info). Approvals can be user-specific, team-based, risk-based, or time-limited.

## Agent Budgets & Performance

**Budgets:** Controls for token usage, API calls, compute, GPU, time limits, and daily/monthly monetary constraints.
**Performance:** Tracking metrics like tasks completed, success/failure rate, average runtime/cost, human correction rate, and evaluation score.

## Task System

A unified task system powers the user, ATLAS AI, workflows, and agents. Tasks include dependencies, priorities, status, deadlines, inputs/outputs, artifacts, and logs.
*Lifecycle:* Backlog -> Queued -> Working -> Waiting -> Needs Approval -> Review -> Completed (or Blocked/Failed/Cancelled).
