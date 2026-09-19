# Core Business Logic

## Agent Decision Flow (main.py:100-170)

### Main Loop
1. Accept user input
2. Log interaction
3. Retrieve relevant context from knowledge base
4. Construct system prompt with active knowledge
5. Send conversation history to LLM
6. Process LLM response for execution commands
7. If `[[EXEC: command]]` found:
   - Request user confirmation (unless automation enabled)
   - Execute command via TerminalTool
   - Log execution and output
   - Append output to conversation for LLM analysis
8. Repeat until break condition

### Context Management (main.py:77-86)
- Scans user input for trigger words
- Returns relevant knowledge base content if triggers match
- Currently only supports "BashScriptMaster" context
- Triggers: ["bash", "shell", "script", "loop", "variable", "pipe", "sed", "awk", "grep", "automation"]

### LLM Interaction (main.py:87-96)
- Sends messages to local LLM API endpoint
- Configurable temperature (0.1 for low randomness)
- Stop sequences to prevent role confusion
- Error handling for connection issues

### Safety Mechanisms
- TerminalTool blocks high-risk commands (rm -rf /, fork bombs)
- User confirmation required for command execution
- Timeout limits (30 seconds for commands, 120 for LLM)
- Input validation and sanitization