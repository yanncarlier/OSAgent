# Agent-Specific Cheat Sheet

## Common Patterns

### Knowledge Injection Pattern
When you need to provide domain-specific knowledge to the LLM:
1. Add a new entry to the `KNOWLEDGE_BASE` dictionary in `main.py`
2. Define trigger keywords that will activate this knowledge
3. Provide the specialized content in markdown format
4. The `ContextManager` will automatically inject this knowledge when triggers are detected

### MCP Tool Pattern
When adding new capabilities to the infrastructure server:
1. Create an async function in `mcp_self_healing_server.py`
2. Decorate with `@mcp.tool()`
3. Include a clear docstring describing the tool's purpose
4. Add type hints for parameters and return value
5. Return informative strings that the LLM can act upon

### Safety-First Execution Pattern
For any terminal command execution:
1. Always validate and sanitize inputs (see `TerminalTool.execute()`)
2. Block known dangerous patterns (like `rm -rf /`)
3. Require user confirmation unless automation is explicitly enabled
4. Log all execution attempts and results
5. Provide clear error messages to the LLM

## Do's and Don'ts

### Do:
- **Do** use descriptive names for knowledge domains, triggers, and MCP tools/resources
- **Do** keep knowledge content concise but comprehensive (use markdown for readability)
- **Do** follow the existing code style (indentation, naming conventions)
- **Do** add appropriate error handling and return meaningful messages
- **Do** update both the code and this cheat sheet when adding new patterns
- **Do** leverage the logging system for debugging and audit trails
- **Do** test new knowledge triggers with various user inputs
- **Do** consider edge cases in MCP tool implementations (e.g., non-existent resources)

### Don't:
- **Don't** add overly broad trigger keywords that might cause false positives
- **Don't** make MCP tools perform complex logic that should be handled elsewhere
- **Don't** hardcode values that might need to be configurable (use constants or config)
- **Don't** neglect to update the simulated infrastructure state when it should change
- **Don't** expose internal implementation details in tool/resource responses unnecessarily
- **Don't** forget to handle exceptions in async MCP tools
- **Don't** make assumptions about the LLM's capabilities beyond what's in the prompt

## Pre-formatted Snippets

### Adding a New API-like Endpoint (MCP Tool)
```python
@mcp.tool()
async def new_tool_name(param1: str, param2: int = 10) -> str:
    """
    Brief description of what this tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)
        
    Returns:
        String result that the LLM can use
    """
    # Implementation here
    return f"Result: {param1} with {param2}"
```

### Adding Specialized Knowledge
```python
"DomainExpert": {
    "description": "Expert knowledge in [specific domain]",
    "triggers": ["keyword1", "keyword2", "keyword3"],
    "content": """
    ### SPECIALIZED CONTEXT: [DOMAIN NAME] ###
    - Key point 1
    - Key point 2
    - Best practice: [advice]
    - Common mistake to avoid: [warning]
    """
}
```

### Creating a New MCP Resource
```python
@mcp.resource("config://your-resource")
def get_your_resource() -> str:
    """Provides [specific] context to the LLM."""
    return "Your contextual information here that helps the LLM make better decisions."
```

### Modifying Agent Behavior
```python
# In main.py, adjust these variables:
MODEL_TEMPERATURE = 0.3  # Increase for more creative responses (0.0-1.0)
MODEL_AUTOMATION = True  # Set to True for hands-free operation (use with caution!)
LOG_DIR = "custom_logs"  # Change log directory location
```

## Token-Saving Tips

### For Knowledge Base:
- Use concise trigger words that are highly specific to the domain
- Keep knowledge content focused on what's most likely needed
- Avoid duplicating information across domains
- Consider using abbreviations that the LLM will understand from context

### For MCP Interactions:
- Name tools and resources descriptively but concisely
- Return only necessary information from tools/resources
- Use structured responses when beneficial (e.g., JSON-like strings)
- Leverage the LLM's ability to infer from tool/resource names and descriptions

### For Conversation Management:
- Be aware that long conversations will include all history in the prompt
- Consider implementing conversation summarization for very long sessions
- The system prompt is reused; keep it focused on rules and roles
- Knowledge injection adds to context, so be mindful of total size

## Troubleshooting Common Issues

### Issue: Knowledge not being injected
- Check that trigger keywords match user input (case-insensitive)
- Verify the knowledge domain exists in `KNOWLEDGE_BASE`
- Ensure you've restarted the application after changes

### Issue: MCP tool not responding
- Verify the tool is properly decorated with `@mcp.tool()`
- Check async function definition and await any internal async calls
- Confirm the MCP server is running and connected
- Look for exceptions in server logs

### Issue: Terminal command failing unexpectedly
- Review the safety filter in `TerminalTool.execute()`
- Check command syntax and permissions
- Verify timeout settings (30 seconds by default)
- Examine the logged command output for details

### Issue: LLM not using provided context
- Ensure knowledge is being injected (check logs or add debug prints)
- Verify the system prompt includes the knowledge when relevant
- Consider making knowledge more directly applicable to the user's request
- Check token limits if context becomes too large