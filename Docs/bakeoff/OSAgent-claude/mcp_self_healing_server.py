"""
Filename: mcp_self_healing_server.py
Author: Yann Carlier (Proposal)
Description: A Model Context Protocol (MCP) server that provides an LLM 
with tools to monitor system health and trigger self-healing actions.
Requirements: pip install mcp
"""

import asyncio
import os
import time
from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Configuration from environment variables
HEALTH_CHECK_THRESHOLD_CPU = int(os.getenv("MCP_HEALTH_CPU_THRESHOLD", "80"))
HEALTH_CHECK_THRESHOLD_MEMORY = int(os.getenv("MCP_HEALTH_MEMORY_THRESHOLD", "85"))
REMEDIATION_COOLDOWN = int(os.getenv("MCP_REMEDIATION_COOLDOWN", "300"))  # 5 minutes

# Initialize the FastMCP server
# Reflects your expertise in AI-driven ops and self-healing systems.
mcp = FastMCP("Infrastructure-Self-Healing-Bridge")

# Simulated infrastructure state
INFRA_DATABASE = {
    "web-server-01": {"status": "healthy", "cpu_usage": 12, "memory_usage": 45},
    "db-cluster-01": {"status": "degraded", "cpu_usage": 88, "memory_usage": 92},
    "cache-node-01": {"status": "healthy", "cpu_usage": 5, "memory_usage": 10},
}

# Track last remediation time per resource to prevent rapid-fire actions
LAST_REMEDIATION_TIME = {}

# Actions that require additional confirmation in autonomous mode
SENSITIVE_ACTIONS = ["restart", "scale_up"]

@mcp.tool()
async def get_system_status(resource_id: Optional[str] = None) -> str:
    """
    Retrieves the current health status of infrastructure components.
    If resource_id is provided, returns details for that specific resource.
    Includes health assessment based on configured thresholds.
    """
    if resource_id:
        status = INFRA_DATABASE.get(resource_id, "Resource not found")
        if isinstance(status, dict):
            # Add health assessment
            cpu_usage = status.get("cpu_usage", 0)
            memory_usage = status.get("memory_usage", 0)
            
            is_healthy = (
                cpu_usage < HEALTH_CHECK_THRESHOLD_CPU and 
                memory_usage < HEALTH_CHECK_THRESHOLD_MEMORY
            )
            
            status["health_assessment"] = "healthy" if is_healthy else "degraded"
            status["health_details"] = {
                "cpu_threshold": HEALTH_CHECK_THRESHOLD_CPU,
                "memory_threshold": HEALTH_CHECK_THRESHOLD_MEMORY,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage
            }
            
            return f"Status for {resource_id}: {status}"
        
        return f"Status for {resource_id}: {status}"
    
    # Return full inventory with health assessments
    result = {}
    for key, value in INFRA_DATABASE.items():
        if isinstance(value, dict):
            cpu_usage = value.get("cpu_usage", 0)
            memory_usage = value.get("memory_usage", 0)
            
            is_healthy = (
                cpu_usage < HEALTH_CHECK_THRESHOLD_CPU and 
                memory_usage < HEALTH_CHECK_THRESHOLD_MEMORY
            )
            
            value["health_assessment"] = "healthy" if is_healthy else "degraded"
            value["health_details"] = {
                "cpu_threshold": HEALTH_CHECK_THRESHOLD_CPU,
                "memory_threshold": HEALTH_CHECK_THRESHOLD_MEMORY,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage
            }
        result[key] = value
    
    return f"Full Inventory Status: {result}"

@mcp.tool()
async def trigger_remediation(resource_id: str, action: str) -> str:
    """
    Executes a self-healing action on a degraded resource.
    Supported actions: 'restart', 'flush_cache', 'scale_up'.
    """
    if resource_id not in INFRA_DATABASE:
        return f"Error: {resource_id} does not exist in registry."

    # Check if action requires additional confirmation
    if action in SENSITIVE_ACTIONS:
        # Check cooldown period
        import time
        current_time = time.time()
        if resource_id in LAST_REMEDIATION_TIME:
            time_since_last = current_time - LAST_REMEDIATION_TIME[resource_id]
            if time_since_last < REMEDIATION_COOLDOWN:
                return f"Action {action} on {resource_id} is in cooldown. Please wait {int(REMEDIATION_COOLDOWN - time_since_last)} seconds."
        
        # In a real implementation, this would trigger a confirmation request
        # For now, we'll log that confirmation would be required
        return f"Action {action} on {resource_id} requires confirmation due to sensitivity. In autonomous mode with confirmation enabled, this would prompt for approval."

    # Logic for self-healing automation
    if action == "restart":
        INFRA_DATABASE[resource_id]["status"] = "healthy"
        INFRA_DATABASE[resource_id]["cpu_usage"] = 10
        LAST_REMEDIATION_TIME[resource_id] = time.time()
        return f"Successfully executed {action} on {resource_id}. System is now healthy."
    
    elif action == "scale_up":
        # In a real implementation, this would interact with cloud provider APIs
        LAST_REMEDIATION_TIME[resource_id] = time.time()
        return f"Scaling signal sent to Cloud Provider for {resource_id}."
    
    elif action == "flush_cache":
        # For cache nodes, we might reset memory usage or similar
        if resource_id in INFRA_DATABASE:
            INFRA_DATABASE[resource_id]["memory_usage"] = max(10, INFRA_DATABASE[resource_id]["memory_usage"] - 50)
        return f"Cache flush initiated on {resource_id}."
    
    return f"Action {action} initiated, but pending verification."

@mcp.resource("config://sla-policy")
def get_sla_policy() -> str:
    """Provides the LLM with context on SLO/SLI thresholds."""
    return "SLA Policy: CPU > 80% for 5 mins requires 'scale_up' or 'restart'."

if __name__ == "__main__":
    # Running the server via STDIO for LLM integration (like Claude Desktop)
    print("Starting MCP Self-Healing Server...")
    mcp.run(transport='stdio')