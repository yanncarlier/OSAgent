# Specialized Agents Directory

This directory contains specialized agent workspaces for Progressive Disclosure and token efficiency.

## Purpose
- **Token Savings**: Load only relevant context when spawning specialized agents
- **Quality Improvement**: Domain-specific personas and expertise
- **Parallel Processing**: Run multiple specialized agents simultaneously

## Available Agents

### Programming Languages
- **Assembly** - Low-level programming
- **C** - C programming language  
- **C++** - C++ programming
- **C#** - C#/.NET development
- **Dart** - Dart/Flutter development
- **Go** - Go programming
- **Java** - Java development
- **JavaScript** - JavaScript/TypeScript development
- **PHP** - PHP development
- **Python** - Python development (most developed)
- **Rust** - Rust programming
- **ShellScript** - Shell scripting

### Domain Specialists
- **Bitcoin** - Cryptocurrency/blockchain expert (most developed)
- **Creative_Writer** - Creative writing/content creation
- **Project_Manager** - Project management and coordination

## Usage

### 1. Spawn as Sub-Agent
```bash
# Spawn Python agent for coding task
sessions_spawn agentId=main task="Write Python script" label="python-task"

# Spawn Bitcoin agent for crypto analysis
sessions_spawn agentId=main task="Analyze Bitcoin trends" label="bitcoin-analysis"
```

### 2. Reference as Knowledge Base
```bash
# Get domain-specific knowledge
read agents/Python/TOOLS.md
read agents/Bitcoin/IDENTITY.md
```

### 3. Progressive Disclosure Benefits
- **Context Isolation**: Each agent loads only its specialized context
- **Reduced Tokens**: No need to load general knowledge for specialized tasks
- **Improved Quality**: Domain-specific personas and memory
- **Parallel Work**: Multiple agents can work simultaneously

## Maintenance
- Keep memory directories only in frequently used agents
- Update TOOLS.md with domain-specific tool configurations
- Use MEMORY.md for long-term domain knowledge
- Remove unused agents to save space

## Notes
- All .git directories have been removed for cleanliness
- JavaScript_TypeScript renamed to JavaScript for simplicity
- Bitcoin, JavaScript, and Python have memory directories (most developed)
