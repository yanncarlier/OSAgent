## Logging System

**Role:** Handles file-based logging for all agent communications with timestamps.
**Entry point:** main.py:SessionLogger class
**Public API:** 
  __init__(directory: str) -> SessionLogger — Initializes logger with log directory
  log(sender: str, message: str) -> None — Writes formatted log entry to session file
**Internal structure:** Simple class that creates timestamped log files in the specified directory. Each log entry includes a timestamp, sender identifier, and the message content separated by dashes. Does not use any external logging frameworks.
**State / side effects:** Owns the log file path and ensures the log directory exists. Appends to log files without rotating or limiting size. No external side effects beyond file system writes.
**Error handling contract:** 
  - __init__ may raise OSError if directory cannot be created
  - log() may raise IOError if file cannot be written to
  - Errors are not caught within the class - they propagate to the caller
**Common pitfalls:** 
  - Log files grow indefinitely without rotation (not an issue for demo sessions)
  - All logs for a session go to a single file named by start timestamp
  - No log levels or filtering capabilities
**Tests:** No explicit tests. Logging output can be verified by checking files in the logs/ directory after running the agent.