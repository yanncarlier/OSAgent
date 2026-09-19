# OSAgent

This project case study is designed to bridge your extensive background in SRE and Platform Engineering with your recent 2026 focus on AI for Business. It frames the code provided previously as a strategic enterprise asset rather than just a script.

Case Study: AI-Driven Autonomous Terminal Agent
Focus: Reducing Toil through intelligent command execution and self-healing infrastructure.

## Development Setup

This project uses UV for Python package management and relies on a virtual environment for isolated dependencies.

### Prerequisites
- UV installed (https://docs.astral.sh/uv/)
- Python 3.12+

### Installing UV
Follow the official installation guide: https://docs.astral.sh/uv/#installation

On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Verify installation:
```bash
uv --version
```

### Installation Steps
1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd OSAgent
   ```

2. **Install dependencies using UV**:
   ```bash
   uv sync
   ```
   This creates a virtual environment at `.venv` and installs all required packages.

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate   # On Unix/macOS
   .venv\Scripts\activate      # On Windows
   ```

4. **Run the application**:
   - **Interactive mode** (default):
     ```bash
     uv run python main.py
     ```
     Or after activating the environment:
     ```bash
     python main.py
     ```
   - **Single prompt mode**:
     ```bash
     uv run python main.py -p "your prompt here"
     ```
     Example:
     ```bash
     uv run python main.py -p "Check the current disk usage"
     ```
   - **Loop mode** (for continuous agentic behavior):
     ```bash
     uv run python main.py -l "your prompt here"
     ```
     Example:
     ```bash
     uv run python main.py -l "Monitor system load and report any issues"
     ```
     The agent will execute the prompt repeatedly with a 5-second delay between iterations.
     Press Ctrl+C to exit loop mode.

5. **Updating dependencies**:
   If you modify `pyproject.toml` or `uv.lock`, run:
   ```bash
   uv sync
   ```

Executive Summary
In modern enterprise environments, the "Mean Time to Recovery" (MTTR) is often delayed by human intervention during routine failures. Leveraging my background in SRE and DevSecOps, I developed an intelligent terminal agent that allows Large Language Models (LLMs) to securely execute system administration commands with built-in safety checks, effectively moving toward "Zero-Toil" operations.

1. The Challenge: The "Human-in-the-Middle" Bottleneck
Problem: Traditional system administration requires an engineer to manually investigate issues and execute remediation commands.

Impact: Increased operational costs and potential SLA breaches during off-hours.

Goal: Create a secure, auditable layer where an AI agent can perform routine system administration tasks autonomously with safety validation.

2. The Solution: Intelligent Terminal Agent
I engineered a standalone Python-based agent that exposes system administration capabilities to an AI assistant with embedded safety checks:

Introspection Tool: The AI can query the live state of system resources (CPU, memory, disk, services).

Remediation Tool: The AI can execute predefined, safe system administration commands like checking service status, viewing logs, or managing files based on real-time system data.

3. Technical Architecture
Language & Framework: Python, with requests library for LLM communication and subprocess for command execution.

Deployment: Runs as a standalone script, can be containerized via Docker, integrated into existing automation pipelines.

Security: Implements multi-layer safety validation including dangerous command blocking, safe command whitelisting, and user confirmation requirements.

4. Key Results
Toil Reduction: Automates routine system administration tasks through AI-guided command execution.

Scalability: The modular design allows for deployment across different Linux environments.

Strategic Alignment: Successfully applied AI principles to reduce manual system administration toil.