# OSAgent

This project case study is designed to bridge your extensive background in SRE and Platform Engineering with your recent 2026 focus on AI for Business. It frames the code provided previously as a strategic enterprise asset rather than just a script.

Case Study: AI-Driven Autonomous Ubuntu 24.04 System Administration Agent
Focus: Reducing Toil through AI-powered system administration and remediation.

Executive Summary
In modern enterprise environments, the "Mean Time to Recovery" (MTTR) is often delayed by human intervention during routine failures. Leveraging my background in SRE and DevSecOps, I developed an AI agent that can securely interface with system telemetry and execute remediation scripts, effectively moving toward "Zero-Toil" operations.

## Key Improvements

1. **Enhanced Safety Filtering**: Improved terminal command validation with comprehensive pattern matching for Ubuntu 24.04 LTS system administration
2. **Ubuntu 24.04 Specific Knowledge Base**: Added specialized context for Ubuntu 24.04 system administration, monitoring, and best practices
3. **Modern Python Workflow**: Uses `uv` for package management and `.venv` virtual environment for reproducible dependencies

1. The Challenge: The "Human-in-the-Middle" Bottleneck
Problem: Traditional alerting (Prometheus/Grafana) requires an engineer to acknowledge, investigate, and manually run a playbook.

Impact: Increased operational costs and potential SLA breaches during off-hours.

Goal: Create a secure, auditable layer where an AI agent can perform "Level 1" support tasks autonomously.

2. The Solution: AI-Powered System Administration Agent
I engineered a Python-based agent that provides intelligent system administration capabilities:

Introspection Capability: The AI can query the live state of the system (CPU usage, memory, disk space, running services, etc.).

Remediation Capability: The AI can execute predefined, safe actions like service restarts, cache clearing, and system maintenance tasks based on real-time system data.

3. Technical Architecture
Language & Framework: Python, requests library for LLM communication.

Deployment: Single-file agent that can be run directly with Python.

Security: Implemented specific action-aliasing to ensure the LLM cannot execute arbitrary shell commands, maintaining DevSecOps compliance.

4. Key Results
Toil Reduction: Automated routine system administration tasks through AI assistance.

Simplicity: Single-file design eliminates deployment complexity and dependency conflicts.

Accessibility: Easy to run and modify for various system administration use cases.

## Installation

### Prerequisites
- Python 3.12 or higher
- Git
- uv package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Step-by-Step Installation
```bash
# Clone the repository
git clone <repository-url>
cd OSAgent

# Initialize virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Verify installation
python -c "import psutil, yaml, requests; print('All dependencies installed successfully')"
```

## Usage

### Setup
If you haven't completed the installation steps above, please do so first.

### Running the Agent
```bash
# Activate virtual environment if not already active
source .venv/bin/activate

# Run the main agent in interactive mode (default)
python main.py

# Run the main agent with a specific prompt (non-interactive)
python main.py "Your specific prompt here"
```

### Examples
- Interactive mode: `python main.py`
- Single prompt: `python main.py "Check system uptime and disk usage"`
- Single prompt: `python main.py "List all running services and their status"`

The agent operates in two modes:
- **Ask First (Default)**: Prompts for user confirmation before executing any action
- **Autonomous**: Independently manages tasks within defined safety parameters (set MODEL_AUTOMATION = True in main.py)