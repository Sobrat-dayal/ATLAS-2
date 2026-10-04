# ATLAS Glossary

This document defines the core terminology used throughout the ATLAS platform and its documentation. Using precise, consistent terminology is required for future development.

**Agent:** An autonomous AI employee configured with a mission, tools, memory, and permissions to execute tasks within ATLAS.

**Agent Dock:** A collapsible right-side panel in the UI that allows users to monitor, manage, and interact with pinned and active agents.

**Agent Team:** An organized group of agents (e.g., Financial Research, Trading) where a manager agent can delegate subtasks to specialized worker agents.

**Approval:** A first-class workflow concept requiring human intervention (approve, reject, modify) before a high-risk or permission-gated action is executed.

**ATLAS AI:** The globally accessible, AI-powered assistant overlay (top-right) used for quick questions, navigation, contextual help, and simple task delegation. (Distinct from the full AI Assistant Module).

**Capability:** A reusable core business function (e.g., fetching a company profile, pricing an option) that is accessible via the UI, Agents, Terminal, and API.

**Context (Global Context):** The shared state of the application representing the user's current focus, including the selected entity, module, workspace, or active agent, which automatically propagates across all modules.

**Entity (Universal Entity):** A discrete, trackable concept within ATLAS possessing a stable internal identifier rather than relying solely on external symbols. Examples include Companies, Securities, Facilities, News Events, and Portfolios.

**Event:** A distinct occurrence (e.g., earnings report, price spike, geopolitical incident, facility disruption) that can act as a trigger for workflows or signal intelligence models.

**Global Settings:** Application-wide configurations (e.g., theme, account security, global API keys, default models) accessible from the bottom-left menu.

**Intelligence Signal:** A cross-domain anomaly, catalyst, or derived narrative identifying significant market or geopolitical movements and their potential impacts.

**MCP (Model Context Protocol):** A standardized protocol allowing ATLAS (and its Agents) to connect securely to external tools and data sources, managed as a first-class citizen in the platform.

**Provider:** A third-party source of financial, geospatial, or news data.

**Run:** A single execution instance of an agent, workflow, or task, which tracks state, logs, costs, and outputs.

**Section Settings:** Contextual settings specific to one of the 20 modules (e.g., Chart appearance, News sentiment filters).

**Security:** A tradable financial instrument (Equity, Bond, Option) treated as a specific type of Entity.

**Task:** A structured unit of work within ATLAS containing inputs, outputs, assignees, deadlines, and logs. Shared across human users, ATLAS AI, workflows, and Agents.

**Tool:** A specific, permission-gated function (often connected via MCP or the Agent Tool Gateway) that an agent or workflow can execute.

**Widget:** An individual component or panel (e.g., a specific chart or news feed) within a customized workspace.

**Workflow:** An automated sequence of nodes (Triggers, Agents, Tools, Logic, Code) constructed via the visual builder or defined in code to accomplish complex, multi-step processes.

**Workspace:** The configurable terminal environment where users arrange widgets, panels, and tools into saved, persistent layouts.
