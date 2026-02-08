# os_gateway.py

import json
import subprocess
import urllib.request
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# --- Configuration ---
API_URL = "http://localhost:8080/v1/chat/completions"
CONTEXT_DIR = "context_files"
MAX_TOKENS = 32768
TOKEN_BUFFER = 2000  # Reserve tokens for conversation

# Context priorities (lower = higher priority)
CONTEXT_PRIORITIES = {
    "identity": 1,
    "agent": 2,
    "soul": 3,
    "tools": 4,
    "heartbeat": 5,
    "skill": 6
}

# Base system prompt without contexts
BASE_SYSTEM_PROMPT = """You are an OS Agent. You have access to the user's computer.
To run a command, you MUST use the following format:
RUN_COMMAND: ["command", "arg1", "arg2"]

After a command runs, I will give you the output. You should:
1. Analyze the output.
2. If you need more info, run another command.
3. If you have the answer, explain it to the user and start with 'FINISH:'.

If you need additional context to complete the task, you can request it by saying:
REQUEST_CONTEXT: ["context_name1", "context_name2"]
Available contexts: identity, agent, soul, tools, heartbeat, skill"""


class ContextManager:
    """Manages progressive disclosure of context files."""
    
    def __init__(self, context_dir: str, max_tokens: int, token_buffer: int):
        self.context_dir = Path(context_dir)
        self.max_tokens = max_tokens
        self.token_buffer = token_buffer
        self.contexts: Dict[str, Dict] = {}
        self.loaded_contexts: List[str] = []
        self.tokens_used = 0
        
        # Load context metadata
        self._scan_contexts()
    
    def _scan_contexts(self):
        """Scan context directory and load metadata."""
        if not self.context_dir.exists():
            print(f"[!] Context directory '{self.context_dir}' not found!")
            return
        
        for file_path in self.context_dir.glob("*.md"):
            context_name = file_path.stem.lower()
            content = file_path.read_text(encoding='utf-8')
            
            # Rough token estimation (1 token ≈ 4 characters)
            token_count = len(content) // 4
            
            self.contexts[context_name] = {
                "path": file_path,
                "content": content,
                "tokens": token_count,
                "priority": CONTEXT_PRIORITIES.get(context_name, 999),
                "loaded": False
            }
    
    def get_initial_contexts(self, user_query: str) -> Tuple[str, int]:
        """
        Load essential contexts based on query analysis.
        Returns: (context_text, tokens_used)
        """
        # Always load identity first (core personality)
        essential = ["identity"]
        
        # Analyze query for keywords to determine relevant contexts
        query_lower = user_query.lower()
        
        # Keyword mapping to contexts
        if any(word in query_lower for word in ["how", "explain", "what", "why", "help"]):
            essential.append("agent")
        
        if any(word in query_lower for word in ["file", "command", "execute", "run", "tool"]):
            essential.append("tools")
        
        if any(word in query_lower for word in ["learn", "skill", "ability", "can you"]):
            essential.append("skill")
        
        # Load selected contexts
        return self._load_contexts(essential)
    
    def _load_contexts(self, context_names: List[str]) -> Tuple[str, int]:
        """Load specific contexts and return combined text."""
        combined_text = ""
        tokens = 0
        
        # Sort by priority
        sorted_names = sorted(
            context_names,
            key=lambda x: self.contexts.get(x, {}).get("priority", 999)
        )
        
        for name in sorted_names:
            if name not in self.contexts:
                print(f"[!] Context '{name}' not found")
                continue
            
            context = self.contexts[name]
            available_tokens = self.max_tokens - self.tokens_used - self.token_buffer
            
            if context["tokens"] > available_tokens:
                print(f"[!] Not enough tokens to load '{name}' ({context['tokens']} needed, {available_tokens} available)")
                continue
            
            if not context["loaded"]:
                combined_text += f"\n\n--- Context: {name.upper()} ---\n{context['content']}"
                tokens += context["tokens"]
                context["loaded"] = True
                self.loaded_contexts.append(name)
                print(f"[✓] Loaded context: {name} ({context['tokens']} tokens)")
        
        self.tokens_used += tokens
        return combined_text, tokens
    
    def request_contexts(self, context_names: List[str]) -> Tuple[str, int]:
        """Load additional contexts on demand."""
        return self._load_contexts(context_names)
    
    def get_metrics(self) -> str:
        """Return token usage metrics."""
        utilization = (self.tokens_used / self.max_tokens) * 100
        
        metrics = f"""
Token Budget:
  Used: {self.tokens_used}/{self.max_tokens}
  Utilization: {utilization:.1f}%

Loaded Contexts ({len(self.loaded_contexts)} total):
"""
        for name in self.loaded_contexts:
            ctx = self.contexts[name]
            metrics += f"  ✓ {name:<12} {ctx['tokens']:>4} tokens (priority: {ctx['priority']})\n"
        
        metrics += f"\nContext Summary:\n"
        metrics += f"  Total contexts: {len(self.contexts)}\n"
        metrics += f"  Loaded contexts: {len(self.loaded_contexts)}\n"
        metrics += f"  Available contexts: {list(self.contexts.keys())}\n"
        
        return metrics


def call_llama(messages):
    """Sends a request to the llama.cpp server."""
    payload = {
        "messages": messages,
        "temperature": 0.1, 
        "stream": False
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            return res_body['choices'][0]['message']['content']
    except Exception as e:
        print(f"\n[!] Error connecting to llama.cpp: {e}")
        sys.exit(1)


def execute_os_command(cmd_list):
    """Runs a system command and returns results."""
    try:
        process = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr
        }
    except Exception as e:
        return {"code": -1, "stdout": "", "stderr": str(e)}


def main():
    print("=" * 60)
    print("  Llama OS Bridge with Progressive Context Loading")
    print("=" * 60)
    
    # Initialize context manager
    context_mgr = ContextManager(CONTEXT_DIR, MAX_TOKENS, TOKEN_BUFFER)
    
    if not context_mgr.contexts:
        print("\n[!] No contexts loaded. Proceeding with base prompt only.")
    
    user_goal = input("\nWhat should the OS Agent do?: ")
    
    # Load initial contexts based on query
    print("\n[Loading relevant contexts...]")
    initial_contexts, initial_tokens = context_mgr.get_initial_contexts(user_goal)
    
    # Build system prompt with loaded contexts
    system_prompt = BASE_SYSTEM_PROMPT + initial_contexts
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_goal}
    ]
    
    # Show initial metrics
    print("\n" + "─" * 60)
    print(context_mgr.get_metrics())
    print("─" * 60)
    
    iteration = 0
    max_iterations = 20  # Prevent infinite loops
    
    while iteration < max_iterations:
        iteration += 1
        
        # 1. AI decides what to do
        print(f"\n[Iteration {iteration} - Thinking...]", end="", flush=True)
        ai_response = call_llama(messages)
        messages.append({"role": "assistant", "content": ai_response})
        
        print(f"\n[OS Agent]: {ai_response}")

        if ai_response.startswith("FINISH:"):
            print("\n[✓] Task completed!")
            break

        # 2. Handle context requests
        if "REQUEST_CONTEXT:" in ai_response:
            try:
                raw_json = ai_response.split("REQUEST_CONTEXT:")[1].strip().split("\n")[0]
                requested_contexts = json.loads(raw_json)
                
                print(f"\n[Loading requested contexts: {', '.join(requested_contexts)}]")
                new_contexts, new_tokens = context_mgr.request_contexts(requested_contexts)
                
                if new_contexts:
                    # Append new contexts to system message
                    messages[0]["content"] += new_contexts
                    messages.append({"role": "user", "content": f"Contexts loaded: {', '.join(requested_contexts)}"})
                    print(context_mgr.get_metrics())
                else:
                    messages.append({"role": "user", "content": "No additional contexts could be loaded."})
                    
            except Exception as e:
                msg = f"Error loading contexts: {e}"
                print(f"[!] {msg}")
                messages.append({"role": "user", "content": msg})
            
            continue

        # 3. Extract and execute command
        if "RUN_COMMAND:" in ai_response:
            try:
                # Clean up the string to find the JSON list
                raw_json = ai_response.split("RUN_COMMAND:")[1].strip().split("\n")[0]
                cmd_list = json.loads(raw_json)
                
                print(f"\n[Executing]: {' '.join(cmd_list)}")
                
                # Run and print output
                result = execute_os_command(cmd_list)
                
                if result['stdout']:
                    print(f"--- STDOUT ---\n{result['stdout']}")
                if result['stderr']:
                    print(f"--- STDERR ---\n{result['stderr']}")
                
                # Feed back to AI
                result_str = f"Exit Code: {result['code']}\nSTDOUT: {result['stdout']}\nSTDERR: {result['stderr']}"
                messages.append({"role": "user", "content": f"COMMAND RESULT:\n{result_str}"})
                
            except Exception as e:
                msg = f"Error: Could not parse or run command. {e}"
                print(f"[!] {msg}")
                messages.append({"role": "user", "content": msg})
        else:
            messages.append({"role": "user", "content": "I didn't see a command or context request. If you are done, say FINISH:. Otherwise, provide a RUN_COMMAND or REQUEST_CONTEXT."})
    
    if iteration >= max_iterations:
        print(f"\n[!] Reached maximum iterations ({max_iterations}). Stopping.")
    
    # Final metrics
    print("\n" + "=" * 60)
    print("Final Token Usage:")
    print("=" * 60)
    print(context_mgr.get_metrics())


if __name__ == "__main__":
    main()