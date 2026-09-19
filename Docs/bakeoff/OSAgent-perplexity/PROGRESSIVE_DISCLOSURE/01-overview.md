# OSAgent Overview

## Purpose
AI-driven autonomous remediation system that reduces Mean Time To Recovery (MTTR) by enabling LLMs to monitor infrastructure and execute self-healing actions via the Model Context Protocol (MCP).

## Core Components
1. **main.py**: CLI-based agent orchestrator that interacts with users and LLMs
2. **mcp_self_healing_server.py**: MCP server exposing infrastructure monitoring and remediation tools
3. **Knowledge Base**: Embedded domain-specific context (currently Bash scripting)
4. **Logging System**: Session-based audit trail of all interactions
5. **Terminal Tool**: Safe command execution with safety filters

## Key Features
- Natural language interface for infrastructure queries
- Automated remediation actions (restart, scale_up, flush_cache)
- Context-aware LLM prompting with domain knowledge
- Comprehensive logging for audit and improvement
- Safety mechanisms to prevent dangerous command execution

## Typical Usage Flow
1. User asks about infrastructure status (e.g., "How is db-cluster-01?")
2. Agent queries MCP server for system status
3. MCP returns health data from simulated infrastructure
4. Agent formulates response and may suggest remediation
5. If remediation needed and approved, agent triggers action via MCP
6. All interactions logged for audit trail