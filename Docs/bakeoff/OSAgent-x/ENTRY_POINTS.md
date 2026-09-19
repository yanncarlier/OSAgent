# Entry Points

## Primary Starting Points

### 1. `main.py:run_agentic_session()`
- **Purpose**: Main agent orchestration loop
- **Why start here**: Shows the complete interaction flow from user input to command execution
- **Key aspects**: 
  - Conversation history management
  - Knowledge injection via ContextManager
  - LLM communication through AgentLLM
  - Command parsing and execution with TerminalTool
  - Session logging
- **Tokens to understand**: ~450 (entire file)

### 2. `main.py:SessionLogger`
- **Purpose**: Centralized logging system
- **Why start here**: Critical for audit trails and debugging agent behavior
- **Key aspects**:
  - Timestamped log entries with sender identification
  - Automatic log directory creation
  - Session-based log files
  - Consistent log entry format
- **Tokens to understand**: ~50 (class definition)

### 3. `main.py:ContextManager.get_relevant_context()`
- **Purpose**: Knowledge injection mechanism
- **Why start here**: Shows how the system augments LLM prompts with specialized knowledge
- **Key aspects**:
  - Keyword-triggered context retrieval
  - Embedded knowledge base structure
  - Progressive context building
- **Tokens to understand**: ~30 (method definition)

### 4. `main.py:TerminalTool.execute()`
- **Purpose**: Secure command execution layer
- **Why start here**: Implements security boundaries and safe command execution
- **Key aspects**:
  - High-risk command filtering
  - Subprocess execution with timeout
  - Structured output/error handling
  - Safety net for LLM-generated commands
- **Tokens to understand**: ~40 (method definition)

## Secondary Starting Points (for deeper understanding)

### 5. `main.py:AgentLLM.chat()`
- **Purpose**: LLM communication abstraction
- **Relevance**: Understands how the system interacts with the LLM API
- **Tokens**: ~20

### 6. `main.py` knowledge base structure (`KNOWLEDGE_BASE`)
- **Purpose**: Domain-specific knowledge storage
- **Relevance**: See how specialized contexts are organized and triggered
- **Tokens**: ~15