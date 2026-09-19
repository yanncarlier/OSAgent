## System identity
OSAgent is an AI-powered terminal agent that enables LLMs to perform infrastructure monitoring and remediation through MCP tools while maintaining safety via command filtering. Its core invariant is that all shell commands pass through TerminalTool's safety filter before execution.

## Must-know facts
1. The agent operates in a REPL loop where user input triggers LLM responses that may include [[EXEC: command]] patterns for tool use
2. MCP server (mcp_self_healing_server.py) must be running separately to provide get_system_status and trigger_remediation tools
3. TerminalTool blocks only two specific high-risk commands: "rm -rf /" and ":(){ :|:& };:" (fork bomb)
4. Knowledge injection occurs when user input contains triggers matching KNOWLEDGE_BASE entries (currently only BashScriptMaster)
5. All interactions are logged to timestamped files in the logs/ directory via SessionLogger
6. MODEL_AUTOMATION flag controls whether command executions require manual confirmation (False by default)
7. LLM communication uses a local API endpoint (default: http://localhost:1234/v1/chat/completions)
8. Infrastructure state is simulated in INFRA_DATABASE and reset when MCP server restarts
9. The agent maintains conversation history in two parallel arrays: history (for logging) and messages (for LLM context)
10. MCP resources (like SLA policy) are accessed via MCP protocol, not as callable tools

## Module quick-ref
Module | Owns | Do not touch unless...
--- | --- | ---
Main Orchestrator (main.py) | Session state, conversation history | Changing the agent's core interaction loop or tool execution flow
MCP Server | INFRA_DATABASE (simulated infrastructure state) | Modifying the simulation or adding real infrastructure integrations
Logging System | Log files in logs/ directory | Changing log format or rotation policy
Terminal Tool | None (stateless) | Modifying safety filters or command execution logic
Context Manager | KNOWLEDGE_BASE (embedded knowledge) | Adding/removing knowledge domains or trigger words
LLM Interface | None (stateless) | Changing API endpoint format or communication protocol

## Patterns in use
Tool execution pattern → [[EXEC: command]] in main.py lines 144-165 → Enables LLM to request shell command execution → Example: [[EXEC: ls -la]]
Knowledge injection → ContextManager.get_relevant_context() in main.py lines 125-128 → Adds domain-specific context to LLM prompts → Example: Specialized bash scripting advice
Safety filtering → TerminalTool.execute() in main.py lines 56-73 → Prevents execution of dangerous commands → Example: Blocks rm -rf / and fork bomb
Session logging → SessionLogger.log() throughout main.py → Persists all agent interactions → Example: Logging user inputs and agent responses
MCP tool decoration → @mcp.tool() in mcp_self_healing_server.py → Exposes functions to LLM via MCP → Example: get_system_status and trigger_remediation

## Red lines
❌ Allowing arbitrary shell command execution without safety filtering because it could lead to system compromise or data loss
❌ Modifying MCP server to expose raw shell access because it would violate the security model
❌ Storing API keys or secrets in plaintext within the codebase because it creates security vulnerabilities
❌ Removing the MODEL_AUTOMATION confirmation requirement without equivalent safety measures because it increases accident risk
❌ Using the same log file for multiple sessions because it makes debugging and auditing difficult
❌ Tightly coupling the MCP server to specific infrastructure providers because it reduces extensibility

## Agent task routing
- Add a new API endpoint → Modify AgentLLM.chat() in main.py to handle different API formats or endpoints
- Add a new UI page → Not applicable (this is a terminal-based agent with no UI)
- Change a data model → Update INFRA_DATABASE in mcp_self_healing_server.py or KNOWLEDGE_BASE in main.py
- Add a background job → Not applicable (agent is interactive, not designed for background processes)
- Modify auth/permissions → Not applicable (no authentication system; assumes trusted MCP-LLM communication)