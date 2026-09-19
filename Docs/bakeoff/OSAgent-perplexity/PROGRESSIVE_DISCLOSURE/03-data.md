# Data Models and Infrastructure State

## Infrastructure State (mcp_self_healing_server.py:18-22)
Simulated infrastructure database:
```python
INFRA_DATABASE = {
    "web-server-01": {"status": "healthy", "cpu_usage": 12, "memory_usage": 45},
    "db-cluster-01": {"status": "degraded", "cpu_usage": 88, "memory_usage": 92},
    "cache-node-01": {"status": "healthy", "cpu_usage": 5, "memory_usage": 10},
}
```
- Fields: status (string), cpu_usage (int), memory_usage (int)
- Updated by remediation actions (e.g., restart sets status to healthy, cpu_usage to 10)

## Knowledge Base (main.py:16-30)
Embedded dictionary for domain-specific context:
```python
KNOWLEDGE_BASE = {
    "BashScriptMaster": {
        "description": "Advanced shell scripting best practices and automation logic.",
        "triggers": ["bash", "shell", "script", "loop", "variable", "pipe", "sed", "awk", "grep", "automation"],
        "content": "..."
    }
}
```
- Structure: {name: {description, triggers(list), content(string)}}
- Used by ContextManager.get_relevant_context() to augment LLM prompts

## Logging System (main.py:34-52)
SessionLogger class:
- Creates log files in LOG_DIR with timestamped names
- Logs entries with format: `[timestamp] SENDER:\nmessage\n{'-'*40}\n`
- Ensures directory exists before writing