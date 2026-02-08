# os_gateway.py

import json
import subprocess
import urllib.request
import os
import sys

# --- Configuration ---
API_URL = "http://localhost:8080/v1/chat/completions"
CONTEXT_DIR = "context_files"

# The System Prompt now defines "Progressive Disclosure" behavior.
# The Agent starts with a manifest of files and must 'cat' them to see contents.
SYSTEM_PROMPT = f"""You are an OS Agent with access to the user's computer.
You use "Progressive Disclosure" to manage your memory. You know these context files exist:
- IDENTITY.md: Who you are.
- AGENT.md: Operational protocols.
- SOUL.md: Core values and personality.
- TOOLS.md: Technical capabilities.
- HEARTBEAT.md: System status and frequency.
- SKILL.md: Specific task-based knowledge.
- PLAN.md: Current long-term objectives.

GUIDELINES:
1. Do NOT assume you know the contents of these files yet.
2. To narrow your focus and save tokens, use RUN_COMMAND: ["cat", {CONTEXT_DIR}/FILE_NAME.md"] to read only what you need.
3. Once you have the necessary context, proceed with the user's goal.
4. To run any command, use the format: RUN_COMMAND: ["command", "arg1", "arg2"]
5. When finished, explain the result and start with 'FINISH:'."""

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
        # Cross-platform support for 'cat'
        if cmd_list[0] == "cat" and os.name == 'nt':
            cmd_list[0] = "type"
            
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
    print("--- Llama OS Bridge: Progressive Disclosure Mode ---")
    
    # Check if context directory exists
    if not os.path.exists(CONTEXT_DIR):
        print(f"[!] Warning: Context directory '{CONTEXT_DIR}' not found.")
    
    user_goal = input("\nWhat should the OS Agent do?: ")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Goal: {user_goal}\n\nNote: You have not loaded any context files yet. Use 'cat' to load relevant files if needed."}
    ]
    
    while True:
        print("\n[Thinking...]", end="", flush=True)
        ai_response = call_llama(messages)
        messages.append({"role": "assistant", "content": ai_response})
        
        print(f"\n[OS Agent]: {ai_response}")

        if ai_response.startswith("FINISH:"):
            break

        if "RUN_COMMAND:" in ai_response:
            try:
                # Parsing the command list from the response
                start_idx = ai_response.find("RUN_COMMAND:") + len("RUN_COMMAND:")
                raw_json = ai_response[start_idx:].strip().split("\n")[0]
                cmd_list = json.loads(raw_json)
                
                print(f"[Executing]: {' '.join(cmd_list)}")
                
                result = execute_os_command(cmd_list)
                
                # Visual feedback for the human
                if result['stdout']:
                    # Truncate output in terminal if it's too long, but send full text to AI
                    preview = result['stdout'][:500] + "..." if len(result['stdout']) > 500 else result['stdout']
                    print(f"--- STDOUT ---\n{preview}")
                if result['stderr']:
                    print(f"--- STDERR ---\n{result['stderr']}")
                
                # Feedback to AI
                result_str = f"Exit Code: {result['code']}\nSTDOUT: {result['stdout']}\nSTDERR: {result['stderr']}"
                messages.append({"role": "user", "content": f"COMMAND RESULT:\n{result_str}"})
                
            except Exception as e:
                msg = f"Error: Could not parse or run command. {e}"
                print(f"[!] {msg}")
                messages.append({"role": "user", "content": msg})
        else:
            prompt_fix = "I didn't see a command. If you are done, say FINISH:. If you need context, use RUN_COMMAND with 'cat'."
            messages.append({"role": "user", "content": prompt_fix})

if __name__ == "__main__":
    main()