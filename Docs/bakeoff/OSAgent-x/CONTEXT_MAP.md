# OSAgent Context Map

## Domain Concepts & Ubiquitous Language

### Core Concepts
- **Intelligent System Administration Agent**: An autonomous agent that understands natural language requests and executes appropriate system administration commands on Ubuntu 24.04 LTS systems.
- **Level 1 (L1) Support**: Routine IT tasks like service restarts, cache flushes, and basic diagnostics that follow deterministic playbooks.
- **Mean Time to Recovery (MTTR)**: Key metric measuring average time to restore service after failure; primary target for reduction.
- **Toil**: Manual, repetitive, automatable work that scales linearly with traffic/service size (e.g., manual service restarts).

### Technical Primitives
- **Knowledge Base Entry**: Specialized context package with:
  - `description`: Human-readable purpose
  - `triggers`: Keywords that activate context injection
  - `content`: Specialized instructions appended to system prompt
- **Tool Use Signature**: Standardized LLM command format `[[EXEC: <command>]]` for terminal execution requests
- **Session Log Entry**: Timestamped record with sender (USER/AGENT/SYSTEM/TERMINAL_OUTPUT) and message content

## Important Type Aliases & Domain Primitives

### Data Structures
```python
# Knowledge base (main.py)
KNOWLEDGE_BASE: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "BashScriptMaster": {
        "description": "...",
        "triggers": ["bash", "shell", ...],
        "content": "..."
    }
}
```

### Key Classes & Their Responsibilities
- `SessionLogger`: Manages file-based audit trails of all agent interactions
- `TerminalTool`: Executes shell commands with safety filtering and timeout
- `ContextManager`: Retrieves relevant knowledge base entries based on user input
- `AgentLLM`: Abstracts communication with the LLM API endpoint

## Anti-patterns & Deliberate Exclusions

### Security Boundaries
- **NO arbitrary shell execution**: Commands filtered against high-risk patterns (e.g., `rm -rf /`)
- **NO persistent agent state**: Conversation history limited to current session (no cross-session memory)
- **NO secret storage**: Credentials/configuration must be provided externally (not in code)

### Design Constraints
- **NO automatic remediation by default**: Requires explicit user approval (`MODEL_AUTOMATION=False`)
- **NO unbounded context growth**: Knowledge injection limited to triggered entries only
- **NO complex orchestration**: Agent responses are focused on single interactions; no workflow chaining or conditional logic

### Operational Principles
- **NO silent failures**: All tool executions return structured output/error messages
- **NO unbounded command execution**: 30-second timeout on all terminal commands
- **NO privileged operations**: Runs with user-level permissions; no sudo/escalation by design