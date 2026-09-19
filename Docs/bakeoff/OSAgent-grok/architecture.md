# Software Architecture

## Overview
Single-file Python application implementing an agentic terminal assistant that interacts with a local LLM API.

## Module Dependencies
- Standard Library: os, re, json, subprocess, sys, datetime, typing
- External: requests (for HTTP API calls)

## Key Patterns
- **Context Injection**: Knowledge base triggers add specialized context to system prompts
- **Command Execution Loop**: Agent thinks, user confirms EXEC, executes, feeds output back
- **Session Logging**: All interactions timestamped and stored in log files
- **Safety Filtering**: Blocks high-risk commands (rm -rf /, fork bombs)

## Entry Point
`main.py`: Starts `run_agentic_session()` when executed directly.

## Data Flow
1. User input → ContextManager adds relevant knowledge
2. Combined prompt → AgentLLM (local API) → Response
3. Response parsed for [[EXEC: command]] → User confirmation → TerminalTool execution
4. Output fed back into conversation history → Loop continues
5. All interactions logged via SessionLogger

## Configuration
- API_URL: Local LLM endpoint (default: http://localhost:1234/v1/chat/completions)
- MODEL_TEMPERATURE: 0.1 (low for deterministic outputs)
- MODEL_AUTOMATION: False (requires user confirmation for execution)
- LOG_DIR: "logs/" directory for session logs