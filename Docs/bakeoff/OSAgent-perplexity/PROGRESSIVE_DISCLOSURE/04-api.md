# API and MCP Tools

## MCP Server Tools (mcp_self_healing_server.py)

### get_system_status(resource_id: Optional[str] = None) -> str
- **Lines**: 24-34
- **Description**: Retrieves health status of infrastructure components.
- **Parameters**: 
  - resource_id (optional): Specific component to query (e.g., "db-cluster-01")
- **Returns**: 
  - If resource_id provided: Status string for that component
  - If not provided: Full infrastructure status dictionary
- **MCP Decorator**: @mcp.tool()

### trigger_remediation(resource_id: str, action: str) -> str
- **Lines**: 36-55
- **Description**: Executes self-healing action on a degraded resource.
- **Parameters**:
  - resource_id: Target component (must exist in INFRA_DATABASE)
  - action: One of 'restart', 'flush_cache', 'scale_up'
- **Returns**: 
  - Success/error message based on action execution
  - For 'restart': Updates INFRA_DATABASE to healthy state
  - For 'scale_up': Returns scaling signal message
  - For 'flush_cache': Returns pending verification message
- **MCP Decorator**: @mcp.tool()

### get_sla_policy() -> str
- **Lines**: 56-60
- **Description**: Provides SLA/SLI threshold context to LLM.
- **Returns**: String describing CPU threshold policy
- **MCP Decorator**: @mcp.resource("config://sla-policy")

## External Interfaces

### LLM API Endpoint
- **URL**: http://localhost:1234/v1/chat/completions
- **Used by**: AgentLLM.chat() in main.py:87-96
- **Method**: POST with JSON payload
- **Payload**: 
  ```json
  {
    "messages": [...],
    "temperature": 0.1,
    "stream": false,
    "stop": ["User>", "System:"]
  }
  ```

### Terminal Tool Interface
- **Class**: TerminalTool (main.py:56-73)
- **Method**: execute(command: str) -> str
- **Safety**: Blocks high-risk commands (rm -rf /, fork bombs)
- **Timeout**: 30 seconds for command execution
- **Return**: Command output or error message