# Utilities and Helpers

## Terminal Tool (main.py:56-73)
Provides safe command execution with safety filters.
- **Method**: `execute(command: str) -> str`
- **Safety**: Blocks commands containing:
  - `rm -rf /` (attempt to delete root)
  - `:(){ :|:& };:` (fork bomb)
- **Timeout**: 30 seconds for command execution
- **Return**: 
  - Success: Command output or "Success (no output). Stderr: {errors}"
  - Error: "Execution Error (Exit Code {code}): {stderr}" or timeout/exception messages

## Session Logger (main.py:34-52)
Handles file-based logging for audit trails.
- **Method**: `log(sender: str, message: str)`
- **Log Format**: 
  ```
  [timestamp] SENDER:
  message
  ----------------------------------------
  ```
- **File Naming**: `session_{timestamp}.log` in LOG_DIR (default: "logs")
- **Directory Creation**: Automatically creates LOG_DIR if missing

## Context Manager (main.py:77-86)
Manages domain-specific knowledge injection.
- **Method**: `get_relevant_context(user_input: str) -> str`
- **Process**: 
  1. Converts input to lowercase
  2. Checks each knowledge base entry for trigger words
  3. Concatenates matching content with separator
- **Current Knowledge Base**: Only "BashScriptMaster" entry

## Configuration Constants (main.py:10-15)
- `API_URL`: Local LLM endpoint (http://localhost:1234/v1/chat/completions)
- `MODEL_TEMPERATURE`: 0.1 (low randomness for consistent outputs)
- `MODEL_AUTOMATION`: False (requires user confirmation for command execution)
- `LOG_DIR`: "logs" (directory for session logs)