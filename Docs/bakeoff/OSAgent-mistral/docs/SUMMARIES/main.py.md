# main.py Summary

## Purpose
Main entry point for the agentic terminal interface that enables LLMs to interact with system terminals while providing contextual knowledge and safety controls.

## Key Components

### Configuration (Lines 11-15)
- `API_URL`: Endpoint for LLM API communication
- `MODEL_TEMPERATURE`: Controls randomness in LLM responses (0.1 = deterministic)
- `MODEL_AUTOMATION`: Toggle for automatic command execution without user confirmation
- `LOG_DIR`: Directory for storing session logs

### Embedded Knowledge Base (Lines 17-30)
- Contains specialized knowledge domains (currently only "BashScriptMaster")
- Each domain has description, trigger keywords, and content
- Knowledge is selectively injected into LLM context based on user input

### SessionLogger Class (Lines 34-53)
- Handles timestamped logging of all interactions
- Creates log files in specified directory
- Logs sender, message, and timestamps with separators

### TerminalTool Class (Lines 56-73)
- Executes shell commands with safety controls
- Blocks high-risk commands (rm -rf/, fork bombs)
- Returns formatted output/error messages
- Includes timeout handling (30 seconds)

### ContextManager Class (Lines 77-86)
- Determines relevant knowledge based on user input triggers
- Returns concatenated content from matching knowledge domains
- Simple keyword matching algorithm

### AgentLLM Class (Lines 87-97)
- Wrapper for LLM API communication
- Handles request formatting and error handling
- Uses configured API URL and temperature settings

### Orchestrator Function (Lines 100-169)
- Main interaction loop: run_agentic_session()
- Sets up terminal, logger, and base system prompt
- Processes user input, injects context, gets LLM responses
- Handles command execution requests with user confirmation
- Maintains conversation history

## Data Flow
1. User input → ContextManager (checks for knowledge triggers)
2. User input + relevant knowledge → AgentLLM (gets response)
3. LLM response → Regex check for [[EXEC: command]] pattern
4. If EXEC found → User confirmation → TerminalTool execution
5. All interactions logged via SessionLogger
6. Results fed back into conversation for continued interaction

## Token-Saving Tips
- Knowledge base only injects relevant content based on triggers
- System prompt is concise but includes essential rules
- Conversation history maintained but could be truncated for very long sessions
- Consider implementing knowledge domain prioritization for better relevance