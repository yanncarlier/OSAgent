# Agent Guide for OSAgent

## How to Progressively Load Context
1. Start with PROGRESSIVE_DISCLOSURE/01-overview.md for high-level understanding
2. Proceed to 02-core.md for business logic and decision flow
3. Continue with 03-data.md for data models and infrastructure state
4. Review 04-api.md for MCP tools and external interfaces
5. Finish with 05-utils.md for helper functions and safety mechanisms

## Token-Efficient Query Patterns
- Use specific resource IDs when querying system status: "What is the status of db-cluster-01?"
- Reference exact file paths:lines when discussing code (e.g., main.py:100)
- Leverage search_tags in TOKEN_SAVER.json for topic-based searches
- Ask about specific components: "How does the logging system work?"

## Common Debugging Paths
1. **No LLM Response**: Check API_URL in main.py:11 and ensure local LLM server is running
2. **Command Execution Failures**: Verify TerminalTool safety filters aren't blocking legitimate commands
3. **Context Not Loading**: Check if user input contains trigger words matching knowledge base entries
4. **MCP Connection Issues**: Ensure mcp_self_healing_server.py is running and accessible
5. **Logging Problems**: Verify LOG_DIR exists and is writable (main.py:14)

## Code Style Conventions
- **Constants**: UPPER_SNAKE_CASE (API_URL, MODEL_TEMPERATURE)
- **Classes**: PascalCase (SessionLogger, TerminalTool, AgentLLM)
- **Functions/Methods**: snake_case (execute, log, get_relevant_context)
- **Variables**: snake_case (user_input, specialized_context)
- **Comments**: Descriptive section headers in ALL CAPS with explanation below
- **String Quotes**: Double quotes for consistency
- **Line Length**: Prefer readability over strict 80-char limit