## Domain terms
**MCP** — Model Context Protocol, a standard for connecting LLMs to external tools and data sources.
**SRE** — Site Reliability Engineering, practices for operating large-scale systems.
**MTTR** — Mean Time To Recovery, average time to restore service after failure.
**SLI/SLO** — Service Level Indicator/Objective, metrics for measuring service performance.
**Toil** — Manual, repetitive work that can be automated in SRE context.

## Codebase-specific terms
**AgentLLM** — Class handling communication with local LLM API via HTTP requests.
**ContextManager** — Injects specialized knowledge into LLM context based on user input triggers.
**TerminalTool** — Wrapper for subprocess execution with safety filters for high-risk commands.
**Infrastructure-Self-Healing-Bridge** — MCP server name providing system status and remediation tools.
**KNOWLEDGE_BASE** — Embedded dictionary storing specialized context snippets for different domains.

## Dangerous homonyms
**Agent** — In this codebase, refers to the LLM-powered automation assistant, not a human operator or software agent in distributed systems.
**Tool** — Refers specifically to MCP-exposed functions (get_system_status, trigger_remediation) or TerminalTool class, not general software utilities.
**Server** — Refers to the MCP server (mcp_self_healing_server.py) or LLM API endpoint, not infrastructure servers being monitored.