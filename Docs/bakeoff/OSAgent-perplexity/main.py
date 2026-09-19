import os
import re
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional

# --- CONFIGURATION ---
API_URL = "http://10.167.32.1:1234/v1/chat/completions"
MODEL_TEMPERATURE = 0.1
MODEL_AUTOMATION = False  # Default to ask-first mode for safety
LOG_DIR = "logs"
# Automation mode restrictions
AUTOMATION_MAX_COMMANDS_PER_MINUTE = 10  # Rate limiting
AUTOMATION_REQUIRED_CONFIRMATION_INTERVAL = 5  # Require reconfirmation after N commands in automation mode

# Track automation mode usage for safety
automation_command_count = 0
last_automation_reset_time = None

# --- EMBEDDED KNOWLEDGE BASE ---
KNOWLEDGE_BASE = {
    "BashScriptMaster": {
        "description": "Advanced shell scripting best practices and automation logic.",
        "triggers": ["bash", "shell", "script", "loop", "variable", "pipe", "sed", "awk", "grep", "automation"],
        "content": """
### SPECIALIZED CONTEXT: PROFESSIONAL BASH SCRIPTING ###
- **Strict Mode:** Every script suggested must start with `set -euo pipefail`.
- **Portability:** Use `#!/usr/bin/env bash`.
- **Syntax:** Use `[[ ]]` for tests and `$(...)` for command substitution. Quote all variables.
- **Functionality:** Group logic into functions using `local` variables.
- **Performance:** Prefer `awk` or `sed` for large file processing.
"""
    }
}

# --- LOGGING SYSTEM ---

class SessionLogger:
    """
    Handles file-based logging for all agent communications.
    """
    def __init__(self, directory: str):
        self.directory = directory
        self._ensure_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.directory, f"session_{timestamp}.log")
        # Also create a security audit log
        self.security_log_file = os.path.join(self.directory, f"security_{timestamp}.log")

    def _ensure_dir(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def log(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-'*40}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def log_security(self, event_type: str, details: str):
        """Log security-related events to a separate audit log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] SECURITY [{event_type}]:\n{details}\n{'-'*40}\n"
        with open(self.security_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

# --- TOOLS ---

class TerminalTool:
    # Comprehensive blacklist of dangerous commands and patterns
    DANGEROUS_PATTERNS = [
        # Destructive file operations
        r"rm\s+-[rf]",  # rm with -r or -f flags
        r">\s*/dev/",   # Writing to device files
        r"dd\s+if=",    # Direct disk operations
        r">\s*/",       # Writing to root directory
        
        # Privilege escalation
        r"sudo\s+",     # sudo commands (could be restricted further)
        r"su\s+",       # switch user
        r"chmod\s+[0-9]*\s+.*\/", # chmod on system paths
        
        # System modification
        r"mkfs\s+",     # filesystem formatting
        r"fdisk\s+",    # disk partitioning
        r"parted\s+",   # partition editing
        r">\s*/etc/",   # writing to config files
        r">\s*/boot/",  # writing to boot directory
        
        # Dangerous shell constructs
        r":(){.*};:",   # fork bomb
        r"\|.*\||.*&&.*\||.*\||.*;", # Complex chaining that could hide malicious intent
        
        # Network dangers (in automated mode)
        r"wget\s+.*http", # downloading from internet
        r"curl\s+.*http", # transferring data from internet
        r"nc\s+",       # netcat
        r"telnet\s+",   # telnet
        
        # Information gathering that could be malicious
        r"cat\s+/etc/passwd", # reading password file
        r"cat\s+/etc/shadow", # reading shadow file
        r"iptables\s+",   # firewall modification
        r"firewall-cmd\s+", # firewall modification
    ]
    
    # Whitelist of safe commands (only used in strict mode)
    SAFE_COMMANDS = [
        "ls", "pwd", "cat", "grep", "echo", "ps", "df", "du", "free", 
        "uname", "whoami", "date", "timeout", "head", "tail", "wc",
        "find", "which", "whereis", "man", "info", "touch", "mkdir",
        "cp", "mv", "chmod", "chown", "tar", "zip", "unzip", "gzip", "gunzip"
    ]
    
    @staticmethod
    def _is_command_safe(command: str, automation_mode: bool = False) -> tuple[bool, str]:
        """
        Check if a command is safe to execute.
        Returns (is_safe, reason_if_unsafe)
        """
        command_lower = command.lower().strip()
        
        # Empty command check
        if not command_lower:
            return False, "Empty command"
            
        # Check against dangerous patterns
        import re
        for pattern in TerminalTool.DANGEROUS_PATTERNS:
            if re.search(pattern, command_lower, re.IGNORECASE):
                return False, f"Command matches dangerous pattern: {pattern}"
        
        # In automation mode, only allow whitelisted commands
        if automation_mode:
            # Extract the base command (first word)
            parts = command_lower.split()
            if not parts:
                return False, "Cannot determine base command"
                
            base_cmd = parts[0]
            # Check if base command is in whitelist
            if base_cmd not in TerminalTool.SAFE_COMMANDS:
                return False, f"Command '{base_cmd}' not in automation mode whitelist"
                
            # Additional checks for specific commands with arguments
            if base_cmd in ["chmod", "chown"] and len(parts) > 2:
                # Prevent changing permissions/ownership of system directories
                system_paths = ["/etc", "/bin", "/sbin", "/usr", "/var", "/root", "/boot", "/lib", "/lib64"]
                for arg in parts[2:]:  # Skip command and first argument (mode/user)
                    if arg.startswith("/"):
                        for sys_path in system_paths:
                            if arg.startswith(sys_path):
                                return False, f"Modifying system path {arg} not allowed in automation mode"
        
        return True, "Command deemed safe"
    
    @staticmethod
    def execute(command: str, automation_mode: bool = False) -> str:
        # Check if we're in automation mode (would be passed from orchestrator)
        # For now, we'll check a global or could pass it as parameter
        # We'll enhance this in the orchestrator to pass automation mode info
        
        # Basic safety check
        is_safe, reason = TerminalTool._is_command_safe(command, automation_mode)
        if not is_safe:
            # In automation mode, provide less detailed error information
            if automation_mode:
                return "Error: Command blocked by security policy."
            else:
                return f"Error: Command blocked by safety filter. Reason: {reason}"
            
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout if result.stdout else ""
            errors = result.stderr if result.stderr else ""
            if result.returncode != 0:
                # In automation mode, provide less detailed error information
                if automation_mode:
                    return f"Error: Command failed with exit code {result.returncode}."
                else:
                    return f"Execution Error (Exit Code {result.returncode}):\n{errors}"
            return output if output.strip() else f"Success (no output). Stderr: {errors}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            # In automation mode, provide less detailed error information
            if automation_mode:
                return "Error: Command execution failed."
            else:
                return f"Error executing command: {str(e)}"

# --- AGENT CORE ---

class ContextManager:
    @staticmethod
    def get_relevant_context(user_input: str) -> str:
        disclosed_text = ""
        input_lower = user_input.lower()
        for name, data in KNOWLEDGE_BASE.items():
            if any(trigger in input_lower for trigger in data.get('triggers', [])):
                disclosed_text += f"\n{data['content']}\n"
        return disclosed_text

class AgentLLM:
    @staticmethod
    def chat(messages: List[Dict]) -> str:
        payload = {"messages": messages, "temperature": MODEL_TEMPERATURE, "stream": False, "stop": ["User>", "System:"]}
        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            # Return generic error message to prevent information leakage
            return "Error: Unable to connect to language model service."

# --- ORCHESTRATOR ---

def run_agentic_session(initial_prompt=None, single_interaction=False):
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)
    
    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response."
    )

    if initial_prompt is not None and not single_interaction:
        print(f"\n--- AGENTIC TERMINAL READY with initial prompt (Logging to {LOG_DIR}/) ---")
    elif initial_prompt is not None and single_interaction:
        print(f"\n--- AGENTIC TERMINAL SINGLE INTERACTION (Logging to {LOG_DIR}/) ---")
    else:
        print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    
    history = []
    
    # Automation mode tracking variables
    automation_command_count = 0
    last_automation_reset_time = None

    # If we have an initial prompt, process it first
    if initial_prompt is not None:
        user_input = initial_prompt
        
        # Skip the normal input prompt for the initial prompt
        if user_input.lower() in ['exit', 'quit', 'q']:
            logger.log("SYSTEM", "User terminated session.")
            return
        
        logger.log("USER", user_input)
        
        specialized_context = ContextManager.get_relevant_context(user_input)
        current_system_message = base_system_prompt
        if specialized_context:
            current_system_message += f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"
        
        messages = [{"role": "system", "content": current_system_message}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        history.append({"role": "user", "content": user_input})
        
        while True:
               print("Agent thinking...", end="\r")
               response = AgentLLM.chat(messages)
               print(f"\rAgent: {response}\n")
               
               logger.log("AGENT", response)
               history.append({"role": "assistant", "content": response})
               messages.append({"role": "assistant", "content": response})
   
               match = re.search(r'\[\[EXEC:\s*(.*?)\s*\]\]', response, re.DOTALL)
               if match:
                   cmd = match.group(1).strip()
                   print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")
                   
                   # Automation mode safeguards
                   if MODEL_AUTOMATION:
                       # Rate limiting for automation mode
                       import time
                       current_time = time.time()
                       
                       # Reset counter if a minute has passed
                       if last_automation_reset_time is None or (current_time - last_automation_reset_time) > 60:
                           automation_command_count = 0
                           last_automation_reset_time = current_time
                       
                       # Check if we've exceeded the rate limit
                       if automation_command_count >= AUTOMATION_MAX_COMMANDS_PER_MINUTE:
                           print(f"[!] Automation mode rate limit exceeded ({AUTOMATION_MAX_COMMANDS_PER_MINUTE} commands/minute).")
                           execution_result = "Error: Automation mode rate limit exceeded."
                           logger.log("SYSTEM", "Automation mode rate limit exceeded.")
                           logger.log_security("RATE_LIMIT_EXCEEDED", f"Automation mode rate limit exceeded. Count: {automation_command_count}")
                           confirm = 'n'  # Set confirm to 'n' to skip execution
                       else:
                           # Require periodic reconfirmation in automation mode
                           if automation_command_count > 0 and automation_command_count % AUTOMATION_REQUIRED_CONFIRMATION_INTERVAL == 0:
                               print(f"\n[!!] Automation mode reconfirmation required after {automation_command_count} commands.")
                               confirm = input("[y/n] > ").lower()
                               if confirm != 'y':
                                   execution_result = "User denied execution during reconfirmation."
                                   logger.log("SYSTEM", "User denied execution during automation mode reconfirmation.")
                                   logger.log_security("USER_DENIED_RECONFIRMATION", f"User denied execution during automation mode reconfirmation after {automation_command_count} commands.")
                                   print("[!] Execution denied.")
                               else:
                                   confirm = 'y'  # Proceed with execution
                           else:
                               confirm = 'y'  # Automatic confirmation in automation mode
                   else:
                       confirm = input("[y/n] > ").lower()
                   
                   if confirm == 'y':
                       logger.log("SYSTEM", f"Executing Command: {cmd}")
                       execution_result = terminal.execute(cmd, automation_mode=MODEL_AUTOMATION)
                       logger.log("TERMINAL_OUTPUT", execution_result)
                       print(f"[*] Output:\n{execution_result}")
                       
                       # Increment automation command counter if in automation mode
                       if MODEL_AUTOMATION and execution_result and not execution_result.startswith("Error:"):
                           automation_command_count += 1
                       
                       # Log if command was blocked by safety filters
                       if execution_result.startswith("Error: Command blocked by safety filter"):
                           logger.log_security("COMMAND_BLOCKED", f"Blocked command: {cmd}. Reason: {execution_result}")
                   else:
                       execution_result = "User denied execution."
                       logger.log("SYSTEM", "User denied command execution.")
                       logger.log_security("USER_DENIED", f"User denied command: {cmd}")
                       print("[!] Execution denied.")
 
                   messages.append({"role": "user", "content": f"COMMAND OUTPUT:\n{execution_result}"})
                   continue 
               else:
                   break
                   
        # If single_interaction is True, we're done after processing the initial prompt
        if single_interaction:
            return
    
    # Continue with interactive mode (unless we just did a single interaction and want to exit)
    if initial_prompt is None or not single_interaction:
        while True:
            try:
                user_input = input("\nUser> ")
            except KeyboardInterrupt:
                break
            
            # Input validation and sanitization
            if not user_input or not user_input.strip():
                print("[!] Empty input not allowed.")
                continue
                
            # Limit input length to prevent DoS
            if len(user_input) > 1000:
                print("[!] Input too long (max 1000 characters).")
                continue
                
            # Basic sanitization - remove null bytes and control characters except common whitespace
            sanitized_input = ""
            for char in user_input:
                if ord(char) == 0:  # Null byte
                    continue
                elif ord(char) < 32 and char not in ['\t', '\n', '\r']:  # Control characters except common whitespace
                    continue
                else:
                    sanitized_input += char
            
            user_input = sanitized_input.strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                logger.log("SYSTEM", "User terminated session.")
                break
            
            logger.log("USER", user_input)
            
            specialized_context = ContextManager.get_relevant_context(user_input)
            current_system_message = base_system_prompt
            if specialized_context:
                current_system_message += f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"
            
            messages = [{"role": "system", "content": current_system_message}]
            messages.extend(history)
            messages.append({"role": "user", "content": user_input})
            history.append({"role": "user", "content": user_input})
            
            while True:
                   print("Agent thinking...", end="\r")
                   response = AgentLLM.chat(messages)
                   print(f"\rAgent: {response}\n")
                   
                   logger.log("AGENT", response)
                   history.append({"role": "assistant", "content": response})
                   messages.append({"role": "assistant", "content": response})
       
                   match = re.search(r'\[\[EXEC:\s*(.*?)\s*\]\]', response, re.DOTALL)
                   if match:
                       cmd = match.group(1).strip()
                       print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")
                       
                       # Automation mode safeguards
                       if MODEL_AUTOMATION:
                           # Rate limiting for automation mode
                           import time
                           current_time = time.time()
                           
                           # Reset counter if a minute has passed
                           if last_automation_reset_time is None or (current_time - last_automation_reset_time) > 60:
                               automation_command_count = 0
                               last_automation_reset_time = current_time
                           
                           # Check if we've exceeded the rate limit
                           if automation_command_count >= AUTOMATION_MAX_COMMANDS_PER_MINUTE:
                               print(f"[!] Automation mode rate limit exceeded ({AUTOMATION_MAX_COMMANDS_PER_MINUTE} commands/minute).")
                               execution_result = "Error: Automation mode rate limit exceeded."
                               logger.log("SYSTEM", "Automation mode rate limit exceeded.")
                               logger.log_security("RATE_LIMIT_EXCEEDED", f"Automation mode rate limit exceeded. Count: {automation_command_count}")
                               confirm = 'n'  # Set confirm to 'n' to skip execution
                           else:
                               # Require periodic reconfirmation in automation mode
                               if automation_command_count > 0 and automation_command_count % AUTOMATION_REQUIRED_CONFIRMATION_INTERVAL == 0:
                                   print(f"\n[!!] Automation mode reconfirmation required after {automation_command_count} commands.")
                                   confirm = input("[y/n] > ").lower()
                                   if confirm != 'y':
                                       execution_result = "User denied execution during reconfirmation."
                                       logger.log("SYSTEM", "User denied execution during automation mode reconfirmation.")
                                       logger.log_security("USER_DENIED_RECONFIRMATION", f"User denied execution during automation mode reconfirmation after {automation_command_count} commands.")
                                       print("[!] Execution denied.")
                                   else:
                                       confirm = 'y'  # Proceed with execution
                               else:
                                   confirm = 'y'  # Automatic confirmation in automation mode
                       else:
                           confirm = input("[y/n] > ").lower()
                       
                       if confirm == 'y':
                           logger.log("SYSTEM", f"Executing Command: {cmd}")
                           execution_result = terminal.execute(cmd, automation_mode=MODEL_AUTOMATION)
                           logger.log("TERMINAL_OUTPUT", execution_result)
                           print(f"[*] Output:\n{execution_result}")
                           
                           # Increment automation command counter if in automation mode
                           if MODEL_AUTOMATION and execution_result and not execution_result.startswith("Error:"):
                               automation_command_count += 1
                           
                           # Log if command was blocked by safety filters
                           if execution_result.startswith("Error: Command blocked by safety filter"):
                               logger.log_security("COMMAND_BLOCKED", f"Blocked command: {cmd}. Reason: {execution_result}")
                       else:
                           execution_result = "User denied execution."
                           logger.log("SYSTEM", "User denied command execution.")
                           logger.log_security("USER_DENIED", f"User denied command: {cmd}")
                           print("[!] Execution denied.")
   
                       messages.append({"role": "user", "content": f"COMMAND OUTPUT:\n{execution_result}"}")
                       continue 
                   else:
                       break

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OSAgent - AI-driven autonomous terminal assistant")
    parser.add_argument("--prompt", "-p", type=str, help="Initial prompt to send to the agent")
    parser.add_argument("--loop-prompt", "-l", type=str, help="Prompt to run repeatedly in a loop")
    parser.add_argument("--interval", "-i", type=int, default=60, help="Interval in seconds between loop prompt executions (default: 60)")
    
    args = parser.parse_args()
    
    if args.loop_prompt:
        # Loop mode: run the prompt repeatedly
        import time
        print(f"--- OSAgent Loop Mode: Repeating prompt every {args.interval} seconds ---")
        print(f"Prompt: {args.loop_prompt}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n[Loop Iteration] Sending prompt: {args.loop_prompt}")
                # Run a single interaction with the loop prompt
                run_agentic_session(args.loop_prompt, single_interaction=True)
                
                print(f"--- Sleeping for {args.interval} seconds ---")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n--- Loop mode stopped by user ---")
    elif args.prompt:
        # Single prompt mode: run with initial prompt then continue interactively
        run_agentic_session(args.prompt)
    else:
        # Normal interactive mode
        run_agentic_session()