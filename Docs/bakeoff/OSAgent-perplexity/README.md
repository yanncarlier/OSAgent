# OSAgent

This project is a single-file Python script designed to demonstrate AI-driven autonomous terminal assistance with built-in safety mechanisms. It frames the code as a strategic asset for reducing operational toil in infrastructure management.

Case Study: AI-Driven Autonomous Terminal Agent
Focus: Reducing Toil through Secure AI-Assisted Infrastructure Operations.

Executive Summary
In modern enterprise environments, routine infrastructure tasks often require manual intervention, leading to increased operational costs and potential delays. This script demonstrates how an AI agent can securely interact with a local terminal to perform routine operations while maintaining strict safety controls. The agent combines language model capabilities with a fortified terminal interface to enable safe, auditable infrastructure operations.

1. The Challenge: Manual Intervention Bottleneck
Problem: Routine infrastructure tasks (service restarts, log checks, system diagnostics) require engineers to manually execute commands, causing context switching and potential delays.

Impact: Increased operational costs from repetitive tasks and potential delays in incident response during off-hours.

Goal: Create a secure, auditable assistant where an AI agent can perform routine infrastructure tasks autonomously with human oversight.

2. The Solution: Secure AI Terminal Agent
I engineered a standalone Python script (main.py) that provides an AI assistant with secure terminal access through multiple safety layers:

Introspection Capability: The AI can query system status and gather information through controlled terminal commands.

Remediation Capability: The AI can execute predefined safe actions like service restarts or system checks based on real-time needs.

3. Technical Architecture
Language & Framework: Python 3.12+ with standard library components (subprocess, requests, json, etc.)

Deployment: Single file execution (main.py) with dependency management via UV/PIP.

Security: Multi-layered protection including:
- Command validation and blacklisting of dangerous patterns
- Whitelist-based restrictions in automation mode
- Rate limiting and confirmation requirements for automated operations
- Separate security audit logging for all operations

4. Key Results
Toil Reduction: Demonstrates automation potential for routine infrastructure tasks through AI-assisted terminal operations.

Safety-First Design: Implements comprehensive security controls to prevent unsafe command execution while enabling useful AI assistance.

Strategic Alignment: Shows practical application of AI for infrastructure operations with strong security boundaries.

## Installation and Setup

1. **Prerequisites**
    - Python 3.12+
    - UV package manager (https://docs.astral.sh/uv/)
    - Access to a language model API (default configured for http://10.167.32.1:1234/v1/chat/completions)

2. **Installation Steps**
    ```bash
    # Save main.py to your desired location
    # Install dependencies using UV
    uv pip install -r requirements.txt

    # (Optional) Configure LLM API endpoint
    # Edit the API_URL in main.py if your LLM service is running on a different endpoint
    ```

3. **Running the Agent**
   ```bash
   # Interactive mode (default)
   python main.py
   
   # Run with an initial prompt, then continue interactively
   python main.py --prompt "Check system status and list running services"
   
   # Run a specific prompt repeatedly in a loop (useful for monitoring)
   python main.py --loop-prompt "Check disk usage and memory consumption" --interval 300
   ```

4. **Configuration**
    - **Automation Mode**: To enable automation mode (where the agent can execute commands without explicit confirmation for each command), set `MODEL_AUTOMATION = True` in `main.py`. Use with caution and review the safety mechanisms in place.
    - **Logging**: Session logs are stored in the `logs/` directory. Security events are logged to separate security log files.
    - **Safety Mechanisms**: The agent includes a terminal tool with command validation to prevent dangerous operations. Review the TerminalTool class in `main.py` for details on allowed and blocked commands.

5. **Notes**
    - Ensure your language model service is running and accessible at the configured API_URL before starting the agent.
    - The agent is designed for use in trusted environments. Review the security implications before deploying in production.
    - This is a single-file implementation - all code is contained in `main.py`.
    - For containerized deployment, consider creating a Dockerfile based on this script and its dependencies.

---
*Updated with installation instructions on 2026-03-23*