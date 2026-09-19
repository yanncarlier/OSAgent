## MCP Server

**Role:** Exposes infrastructure introspection and remediation tools via MCP protocol.
**Entry point:** mcp_self_healing_server.py
**Public API:** 
  get_system_status(resource_id: Optional[str]) -> str — Returns health status of infrastructure components
  trigger_remediation(resource_id: str, action: str) -> str — Executes self-healing actions on resources
  get_sla_policy() -> str — Provides SLA/SLO context to LLM (exposed as MCP resource)
**Internal structure:** Organized around a FastMCP server instance with three tool functions and one resource function. Uses an in-memory dictionary (INFRA_DATABASE) to simulate infrastructure state. Does not persist state between runs.
**State / side effects:** Owns and modifies INFRA_DATABASE (simulated infrastructure state). When trigger_remediation is called with "restart" action, it modifies the status and cpu_usage fields in INFRA_DATABASE. No external side effects - all state is lost when server stops.
**Error handling contract:** 
  - Returns descriptive error strings for invalid resource IDs or actions (does not throw exceptions)
  - get_system_status returns "Resource not found" message for unknown IDs
  - trigger_remediation returns error message if resource_id not in INFRA_DATABASE
  - All functions are async but designed to work with FastMCP's stdio transport
**Common pitfalls:** 
  - Mistaking the simulated INFRA_DATABASE for real infrastructure state
  - Not recognizing that remediation actions only update the simulation, not real systems
  - Overlooking that the server must be running separately for the agent to access its tools
  - Missing that the SLA policy resource is accessed via MCP resource protocol, not as a tool
**Tests:** No explicit test files. Functionality can be verified by running the server and testing MCP tool calls directly or through the agent interface.