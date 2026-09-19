## Module map
Module | Path(s) | Responsibility | Owns | Depends on
--- | --- | --- | --- | ---
Main Orchestrator | main.py | Coordinates agent session, handles user input, manages tool execution and LLM interaction | Session state, conversation history | SessionLogger, TerminalTool, ContextManager, AgentLLM
MCP Server | mcp_self_healing_server.py | Exposes infrastructure introspection and remediation tools via MCP protocol | INFRA_DATABASE (simulated infrastructure state) | None (standalone server)
Logging System | main.py:SessionLogger | Handles file-based logging for all agent communications | Log files in logs/ directory | os, datetime
Terminal Tool | main.py:TerminalTool | Executes shell commands with safety filtering for high-risk operations | None (stateless utility) | subprocess
Context Manager | main.py:ContextManager | Injects specialized knowledge into LLM context based on input triggers | KNOWLEDGE_BASE (embedded knowledge snippets) | None
LLM Interface | main.py:AgentLLM | Handles communication with local LLM API via HTTP requests | None (stateless wrapper) | requests
Configuration | main.py (top-level) | Stores global settings and constants | API_URL, MODEL_TEMPERATURE, MODEL_AUTOMATION, LOG_DIR, KNOWLEDGE_BASE | None

## Data flow
Infrastructure monitoring flow → User query → get_system_status tool → MCP server returns INFRA_DATABASE state → Agent presents to user
Remediation flow → User command → trigger_remediation tool → MCP server updates INFRA_DATABASE → Agent confirms action completion
Knowledge injection flow → User input contains triggers → ContextManager.get_relevant_context returns KNOWLEDGE_BASE content → Added to system prompt → LLM uses enhanced context
Tool execution flow → Agent outputs [[EXEC: command]] → TerminalTool.execute runs command with safety checks → Output returned to agent → Appended to conversation history
Logging flow → Any major event (user input, agent response, system events) → SessionLogger.log writes timestamped entry to session log file

## Boundary rules
Persistence layer is never imported by UI components (there is no UI, but logging is isolated)
MCP server has no direct access to agent conversation state or LLM interaction logic
TerminalTool is the only module allowed to execute shell commands (safety filtering boundary)
ContextManager only reads from KNOWLEDGE_BASE, never modifies it during runtime
AgentLLM only communicates with the configured LLM API endpoint, no direct tool access
Main orchestrator is the only module that coordinates between all other modules

## Key abstractions
SessionLogger — Handles timestamped logging of agent interactions — defined in main.py:SessionLogger — Usage: logger.log("USER", user_input)
TerminalTool — Safe shell command execution with predefined risk filters — defined in main.py:TerminalTool — Usage: TerminalTool.execute("ls -la")
ContextManager — Dynamically injects relevant knowledge based on input triggers — defined in main.py:ContextManager — Usage: ContextManager.get_relevant_context("how to use awk")
AgentLLM — Wrapper for LLM API communication with error handling — defined in main.py:AgentLLM — Usage: AgentLLM.chat(messages)
MCP Tool — Functions decorated with @mcp.tool() exposing capabilities to LLM — defined in mcp_self_healing_server.py — Usage: @mcp.tool() async def get_system_status(...)
KNOWLEDGE_BASE — Embedded dictionary of specialized context snippets — defined in main.py line 17 — Usage: KNOWLEDGE_BASE["BashScriptMaster"]["content"]

## Known design decisions (ADR-lite)
Decision | Why | What was rejected
--- | --- | ---
Use simulated infrastructure state (INFRA_DATABASE) instead of real APIs | Simplified demonstration and testing without requiring external dependencies | Actual cloud/provider integrations (would add complexity for demo)
Embed knowledge base directly in code rather than external files | Ensured availability and simplified deployment | External knowledge base files (added deployment complexity)
Implement safety filtering in TerminalTool rather than relying on LLM | Defense-in-depth approach to prevent accidental execution of dangerous commands | Trusting LLM to avoid dangerous commands
Use FastMCP stdio transport for server communication | Simple integration with local LLM applications | HTTP/SSE transports (added unnecessary complexity for local use)
Store logs in timestamped files under logs/ directory | Easy session tracking and debugging | Single log file or database (harder to correlate sessions)