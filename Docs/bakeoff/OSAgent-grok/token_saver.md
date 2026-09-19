# Token Saver: Ultra-Concise Context

## Repo Map
- `main.py`: Core agentic terminal assistant (170 lines)
- `mcp_self_healing_server.py`: MCP server for infrastructure self-healing (64 lines)
- `logs/`: Session log files
- Config: `.gitignore`, `README.md`, `requirements.txt`, `pyproject.toml`

## Critical Files
1. **main.py** - Primary implementation
2. **mcp_self_healing_server.py** - Secondary MCP server

## Key Functions/Classes (1-line purpose)
- `SessionLogger` (main.py): Logs all interactions to timestamped files
- `TerminalTool.execute` (main.py): Safely runs shell commands with safety filters
- `ContextManager.get_relevant_context` (main.py): Injects knowledge base triggers
- `AgentLLM.chat` (main.py): Wraps local LLM API calls
- `run_agentic_session` (main.py): Main agent loop (input → think → confirm EXEC → execute → log)
- `get_system_status` (mcp_self_healing_server.py): Returns infrastructure health
- `trigger_remediation` (mcp_self_healing_server.py): Executes self-healing actions
- `get_sla_policy` (mcp_self_healing_server.py): Provides SLA context to LLM

## Import Graph Highlights
- **main.py**: `os`, `re`, `json`, `requests`, `subprocess`, `sys`, `datetime`, `typing`
- **mcp_self_healing_server.py**: `asyncio`, `typing`, `mcp.server.fastmcp`

## Instructions
**Read this first, then only referenced files.**
1. Start with `main.py` for core agent logic
2. Review `mcp_self_healing_server.py` for MCP/self-healing context
3. Check `logs/` for session history
4. Configuration in `main.py` top section (API_URL, MODEL_TEMPERATURE, etc.)
5. Knowledge base in `main.py` lines 17-30 for extensibility

## Key Constants (main.py)
- `API_URL`: Local LLM endpoint (default: http://localhost:1234/v1/chat/completions)
- `MODEL_TEMPERATURE`: 0.1 (deterministic outputs)
- `MODEL_AUTOMATION`: False (user confirmation required for EXEC)
- `LOG_DIR`: "logs/" (session storage)