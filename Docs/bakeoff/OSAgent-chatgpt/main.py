import os
import re
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional
import shlex
import argparse
import time


# --- VIRTUAL ENVIRONMENT CHECK ---
def check_virtual_environment():
    """Warn if not running in the project's virtual environment."""
    venv_path = os.path.join(os.path.dirname(__file__), ".venv")
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # We're in a virtual environment
        if not os.path.samefile(sys.prefix, venv_path):
            print(f"Warning: Not using project virtual environment at {venv_path}")
            print(f"Current Python: {sys.executable}")
            print(f"Expected Python: {os.path.join(venv_path, 'bin', 'python')}")
    elif not (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        # Not in any virtual environment
        print(f"Warning: Not running in a virtual environment.")
        print(f"Please activate the project virtual environment:")
        print(f"  source {os.path.join(venv_path, 'bin', 'activate')}")
        print(
            f"Or run with: {os.path.join(venv_path, 'bin', 'python')} {os.path.basename(__file__)}"
        )


# --- CONFIGURATION ---
API_URL = "http://10.167.32.1:1234/v1/chat/completions"
MODEL_TEMPERATURE = 0.1
MODEL_AUTOMATION = False
LOG_DIR = "logs"
SAFETY_LEVEL = "strict"  # Options: "permissive", "moderate", "strict"

# --- ENHANCED SAFETY SYSTEM ---
DANGEROUS_COMMANDS = [
    # Destructive commands
    r"rm\s+-rf\s+/",
    r":(){ :|:& };:",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r">\s*/dev/sd",
    r"chmod\s+-R\s+777\s+/",
    r">\s*/etc/passwd",
    r">\s*/etc/shadow",
    r"mv\s+/.*/\s+/dev/null",
    # Privilege escalation risks
    r"sudo\s+rm",
    r"su\s+-c",
    r"echo\s+.*>\s*/etc/sudoers",
    # System modification risks
    r"systemctl\s+disable\s+.*ssh",
    r"service\s+.*stop\s+.*ssh",
    r"iptables\s+-F",
    r"ufw\s+disable",
    # Network risks
    r"wget\s+http.*\|\s*bash",
    r"curl\s+.*\|\s*bash",
    r"nc\s+-l\s+.*>\s*/dev/tcp",
]

SAFE_COMMAND_PATTERNS = [
    # Safe system administration commands
    r"^systemctl\s+(status|show|is-active|is-enabled)\s+",
    r"^service\s+.*\s+(status|)",
    r"^df\s+-h",
    r"^du\s+-sh",
    r"^free\s+-h",
    r"^top\s+-b\s+-n\s+1",
    r"^ps\s+aux",
    r"^ls\s+(-[a-zA-Z]*l[a-zA-Z]*)?\s+",
    r"^cat\s+",
    r"^grep\s+",
    r"^tail\s+",
    r"^head\s+",
    r"^mkdir\s+-p\s+",
    r"^cp\s+",
    r"^mv\s+(?!/)",  # mv but not to root
    r"^chmod\s+[0-7]{3,4}\s+",  # chmod with numeric permissions
    r"^chown\s+[a-zA-Z0-9_.:-]+\s+[a-zA-Z0-9_.:-]+\s+",  # chown user:group file
    r"^find\s+/[^ ]*\s+-type\s+f\s+-name\s+",
    r"^tar\s+-[czx]",
    r"^gzip\s+",
    r"^gunzip\s+",
    r"^apt\s+update",
    r"^apt\s+list\s+--upgradable",
    r"^apt-cache\s+search",
    r"^which\s+",
    r"^whoami",
    r"^hostname",
    r"^date",
    r"^uname\s+-a",
    r"^lsb_release\s+-a",
    r"^netstat\s+-tuln",
    r"^ss\s+-tuln",
    r"^ping\s+-c\s+[0-9]+\s+",
    r"^traceroute\s+",
    r"^mtr\s+-r",
    r"^journalctl\s+-n\s+[0-9]+",
    r"^dmesg\s+-T",
    r"^lsblk",
    r"^blkid",
    r"^fdisk\s+-l",
    r"^df\s+-h",
    r"^du\s+-sh",
]

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
    "UbuntuSystemAdmin": {
        "description": "Ubuntu 24.04 LTS specific system administration guidelines.",
        "triggers": [
            "ubuntu",
            "apt",
            "systemctl",
            "service",
            "package",
            "update",
            "upgrade",
        ],
        "content": """
### SPECIALIZED CONTEXT: UBUNTU 24.04 LTS SYSTEM ADMINISTRATION ###
- **Package Management:** Use `apt update && apt upgrade -y` for updates
- **Service Management:** Prefer `systemctl` over `service` when available
- **Logging:** Check `/var/log/syslog` and `/var/log/auth.log` for system events
- **Monitoring:** Use `systemctl status` for service health, `journalctl` for logs
- **Security:** Regularly run `apt list --upgradable` and apply security patches
- **Backups:** Never modify system files without creating backups first
""",
    },
    "SafetyFirst": {
        "description": "Risk-averse system administration principles.",
        "triggers": ["safe", "safety", "risk", "caution", "careful", "conservative"],
        "content": """
### SPECIALIZED CONTEXT: SAFETY-FIRST SYSTEM ADMINISTRATION ###
- **Principle of Least Privilege:** Use minimum required permissions
- **Change Management:** Document all changes before making them
- **Rollback Planning:** Always have a way to revert changes
- **Verification:** Validate system state before and after changes
- **Non-Destructive:** Prefer read-only operations when uncertain
- **Idempotency:** Design operations to be safely repeatable
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
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def log(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-' * 40}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)


# --- ENHANCED SAFETY TOOLS ---


class SafetyChecker:
    """Handles safety validation of commands."""

    @staticmethod
    def is_command_safe(
        command: str, safety_level: str = SAFETY_LEVEL
    ) -> tuple[bool, str]:
        """
        Check if a command is safe to execute.
        Returns (is_safe, reason_if_unsafe)
        """
        command = command.strip()

        # Empty command check
        if not command:
            return False, "Empty command"

        # Check against dangerous patterns
        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Command matches dangerous pattern: {pattern}"

        # For strict mode, only allow explicitly safe commands
        if safety_level == "strict":
            # Check if command matches any safe patterns
            is_safe_pattern = False
            for pattern in SAFE_COMMAND_PATTERNS:
                if re.match(pattern, command):
                    is_safe_pattern = True
                    break

            if not is_safe_pattern:
                # Additional checks for common safe commands
                safe_prefixes = [
                    "echo ",
                    "ls ",
                    "cat ",
                    "grep ",
                    "head ",
                    "tail ",
                    "mkdir ",
                    "cp ",
                    "mv ",
                    "chmod ",
                    "chown ",
                    "df ",
                    "du ",
                    "free ",
                    "ps ",
                    "top ",
                    "systemctl ",
                    "service ",
                    "apt ",
                    "which ",
                    "whoami ",
                    "hostname ",
                    "date ",
                    "uname ",
                    "lsb_release ",
                    "netstat ",
                    "ss ",
                    "ping ",
                    "traceroute ",
                    "mtr ",
                    "journalctl ",
                    "dmesg ",
                    "lsblk ",
                    "blkid ",
                    "fdisk ",
                ]

                is_safe_prefix = any(
                    command.startswith(prefix) for prefix in safe_prefixes
                )

                if not is_safe_prefix:
                    return (
                        False,
                        f"Command not in approved safe list for strict mode: {command}",
                    )

        return True, "Command passed safety check"


class TerminalTool:
    @staticmethod
    def execute(command: str) -> str:
        # Safety check
        is_safe, reason = SafetyChecker.is_command_safe(command)
        if not is_safe:
            return f"Error: Command blocked by safety filter - {reason}"

        # Additional blocking for obvious destructive commands
        if any(x in command for x in ["rm -rf /", ":(){ :|:& };:"]):
            return "Error: High-risk command blocked by safety filter."

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
    # Check virtual environment
    check_virtual_environment()

    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response.\n\n"
        "**SAFETY:** You operate in a risk-averse mode. Only suggest commands that are:\n"
        "- Non-destructive\n"
        "- Reversible or have clear rollback procedures\n"
        "- Appropriate for Ubuntu 24.04 LTS systems\n"
        "- Well-understood and documented\n"
        "- Never suggest commands that could compromise system integrity\n"
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

                # Safety check before asking for confirmation
                is_safe, reason = SafetyChecker.is_command_safe(cmd)
                if not is_safe:
                    print(f"[!] Safety violation: {reason}")
                    execution_result = (
                        f"Error: Command blocked by safety filter - {reason}"
                    )
                    logger.log("SYSTEM", f"Command blocked: {reason}")
                    print(f"[*] Output:\n{execution_result}")
                else:
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


def run_single_prompt(prompt: str):
    """Run a single prompt and exit."""
    # Check virtual environment
    check_virtual_environment()

    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response.\n\n"
        "**SAFETY:** You operate in a risk-averse mode. Only suggest commands that are:\n"
        "- Non-destructive\n"
        "- Reversible or have clear rollback procedures\n"
        "- Appropriate for Ubuntu 24.04 LTS systems\n"
        "- Well-understood and documented\n"
        "- Never suggest commands that could compromise system integrity\n"
    )

    print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    history = []

    logger.log("USER", prompt)

    specialized_context = ContextManager.get_relevant_context(prompt)
    current_system_message = base_system_prompt
    if specialized_context:
        current_system_message += f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"

    messages = [{"role": "system", "content": current_system_message}]
    messages.append({"role": "user", "content": prompt})
    history.append({"role": "user", "content": prompt})

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

            # Safety check before asking for confirmation
            is_safe, reason = SafetyChecker.is_command_safe(cmd)
            if not is_safe:
                print(f"[!] Safety violation: {reason}")
                execution_result = f"Error: Command blocked by safety filter - {reason}"
                logger.log("SYSTEM", f"Command blocked: {reason}")
                print(f"[*] Output:\n{execution_result}")
            else:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSAgent - AI-powered terminal agent")
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        help="Execute a single prompt and exit (instead of interactive mode)",
    )
    parser.add_argument(
        "-l",
        "--loop",
        type=str,
        help="Run in a loop with the specified prompt (for continuous agentic behavior)",
    )

    args = parser.parse_args()

    if args.prompt:
        run_single_prompt(args.prompt)
    elif args.loop:
        # Loop mode: continuously execute the same prompt
        print(f"--- LOOP MODE: Repeatedly executing prompt: '{args.loop}' ---")
        print("Press Ctrl+C to exit")
        try:
            while True:
                run_single_prompt(args.loop)
                print(
                    "\n--- Loop iteration completed. Waiting 5 seconds before next iteration ---\n"
                )
                time.sleep(5)  # Wait 5 seconds between iterations
        except KeyboardInterrupt:
            print("\n--- Loop mode terminated by user ---")
    else:
        # Default interactive mode
        run_agentic_session()
