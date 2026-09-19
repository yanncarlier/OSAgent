## What this system does
OSAgent is an AI-powered automation agent that enables LLMs to perform infrastructure monitoring and self-healing actions through the Model Context Protocol (MCP), reducing manual toil in SRE operations by providing secure, contextualized access to system telemetry and remediation capabilities.

## Primary user flows
1. User queries system status → MCP server returns infrastructure health data from simulated database
2. User identifies degraded resource → MCP server executes remediation action (restart/scale_up/flush_cache)  
3. User requests bash scripting help → Agent injects specialized knowledge from embedded KNOWLEDGE_BASE
4. User executes terminal command → TerminalTool runs command with safety filtering and logs output
5. User ends session → SessionLogger saves conversation history to timestamped log file

## Tech stack
Runtime — Python 3.12, chosen for broad compatibility and rich ecosystem
Framework — FastMCP for MCP server implementation, requests for LLM API communication
Persistence — In-memory dictionaries (INFRA_DATABASE, KNOWLEDGE_BASE) for simplicity
Key libs — mcp, requests, subprocess for core functionality; no external persistence layer

## Where to start reading
main.py — Contains the primary agent orchestrator with logging, tool use, and LLM interaction loops
mcp_self_healing_server.py — Implements the MCP server exposing introspection and remediation tools
project_manifest.md — Documents the project vision, features, and professional alignment
README.md — Provides executive summary and technical architecture overview
logs/ — Directory where session logs are stored (examining these reveals usage patterns)

## What is intentionally NOT here
Actual cloud/provider integrations (Kubernetes, Proxmox, AWS) — designed as extensible hooks
Real infrastructure monitoring — uses simulated state for demonstration purposes
Persistent storage — all state is in-memory and lost on restart
Authentication/authorization — assumes trusted environment for MCP-LLM communication