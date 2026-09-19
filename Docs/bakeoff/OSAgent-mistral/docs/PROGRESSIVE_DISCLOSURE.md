# Progressive Disclosure Guide

## Hierarchical Codebase Map

```
OSAgent_mistral/
├── main.py                 # Agentic terminal interface (START HERE for agent customization)
├── mcp_self_healing_server.py  # MCP infrastructure server (START HERE for infrastructure integration)
├── logs/                   # Session logs (generated automatically)
├── docs/                   # Documentation (this directory)
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # Project overview (START HERE for general understanding)
```

## Start Here Sections

### For New Contributors
1. Begin with `README.md` to understand the project vision
2. Review `project_manifest.md` for professional context
3. Examine `main.py` to understand the agentic terminal flow
4. Look at `mcp_self_healing_server.py` for infrastructure integration details

### Adding a New Knowledge Domain (to main.py)
1. Open `main.py` and locate the `KNOWLEDGE_BASE` dictionary (lines 17-30)
2. Add a new entry following the existing pattern:
   ```python
   "YourDomainExpert": {
       "description": "Brief description of the expertise area",
       "triggers": ["keyword1", "keyword2", "keyword3"],  # Words that activate this knowledge
       "content": """
       ### SPECIALIZED CONTEXT: [DOMAIN NAME] ###
       - Your specialized knowledge content here
       - Use markdown formatting for readability
       """
   }
   ```
3. Restart the application for changes to take effect

### Adding a New MCP Tool/Resource (to mcp_self_healing_server.py)
1. Open `mcp_self_healing_server.py`
2. To add a new tool:
   - Create an async function decorated with `@mcp.tool()`
   - Follow the pattern of existing tools like `get_system_status` or `trigger_remediation`
   - Add appropriate docstring and type hints
3. To add a new resource:
   - Create a function decorated with `@mcp.resource("your://resource-path")`
   - Return string content that provides context to the LLM
4. Restart the MCP server for changes to take effect

### Customizing Terminal Behavior
1. Modify `base_system_prompt` in `main.py` (lines 104-108) to change agent behavior
2. Adjust `MODEL_TEMPERATURE` (line 12) for more/less deterministic responses
3. Change `MODEL_AUTOMATION` (line 13) to enable/disable automatic command execution
4. Modify `LOG_DIR` (line 14) to change log storage location

## Deep Dive Sections

<details>
<summary>Advanced: Knowledge Base Optimization</summary>

The `ContextManager.get_relevant_context()` method uses a simple keyword matching algorithm. For production systems, consider:

1. **Semantic Matching**: Replace keyword matching with embedding-based similarity search
2. **Priority Weighting**: Assign weights to different knowledge domains based on relevance
3. **Context Caching**: Cache frequently accessed knowledge to reduce computation
4. **Dynamic Loading**: Load knowledge domains on-demand rather than keeping all in memory

Example enhancement:
```python
def get_relevant_context(self, user_input: str) -> str:
    # Instead of simple keyword matching:
    input_embedding = self.embed_model.encode([user_input])
    similarities = {}
    
    for name, data in self.KNOWLEDGE_BASE.items():
        # Calculate similarity with domain description/examples
        domain_text = data['description'] + ' ' + ' '.join(data['triggers'])
        domain_embedding = self.embed_model.encode([domain_text])
        similarity = cosine_similarity(input_embedding, domain_embedding)
        similarities[name] = similarity
    
    # Return top-k most relevant domains
    sorted_domains = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    disclosed_text = ""
    for name, similarity in sorted_domains[:3]:  # Top 3
        if similarity > 0.3:  # Threshold
            disclosed_text += f"\n{self.KNOWLEDGE_BASE[name]['content']}\n"
            
    return disclosed_text
```
</details>

<details>
<summary>Advanced: MCP Server Productionization</summary>

For production deployment of the MCP server:

1. **Real Infrastructure Integration**: Replace `INFRA_DATABASE` with actual API calls:
   ```python
   # Example for Kubernetes
   from kubernetes import client, config
   
   async def get_k8s_pod_status(pod_name: str):
       try:
           v1 = client.CoreV1Api()
           pod = v1.read_namespaced_pod_status(pod_name, "default")
           return {
               "status": pod.status.phase,
               "cpu_usage": get_cpu_usage(pod_name),  # Implement from metrics API
               "memory_usage": get_memory_usage(pod_name)
           }
       except Exception as e:
           return f"Error fetching pod status: {str(e)}"
   ```

2. **Authentication & Authorization**: Add middleware to validate MCP requests
3. **Logging & Auditing**: Implement comprehensive audit trails for all actions
4. **Horizontal Scaling**: Deploy multiple instances behind a load balancer
5. **Health Endpoints**: Add liveness/readiness probes for orchestration systems
</details>

<details>
<summary>Advanced: Terminal Security Enhancements</summary>

Beyond the basic safety filter in `TerminalTool.execute()`:

1. **Command Allowlisting**: Maintain a whitelist of permitted commands
2. **Argument Validation**: Validate and sanitize all command arguments
3. **Timeouts & Resource Limits**: Implement stricter resource constraints
4. **Output Filtering**: Sanitize command output before returning to LLM
5. **Session Isolation**: Run commands in restricted environments (containers, namespaces)
6. **Approval Workflows**: Implement multi-step approval for high-risk operations
</details>

## FAQs

### Q: How does the agent know when to use specialized knowledge?
A: The `ContextManager` scans user input for trigger keywords defined in each knowledge domain. When matches are found, the corresponding knowledge is injected into the system prompt.

### Q: Can I add multiple knowledge domains that might trigger on the same words?
A: Yes, all matching domains will have their content concatenated and added to the context. Consider using more specific triggers to avoid unintended activations.

### Q: Is the MCP server secure against prompt injection?
A: The MCP server uses a strict tool-calling schema that prevents arbitrary command execution. However, always validate and sanitize inputs to any tools you add.

### Q: How do I persist infrastructure state between restarts?
A: Currently, `INFRA_DATABASE` is in-memory only. For persistence, replace it with a database connection or file-based storage.

### Q: Can I change the LLM endpoint or model?
A: Yes, modify `API_URL` (line 11) in `main.py` to point to different LLM endpoints. The model is specified in the API request payload.

## Suggested Reading Paths

### For Backend Developers
1. README.md → project_manifest.md → mcp_self_healing_server.py → main.py
2. Focus on: MCP implementation, tool/resource patterns, async programming

### For AI/ML Engineers
1. README.md → main.py → notes.md (for API examples)
2. Focus on: LLM interaction patterns, context management, prompt engineering

### For DevOps/SRE Engineers
1. README.md → mcp_self_healing_server.py → main.py
2. Focus on: Infrastructure integration, self-healing patterns, safety mechanisms

### For Security Engineers
1. Review safety mechanisms in both files
2. Examine TerminalTool.execute() restrictions
3. Review MCP tool/resource security boundaries
4. Check logging and audit capabilities