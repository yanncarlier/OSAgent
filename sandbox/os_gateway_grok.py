import json
import subprocess
import urllib.request
import os
import sys

# --- Configuration ---
API_URL = "http://localhost:8080/v1/chat/completions"
CONTEXT_DIR = "context_files"

# Context mapping and priorities (lower number = higher priority)
CONTEXT_MAP = {
    "identity": "IDENTITY.md",
    "agent": "AGENT.md",
    "soul": "SOUL.md",
    "tools": "TOOLS.md",
    "heartbeat": "HEARTBEAT.md",
    "skill": "SKILL.md",
    "plan": "PLAN.md",
}

PRIORITIES = {
    "identity": 1,
    "agent": 2,
    "soul": 3,
    "tools": 4,
    "heartbeat": 5,
    "skill": 6,
    "plan": 7,
}

# Approximate token counts from your metrics (fallback to estimate)
TOKEN_ESTIMATES = {
    "identity": 268,
    "agent": 552,
    "soul": 225,
    "tools": 217,
    "heartbeat": 235,
    "skill": 502,
    # plan will be estimated
}

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)  # rough heuristic (~4 chars/token)

def load_context_contents():
    contents = {}
    for name, filename in CONTEXT_MAP.items():
        path = os.path.join(CONTEXT_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                contents[name] = f.read().strip()
        else:
            print(f"[!] Warning: {filename} not found")
            contents[name] = ""
    return contents

def build_context_text(loaded: list, contents: dict) -> str:
    parts = []
    for name in loaded:
        if name in contents and contents[name]:
            parts.append(f"--- {name.upper()} CONTEXT ---\n{contents[name]}")
    return "\n\n".join(parts)

# --- Improved System Prompt with Progressive Disclosure instructions ---
SYSTEM_PROMPT = """You are an OS Agent. You have access to the user's computer.

To run a command, you MUST use:
RUN_COMMAND: ["command", "arg1", "arg2"]

After command output, analyze it. If you need more info, run another command. When done, explain to the user and start with 'FINISH:'.

**Progressive Context Disclosure (Token Saving Mode)**
- Only core contexts are initially loaded: IDENTITY, AGENT, SOUL
- Request additional contexts **only when needed** for the current task:
  LOAD_CONTEXT: ["skill", "tools"]
- Unload contexts that are no longer relevant:
  UNLOAD_CONTEXT: ["heartbeat"]
- Available contexts:
  - tools: Available commands, APIs, and tool usage instructions
  - skill: Specialized skills and capabilities of the agent
  - heartbeat: System status monitoring and heartbeat checks
  - plan: Current high-level plan, milestones, and goals

Always try to solve the task with currently loaded contexts first.
Keep context narrow and focused to stay within token budget.
"""

def call_llama(messages):
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
    try:
        process = subprocess.run(cmd_list, capture_output=True, text=True, timeout=60)
        return {
            "code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr
        }
    except Exception as e:
        return {"code": -1, "stdout": "", "stderr": str(e)}

def main():
    print("--- Llama OS Bridge Active (Progressive Context Loading) ---")
    
    contents = load_context_contents()
    
    # Start with core high-priority contexts only
    loaded_contexts = ["identity", "agent", "soul"]
    loaded_contexts = [n for n in loaded_contexts if n in contents]
    
    context_text = build_context_text(loaded_contexts, contents)
    full_system = SYSTEM_PROMPT + "\n\n**Progressive Context Disclosure Active**\nLoaded: " + ", ".join(loaded_contexts) + "\n\n" + context_text
    
    messages = [
        {"role": "system", "content": full_system},
        {"role": "user", "content": input("\nWhat should the OS Agent do?: ")}
    ]
    
    # Initial status
    ctx_tokens = sum(TOKEN_ESTIMATES.get(n, estimate_tokens(contents.get(n, ""))) for n in loaded_contexts)
    print(f"✓ Core contexts loaded: {', '.join(loaded_contexts)}")
    print(f"≈ Context tokens: {ctx_tokens} / 32768 (6.1% utilization)")
    print(f"Available to load: tools, skill, heartbeat, plan\n")

    while True:
        print("\n[Thinking...]", end="", flush=True)
        ai_response = call_llama(messages)
        messages.append({"role": "assistant", "content": ai_response})
        
        print(f"\n[OS Agent]: {ai_response}")

        if ai_response.startswith("FINISH:"):
            break

        updated_context = False

        # === LOAD CONTEXT ===
        if "LOAD_CONTEXT:" in ai_response:
            try:
                raw = ai_response.split("LOAD_CONTEXT:")[1].strip().split("\n")[0].strip()
                to_load = json.loads(raw)
                newly_loaded = []
                for name in to_load if isinstance(to_load, list) else []:
                    if name in contents and name not in loaded_contexts:
                        loaded_contexts.append(name)
                        newly_loaded.append(name)
                if newly_loaded:
                    context_text = build_context_text(loaded_contexts, contents)
                    messages[0]["content"] = SYSTEM_PROMPT + "\n\n**Progressive Context Disclosure Active**\nLoaded: " + ", ".join(loaded_contexts) + "\n\n" + context_text
                    conf = f"Loaded: {', '.join(newly_loaded)}. Total loaded: {len(loaded_contexts)}"
                    messages.append({"role": "user", "content": conf})
                    print(f"[Context] {conf}")
                    updated_context = True
            except Exception as e:
                print(f"[!] Load context error: {e}")

        # === UNLOAD CONTEXT ===
        if "UNLOAD_CONTEXT:" in ai_response:
            try:
                raw = ai_response.split("UNLOAD_CONTEXT:")[1].strip().split("\n")[0].strip()
                to_unload = json.loads(raw)
                newly_unloaded = []
                for name in to_unload if isinstance(to_unload, list) else []:
                    if name in loaded_contexts:
                        loaded_contexts.remove(name)
                        newly_unloaded.append(name)
                if newly_unloaded:
                    context_text = build_context_text(loaded_contexts, contents)
                    messages[0]["content"] = SYSTEM_PROMPT + "\n\n**Progressive Context Disclosure Active**\nLoaded: " + ", ".join(loaded_contexts) + "\n\n" + context_text
                    conf = f"Unloaded: {', '.join(newly_unloaded)}. Total loaded: {len(loaded_contexts)}"
                    messages.append({"role": "user", "content": conf})
                    print(f"[Context] {conf}")
                    updated_context = True
            except Exception as e:
                print(f"[!] Unload context error: {e}")

        if updated_context:
            # Recalculate tokens
            ctx_tokens = sum(TOKEN_ESTIMATES.get(n, estimate_tokens(contents.get(n, ""))) for n in loaded_contexts)
            print(f"≈ Current context tokens: {ctx_tokens} / 32768")
            continue  # Let AI re-think with updated context

        # === RUN COMMAND (only if no context command was processed) ===
        if "RUN_COMMAND:" in ai_response:
            try:
                raw_json = ai_response.split("RUN_COMMAND:")[1].strip().split("\n")[0]
                cmd_list = json.loads(raw_json)
                print(f"[Executing]: {' '.join(cmd_list)}")
                result = execute_os_command(cmd_list)
                if result['stdout']:
                    print(f"--- STDOUT ---\n{result['stdout']}")
                if result['stderr']:
                    print(f"--- STDERR ---\n{result['stderr']}")
                result_str = f"Exit Code: {result['code']}\nSTDOUT: {result['stdout']}\nSTDERR: {result['stderr']}"
                messages.append({"role": "user", "content": f"COMMAND RESULT:\n{result_str}"})
            except Exception as e:
                msg = f"Error parsing/running command: {e}"
                print(f"[!] {msg}")
                messages.append({"role": "user", "content": msg})
        else:
            messages.append({"role": "user", "content": "No RUN_COMMAND or context command detected. If done, say FINISH:. Otherwise provide RUN_COMMAND or LOAD_CONTEXT / UNLOAD_CONTEXT."})

if __name__ == "__main__":
    main()