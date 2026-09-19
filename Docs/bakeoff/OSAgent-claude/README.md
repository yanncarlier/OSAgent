# OSAgent

This project case study is designed to bridge your extensive background in SRE and Platform Engineering with your recent 2026 focus on AI for Business. It frames the code provided previously as a strategic enterprise asset rather than just a script.

Case Study: AI-Powered Terminal Assistant with Safety Controls
Focus: Providing intelligent terminal assistance with built-in safety mechanisms for infrastructure operations.

Executive Summary
In modern enterprise environments, terminal operations often require careful attention to avoid costly mistakes. Leveraging my background in SRE and DevSecOps, I developed a standalone Python application (main.py) that provides AI-powered terminal assistance while maintaining strict safety controls. This system allows users to interact with an AI agent that can help with terminal tasks while preventing dangerous operations.

1. The Challenge: Human Error in Terminal Operations
Problem: Manual terminal operations are prone to errors, especially when dealing with complex infrastructure commands, leading to potential system downtime or data loss.

Impact: Increased operational costs from mistake-related incidents and potential service disruptions.

Goal: Create an intelligent terminal assistant that provides helpful guidance while preventing execution of dangerous commands through built-in safety filters.

2. The Solution: AI-Powered Terminal Agent (main.py)
I developed a standalone Python application (main.py) that combines:
- An AI assistant interface for natural language terminal interactions
- Built-in safety mechanisms to filter dangerous commands
- Session logging for audit trails
- Configurable automation modes

3. Technical Architecture
Language & Framework: Python 3.12+

Deployment: Single-file Python application (main.py) with optional dependencies

Security: Implemented command filtering to prevent dangerous operations (like rm -rf / or fork bombs), rate limiting on command executions, and user confirmation requirements for command execution (unless automation mode is enabled).

4. Key Results
Error Prevention: Automatically blocks dangerous terminal commands through pattern matching.

Audit Capability: Complete session logging to logs/ directory for all interactions.

Flexibility: Configurable operation modes from fully manual to supervised automation.

Strategic Alignment: Successfully applied AI assistance principles to terminal operations while maintaining strict safety controls.

## Installation and Setup

### Prerequisites
- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) (Python package installer and resolver, faster than pip)
- Access to a compatible LLM API endpoint (default: http://10.167.32.1:1234/v1/chat/completions)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OSAgent-claude
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Configure environment variables** (optional)
   Create a `.env` file or set environment variables:
   ```bash
   export OSAGENT_API_URL="http://your-llm-api-endpoint/v1/chat/completions"
   export OSAGENT_MODEL_TEMPERATURE="0.1"
   export OSAGENT_MODEL_AUTOMATION="False"
   export OSAGENT_LOG_DIR="logs"
   export OSAGENT_MAX_COMMAND_EXECUTIONS="50"
   ```

4. **Run the application**
   ```bash
   uv run python main.py
   ```

### Usage
The agent can be used in multiple ways:

**Interactive Mode (default):**
```bash
uv run python main.py
```
- Enter commands or questions at the `User>` prompt
- Use `exit`, `quit`, or `q` to terminate the session

**Single Prompt Mode:**
```bash
uv run python main.py --prompt "your prompt here"
```
- Executes a single prompt and exits
- Useful for automation scripts or one-off tasks

**Loop Mode:**
```bash
uv run python main.py --prompt "your prompt here" --loop
```
- Continuously executes the same prompt in a loop
- Press Ctrl+C to exit the loop
- After each iteration, press Enter to continue or Ctrl+C to exit

All terminal commands are processed through built-in safety filters.
The agent will request confirmation before executing commands unless `OSAGENT_MODEL_AUTOMATION` is set to `true`.

### Safety Features
The agent includes built-in safety mechanisms:
- Command filtering to prevent dangerous operations (blocks patterns like rm -rf / and fork bombs)
- Rate limiting on command executions (configurable via OSAGENT_MAX_COMMAND_EXECUTIONS)
- User confirmation requirement for command execution (unless automation mode is enabled via OSAGENT_MODEL_AUTOMATION=true)
- Session logging to `logs/` directory for complete audit trail of all interactions
- Input length and complexity checks to prevent obfuscation attempts