## Terminal Tool

**Role:** Executes shell commands with safety filtering for high-risk operations.
**Entry point:** main.py:TerminalTool class
**Public API:** 
  execute(command: str) -> str — Runs shell command with safety checks and returns output
**Internal structure:** Static utility class that wraps subprocess.run with safety filtering. Blocks specific high-risk commands (like rm -rf / and fork bombs) before execution. Captures stdout, stderr, and return code to format results.
**State / side effects:** Stateless utility - owns no persistent state. Side effect is executing the requested command on the host system (subject to safety filters).
**Error handling contract:** 
  - Returns error string for blocked high-risk commands
  - Returns formatted error output for non-zero exit codes (includes stderr)
  - Returns timeout message if command exceeds 30 seconds
  - Returns exception message for other execution failures
  - Never throws exceptions - all errors returned as strings
**Common pitfalls:** 
  - Safety filter only blocks specific known dangerous commands, not all potentially harmful ones
  - Command execution happens on the host where the agent runs, not in a sandbox
  - 30-second timeout may be too short for some legitimate operations
  - Output may be truncated if very large (limited by subprocess communication)
**Tests:** No explicit tests. Safety filtering can be verified by attempting blocked commands. Normal command execution can be verified by running simple commands like "ls" or "echo".