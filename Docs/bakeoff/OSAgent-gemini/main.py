"""
OSAgent: Autonomous Ubuntu 24.04 LTS System Administration Agent

This agent provides an AI-powered interface for Ubuntu 24.04 LTS system administration
tasks with a strong focus on safety and stability. It operates in two modes:
1. Ask First (Default): Prompts for user confirmation before executing any action
2. Autonomous: Independently manages tasks within defined safety parameters

The agent uses a local LLM (via API_URL) to interpret user requests and determine
appropriate system administration actions, which are executed through a secure
terminal interface with comprehensive safety checks.
"""

import os
import re
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional

# --- CONFIGURATION ---
# API endpoint for the local LLM server (using llama.cpp or similar)
API_URL = "http://10.167.32.1:1234/v1/chat/completions"
# Temperature for LLM responses (lower = more deterministic)
MODEL_TEMPERATURE = 0.1
# Set to True for fully autonomous mode (use with caution)
MODEL_AUTOMATION = False
# Directory for storing session logs
LOG_DIR = "logs"

# To run this agent with proper dependency management:
# 1. Ensure you have uv installed: https://docs.astral.sh/uv/
# 2. Create and activate virtual environment: uv venv && source .venv/bin/activate
# 3. Install dependencies: uv pip install -r requirements.txt
# 4. Run the agent: python main.py

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
    },
    "Ubuntu2404LTSAdmin": {
        "description": "Ubuntu 24.04 LTS specific system administration knowledge.",
        "triggers": [
            "ubuntu",
            "24.04",
            "lts",
            "apt",
            "systemctl",
            "service",
            "network",
            "firewall",
            "ufw",
            "ssh",
            "users",
            "groups",
        ],
        "content": """
### SPECIALIZED CONTEXT: UBUNTU 24.04 LTS SYSTEM ADMINISTRATION ###
- **Package Management:** Use `apt update && apt upgrade -y` for regular updates. Use `apt install <package>` for installations.
- **Service Management:** Use `systemctl status|start|stop|restart|enable|disable <service>` for service control.
- **Network Configuration:** Use `nmcli` or `netplan` for network configuration. Check with `ip a` or `ip link`.
- **Firewall:** Use `ufw enable/disable` and `ufw allow|deny <port/protocol>` for firewall management.
- **SSH Hardening:** Ensure `PermitRootLogin no` in `/etc/ssh/sshd_config`. Use key-based authentication.
- **User Management:** Use `adduser`, `deluser`, `usermod` for user management. Manage groups with `groupadd`, `groupdel`, `usermod -aG`.
- **Logging:** Check logs with `journalctl -u <service>` or `tail -f /var/log/<logfile>`. Use `systemd-analyze` for boot time analysis.
- **Security:** Regularly run `apt upgrade --show-upgradable` to see available security updates. Enable automatic security updates.
- **Performance:** Use `htop`, `top`, `free -h`, `df -h` for resource monitoring. Use `systemctl list-unit-files` to see enabled services.
""",
    },
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

    def _ensure_dir(self):
        try:
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
        except OSError as e:
            print(f"Warning: Could not create log directory {self.directory}: {e}")
            # Fall back to current directory
            self.directory = "."

    def log(self, sender: str, message: str):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not hasattr(self, "log_file"):
                self.log_file = os.path.join(self.directory, f"session_{timestamp}.log")
            log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-' * 40}\n"
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except IOError as e:
            print(
                f"Warning: Could not write to log file {getattr(self, 'log_file', 'unknown')}: {e}"
            )


# --- TOOLS ---


class TerminalTool:
    # List of dangerous commands/patterns that should never be executed
    DANGEROUS_PATTERNS = [
        # Destructive file operations
        r"rm\s+-[rf]{1,2}",  # rm -r, rm -f, rm -rf
        r"rm\s+-[rf]{1,2}\s+/",  # rm -rf / (already covered but explicit)
        r">\s*/dev/(sd|hd|vd)",  # Writing directly to disk devices
        r"dd\s+if=.*of=/dev/(sd|hd|vd)",  # dd to disk devices
        r">\s*/",  # Redirecting to root directory
        # Fork bombs and resource exhaustion
        r":\(\)\s*{\s*:\|:\&\ };:",  # Classic fork bomb
        r"\(\)\s*{\s*.*\s*\&\s*}",  # Other fork bomb variants
        # System modification commands
        r"mkfs\.",  # Formatting filesystems
        r"fdisk",  # Partition manipulation
        r"parted",  # Partition manipulation
        r"fsck",  # Filesystem check (can be dangerous if misused)
        r"mount.*bind",  # Bind mounts (can be used maliciously)
        r"chroot",  # Changing root directory
        # Privilege escalation risks
        r"sudo\s+rm",  # sudo with remove commands
        r"su\s+-",  # Switching user
        r"sudo\s+su",  # Double sudo/su
        # Network dangers
        r"wget\s+.*\|\s*sh",  # Piping download to shell
        r"curl\s+.*\|\s*sh",  # Piping download to shell
        r"nc\s+.*\-e",  # Netcat with exec
        r"bash\s+.*i\s+>\s*&",  # Reverse shell
        # System control
        r"shutdown",  # Shutting down system
        r"reboot",  # Rebooting system
        r"halt",  # Halting system
        r"init\s+[0-6]",  # Changing runlevels
        r"systemctl\s+(stop|disable)",  # Stopping/disabling services
        # Dangerous utilities
        r">\s*&>",  # Redirecting both stdout and stderr to file (can overwrite important files)
        r">\s*/etc/",  # Writing to /etc directory
        r">\s*/boot/",  # Writing to /boot directory
        r">\s*/var/",  # Writing to /var directory (can fill logs)
    ]

    @staticmethod
    def _is_command_safe(command: str) -> tuple[bool, str]:
        """Check if a command is safe to execute.

        Returns:
            tuple: (is_safe, reason_if_unsafe)
        """
        command_lower = command.lower().strip()

        # Check against dangerous patterns
        for pattern in TerminalTool.DANGEROUS_PATTERNS:
            if re.search(pattern, command_lower, re.IGNORECASE):
                return False, f"Command matches dangerous pattern: {pattern}"

        # Additional safety checks
        # Prevent commands that try to modify critical system files without explicit allowance
        critical_paths = [
            r"/etc/passwd",
            r"/etc/shadow",
            r"/etc/gshadow",
            r"/etc/sudoers",
            r"/boot/",
            r"/dev/",
            r"/proc/sys/",
        ]

        for path in critical_paths:
            # Check for write operations to critical paths
            if re.search(rf">\s*{path}|>>\s*{path}|\|\s*tee\s*{path}", command_lower):
                return False, f"Attempt to write to critical path: {path}"

        return True, ""

    @staticmethod
    def execute(command: str) -> str:
        # First check if command is safe
        is_safe, reason = TerminalTool._is_command_safe(command)
        if not is_safe:
            return f"Error: Command blocked by safety filter. {reason}"

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

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response."
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


def print_usage():
    """Print usage information"""
    print("""
OSAgent: AI-Powered Ubuntu System Administration Agent

Usage:
  python main.py                           # Interactive mode (default)
  python main.py "your prompt here"       # Single shot mode
  python main.py -l "your goal here"      # Loop/Agentic mode
  python main.py --agentic "your goal here" # Loop/Agentic mode
  python main.py -h                       # Show this help

Modes:
  Interactive mode: Continuous conversation with the agent
  Single shot mode: Process one prompt then exit
  Loop/Agentic mode: Continuously work toward achieving a goal

Examples:
  python main.py
  python main.py "Check system status"
  python main.py -l "Keep web server running and responsive"
  python main.py --agentic "Monitor logs and alert on errors"
""")


if __name__ == "__main__":
    # Check for command-line flags
    if len(sys.argv) > 1:
        # Check for loop/agentic mode flag
        if sys.argv[1] in ["-l", "--loop", "-a", "--agentic"] and len(sys.argv) > 2:
            # Loop/Agentic mode: Continuous operation with initial prompt as goal
            initial_prompt = " ".join(sys.argv[2:])
            run_agentic_loop(initial_prompt)
        elif sys.argv[1] in ["-h", "--help"]:
            print_usage()
            sys.exit(0)
        else:
            # Single shot mode: All arguments form the prompt
            initial_prompt = " ".join(sys.argv[1:])
            run_agentic_single_shot(initial_prompt)
    else:
        # Run the interactive session if no arguments provided
        run_agentic_session()


def run_agentic_single_shot(initial_prompt: str):
    """Run a single interaction with the provided prompt"""
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response."
    )

    specialized_context = ContextManager.get_relevant_context(initial_prompt)
    current_system_message = base_system_prompt
    if specialized_context:
        current_system_message += f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"

    messages = [{"role": "system", "content": current_system_message}]
    messages.append({"role": "user", "content": initial_prompt})

    print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    print(f"User> {initial_prompt}")

    # Process the interaction
    while True:
        print("Agent thinking...", end="\r")
        response = AgentLLM.chat(messages)
        print(f"\rAgent: {response}\n")

        logger.log("USER", initial_prompt)
        logger.log("AGENT", response)

        match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
        if match:
            cmd = match.group(1).strip()
            print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")

            if MODEL_AUTOMATION:
                confirm = "y"
            else:
                confirm = input("[y/n] > ").lower()

            if confirm == "y":
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


def run_agentic_loop(initial_goal: str):
    """Run in continuous agentic loop mode"""
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent working in continuous agentic mode. "
        'Your goal is: "{}"\n\n'
        "In this mode, you will continuously work toward achieving this goal by:\n"
        "1. Assessing the current system state\n"
        "2. Determining what actions would move you closer to your goal\n"
        "3. Proposing those actions for execution\n"
        "4. Learning from the results\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response.\n"
        "If you believe your goal has been achieved, state this clearly in your response."
    ).format(initial_goal)

    print(f"\n--- AGENTIC LOOP MODE READY (Logging to {LOG_DIR}/) ---")
    print(f"Goal: {initial_goal}")
    print("Press Ctrl+C to exit loop mode\n")

    # Initialize conversation with goal assessment
    messages = [{"role": "system", "content": base_system_prompt}]

    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            # Agent thinks about what to do next
            print("Agent thinking...", end="\r")
            response = AgentLLM.chat(messages)
            print(f"\rAgent: {response}\n")

            logger.log("AGENT", response)

            # Check if agent believes goal is achieved
            if (
                "goal has been achieved" in response.lower()
                or "goal achieved" in response.lower()
            ):
                print("\n[!] Agent indicates goal has been achieved!")
                logger.log("SYSTEM", "Agent indicated goal achievement")
                break

            # Look for execution commands
            match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
            if match:
                cmd = match.group(1).strip()
                print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")

                # In loop mode, we still ask for confirmation for safety
                # but make it clear this is an autonomous agent working toward a goal
                confirm = input("[y/n/q] (q to quit loop) > ").lower()

                if confirm == "q":
                    print("[!] Quitting agentic loop")
                    logger.log("SYSTEM", "User quit agentic loop")
                    break
                elif confirm == "y":
                    logger.log("SYSTEM", f"Executing Command: {cmd}")
                    execution_result = terminal.execute(cmd)
                    logger.log("TERMINAL_OUTPUT", execution_result)
                    print(f"[*] Output:\n{execution_result}")

                    # Add result to conversation for context
                    messages.append({"role": "assistant", "content": response})
                    messages.append(
                        {
                            "role": "user",
                            "content": f"COMMAND OUTPUT:\n{execution_result}",
                        }
                    )
                else:
                    execution_result = "User denied execution."
                    logger.log("SYSTEM", "User denied command execution.")
                    print("[!] Execution denied.")

                    # Still add to conversation so agent learns from denial
                    messages.append({"role": "assistant", "content": response})
                    messages.append(
                        {
                            "role": "user",
                            "content": f"COMMAND OUTPUT:\n{execution_result}",
                        }
                    )
            else:
                # No execution command, just add to conversation and continue
                logger.log("AGENT", response)
                messages.append({"role": "assistant", "content": response})

                # Ask if user wants to continue
                cont = input("\nContinue? [y/n] > ").lower()
                if cont != "y":
                    print("[!] Exiting agentic loop")
                    logger.log("SYSTEM", "User exited agentic loop")
                    break

    except KeyboardInterrupt:
        print("\n[!] Agentic loop interrupted by user")
        logger.log("SYSTEM", "Agentic loop interrupted by user (Ctrl+C)")
