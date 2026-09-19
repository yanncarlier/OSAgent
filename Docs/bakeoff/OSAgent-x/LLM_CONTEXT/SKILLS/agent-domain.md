# Agent Domain

## Summary
The agent domain encompasses the core conversational agent that interacts with users, manages context, communicates with LLMs, and orchestrates tool use. It's implemented primarily in `main.py` and handles the complete agent lifecycle from input processing to action execution.

## Key Invariants & Business Rules
- **Tool Use Protocol**: LLMs must use `[[EXEC: <command>]]` syntax to request terminal execution
- **Human-in-the-Loop Default**: Requires explicit user approval (`y/n`) for command execution unless `MODEL_AUTOMATION=True`
- **Context Isolation**: Each session maintains independent conversation history and knowledge injection
- **Progressive Knowledge Building**: System prompt augmented only with relevant specialized knowledge based on input triggers
- **Complete Audit Trail**: All interactions (user, agent, system, terminal output) logged with timestamps

## Most Important Symbols

### `SessionLogger` Class
Handles file-based logging for all agent communications. Creates timestamped log files in the `logs/` directory with standardized format: `[TIMESTAMP] SENDER:\nMESSAGE\n-` separator.

### `TerminalTool.execute()` Method
Secure command execution layer that:
1. Filters high-risk commands (e.g., `rm -rf /`, fork bombs)
2. Executes via subprocess with 30-second timeout
3. Returns structured output including stdout, stderr, and exit codes
4. Provides safety net for LLM-generated commands

### `ContextManager.get_relevant_context()` Method
Retrieves specialized knowledge from embedded knowledge base:
1. Scans user input for trigger keywords
2. Returns matching knowledge base content
3. Enables progressive disclosure of domain-specific expertise
4. Currently implements `BashScriptMaster` context for shell scripting

### `AgentLLM.chat()` Method
Abstracts communication with the LLM API:
1. Sends POST request to configured endpoint
2. Handles request/response formatting
3. Manages error handling and timeout
4. Returns LLM response content

### `run_agentic_session()` Function
Main orchestration loop that:
1. Initializes tools and logger
2. Processes user input in continuous loop
3. Builds system prompt with active knowledge
4. Manages conversation history
5. Parses LLM responses for `[[EXEC:]]` commands
6. Coordinates command execution and result feedback
7. Handles session termination

## References to Other Context Files
- Read `ARCHITECTURE.md` for overall system structure
- Read `ENTRY_POINTS.md` for detailed execution flow

## When to Load This File
Load this file when you need to understand:
- How the agent processes user input and generates responses
- The security model for command execution
- How specialized knowledge is injected into LLM prompts
- The conversation flow and state management
- How to modify or extend the agent's core behavior