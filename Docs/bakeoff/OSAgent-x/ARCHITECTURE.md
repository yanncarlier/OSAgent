# OSAgent Architecture Overview

## System Purpose
OSAgent is an AI-driven autonomous system administration agent that provides intelligent assistance for Ubuntu 24.04 LTS systems through natural language interaction. It enables users to perform system administration tasks through an intelligent agent that understands natural language commands.

## Core Components

### 1. Agentic Terminal Interface (`main.py`)
- **Role**: Primary user interface for intelligent agent interaction
- **Technology**: Python with custom agent orchestration
- **Responsibilities**:
  - Accept user input and route to LLM
  - Manage conversation history and logging
  - Provide contextual knowledge injection
  - Execute terminal commands via secure tool interface
  - Handle command approval workflow

## Key Design Decisions

### Security Model
- **Command Filtering**: Blocks high-risk commands like `rm -rf /`
- **User Approval**: Optional manual confirmation for command execution
- **Sandboxed Execution**: All commands run in subprocess with timeout

### Knowledge Management
- **Embedded Knowledge Base**: Specialized contexts (e.g., BashScriptMaster)
- **Trigger-Based Disclosure**: Context injection based on user input keywords
- **Progressive Context Building**: System prompt augmented with relevant knowledge

### Communication Patterns
- **Human-in-the-Loop**: Default requires user confirmation for actions
- **Automation Mode**: Optional fully autonomous operation via flag
- **Structured Tool Use**: Standardized `[[EXEC: <command>]]` syntax
- **Session Logging**: Complete audit trail of all interactions

## Data & Control Flow

```
User Input
    ↓
[main.py] → Context Manager (knowledge injection)
    ↓
[main.py] → Agent LLM (via API)
    ↓
LLM Response → [[EXEC: cmd]] parsing
    ↓
[main.py] → Terminal Tool (command execution)
    ↓
Execution Results → Back to LLM for analysis
```

## Architecturally Significant Files

1. `main.py` - Core agent orchestration and terminal interface
2. `SessionLogger` class (in main.py) - Centralized logging system
3. `ContextManager` class (in main.py) - Knowledge retrieval system
4. `AgentLLM` class (in main.py) - LLM communication abstraction
5. `TerminalTool` class (in main.py) - Secure command execution layer