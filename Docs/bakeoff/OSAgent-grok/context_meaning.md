# Context & Meaning Glossary

## Core Concepts
- **Agentic Terminal Assistant**: AI that autonomously suggests and executes terminal commands via a local LLM, with user oversight.
- **Knowledge Base Triggers**: User input keywords that inject specialized context (e.g., "bash" adds scripting best practices).
- **[[EXEC: command]]**: Special syntax for the agent to request terminal execution; pauses for user confirmation unless automation mode is on.
- **SessionLogger**: Logs all user, agent, system, and terminal output to timestamped files in the logs/ directory for audit and replay.
- **ContextManager**: Scans user input for knowledge base triggers and returns embedded contextual content to augment the system prompt.
- **Safety Filter**: Blocks high-risk commands (e.g., `rm -rf /`, fork bombs) in TerminalTool.execute to prevent accidental system damage.

## Naming Conventions
- `UPPER_CASE`: Constants (API_URL, MODEL_TEMPERATURE, LOG_DIR)
- `PascalCase`: Classes (SessionLogger, TerminalTool, ContextManager, AgentLLM)
- `snake_case`: Functions and variables (run_agentic_session, base_system_prompt, specialized_context)
- `_prefix`: Internal methods (_ensure_dir)

## Business Logic Summary
The agent operates in a loop: 
1. Capture user input. 
2. Augment system prompt with relevant knowledge from the static KNOWLEDGE_BASE. 
3. Query the local LLM for a response. 
4. If the response contains an [[EXEC: ...]] block, prompt the user for confirmation (unless in automation mode). 
5. Execute the command safely, log the output, and feed it back into the conversation. 
6. Repeat until user exits.

## Key Design Decisions
- **Single-file simplicity**: All logic in main.py for ease of deployment and understanding.
- **Local LLM focus**: Designed to work with a locally hosted LLM API (e.g., via llama.cpp) for privacy and low latency.
- **User-in-the-loop execution**: By default, requires explicit user confirmation for any command execution, balancing autonomy with safety.
- **Structured logging**: Enables post-session analysis, debugging, and audit trails.
- **Embedded knowledge base**: Allows domain-specific guidance without external dependencies; easily extensible.