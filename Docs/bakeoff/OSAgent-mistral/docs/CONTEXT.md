# Context Meaning Guide

## Overview
This codebase implements an AI-driven autonomous remediation system using the Model Context Protocol (MCP) to bridge Large Language Models (LLMs) with infrastructure monitoring and self-healing capabilities. The system reduces operational toil by enabling AI agents to perform Level 1 support tasks autonomously.

## Domain
The project operates in the intersection of:
- Site Reliability Engineering (SRE)
- DevOps and Platform Engineering
- Artificial Intelligence for IT Operations (AIOps)
- Model Context Protocol (MCP) implementations

## Key Concepts

### Model Context Protocol (MCP)
A standardized way for AI models to interact with external tools, resources, and prompts. In this implementation, MCP enables LLMs to:
- Query infrastructure status through introspection tools
- Trigger remediation actions through action tools
- Access SLA/SLO policies as contextual resources

### Self-Healing Infrastructure
Systems that can automatically detect and resolve common issues without human intervention, reducing Mean Time to Recovery (MTTR).

### Agentic Terminal
An interactive interface where users can communicate with an LLM agent that has access to terminal execution capabilities, with safety controls.

## Glossary

| Term | Definition |
|------|------------|
| MCP | Model Context Protocol - Standard for AI model tool integration |
| SRE | Site Reliability Engineering - Discipline combining software engineering with operations |
| SLI | Service Level Indicator - Quantitative measure of service performance |
| SLO | Service Level Objective - Target value for an SLI |
| MTTR | Mean Time to Recovery - Average time to restore service after failure |
| Toil | Manual, repetitive, automatable operational work |
| LLM | Large Language Model - AI model capable of understanding and generating text |
| FastMCP | Python SDK for implementing MCP servers |

## Key Entities and Relationships

```
[User] ↔ [Agentic Terminal (main.py)] ↔ [LLM]
                                    ↓
                        [Context Manager] → [Knowledge Base]
                                    ↓
                        [Terminal Tool] ↔ [System Commands]
                                    ↓
                        [Session Logger] ↔ [Log Files]

[MCP Server (mcp_self_healing_server.py)]
                                    ↓
              [Infrastructure State] ←→ [Simulated Resources]
                                    ↓
                    [SLA Policy Resource] ←→ [Remediation Tools]
```

## Typical Workflows

### 1. Bash Scripting Assistance
1. User asks about bash scripting concepts
2. ContextManager detects triggers in user input ("bash", "script", etc.)
3. Relevant knowledge from KNOWLEDGE_BASE is injected into system prompt
4. LLM provides expert bash scripting advice with best practices
5. User can request terminal execution of suggested commands

### 2. Infrastructure Self-Healing
1. User queries status of infrastructure components via MCP
2. MCP server returns current state from INFRA_DATABASE
3. User requests remediation action on degraded resource
4. MCP server executes predefined safe action (restart, scale_up, etc.)
5. System updates infrastructure state to reflect remediation

## Design Decisions

### Modular Architecture
Separated concerns into distinct components:
- **main.py**: Handles LLM interaction, logging, and terminal execution
- **mcp_self_healing_server.py**: Provides MCP interface for infrastructure operations
This separation allows independent evolution of agentic capabilities and infrastructure integration.

### Safety-First Approach
Implemented multiple safety layers:
1. TerminalTool blocks high-risk commands (rm -rf/, fork bombs)
2. MCP server uses predefined, safe actions only
3. User confirmation required for command execution (unless MODEL_AUTOMATION enabled)
4. Tool-calling schema prevents arbitrary command injection

### Progressive Knowledge Disclosure
The ContextManager selectively injects domain-specific knowledge only when relevant triggers are detected in user input, preventing context window overflow and maintaining focused responses.

### Extensibility
Designed for easy extension:
- Add new knowledge domains to KNOWLEDGE_BASE in main.py
- Extend MCP server with additional tools/resources
- Hook into real infrastructure APIs (Kubernetes, cloud providers, etc.)