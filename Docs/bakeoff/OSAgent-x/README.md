# OSAgent

This project case study is designed to bridge your extensive background in SRE and Platform Engineering with your recent 2026 focus on AI for Business. It frames the code provided previously as a strategic enterprise asset rather than just a script.

Case Study: AI-Driven Autonomous System Administration
Focus: Reducing Toil through Intelligent Automation for Ubuntu 24.04 LTS.

Executive Summary
In modern enterprise environments, system administrators face numerous repetitive tasks that consume valuable time and increase operational overhead. Leveraging my background in SRE and DevSecOps, I developed an autonomous agent that can intelligently perform routine system administration tasks on Ubuntu 24.04 LTS systems through natural language interaction.

1. The Challenge: Repetitive System Administration Tasks
Problem: System administrators spend significant time on routine tasks like checking system status, managing services, reviewing logs, and performing basic maintenance operations.

Impact: Increased operational costs, reduced focus on strategic initiatives, and potential delays in incident response.

Goal: Create an intelligent agent that can understand natural language requests and execute appropriate system administration commands safely and efficiently.

2. The Solution: Intelligent System Administration Agent
I engineered an autonomous agent (Python-based) that provides intelligent assistance for Ubuntu 24.04 LTS system administration:

Natural Language Interface: Users can interact with the agent using plain English commands.

Safety-First Design: The agent implements strict command filtering to prevent execution of destructive operations.

Context-Aware Assistance: The agent provides relevant technical context based on the user's request.

3. Technical Architecture
Language & Framework: Python, with integration to local LLM APIs.

Deployment: Runs as a standalone Python script with virtual environment management.

Safety Systems: Multi-layered command validation including allowlists, blocklists, and pattern matching to prevent dangerous operations.

4. Key Results
Toil Reduction: Automates routine system administration tasks through intelligent command interpretation.

Safety: Comprehensive safety mechanisms prevent accidental system damage.

Accessibility: Makes system administration more accessible to junior team members through guided assistance.

## Installation and Setup

### Prerequisites
- Python 3.12 or higher
- UV package manager (https://github.com/astral-sh/uv)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd OSAgent
   ```

2. Install dependencies using UV:
   ```bash
   uv sync
   ```

### Running the Application
To start the OSAgent system administration assistant:
```bash
uv run python main.py
```

The agent will start and present an interactive terminal interface where you can enter natural language requests for system administration tasks.

### Usage Modes

#### Interactive Mode (Default)
Run without arguments for interactive use:
```bash
uv run python main.py
```
You'll be prompted to enter natural language requests for system administration tasks.

#### One-Shot Mode
Process a single prompt and exit:
```bash
uv run python main.py --prompt "Show me the current system status"
```

#### Agentic Mode
Run continuously working toward a goal:
```bash
uv run python main.py --agent --prompt "Check if nginx is running and start it if not" --max-iterations 5
```

### Usage Examples
Once the agent is running (in any mode), you can:
- Ask for system information (e.g., "Show me the current CPU usage")
- Request service management (e.g., "Restart the nginx service")
- Query system logs (e.g., "Show me recent SSH login attempts")
- Perform file operations (e.g., "List all files in /var/log")
- Execute safe system administration commands through natural language interaction

The agent includes specialized knowledge bases for Bash scripting and Ubuntu 24.04 LTS administration to provide context-aware assistance.