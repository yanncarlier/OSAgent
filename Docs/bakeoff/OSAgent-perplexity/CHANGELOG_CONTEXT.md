# Changelog Context

## Recent Releases

### v0.4.0 (Current) - Feature Complete
- Added MCP server for infrastructure self-healing capabilities
- Implemented agentic terminal with LLM integration
- Created knowledge base system for contextual assistance
- Added comprehensive logging for audit trails

### v0.3.0 - Agentic Foundation
- Core agent loop with user interaction
- Basic command execution via TerminalTool
- Session logging system
- Initial knowledge base implementation

### v0.2.0 - Infrastructure Simulation
- Mock infrastructure database (INFRA_DATABASE)
- Basic system status querying
- Remediation action framework

## Breaking Changes
- v0.4.0: Changed API endpoint format for LLM communication
- v0.3.0: Modified logging directory structure

## Migration Guides
- To v0.4.0: Update API_URL in main.py to match your LLM endpoint
- To v0.3.0: Ensure LOG_DIR exists or update path in main.py:14
- General: Install required dependencies via `pip install -r requirements.txt`

## Key Improvements by Version
**v0.4.0**: Added MCP protocol for standardized tool exposure, enabling plug-and-play LLM infrastructure integration.

**v0.3.0**: Established core agent architecture with safety mechanisms and context-aware prompting.

**v0.2.0**: Created foundational infrastructure simulation and remediation framework.