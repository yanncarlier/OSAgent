import os
import re
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# --- CONFIGURATION ---
import os

API_URL = os.getenv("OSAGENT_API_URL", "http://10.167.32.1:1234/v1/chat/completions")
MODEL_TEMPERATURE = float(os.getenv("OSAGENT_MODEL_TEMPERATURE", "0.1"))
MODEL_AUTOMATION = os.getenv("OSAGENT_MODEL_AUTOMATION", "False").lower() == "true"
LOG_DIR = os.getenv("OSAGENT_LOG_DIR", "logs")
MAX_COMMAND_EXECUTIONS = int(os.getenv("OSAGENT_MAX_COMMAND_EXECUTIONS", "50"))

# --- EMBEDDED KNOWLEDGE BASE ---
KNOWLEDGE_BASE = {
    "BashScriptMaster": {
        "description": "Advanced shell scripting best practices and automation logic.",
        "triggers": [
            "bash",
            "shell",
            "script",
            "loop",
            "variable",
            "pipe",
            "sed",
            "awk",
            "grep",
            "automation",
        ],
        "content": """
### SPECIALIZED CONTEXT: PROFESSIONAL BASH SCRIPTING ###
- **Strict Mode:** Every script suggested must start with `set -euo pipefail`.
- **Portability:** Use `#!/usr/bin/env bash`.
- **Syntax:** Use `[[ ]]` for tests and `$(...)` for command substitution. Quote all variables.
- **Functionality:** Group logic into functions using `local` variables.
- **Performance:** Prefer `awk` or `sed` for large file processing.
""",
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
        # Log session start
        self.log("SYSTEM", f"Session started. Log file: {self.log_file}")

    def _ensure_dir(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def log(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-' * 40}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except IOError as e:
            # Fallback to stderr if logging fails
            print(f"Logging error: {e}", file=sys.stderr)


# --- TOOLS ---


class TerminalTool:
    # List of dangerous command patterns to block
    DANGEROUS_PATTERNS = [
        # File system destruction
        r"rm\s+-rf\s+/",  # rm -rf /
        r"rm\s+-rf\s+/\*",  # rm -rf /*
        r"mkfs",  # Format filesystem commands
        r"dd\s+if=.*of=/dev/sd",  # Direct disk writes
        r">\s*/dev/sd",  # Redirects to disk devices
        # Fork bombs and resource exhaustion
        r":\(\|\)&\|:\)&",  # Fork bomb variants
        r"\[\s*\]\s*&\s*\[\s*\]",  # Array fork bomb
        # Privilege escalation and backdoors
        r"sudo\s+.*",  # sudo commands (could be restricted further)
        r"su\s+",  # Switch user
        r"chmod\s+.*[47]",  # Setting SUID/SGID bits
        r"chown\s+.*root",  # Changing ownership to root
        # Network and data exfiltration
        r"nc\s+-l",  # Netcat listener
        r"telnet\s+",  # Telnet
        r"wget\s+.*http",  # wget with URLs
        r"curl\s+.*http",  # curl with URLs
        r"/etc/passwd",  # Access to password file
        r"/etc/shadow",  # Access to shadow file
        # System manipulation
        r"mount\s+",  # Mount commands
        r"umount\s+",  # Unmount commands
        r"iptables\s+",  # Firewall manipulation
        r"systemctl\s+",  # Service control
        r"service\s+",  # Service control (older)
        # Process manipulation
        r"kill\s+-9\s+1",  # Kill init process
        r"pkill\s+",  # Process killing
        r"killall\s+",  # Process killing by name
        # Reconnaissance
        r"ps\s+aux",  # Detailed process listing
        r"netstat\s+-",  # Network statistics
        r"ss\s+-",  # Socket statistics
        r"lsof\s+",  # List open files
        r"ifconfig\s+",  # Network interfaces
        r"ip\s+addr\s+",  # IP address info
        # Archive and compression (could be used to hide data)
        r"tar\s+.*czf",  # Creating compressed archives
        r"zip\s+.*\-r",  # Recursive zip
    ]

    @staticmethod
    def execute(command: str) -> str:
        # Check against dangerous patterns
        import re

        for pattern in TerminalTool.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return f"Error: Command blocked by safety filter - matches dangerous pattern: {pattern}"

        # Additional safety checks
        # Block commands with excessive length (potential buffer overflow attempts)
        if len(command) > 500:
            return "Error: Command too long - potential security risk."

        # Block commands with too many pipes or redirects (potential for obfuscation)
        if command.count("|") > 10 or command.count(">") > 5 or command.count("<") > 5:
            return "Error: Command has excessive pipes/redirects - potential security risk."

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout if result.stdout else ""
            errors = result.stderr if result.stderr else ""
            if result.returncode != 0:
                return f"Execution Error (Exit Code {result.returncode}):\n{errors}"
            return (
                output if output.strip() else f"Success (no output). Stderr: {errors}"
            )
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"


# --- AGENT CORE ---


class ContextManager:
    @staticmethod
    def get_relevant_context(user_input: str) -> str:
        disclosed_text = ""
        input_lower = user_input.lower()
        for name, data in KNOWLEDGE_BASE.items():
            if any(trigger in input_lower for trigger in data.get("triggers", [])):
                disclosed_text += f"\n{data['content']}\n"
        return disclosed_text


class AgentLLM:
    @staticmethod
    def chat(messages: List[Dict]) -> str:
        payload = {
            "messages": messages,
            "temperature": MODEL_TEMPERATURE,
            "stream": False,
            "stop": ["User>", "System:"],
        }
        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"


# --- ORCHESTRATOR ---


def run_agentic_session():
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    # Track command executions for rate limiting
    command_count = 0

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response.\n\n"
        "**SAFETY:** This agent operates in a risk-averse mode prioritizing system stability. "
        "All commands are filtered through safety mechanisms. Never attempt to bypass security controls."
    )

    print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    history = []

    while True:
        try:
            user_input = input("\nUser> ")
        except KeyboardInterrupt:
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            logger.log("SYSTEM", "User terminated session.")
            break

        logger.log("USER", user_input)

        specialized_context = ContextManager.get_relevant_context(user_input)
        current_system_message = base_system_prompt
        if specialized_context:
            current_system_message += (
                f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"
            )

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

            match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
            if match:
                cmd = match.group(1).strip()
                print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")

                if MODEL_AUTOMATION:
                    confirm = "y"
                else:
                    confirm = input("[y/n] > ").lower()

                if confirm == "y":
                    # Rate limit command executions
                    command_count += 1
                    if command_count > MAX_COMMAND_EXECUTIONS:
                        execution_result = f"Error: Command execution limit exceeded ({MAX_COMMAND_EXECUTIONS}). Please restart the session to continue."
                        logger.log("SYSTEM", execution_result)
                        print(f"[!] {execution_result}")
                    else:
                        logger.log("SYSTEM", f"Executing Command: {cmd}")
                        execution_result = terminal.execute(cmd)
                        logger.log("TERMINAL_OUTPUT", execution_result)
                        print(f"[*] Output:\n{execution_result}")
                else:
                    execution_result = "User denied execution."
                    logger.log("SYSTEM", "User denied command execution.")
                    print("[!] Execution denied.")

                messages.append(
                    {"role": "user", "content": f"COMMAND OUTPUT:\n{execution_result}"}
                )
                continue
            else:
                break


def run_single_prompt(prompt: str):
    """Run a single prompt and exit"""
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    # Track command executions for rate limiting
    command_count = 0

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response.\n\n"
        "**SAFETY:** This agent operates in a risk-averse mode prioritizing system stability. "
        "All commands are filtered through safety mechanisms. Never attempt to bypass security controls."
    )

    print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    history = []

    # Add the initial prompt
    logger.log("USER", prompt)
    specialized_context = ContextManager.get_relevant_context(prompt)
    current_system_message = base_system_prompt
    if specialized_context:
        current_system_message += f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"

    messages = [{"role": "system", "content": current_system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    history.append({"role": "user", "content": prompt})

    # Process the prompt
    while True:
        print("Agent thinking...", end="\r")
        response = AgentLLM.chat(messages)
        print(f"\rAgent: {response}\n")

        logger.log("AGENT", response)
        history.append({"role": "assistant", "content": response})
        messages.append({"role": "assistant", "content": response})

        match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
        if match:
            cmd = match.group(1).strip()
            print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")

            if MODEL_AUTOMATION:
                confirm = "y"
            else:
                confirm = input("[y/n] > ").lower()

            if confirm == "y":
                # Rate limit command executions
                command_count += 1
                if command_count > MAX_COMMAND_EXECUTIONS:
                    execution_result = f"Error: Command execution limit exceeded ({MAX_COMMAND_EXECUTIONS}). Please restart the session to continue."
                    logger.log("SYSTEM", execution_result)
                    print(f"[!] {execution_result}")
                else:
                    logger.log("SYSTEM", f"Executing Command: {cmd}")
                    execution_result = terminal.execute(cmd)
                    logger.log("TERMINAL_OUTPUT", execution_result)
                    print(f"[*] Output:\n{execution_result}")
            else:
                execution_result = "User denied execution."
                logger.log("SYSTEM", "User denied command execution.")
                print("[!] Execution denied.")

            messages.append(
                {"role": "user", "content": f"COMMAND OUTPUT:\n{execution_result}"}
            )
            continue
        else:
            break

    print("\nSession completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OSAgent - AI-Powered Terminal Assistant"
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="Single prompt to execute. If not provided, runs in interactive mode.",
    )
    parser.add_argument(
        "-l",
        "--loop",
        action="store_true",
        help="Run in continuous loop mode (requires --prompt). Agent will re-prompt after each completion.",
    )

    args = parser.parse_args()

    if args.prompt:
        if args.loop:
            print("Running in loop mode. Press Ctrl+C to exit.")
            try:
                while True:
                    run_single_prompt(args.prompt)
                    print("\n--- Press Enter for next iteration or Ctrl+C to exit ---")
                    input()
            except KeyboardInterrupt:
                print("\nExiting loop mode.")
        else:
            run_single_prompt(args.prompt)
    else:
        # Original interactive mode
        run_agentic_session()
