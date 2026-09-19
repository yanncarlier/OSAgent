## Main Orchestrator

**Role:** Coordinates agent session, handles user input, manages tool execution and LLM interaction loops.
**Entry point:** main.py
**Public API:** 
  run_agentic_session(): None — Main function that orchestrates the entire agent session
**Internal structure:** Organized around a main loop that processes user input, gets LLM responses, handles tool execution requests, and maintains conversation history. Uses helper classes for logging, tool execution, context management, and LLM communication. Does not contain domain-specific logic itself.
**State / side effects:** Owns session state (conversation history), coordinates logging via SessionLogger, triggers tool execution via TerminalTool, manages knowledge injection via ContextManager, and handles LLM communication via AgentLLM. Persists conversation logs to files in logs/ directory.
**Error handling contract:** 
  - TerminalTool.execute() returns error strings for failed commands (does not throw)
  - AgentLLM.chat() returns error strings for API failures (does not throw)
  - SessionLogger.log() may throw IOError if logging fails (not caught in main flow)
  - Main loop catches KeyboardInterrupt for graceful shutdown
**Common pitfalls:** 
  - Forgetting that MODEL_AUTOMATION flag changes confirmation behavior (set to True for fully automated mode)
  - Not realizing that conversation history is maintained in both `history` and `messages` variables with different purposes
  - Missing that the EXEC pattern matching uses regex with DOTALL flag to capture multiline commands
**Tests:** No explicit test files. Logic is implicitly tested through manual interaction. Logging can be verified by examining logs/ directory after sessions.