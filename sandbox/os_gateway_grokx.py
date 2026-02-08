# os_gateway.py

import json
import subprocess
import urllib.request
import os
import sys

# --- Configuration ---
API_URL = "http://localhost:8080/v1/chat/completions"

# Available contexts and priorities
available_contexts = ['identity', 'agent', 'soul', 'tools', 'heartbeat', 'skill']
priority_dict = {
    'identity': 1,
    'agent': 2,
    'soul': 3,
    'tools': 4,
    'heartbeat': 5,
    'skill': 6
}

# Base System Prompt with progressive disclosure
BASE_PROMPT = f"""You are an OS Agent. You have access to the user's computer.

You have access to additional context files that provide more information about your capabilities and guidelines.
Available contexts: {', '.join(available_contexts)}
To load one or more contexts (to save tokens and narrow focus, load only what's necessary via progressive disclosure), use:
LOAD_CONTEXT: ["context_name1", "context_name2"]

I will then provide the loaded contexts.
Assess if you need additional contexts based on the user goal before running commands or finishing. Load them step by step as needed.

To run a command, you MUST use the following format:
RUN_COMMAND: ["command", "arg1", "arg2"]

After a command runs, I will give you the output. You should:
1. Analyze the output.
2. If you need more info, run another command.
3. If you have the answer, explain it to the user and start with 'FINISH:'."""

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
    print("--- Llama OS Bridge Active ---")
    
    user_goal = input("\nWhat should the OS Agent do?: ")
    
    loaded_contexts = {}  # name: content
    full_system = BASE_PROMPT
    messages = [
        {"role": "system", "content": full_system},
        {"role": "user", "content": user_goal}
    ]
    
    while True:
        # 1. AI decides what to do
        print("\n[Thinking...]", end="", flush=True)
        ai_response = call_llama(messages)
        messages.append({"role": "assistant", "content": ai_response})
        
        print(f"\n[OS Agent]: {ai_response}")

        if ai_response.startswith("FINISH:"):
            break

        updated = False

        # 2. Check for LOAD_CONTEXT
        if "LOAD_CONTEXT:" in ai_response:
            try:
                # Extract the JSON list
                raw_json = ai_response.split("LOAD_CONTEXT:")[1].strip().split("\n")[0]
                to_load = json.loads(raw_json)
                
                for name in to_load:
                    if name in available_contexts:
                        if name not in loaded_contexts:
                            path = os.path.join("context_files", name.upper() + ".md")
                            if os.path.exists(path):
                                with open(path, 'r') as f:
                                    content = f.read().strip()
                                loaded_contexts[name] = content
                                updated = True
                            else:
                                messages.append({"role": "user", "content": f"Context file for '{name}' not found."})
                        else:
                            messages.append({"role": "user", "content": f"Context '{name}' already loaded."})
                    else:
                        messages.append({"role": "user", "content": f"Invalid context '{name}'. Available: {', '.join(available_contexts)}"})
            except Exception as e:
                msg = f"Error parsing or loading context: {e}"
                print(f"[!] {msg}")
                messages.append({"role": "user", "content": msg})

        # 3. Update system prompt if contexts were loaded
        if updated:
            context_sections = "\n\n".join(
                f"### {name.upper()} Context\n{content}"
                for name, content in sorted(loaded_contexts.items(), key=lambda x: priority_dict[x[0]])
            )
            full_system = BASE_PROMPT + "\n\n" + context_sections
            messages[0]["content"] = full_system

        # 4. Check for RUN_COMMAND
        command_executed = False
        if "RUN_COMMAND:" in ai_response:
            try:
                # Extract the JSON list
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
                command_executed = True
            except Exception as e:
                msg = f"Error: Could not parse or run command. {e}"
                print(f"[!] {msg}")
                messages.append({"role": "user", "content": msg})

        # 5. If no action was taken
        if not updated and not command_executed:
            messages.append({"role": "user", "content": "I didn't see a command or context load. If you are done, say FINISH:. Otherwise, provide a RUN_COMMAND or LOAD_CONTEXT."})

if __name__ == "__main__":
    main()