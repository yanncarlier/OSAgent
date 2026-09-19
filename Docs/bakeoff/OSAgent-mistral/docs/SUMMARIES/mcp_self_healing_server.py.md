# mcp_self_healing_server.py Summary

## Purpose
Implements a Model Context Protocol (MCP) server that provides LLMs with tools to monitor system health and trigger self-healing actions on infrastructure components.

## Key Components

### Imports & Initialization (Lines 1-15)
- Uses FastMCP SDK for MCP server implementation
- Sets up server instance with name "Infrastructure-Self-Healing-Bridge"
- Includes descriptive docstring explaining purpose and requirements

### Simulated Infrastructure State (Lines 18-22)
- `INFRA_DATABASE`: Dictionary simulating infrastructure component states
- Contains sample resources: web-server-01, db-cluster-01, cache-node-01
- Each resource has status, cpu_usage, and memory_usage metrics

### MCP Tools

#### get_system_status (Lines 24-34)
- Retrieves health status of infrastructure components
- Optional `resource_id` parameter for specific resource queries
- Returns formatted string with status information

#### trigger_remediation (Lines 36-55)
- Executes self-healing actions on degraded resources
- Supported actions: 'restart', 'flush_cache', 'scale_up'
- Validates resource existence before action execution
- Updates infrastructure state for 'restart' action
- Returns status messages indicating action results

### MCP Resources

#### get_sla_policy (Lines 56-60)
- Provides SLA/SLI context to the LLM
- Returns string describing CPU threshold policy for scaling/restart actions
- Decorated with `@mcp.resource("config://sla-policy")`

## Data Flow
1. MCP client (LLM) connects to server via stdio transport
2. LLM invokes tools/resources through standard MCP protocol
3. Tools access/modify `INFRA_DATABASE` to simulate infrastructure operations
4. Resources provide contextual information to enhance LLM reasoning
5. All interactions follow MCP specification for tool/resource invocation

## Token-Saving Tips
- Tool and resource names are descriptive but concise
- Docstrings provide clear usage information for LLMs
- Simulated state keeps responses predictable and compact
- Consider adding more specific resources for different infrastructure aspects
- Error messages are informative but brief to conserve tokens