# OSAgent

A self-contained Python application for Linux system administration assistance.

## Overview
OSAgent is a single-file Python script (main.py) that provides an interactive terminal interface for system administration tasks. It combines AI assistance with safe command execution capabilities.

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- UV (Python package installer and manager) - Recommended
- Git (for cloning the repository)
- Access to a Language Model API (compatible with OpenAI API format)

### Installation

1. **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd OSAgent-grok
    ```

2. **Install Dependencies with UV**
    ```bash
    uv sync
    ```

### Configuration

Before running, configure the LLM API connection in `main.py`:
- `API_URL`: Endpoint for the LLM API (default: "http://10.167.32.1:1234/v1/chat/completions")
- `MODEL_TEMPERATURE`: Controls randomness in responses (default: 0.1)
- `MODEL_AUTOMATION`: Set to True to skip command confirmation prompts (default: False)
- `LOG_DIR`: Directory for session logs (default: "logs")

### Usage

#### Running the Agent

**Interactive Mode** (default):
```bash
uv run python main.py
```
The agent will start and present an interactive terminal interface where you can:
- Ask questions about Linux system administration
- Request the agent to execute safe terminal commands
- Type `exit` or `quit` to end the session

**Agentic Mode** (with goal prompt):
```bash
uv run python main.py "Your goal or objective here"
```
The agent will work autonomously toward achieving the stated goal, executing commands and analyzing results until completion or until reaching the maximum iteration limit (20 by default).

#### Available Commands
- Use `[[EXEC: <command>]]` syntax to request command execution
- The agent will ask for confirmation before executing commands (unless automation mode is enabled)