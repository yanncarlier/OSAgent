# **Creating context**

### 1 - I used this prompt to generate prompts For each of this AI provider 

```
generate a prompt to: to read a code base and create files to help in: context meaning, progressive disclose, software architecture and token savings for other agents
```

### 2 - The generated prompts are available in this files in AGENTS_context_generation_testing_files/:

OSAgent-chatgpt.md
OSAgent-claude.md
OSAgent-gemini.md
OSAgent-grok.md
OSAgent-mistral.md
OSAgent-perplexity.md
OSAgent-x.md

### 3 - I tested teach prompt in one or my projects codebase OSAgent

### 4 - I used OpenCode Agentic app and NVIDIA Nemotron 3 Super Free model from OpenCode Zen inference provider in Build mode

### 5 - In each copy of the repo I used this prompt:

```
This software function as an autonomous agent tailored for Ubuntu 24.04 LTS system administration.
Designed with a risk-averse philosophy, the agent prioritizes system stability and safety above all else. It follows a strictly non-destructive workflow to ensure that no command compromises the integrity of the environment.
The system operates in two distinct modes:
Ask First (Default): Prompts for user confirmation before executing any action.
Autonomous: Independently manages tasks within defined safety parameters.
Now that you know what this code is about. review it and improve it.
Rebember to always use uv for python and the .venv virtual environment in this project code base.
```

# **Creating VMS**

### 6 - VMs to test 

I created this script to test each one in an isolated VM:
```
./LXD_create_VMs.sh
```

# **Testing local models**

### 7 - tested some local inference models, the results are in this file:

 local_models_benchmark_as_sysadmin.md



### 8 - There can be only one

I will test each one and decide which one will will be the winner





# Miscellaneous

```

rm -rf OSAgent_*/__pycache__/
rm -rf OSAgent_*/.venv/

lxc exec OSAgent-chatgpt -- bash

source .venv/bin/activate
uv pip install -r requirements.txt
uv run main.py
uv run python mcp_self_healing_server.py
```





























