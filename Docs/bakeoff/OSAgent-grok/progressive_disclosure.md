# Progressive Disclosure Guide

## Level 1: 30-Second Overview
This is an agentic terminal assistant that uses a local LLM to suggest and execute shell commands. 
- **Entry point**: `main.py` 
- **Core loop**: User input → LLM suggests command → User confirms → Command runs → Output fed back → Repeat
- **Safety**: Requires user confirmation for command execution (configurable)
- **Logging**: All interactions saved to timestamped logs in `logs/`

## Level 2: 5-Minute Summary
**Architecture**:
- Single Python file (`main.py`) with no external dependencies beyond `requests`
- Components: 
  - `SessionLogger`: Handles logging to `logs/` directory
  - `TerminalTool`: Executes commands with safety filters (blocks `rm -rf /`, fork bombs)
  - `ContextManager`: Injects domain-specific knowledge from embedded `KNOWLEDGE_BASE` when triggers detected
  - `AgentLLM`: Wrapper for local LLM API calls (default: http://localhost:1234/v1/chat/completions)
- **Knowledge Base**: Currently contains one entry (`BashScriptMaster`) triggered by shell-related keywords
- **Execution Flow**:
  1. User types command/query
  2. System checks for knowledge triggers (e.g., "bash", "script") and appends relevant context
  3. Agent (LLM) responds with potential `[[EXEC: command]]` syntax
  4. If `[[EXEC: ...]]` found, user prompted for confirmation (y/n)
  5. On confirmation, command executed via `subprocess.run` with timeout
  6. Output logged and fed back into conversation history
  7. Loop continues until user types `exit`, `quit`, or `q`

**Configuration** (top of `main.py`):
- `API_URL`: Local LLM endpoint
- `MODEL_TEMPERATURE`: 0.1 (low for focused responses)
- `MODEL_AUTOMATION`: False (set True to skip confirmation)
- `LOG_DIR`: "logs" (session logs stored here)

## Level 3: Full Details with File Links
**File: main.py** (complete implementation)
- Lines 1-9: Imports (stdlib + requests)
- Lines 11-15: Configuration constants
- Lines 17-30: Embedded `KNOWLEDGE_BASE` (dict with trigger-based contextual content)
- Lines 34-53: `SessionLogger` class (logging to files)
- Lines 56-74: `TerminalTool.execute()` (safe command execution with safety checks)
- Lines 77-85: `ContextManager.get_relevant_context()` (scans input for triggers)
- Lines 87-96: `AgentLLM.chat()` (HTTP POST to local LLM API)
- Lines 100-170: `run_agentic_session()` (main loop) and `__main__` guard

**Key Details**:
- **Safety**: Lines 59-60 block high-risk commands; timeout set to 30s (line 63)
- **Logging**: Each session creates a new file: `session_YYYYMMDD_HHMMSS.log` (line 42)
- **Prompt Structure**: 
  - Base system prompt (lines 104-108) defines tool use syntax `[[EXEC: <command>]]`
  - If knowledge triggered, appended as "--- ACTIVE KNOWLEDGE ---" (line 128)
- **History Management**: 
  - User and assistant messages stored in `history` list (lines 131, 134, 141-142)
  - Used to maintain context across turns in the LLM conversation
- **EXEC Parsing**: Regex `r'\[\[EXEC:\s*(.*?)\s*\]\]'` (line 144) captures command; loop continues after output fed back (line 164)
- **Termination**: Break on user exit or KeyboardInterrupt (Ctrl+C) (lines 115-121)

**To Extend**:
- Add new entries to `KNOWLEDGE_BASE` dict (lines 17-30) with:
  - Unique key (e.g., "PythonExpert")
  - Description (optional, for clarity)
  - `triggers`: list of lowercase keywords that activate this context
  - `content`: string to append to system prompt when triggered
- Adjust LLM parameters (`API_URL`, `MODEL_TEMPERATURE`) as needed
- Modify safety filters in `TerminalTool.execute()` (lines 59-60) to block additional patterns

**Next Steps for Developer**:
1. Review `main.py` for full implementation
2. Check `logs/` directory for session logs after running
3. Ensure local LLM server is running at `API_URL` (default: localhost:1234)
4. Install dependencies: `pip install requests` (if not present)
5. Run: `python main.py`