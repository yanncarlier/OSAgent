# OSAgent

A standalone AI-powered Ubuntu 24.04 LTS system administration agent that operates in multiple modes: Interactive (default), Single Shot, and Loop/Agentic. This single-file Python script provides an AI-powered interface for system administration tasks with a strong focus on safety and stability.

## Installation and Setup

To run the OSAgent system, follow these steps:

1. **Install uv** (Python package installer):
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Or visit: https://docs.astral.sh/uv/

2. **Clone the repository** (if you haven't already):
   ```
   git clone <repository-url>
   cd OSAgent-gemini
   ```

3. **Create and activate virtual environment**:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```
   uv pip install -r requirements.txt
   ```

5. **Configure the LLM API**:
   Edit `main.py` and update the `API_URL` variable to point to your local LLM server (default: http://10.167.32.1:1234/v1/chat/completions)

6. **Run the agent**:
   ```
   python main.py
   ```

---

Usage
OSAgent can be used in three different modes:

**Interactive Mode** (default):
```
python main.py
```
This starts an interactive session where you can continuously interact with the agent, asking follow-up questions and refining requests.

**Single Command Mode**:
```
python main.py "your prompt here"
```
Pass your prompt as a command-line argument for a single interaction. The agent will process the prompt, potentially execute commands (with your confirmation in Ask First mode), and then exit.

Examples:
```
python main.py "Check system status"
python main.py "List files in the current directory"
python main.py "Show memory usage"
```

**Loop/Agentic Mode**:
```
python main.py -l "your goal here"
python main.py --agentic "your goal here"
```
In this mode, the agent works continuously toward achieving a specified goal. It will assess the system state, determine what actions would move it closer to the goal, propose those actions for execution, and learn from the results. This enables true agentic behavior for managing operating systems.

Examples:
```
python main.py -l "Keep web server running and responsive"
python main.py --agentic "Monitor logs and alert on errors"
python main.py -l "Ensure system security and performance"
```

**Help Mode**:
```
python main.py -h
```
Shows usage information.

---

Overview
OSAgent is a standalone AI-powered terminal agent designed for Ubuntu 24.04 LTS system administration tasks. It provides a natural language interface for executing system commands with built-in safety mechanisms to prevent destructive operations.

Key Features:
- **Ask First Mode**: Prompts for user confirmation before executing any action (default, safe mode)
- **Autonomous Mode**: Independently manages tasks within defined safety parameters (use with caution)
- **Safety Filtering**: Comprehensive command validation to prevent destructive operations
- **Knowledge Base**: Embedded expertise in Bash scripting and Ubuntu 24.04 LTS administration
- **Session Logging**: Automatic logging of all interactions for auditing and review
- **Single File**: Everything is contained in main.py for easy deployment and use
- **Multiple Usage Modes**: Interactive, single shot, and loop/agentic modes for different use cases

How It Works:
1. The agent receives natural language input from the user (either interactively or as command-line argument)
2. It consults its embedded knowledge base for relevant context (Bash scripting, Ubuntu admin)
3. Using a local LLM (via API_URL), it determines appropriate system administration actions
4. Before execution, it validates commands against a comprehensive safety filter
5. In Ask First mode, it prompts for user confirmation before executing
6. Results are logged and presented to the user for review

In Loop/Agentic mode, the agent continuously works toward achieving a specified goal by:
1. Assessing the current system state
2. Determining what actions would move it closer to the goal
3. Proposing those actions for execution
4. Learning from the results
5. Repeating until the goal is achieved or interrupted

The agent is designed to be a safe, intelligent assistant for routine system administration tasks, reducing the cognitive load on administrators while maintaining strict safety controls. All functionality is self-contained in the main.py file.